import { ROUTES, ROLES } from './constants.js';
import * as state from './state.js';
import { updateSidebarActiveLink } from './components/sidebar.js';
import { 
    initializeRecruiterDashboard, 
    initializeRecruiterScreen, 
    initializeRecruiterProfile 
} from './pages/recruiter.js';
import {
    initializeCandidateDashboard,
    initializeCandidateScreen,
    initializeCandidateProfile
} from './pages/candidate.js';
import {
    showForgotPasswordView,
    showResetPasswordView,
    resetAuthModalToTabs
} from './pages/login.js';

/**
 * Handles recruiter workspace routing sub-views.
 */
export function handleRecruiterRouting(hash) {
    const recViewDashboard = document.getElementById('rec-view-dashboard');
    const recViewScreen = document.getElementById('rec-view-screen');
    const recViewProfile = document.getElementById('rec-view-profile');
    const recPageTitle = document.getElementById('rec-page-title');
    
    if (!recViewDashboard || !recViewScreen || !recViewProfile || !recPageTitle) {
        return;
    }

    recViewDashboard.classList.add('hidden');
    recViewScreen.classList.add('hidden');
    recViewProfile.classList.add('hidden');
    
    updateSidebarActiveLink(hash);
    
    if (hash === ROUTES.DASHBOARD) {
        recViewDashboard.classList.remove('hidden');
        recPageTitle.textContent = "Dashboard";
        initializeRecruiterDashboard();
    } else if (hash === ROUTES.SCREEN) {
        recViewScreen.classList.remove('hidden');
        recPageTitle.textContent = "Resume Screening";
        initializeRecruiterScreen();
    } else if (hash === ROUTES.PROFILE) {
        recViewProfile.classList.remove('hidden');
        recPageTitle.textContent = "My Profile";
        initializeRecruiterProfile();
    }
}

/**
 * Handles candidate workspace routing sub-views.
 */
export function handleCandidateRouting(hash) {
    const candViewDashboard = document.getElementById('cand-view-dashboard');
    const candViewScreen = document.getElementById('cand-view-screen');
    const candViewProfile = document.getElementById('cand-view-profile');
    const candPageTitle = document.getElementById('cand-page-title');

    if (!candViewDashboard || !candViewScreen || !candViewProfile || !candPageTitle) {
        return;
    }

    candViewDashboard.classList.add('hidden');
    candViewScreen.classList.add('hidden');
    candViewProfile.classList.add('hidden');

    updateSidebarActiveLink(hash);

    if (hash === ROUTES.CANDIDATE_DASHBOARD) {
        candViewDashboard.classList.remove('hidden');
        candPageTitle.textContent = "Dashboard";
        initializeCandidateDashboard();
    } else if (hash === ROUTES.CANDIDATE_SCREEN) {
        candViewScreen.classList.remove('hidden');
        candPageTitle.textContent = "Resume Analysis";
        initializeCandidateScreen();
    } else if (hash === ROUTES.CANDIDATE_PROFILE) {
        candViewProfile.classList.remove('hidden');
        candPageTitle.textContent = "My Profile";
        initializeCandidateProfile();
    }
}

/**
 * Parses a hash string and window query string into its route path and combined URLSearchParams.
 * Conceptually: Supports both '#/reset-password?oobCode=XYZ' and '?mode=resetPassword&oobCode=XYZ#/reset-password'
 */
export function parseHash(hash = window.location.hash) {
    const windowParams = new URLSearchParams(window.location.search);
    if (!hash) {
        return { route: '', params: windowParams };
    }
    const [routePart, queryPart] = hash.split('?');
    const hashParams = new URLSearchParams(queryPart || '');

    // Merge window and hash query parameters
    const combinedParams = new URLSearchParams();
    for (const [key, val] of windowParams.entries()) {
        combinedParams.set(key, val);
    }
    for (const [key, val] of hashParams.entries()) {
        combinedParams.set(key, val);
    }

    return {
        route: routePart || '',
        params: combinedParams
    };
}

let lastHandledRoute = null;
let routerInitialized = false;

/**
 * Central routing router entry point. Enforces role-based route access limits.
 * @param {boolean} force - Whether to bypass duplicate route checking and force handler execution.
 */
export function handleRouting(force = false) {
    const user = state.getUser();
    const { route, params } = parseHash(window.location.hash);
    const pathname = window.location.pathname.toLowerCase();

    // Prevent duplicate routing execution for the exact same route state unless forced
    const fullRouteKey = `${pathname}:${window.location.hash}:${user ? (user.id || user.firebase_uid) : 'anon'}`;
    if (!force && lastHandledRoute === fullRouteKey) {
        return;
    }
    lastHandledRoute = fullRouteKey;

    // 1. Password Reset Action Code Handling (supports Firebase mode=resetPassword or #/reset-password with oobCode/token)
    const mode = params.get('mode');
    const oobCode = params.get('oobCode') || params.get('code') || params.get('token') || '';

    if (mode === 'resetPassword' || route === ROUTES.RESET_PASSWORD || oobCode) {
        const authModal = document.getElementById('auth-modal');
        if (authModal) {
            authModal.classList.remove('hidden');
            showResetPasswordView(oobCode);
        }
        return;
    }

    // 2. Forgot Password: #/forgot-password
    if (route === ROUTES.FORGOT_PASSWORD) {
        const authModal = document.getElementById('auth-modal');
        if (authModal) {
            authModal.classList.remove('hidden');
            showForgotPasswordView();
        }
        return;
    }

    // 3. Unauthenticated User Routes (Login / Sign Up)
    if (!user) {
        if (route === ROUTES.LOGIN || route === ROUTES.SIGNUP || route === '') {
            const authModal = document.getElementById('auth-modal');
            if (authModal) {
                if (route === ROUTES.LOGIN || route === ROUTES.SIGNUP) {
                    authModal.classList.remove('hidden');
                }
                resetAuthModalToTabs();
                const isLogin = route === ROUTES.LOGIN;
                const tabLogin = document.getElementById('tab-login');
                const tabSignup = document.getElementById('tab-signup');
                const loginPlane = document.getElementById('login-plane');
                const signupPlane = document.getElementById('signup-plane');
                if (tabLogin) tabLogin.classList.toggle('active', isLogin);
                if (tabSignup) tabSignup.classList.toggle('active', !isLogin);
                if (loginPlane) {
                    loginPlane.classList.toggle('hidden', !isLogin);
                    loginPlane.classList.toggle('active-plane', isLogin);
                }
                if (signupPlane) {
                    signupPlane.classList.toggle('hidden', isLogin);
                    signupPlane.classList.toggle('active-plane', !isLogin);
                }
            }
        }
        return;
    }

    // 4. Authenticated Workspace Routes
    if (pathname.includes('recruiter')) {
        const currentHash = route || ROUTES.DASHBOARD;
        if (currentHash.startsWith("#/candidate")) {
            window.location.hash = ROUTES.DASHBOARD;
            return;
        }
        handleRecruiterRouting(currentHash);
    } else if (pathname.includes('candidate')) {
        const currentHash = route || ROUTES.CANDIDATE_DASHBOARD;
        if (currentHash.startsWith("#/recruiter")) {
            window.location.hash = ROUTES.CANDIDATE_DASHBOARD;
            return;
        }
        handleCandidateRouting(currentHash);
    }
}

/**
 * Registers hashchange and popstate routing event triggers with single registration guard.
 */
export function initRouter() {
    if (routerInitialized) return;
    routerInitialized = true;

    window.addEventListener('hashchange', () => {
        handleRouting();
    });
    window.addEventListener('popstate', () => {
        handleRouting();
    });
}

