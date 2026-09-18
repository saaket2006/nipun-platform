import * as state from '../state.js';
import { checkAuthStatus } from '../auth.js';
import { showError, validatePassword } from '../utils.js';
import { auth, createUserWithEmailAndPassword, sendEmailVerification } from '../firebase-init.js?v=5';

let initialized = false;

/**
 * Binds event listeners for the Sign Up page (runs once on startup).
 */
export function initSignupPage() {
    if (initialized) return;

    const signupForm = document.getElementById('signup-form');
    const signupEmailInput = document.getElementById('signup-email');
    const signupPasswordInput = document.getElementById('signup-password');
    const emailSignupBtn = document.getElementById('email-signup-btn');
    const authErrorMsg = document.getElementById('auth-error');

    const passwordConstraints = {
        length: document.getElementById('constraint-length'),
        number: document.getElementById('constraint-number'),
        special: document.getElementById('constraint-special')
    };

    // Password Validation Real-time
    signupPasswordInput.addEventListener('input', () => {
        validatePassword(signupPasswordInput.value, passwordConstraints);
    });

    // Signup Submit via Firebase Auth
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = signupEmailInput.value.trim();
        const password = signupPasswordInput.value;

        if (!validatePassword(password, passwordConstraints)) {
            showError(authErrorMsg, "Please meet all password requirements.");
            return;
        }

        const btnText = emailSignupBtn.querySelector('span');
        btnText.textContent = "Creating Account...";
        emailSignupBtn.disabled = true;
        authErrorMsg.classList.add('hidden');

        try {
            // 1. Create user in Firebase Auth
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            
            // 2. Dispatch verification email immediately
            try {
                await sendEmailVerification(userCredential.user);
            } catch (verErr) {
                console.warn("Could not dispatch initial email verification:", verErr);
            }

            // 3. Set token in state and trigger auth status routing
            const idToken = await userCredential.user.getIdToken();
            state.setToken(idToken);
            signupForm.reset();
            Object.values(passwordConstraints).forEach(c => { if (c) c.className = ''; });

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
 * Initializes/resets the Sign Up page view state.
 */
export function initializeSignupPage() {
    const signupForm = document.getElementById('signup-form');
    if (signupForm) signupForm.reset();

    const passwordConstraints = {
        length: document.getElementById('constraint-length'),
        number: document.getElementById('constraint-number'),
        special: document.getElementById('constraint-special')
    };

    Object.values(passwordConstraints).forEach(c => {
        if (c) c.className = '';
    });
}
