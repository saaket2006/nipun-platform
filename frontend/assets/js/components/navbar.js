import * as state from '../state.js';
import { clearRecruiterWorkspaceState } from '../pages/recruiter.js';
import { clearCandidateWorkspaceState } from '../pages/candidate.js';
import { auth, signOut } from '../firebase-init.js?v=5';
import { handleRouting } from '../router.js';
import { ROLES, ROUTES } from '../constants.js';
import { initSidebar } from './sidebar.js';

/**
 * Handles logo navigation across authenticated and unauthenticated states.
 */
export function handleLogoNavigation(e) {
    if (e && typeof e.preventDefault === 'function') {
        e.preventDefault();
    }
    const user = state.getUser();
    const fbUser = auth ? auth.currentUser : null;
    const isAuthenticated = !!(user || fbUser);
    const pathname = window.location.pathname.toLowerCase();
    const isRecruiterPage = pathname.includes('recruiter');
    const isCandidatePage = pathname.includes('candidate');
    const isLandingPage = pathname === '/' || pathname.endsWith('index.html') || pathname === '';

    if (isAuthenticated) {
        const role = user ? user.role : (isRecruiterPage ? ROLES.RECRUITER : (isCandidatePage ? ROLES.CANDIDATE : null));

        if (role === ROLES.RECRUITER || (!role && isRecruiterPage)) {
            if (isRecruiterPage) {
                if (window.location.hash === ROUTES.DASHBOARD) {
                    handleRouting(true);
                } else {
                    window.location.hash = ROUTES.DASHBOARD;
                }
            } else {
                window.location.href = `recruiter.html${ROUTES.DASHBOARD}`;
            }
            return;
        }

        if (role === ROLES.CANDIDATE || (!role && isCandidatePage)) {
            if (isCandidatePage) {
                if (window.location.hash === ROUTES.CANDIDATE_DASHBOARD) {
                    handleRouting(true);
                } else {
                    window.location.hash = ROUTES.CANDIDATE_DASHBOARD;
                }
            } else {
                window.location.href = `candidate.html${ROUTES.CANDIDATE_DASHBOARD}`;
            }
            return;
        }

        if (isLandingPage && !role) {
            window.location.href = 'index.html';
            return;
        }
    }

    // Unauthenticated user
    if (isLandingPage) {
        if (window.location.hash) {
            window.location.hash = '';
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
        window.location.href = 'index.html';
    }
}

/**
 * Helper to execute complete Firebase and client-side sign out.
 */
async function handleLogout(clearWorkspaceCallback) {
    state.clearState();
    if (clearWorkspaceCallback) {
        clearWorkspaceCallback();
    }
    try {
        await signOut(auth);
    } catch (err) {
        console.warn("Firebase sign out error:", err);
    }
    window.location.href = 'index.html#/login';
}

/**
 * Initializes the profile nav drop-down controls, logos, and logout actions.
 * @param {Function} clearCandidateStateCallback - Callback to clear candidate view variables
 */
export function initNavbar(clearCandidateStateCallback) {
    const userProfileDropdown = document.getElementById('user-profile-dropdown');
    const userTrigger = document.getElementById('user-trigger');
    const signOutBtn = document.getElementById('sign-out-btn');
    const recSignOutBtn = document.getElementById('rec-sign-out-btn');
    const candSignOutBtn = document.getElementById('cand-sign-out-btn');

    // Profile Dropdown Trigger Handlers
    if (userTrigger && userProfileDropdown) {
        userTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            userProfileDropdown.classList.toggle('active');
        });

        document.addEventListener('click', (e) => {
            if (!userProfileDropdown.contains(e.target)) {
                userProfileDropdown.classList.remove('active');
            }
        });
    }

    // Candidate Legacy View Sign Out Handler
    if (signOutBtn) {
        signOutBtn.addEventListener('click', () => {
            handleLogout(clearCandidateStateCallback);
        });
    }

    // Recruiter workspace sign out link
    if (recSignOutBtn) {
        recSignOutBtn.addEventListener('click', () => {
            handleLogout(clearRecruiterWorkspaceState);
        });
    }

    // Candidate workspace sign out link
    if (candSignOutBtn) {
        candSignOutBtn.addEventListener('click', () => {
            handleLogout(clearCandidateWorkspaceState);
        });
    }

    // Sidebar Logo and Landing Logo navigation
    const recSidebarLogo = document.getElementById('recruiter-sidebar-logo');
    if (recSidebarLogo) {
        recSidebarLogo.addEventListener('click', handleLogoNavigation);
    }

    const candSidebarLogo = document.getElementById('candidate-sidebar-logo');
    if (candSidebarLogo) {
        candSidebarLogo.addEventListener('click', handleLogoNavigation);
    }

    const landingLogo = document.getElementById('landing-logo');
    if (landingLogo) {
        landingLogo.addEventListener('click', handleLogoNavigation);
    }

    // Fallback: any other element with class .sidebar-logo
    const genericLogos = document.querySelectorAll('.sidebar-logo');
    genericLogos.forEach(logoEl => {
        if (logoEl !== recSidebarLogo && logoEl !== candSidebarLogo) {
            logoEl.addEventListener('click', handleLogoNavigation);
        }
    });

    // Initialize sidebar toggle state & event listeners
    initSidebar();
}
