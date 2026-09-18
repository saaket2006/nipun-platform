import * as state from '../state.js';
import { clearRecruiterWorkspaceState } from '../pages/recruiter.js';
import { clearCandidateWorkspaceState } from '../pages/candidate.js';
import { auth, signOut } from '../firebase-init.js?v=5';

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
 * Initializes the profile nav drop-down controls and logs.
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

    // Sidebar Logo: navigate back to landing page
    const recSidebarLogo = document.getElementById('recruiter-sidebar-logo');
    if (recSidebarLogo) {
        recSidebarLogo.addEventListener('click', () => {
            window.location.href = 'index.html';
        });
    }

    const candSidebarLogo = document.getElementById('candidate-sidebar-logo');
    if (candSidebarLogo) {
        candSidebarLogo.addEventListener('click', () => {
            window.location.href = 'index.html';
        });
    }
}
