import * as api from './api.js';
import * as state from './state.js';
import { ROLES } from './constants.js';
import { handleRouting } from './router.js';
import { auth, signOut, sendEmailVerification, reload, onAuthStateChanged } from './firebase-init.js?v=5';

let resendCooldownTimer = null;
let resendSecondsRemaining = 0;
let isCheckingVerification = false;

/**
 * Renders or reveals the Email Verification Modal if unverified.
 */
export function showEmailVerificationModal(user) {
    let modal = document.getElementById('email-verification-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'email-verification-modal';
        modal.className = 'auth-modal-overlay';
        modal.innerHTML = `
            <div class="glass-card auth-card" style="text-align: center; max-width: 440px;">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">✉️</div>
                <h2 style="margin-bottom: 0.5rem;">Verify Your Email</h2>
                <p style="font-size: 0.95rem; color: #94a3b8; line-height: 1.5; margin-bottom: 1.25rem;">
                    We've sent a verification link to <strong id="verification-user-email" style="color: #10b981;"></strong>.
                    Please confirm your email address to access Nipun.
                </p>
                <div id="verification-feedback" class="auth-success-message hidden" style="margin-bottom: 1rem; text-align: center;"></div>
                <div id="verification-error" class="auth-error-message hidden" style="margin-bottom: 1rem; text-align: center;"></div>

                <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 1rem;">
                    <button type="button" id="check-verification-btn" class="glow-btn">
                        <span>I've verified my email — Check again</span>
                    </button>
                    <button type="button" id="resend-verification-btn" class="google-btn" style="justify-content: center;">
                        <span>Resend verification email</span>
                    </button>
                    <button type="button" id="verification-logout-btn" class="secondary-link" style="background: none; border: none; cursor: pointer; padding: 8px; color: #ef4444;">
                        Log Out
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Bind interactive buttons
        const resendBtn = modal.querySelector('#resend-verification-btn');
        const checkBtn = modal.querySelector('#check-verification-btn');
        const logoutBtn = modal.querySelector('#verification-logout-btn');
        const feedback = modal.querySelector('#verification-feedback');
        const errorMsg = modal.querySelector('#verification-error');

        resendBtn.addEventListener('click', async () => {
            if (resendSecondsRemaining > 0 || !auth.currentUser) return;
            try {
                errorMsg.classList.add('hidden');
                await sendEmailVerification(auth.currentUser);
                feedback.textContent = "A new verification email has been dispatched. Check your inbox!";
                feedback.classList.remove('hidden');

                // Start 60s cooldown
                resendSecondsRemaining = 60;
                resendBtn.disabled = true;
                const updateBtnText = () => {
                    if (resendSecondsRemaining > 0) {
                        resendBtn.querySelector('span').textContent = `Resend in ${resendSecondsRemaining}s`;
                        resendSecondsRemaining--;
                        resendCooldownTimer = setTimeout(updateBtnText, 1000);
                    } else {
                        resendBtn.disabled = false;
                        resendBtn.querySelector('span').textContent = "Resend verification email";
                    }
                };
                updateBtnText();
            } catch (err) {
                console.error("Resend verification email failed:", err);
                errorMsg.textContent = "Failed to resend verification email: " + (err.message || "Please wait a moment and try again.");
                errorMsg.classList.remove('hidden');
            }
        });

        checkBtn.addEventListener('click', async () => {
            if (isCheckingVerification) return;
            isCheckingVerification = true;

            const btnSpan = checkBtn.querySelector('span');
            btnSpan.textContent = "Checking status...";
            checkBtn.disabled = true;
            errorMsg.classList.add('hidden');

            try {
                if (auth.currentUser) {
                    console.log("[AUTH] Verification check started");
                    await reload(auth.currentUser);
                    console.log(`[AUTH] user.reload complete, emailVerified=${auth.currentUser.emailVerified}`);
                    if (auth.currentUser.emailVerified) {
                        btnSpan.textContent = "Verified! Redirecting...";
                        const freshToken = await auth.currentUser.getIdToken(true);
                        state.setToken(freshToken);
                        console.log("[AUTH] Token refreshed with verified email claim. Hiding modal and checking status.");
                        hideEmailVerificationModal();
                        await checkAuthStatus();
                        return;
                    } else {
                        errorMsg.textContent = "Email is not verified yet. Please click the link in your inbox.";
                        errorMsg.classList.remove('hidden');
                        btnSpan.textContent = "I've verified my email — Check again";
                        checkBtn.disabled = false;
                    }
                }
            } catch (err) {
                console.error("[AUTH] Verification check failed:", err);
                errorMsg.textContent = "Could not verify status. Please try again.";
                errorMsg.classList.remove('hidden');
                btnSpan.textContent = "I've verified my email — Check again";
                checkBtn.disabled = false;
            } finally {
                isCheckingVerification = false;
            }
        });

        logoutBtn.addEventListener('click', async () => {
            hideEmailVerificationModal();
            state.clearState();
            try {
                await signOut(auth);
            } catch (err) {
                console.warn("[AUTH] Logout error:", err);
            }
            window.location.replace('index.html#/login');
        });
    }

    const emailEl = modal.querySelector('#verification-user-email');
    if (emailEl && user) {
        emailEl.textContent = user.email || "your email";
    }

    modal.classList.remove('hidden');

    // Hide background app containers while unverified
    const appContainer = document.getElementById('app-container');
    if (appContainer) appContainer.classList.add('hidden');
    const authModal = document.getElementById('auth-modal');
    if (authModal) authModal.classList.add('hidden');
}

export function hideEmailVerificationModal() {
    const modal = document.getElementById('email-verification-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Concurrency mutex and navigation guards
let authCheckPromise = null;
let isNavigating = false;
let authListenerAttached = false;

/**
 * Ensures Firebase Auth has restored state from IndexedDB/localStorage before checking.
 */
export async function waitForAuthState() {
    if (typeof auth.authStateReady === 'function') {
        await auth.authStateReady();
        return auth.currentUser;
    }
    return new Promise((resolve) => {
        const unsubscribe = onAuthStateChanged(auth, (user) => {
            unsubscribe();
            resolve(user);
        });
    });
}

/**
 * Checks authentication status and routes appropriately based on user profile completion and role.
 * Deduplicates concurrent calls via a single shared in-flight Promise.
 */
export async function checkAuthStatus() {
    if (authCheckPromise) {
        return authCheckPromise;
    }
    authCheckPromise = (async () => {
        try {
            return await _doCheckAuthStatus();
        } finally {
            authCheckPromise = null;
        }
    })();
    return authCheckPromise;
}

async function _doCheckAuthStatus() {
    if (isNavigating) return;

    await waitForAuthState();
    const fbUser = auth.currentUser;
    const pathname = window.location.pathname.toLowerCase();

    const isLandingPage = pathname === '/' || pathname.endsWith('index.html') || pathname === '';
    const isOnboardingPage = pathname.includes('onboarding');
    const isRecruiterPage = pathname.includes('recruiter');
    const isCandidatePage = pathname.includes('candidate');

    console.log(`[GUARD] checkAuthStatus on ${pathname} (authenticated=${!!fbUser})`);

    // 1. Unauthenticated User Check
    if (!fbUser) {
        hideEmailVerificationModal();
        if (!isLandingPage) {
            console.log("[GUARD] Unauthenticated on protected route -> redirecting to index.html#/login");
            isNavigating = true;
            window.location.replace('index.html#/login');
        } else {
            const landingContainer = document.getElementById('landing-container');
            if (landingContainer) {
                landingContainer.classList.remove('hidden');
                if (window.initAllLandingAnimations) {
                    window.initAllLandingAnimations();
                } else if (window.ScrollTrigger) {
                    ScrollTrigger.refresh();
                }
            }
        }
        return;
    }

    // 2. Email Verification Check for Password Provider Users
    const isPasswordProvider = fbUser.providerData && fbUser.providerData.some(p => p.providerId === 'password');
    if (isPasswordProvider && !fbUser.emailVerified) {
        // Attempt a server reload to ensure local IndexedDB cache is not lagging behind verified status
        try {
            await reload(fbUser);
            console.log(`[GUARD] Pre-verification check reload: emailVerified=${fbUser.emailVerified}`);
        } catch (reloadErr) {
            console.warn("[GUARD] Verification reload check error:", reloadErr);
        }
    }

    if (isPasswordProvider && !fbUser.emailVerified) {
        console.log("[GUARD] User email not verified yet -> routing to verification modal");
        if (!isLandingPage) {
            isNavigating = true;
            window.location.replace('index.html');
            return;
        }
        showEmailVerificationModal(fbUser);
        return;
    } else {
        hideEmailVerificationModal();
    }

    // 3. Authenticated & Verified: Resolve PostgreSQL Profile
    try {
        const user = await api.getMe();
        state.setUser(user);
        state.setOnboardingStatus(user.profile_completed);
        console.log(`[GUARD] /me resolved: role=${user.role}, profile_completed=${user.profile_completed}`);

        if (user.profile_completed === false) {
            if (!isOnboardingPage) {
                console.log("[GUARD] Profile incomplete -> navigating to onboarding.html");
                isNavigating = true;
                window.location.replace('onboarding.html');
            } else {
                const onboardingModal = document.getElementById('onboarding-modal');
                if (onboardingModal) onboardingModal.classList.remove('hidden');
            }
            return;
        }

        if (user.role === ROLES.RECRUITER) {
            if (!isRecruiterPage) {
                console.log("[GUARD] Recruiter role verified -> navigating to recruiter.html");
                isNavigating = true;
                window.location.replace('recruiter.html');
            } else {
                const recruiterContainer = document.getElementById('recruiter-container');
                if (recruiterContainer) recruiterContainer.classList.remove('hidden');
                // Mount and fetch recruiter dashboard automatically
                handleRouting(true);
            }
        } else if (user.role === ROLES.CANDIDATE) {
            if (!isCandidatePage) {
                console.log("[GUARD] Candidate role verified -> navigating to candidate.html");
                isNavigating = true;
                window.location.replace('candidate.html');
            } else {
                const candidateContainer = document.getElementById('candidate-container');
                if (candidateContainer) candidateContainer.classList.remove('hidden');
                // Mount and fetch candidate dashboard automatically
                handleRouting(true);
            }
        }
    } catch (error) {
        console.error("[GUARD] Auth status verification failed:", error);
        state.clearState();
        if (!isLandingPage) {
            isNavigating = true;
            window.location.replace('index.html#/login');
        } else {
            const landingContainer = document.getElementById('landing-container');
            if (landingContainer) {
                landingContainer.classList.remove('hidden');
                if (window.initAllLandingAnimations) {
                    window.initAllLandingAnimations();
                } else if (window.ScrollTrigger) {
                    ScrollTrigger.refresh();
                }
            }
        }
    }
}

// Global Auth State Observer with single-attachment guard
export function initAuthListener() {
    if (authListenerAttached) return;
    authListenerAttached = true;

    onAuthStateChanged(auth, async (fbUser) => {
        console.log(`[AUTH] onAuthStateChanged: ${fbUser ? `uid=${fbUser.uid}, emailVerified=${fbUser.emailVerified}` : 'unauthenticated'}`);
        if (fbUser) {
            try {
                const token = await fbUser.getIdToken();
                state.setToken(token);
            } catch (e) {
                console.warn("[AUTH] Could not extract token on auth change:", e);
            }
        } else {
            state.clearState();
        }
        await checkAuthStatus();
    });
}

