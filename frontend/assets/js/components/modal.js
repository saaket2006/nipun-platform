import { initializeSignupPage } from '../pages/signup.js?v=35';

let modalsInitialized = false;

/**
 * Opens the Auth Modal in the specified mode ('login' | 'signup' | 'forgot-password' | 'reset-password').
 * Directly updates modal DOM and synchronizes history state without brittle hashchange reliance.
 * @param {string} mode - 'login', 'signup', 'forgot-password', or 'reset-password'
 * @param {string} [token] - Optional token for password reset
 */
export function openAuthModal(mode = 'login', token = '') {
    const authModal = document.getElementById('auth-modal');
    if (!authModal) return;

    // Show modal
    authModal.classList.remove('hidden');
    authModal.setAttribute('aria-hidden', 'false');

    // Close mobile navigation drawer if open
    const mobileDrawer = document.getElementById('landing-mobile-drawer');
    if (mobileDrawer && !mobileDrawer.classList.contains('hidden')) {
        mobileDrawer.classList.add('hidden');
        const menuBtn = document.getElementById('landing-mobile-menu-btn');
        if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
    }

    const tabLogin = document.getElementById('tab-login');
    const tabSignup = document.getElementById('tab-signup');
    const loginPlane = document.getElementById('login-plane');
    const signupPlane = document.getElementById('signup-plane');
    const forgotPlane = document.getElementById('forgot-password-plane');
    const resetPlane = document.getElementById('reset-password-plane');
    const tabsContainer = document.getElementById('auth-tabs-container');
    const divider = document.getElementById('auth-modal-divider');
    const googleBtn = document.getElementById('google-login-btn');
    const authErrorMsg = document.getElementById('auth-error');

    if (authErrorMsg) {
        authErrorMsg.classList.add('hidden');
        authErrorMsg.textContent = '';
    }

    // Reset signup form and conditional confirm password state
    initializeSignupPage();

    if (mode === 'signup') {
        if (tabsContainer) tabsContainer.classList.remove('hidden');
        if (divider) divider.classList.remove('hidden');
        if (googleBtn) googleBtn.classList.remove('hidden');
        if (tabLogin) tabLogin.classList.remove('active');
        if (tabSignup) tabSignup.classList.add('active');
        if (loginPlane) {
            loginPlane.classList.add('hidden');
            loginPlane.classList.remove('active-plane');
        }
        if (signupPlane) {
            signupPlane.classList.remove('hidden');
            signupPlane.classList.add('active-plane');
        }
        if (forgotPlane) forgotPlane.classList.add('hidden');
        if (resetPlane) resetPlane.classList.add('hidden');
    } else if (mode === 'forgot-password') {
        if (tabsContainer) tabsContainer.classList.add('hidden');
        if (divider) divider.classList.add('hidden');
        if (googleBtn) googleBtn.classList.add('hidden');
        if (loginPlane) loginPlane.classList.add('hidden');
        if (signupPlane) signupPlane.classList.add('hidden');
        if (resetPlane) resetPlane.classList.add('hidden');
        if (forgotPlane) {
            forgotPlane.classList.remove('hidden');
            forgotPlane.classList.add('active-plane');
        }
    } else if (mode === 'reset-password') {
        if (tabsContainer) tabsContainer.classList.add('hidden');
        if (divider) divider.classList.add('hidden');
        if (googleBtn) googleBtn.classList.add('hidden');
        if (loginPlane) loginPlane.classList.add('hidden');
        if (signupPlane) signupPlane.classList.add('hidden');
        if (forgotPlane) forgotPlane.classList.add('hidden');
        if (resetPlane) {
            resetPlane.classList.remove('hidden');
            resetPlane.classList.add('active-plane');
        }
        const resetTokenInput = document.getElementById('reset-token-input');
        if (resetTokenInput && token) {
            resetTokenInput.value = token;
        }
    } else {
        // Default to login
        mode = 'login';
        if (tabsContainer) tabsContainer.classList.remove('hidden');
        if (divider) divider.classList.remove('hidden');
        if (googleBtn) googleBtn.classList.remove('hidden');
        if (tabLogin) tabLogin.classList.add('active');
        if (tabSignup) tabSignup.classList.remove('active');
        if (loginPlane) {
            loginPlane.classList.remove('hidden');
            loginPlane.classList.add('active-plane');
        }
        if (signupPlane) {
            signupPlane.classList.add('hidden');
            signupPlane.classList.remove('active-plane');
        }
        if (forgotPlane) forgotPlane.classList.add('hidden');
        if (resetPlane) resetPlane.classList.add('hidden');
    }

    // Keep URL hash in sync cleanly without retriggering full routing loop
    const targetHash = `#/${mode}`;
    if (window.location.hash !== targetHash) {
        if (window.history && window.history.replaceState) {
            window.history.replaceState(null, '', targetHash);
        } else {
            window.location.hash = targetHash;
        }
    }
}

/**
 * Closes the Auth Modal and resets the route hash without causing page reload.
 */
export function closeAuthModal() {
    const authModal = document.getElementById('auth-modal');
    if (authModal) {
        authModal.classList.add('hidden');
        authModal.setAttribute('aria-hidden', 'true');
    }
    initializeSignupPage();

    // Clear hash if it is currently an auth hash
    const currentHash = window.location.hash;
    if (currentHash === '#/login' || currentHash === '#/signup' || currentHash === '#/forgot-password' || currentHash.startsWith('#/reset-password')) {
        if (window.history && window.history.replaceState) {
            window.history.replaceState(null, '', window.location.pathname + window.location.search);
        } else {
            window.location.hash = '';
        }
    }
}

/**
 * Initializes generic modals like Contact modal and sets up resilient Auth Modal handlers.
 */
export function initModals() {
    if (modalsInitialized) return;
    modalsInitialized = true;

    const contactModal = document.getElementById('contact-modal');
    const contactTriggerBtn = document.getElementById('contact-trigger-btn');
    const closeContactBtn = document.getElementById('close-contact-btn');

    // Show/Hide Contact Modal
    if (contactTriggerBtn && contactModal && closeContactBtn) {
        contactTriggerBtn.addEventListener('click', () => {
            contactModal.classList.remove('hidden');
        });

        closeContactBtn.addEventListener('click', () => {
            contactModal.classList.add('hidden');
        });

        contactModal.addEventListener('click', (e) => {
            if (e.target === contactModal) {
                contactModal.classList.add('hidden');
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !contactModal.classList.contains('hidden')) {
                contactModal.classList.add('hidden');
            }
        });
    }

    // Hide Name modal / Change name elements as custom name editing is replaced in Phase 1
    const changeNameBtn = document.getElementById('change-name-btn');
    if (changeNameBtn) {
        changeNameBtn.style.display = "none";
    }

    // Setup Auth Modal triggers & dismissals
    const authModal = document.getElementById('auth-modal');
    if (authModal) {
        const authCloseBtn = document.getElementById('auth-close-btn');
        if (authCloseBtn) {
            authCloseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                closeAuthModal();
            });
        }

        // Close on clicking backdrop outside of auth-card
        authModal.addEventListener('click', (e) => {
            if (e.target === authModal) {
                closeAuthModal();
            }
        });

        // Close on Escape keypress
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !authModal.classList.contains('hidden')) {
                closeAuthModal();
            }
        });
    }

    // Resilient Event Delegation for all Auth Triggers across the entire document
    document.addEventListener('click', (e) => {
        const trigger = e.target.closest('[data-auth-modal], .nav-login-btn, .nav-signup-btn, a[href="#/login"], a[href="#/signup"], a[href="#/forgot-password"]');
        if (!trigger) return;

        // Skip internal clicks inside active auth card unless they have an explicit data-auth-modal attribute
        const insideAuthCard = trigger.closest('#auth-modal .auth-card');
        if (insideAuthCard && !trigger.hasAttribute('data-auth-modal')) {
            return;
        }

        if (trigger.tagName === 'A' || trigger.tagName === 'BUTTON') {
            e.preventDefault();
        }

        let mode = trigger.getAttribute('data-auth-modal');
        if (!mode) {
            const href = trigger.getAttribute('href') || '';
            if (trigger.classList.contains('nav-signup-btn') || href === '#/signup') {
                mode = 'signup';
            } else if (href === '#/forgot-password') {
                mode = 'forgot-password';
            } else {
                mode = 'login';
            }
        }

        openAuthModal(mode);
    });
}
