import * as state from '../state.js';
import { checkAuthStatus } from '../auth.js';
import { showError, hideError, validatePassword } from '../utils.js';
import { auth, createUserWithEmailAndPassword, sendEmailVerification } from '../firebase-init.js?v=5';

let initialized = false;

/**
 * Validates whether the confirm password matches the primary password and updates the UI feedback.
 * @param {string} password - The primary password
 * @param {string} confirmPassword - The confirmed password
 * @param {HTMLElement} [feedbackElem] - The inline feedback element
 * @param {HTMLInputElement} [confirmInputElem] - The confirm password input
 * @returns {boolean} Whether the passwords match exactly and are non-empty
 */
export function validatePasswordMatch(password, confirmPassword, feedbackElem, confirmInputElem) {
    if (!confirmPassword) {
        if (feedbackElem) {
            feedbackElem.textContent = '';
            feedbackElem.className = 'password-match-feedback hidden';
        }
        if (confirmInputElem) {
            confirmInputElem.classList.remove('input-match-success', 'input-match-error');
        }
        return false;
    }

    if (password === confirmPassword) {
        if (feedbackElem) {
            feedbackElem.innerHTML = '<span>✓</span> <span>Passwords match.</span>';
            feedbackElem.className = 'password-match-feedback match-success';
        }
        if (confirmInputElem) {
            confirmInputElem.classList.remove('input-match-error');
            confirmInputElem.classList.add('input-match-success');
        }
        const authErrorMsg = document.getElementById('auth-error');
        if (authErrorMsg && (authErrorMsg.textContent === "Passwords do not match." || authErrorMsg.textContent === "Please confirm your password.")) {
            authErrorMsg.classList.add('hidden');
            authErrorMsg.textContent = '';
        }
        return true;
    } else {
        if (feedbackElem) {
            feedbackElem.innerHTML = '<span>✕</span> <span>Passwords do not match.</span>';
            feedbackElem.className = 'password-match-feedback match-error';
        }
        if (confirmInputElem) {
            confirmInputElem.classList.remove('input-match-success');
            confirmInputElem.classList.add('input-match-error');
        }
        return false;
    }
}

/**
 * Binds event listeners for the Sign Up page (runs once on startup).
 */
export function initSignupPage() {
    if (initialized) return;

    const signupForm = document.getElementById('signup-form');
    const signupEmailInput = document.getElementById('signup-email');
    const signupPasswordInput = document.getElementById('signup-password');
    const signupConfirmGroup = document.getElementById('signup-confirm-group');
    const signupConfirmInput = document.getElementById('signup-confirm-password');
    const matchFeedback = document.getElementById('signup-password-match-feedback');
    const emailSignupBtn = document.getElementById('email-signup-btn');
    const authErrorMsg = document.getElementById('auth-error');

    if (!signupForm || !signupPasswordInput || !signupConfirmGroup || !signupConfirmInput) {
        return;
    }

    const passwordConstraints = {
        length: document.getElementById('constraint-length'),
        number: document.getElementById('constraint-number'),
        special: document.getElementById('constraint-special')
    };

    /**
     * Re-evaluates primary password requirements and updates Confirm Password visibility.
     */
    function handlePasswordChange() {
        const passwordVal = signupPasswordInput.value;
        validatePassword(passwordVal, passwordConstraints);

        if (passwordVal.length > 0) {
            // Reveal Confirm Password directly below Password
            if (!signupConfirmGroup.classList.contains('is-visible')) {
                signupConfirmGroup.classList.add('is-visible');
                signupConfirmGroup.setAttribute('aria-hidden', 'false');
            }
            // If user has already entered a confirm password value, re-evaluate match immediately
            if (signupConfirmInput.value.length > 0) {
                validatePasswordMatch(passwordVal, signupConfirmInput.value, matchFeedback, signupConfirmInput);
            }
        } else {
            // When password is empty, hide confirm password and reset its value & feedback
            signupConfirmGroup.classList.remove('is-visible');
            signupConfirmGroup.setAttribute('aria-hidden', 'true');
            signupConfirmInput.value = '';
            validatePasswordMatch('', '', matchFeedback, signupConfirmInput);
        }
    }

    /**
     * Re-evaluates password matching as the user enters the confirmation password.
     */
    function handleConfirmPasswordChange() {
        const passwordVal = signupPasswordInput.value;
        const confirmVal = signupConfirmInput.value;
        validatePasswordMatch(passwordVal, confirmVal, matchFeedback, signupConfirmInput);
    }

    // Attach reactive input listeners for primary password
    signupPasswordInput.addEventListener('input', handlePasswordChange);
    signupPasswordInput.addEventListener('change', handlePasswordChange);
    signupPasswordInput.addEventListener('keyup', handlePasswordChange);
    signupPasswordInput.addEventListener('paste', () => setTimeout(handlePasswordChange, 10));

    // Attach reactive input listeners for confirm password
    signupConfirmInput.addEventListener('input', handleConfirmPasswordChange);
    signupConfirmInput.addEventListener('change', handleConfirmPasswordChange);
    signupConfirmInput.addEventListener('keyup', handleConfirmPasswordChange);
    signupConfirmInput.addEventListener('paste', () => setTimeout(handleConfirmPasswordChange, 10));

    // Signup Submit via Firebase Auth with Strict Validation Gating
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = signupEmailInput.value.trim();
        const password = signupPasswordInput.value;
        const confirmPassword = signupConfirmInput.value;

        // 1. Validate primary password requirements
        if (!validatePassword(password, passwordConstraints)) {
            showError(authErrorMsg, "Please meet all password requirements.");
            signupPasswordInput.focus();
            return;
        }

        // 2. Validate confirm password presence
        if (!confirmPassword) {
            showError(authErrorMsg, "Please confirm your password.");
            signupConfirmInput.focus();
            return;
        }

        // 3. Validate password equality
        if (password !== confirmPassword) {
            showError(authErrorMsg, "Passwords do not match.");
            validatePasswordMatch(password, confirmPassword, matchFeedback, signupConfirmInput);
            signupConfirmInput.focus();
            return;
        }

        const btnText = emailSignupBtn.querySelector('span');
        btnText.textContent = "Creating Account...";
        emailSignupBtn.disabled = true;
        authErrorMsg.classList.add('hidden');

        try {
            // 4. Create user in Firebase Auth — strictly client-side validation passed.
            // Note: Only the primary password is passed to Firebase; confirmPassword is NEVER stored or transmitted.
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            
            // 5. Dispatch verification email immediately
            try {
                await sendEmailVerification(userCredential.user);
            } catch (verErr) {
                console.warn("Could not dispatch initial email verification:", verErr);
            }

            // 6. Set token in state and trigger auth status routing
            const idToken = await userCredential.user.getIdToken();
            state.setToken(idToken);
            initializeSignupPage();

            // checkAuthStatus() will detect that emailVerified is false and render the verification modal
            await checkAuthStatus();
        } catch (error) {
            console.error("Firebase signup failed:", error);
            let message = error.message || "Registration failed. Please try again.";
            if (error.code === "auth/email-already-in-use") {
                message = "An account already exists with this email address.";
            } else if (error.code === "auth/weak-password") {
                message = "The password is too weak. Please use a stronger password.";
            } else if (error.code === "auth/invalid-email") {
                message = "Please enter a valid email address.";
            }
            showError(authErrorMsg, message);
            emailSignupBtn.disabled = false;
        } finally {
            btnText.textContent = "Sign Up";
        }
    });

    initialized = true;
}

/**
 * Initializes and completely resets the Sign Up form and view state.
 * Clears primary password, confirm password, visibility, validation messages, and bullets.
 */
export function initializeSignupPage() {
    const signupForm = document.getElementById('signup-form');
    if (signupForm) signupForm.reset();

    const signupConfirmGroup = document.getElementById('signup-confirm-group');
    if (signupConfirmGroup) {
        signupConfirmGroup.classList.remove('is-visible');
        signupConfirmGroup.setAttribute('aria-hidden', 'true');
    }

    const signupConfirmInput = document.getElementById('signup-confirm-password');
    if (signupConfirmInput) {
        signupConfirmInput.value = '';
        signupConfirmInput.setAttribute('type', 'password');
        signupConfirmInput.classList.remove('input-match-success', 'input-match-error');
    }

    const signupPasswordInput = document.getElementById('signup-password');
    if (signupPasswordInput) {
        signupPasswordInput.value = '';
        signupPasswordInput.setAttribute('type', 'password');
    }

    // Reset password visibility toggle button SVGs inside signup form
    const toggleBtns = document.querySelectorAll('#signup-form .toggle-password-btn');
    toggleBtns.forEach(btn => {
        btn.setAttribute('aria-label', 'Show password');
        const eyeIcon = btn.querySelector('.icon-eye');
        const eyeOffIcon = btn.querySelector('.icon-eye-off');
        if (eyeIcon) eyeIcon.classList.remove('hidden');
        if (eyeOffIcon) eyeOffIcon.classList.add('hidden');
    });

    const matchFeedback = document.getElementById('signup-password-match-feedback');
    if (matchFeedback) {
        matchFeedback.textContent = '';
        matchFeedback.className = 'password-match-feedback hidden';
    }

    const authErrorMsg = document.getElementById('auth-error');
    if (authErrorMsg) {
        authErrorMsg.classList.add('hidden');
        authErrorMsg.textContent = '';
    }

    const passwordConstraints = {
        length: document.getElementById('constraint-length'),
        number: document.getElementById('constraint-number'),
        special: document.getElementById('constraint-special')
    };

    Object.values(passwordConstraints).forEach(c => {
        if (c) c.className = '';
    });
}
