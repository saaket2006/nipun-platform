/**
 * Shared Horizontal Navigation & Responsive Mobile Drawer Component.
 *
 * Manages active route highlights, workspace header state, and responsive
 * mobile slide-over drawer across recruiter and candidate workspaces.
 */

const SIDEBAR_STORAGE_KEY = "nipun_sidebar_collapsed";

const sidebarLinkIds = {
    "#/recruiter/dashboard": "link-rec-dashboard",
    "#/recruiter/screen": "link-rec-screen",
    "#/recruiter/profile": "link-rec-profile",
    "#/candidate/dashboard": "link-cand-dashboard",
    "#/candidate/screen": "link-cand-screen",
    "#/candidate/profile": "link-cand-profile"
};

/**
 * Checks whether the mobile navigation drawer (or legacy sidebar) is collapsed.
 * @returns {boolean}
 */
export function isSidebarCollapsed() {
    const drawer = document.getElementById('mobile-nav-drawer') || document.querySelector('.mobile-nav-drawer');
    if (drawer) {
        return drawer.classList.contains('hidden');
    }
    const sidebar = document.querySelector('.rec-sidebar');
    if (sidebar) {
        return sidebar.classList.contains('collapsed') || !sidebar.classList.contains('expanded');
    }
    return true;
}

/**
 * Expands / opens the mobile navigation drawer.
 * @param {boolean} [animate=true]
 */
export function expandSidebar(animate = true) {
    const drawer = document.getElementById('mobile-nav-drawer') || document.querySelector('.mobile-nav-drawer');
    const toggleBtns = document.querySelectorAll('.mobile-nav-toggle-btn, .sidebar-toggle-btn, #sidebar-toggle-btn');

    if (drawer) {
        drawer.classList.remove('hidden');
        drawer.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';

        toggleBtns.forEach(btn => {
            btn.setAttribute('aria-expanded', 'true');
            const menuIcon = btn.querySelector('.mobile-nav-icon-menu');
            const closeIcon = btn.querySelector('.mobile-nav-icon-close');
            if (menuIcon) menuIcon.classList.add('hidden');
            if (closeIcon) closeIcon.classList.remove('hidden');
        });

        // Focus close button for accessibility
        const closeBtn = drawer.querySelector('#mobile-nav-close-btn, .mobile-nav-close-btn');
        if (closeBtn) {
            requestAnimationFrame(() => closeBtn.focus());
        }
    }

    // Sync legacy sidebar if present
    const sidebar = document.querySelector('.rec-sidebar');
    if (sidebar) {
        sidebar.classList.remove('collapsed');
        sidebar.classList.add('expanded');
    }

    try {
        localStorage.setItem(SIDEBAR_STORAGE_KEY, "false");
    } catch (e) {}
}

/**
 * Collapses / closes the mobile navigation drawer.
 * @param {boolean} [animate=true]
 */
export function collapseSidebar(animate = true) {
    const drawer = document.getElementById('mobile-nav-drawer') || document.querySelector('.mobile-nav-drawer');
    const toggleBtns = document.querySelectorAll('.mobile-nav-toggle-btn, .sidebar-toggle-btn, #sidebar-toggle-btn');

    if (drawer) {
        drawer.classList.add('hidden');
        drawer.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';

        toggleBtns.forEach(btn => {
            btn.setAttribute('aria-expanded', 'false');
            const menuIcon = btn.querySelector('.mobile-nav-icon-menu');
            const closeIcon = btn.querySelector('.mobile-nav-icon-close');
            if (menuIcon) menuIcon.classList.remove('hidden');
            if (closeIcon) closeIcon.classList.add('hidden');
        });
    }

    // Sync legacy sidebar if present
    const sidebar = document.querySelector('.rec-sidebar');
    if (sidebar) {
        sidebar.classList.add('collapsed');
        sidebar.classList.remove('expanded');
    }

    try {
        localStorage.setItem(SIDEBAR_STORAGE_KEY, "true");
    } catch (e) {}
}

/**
 * Collapses or expands the mobile navigation drawer.
 * @param {boolean} collapsed - Whether to collapse the drawer
 * @param {boolean} [animate=true]
 */
export function setSidebarCollapsed(collapsed, animate = true) {
    if (collapsed) {
        collapseSidebar(animate);
    } else {
        expandSidebar(animate);
    }
}

/**
 * Toggles the mobile navigation drawer open / closed.
 */
export function toggleSidebar() {
    if (isSidebarCollapsed()) {
        expandSidebar(true);
    } else {
        collapseSidebar(true);
    }
}

/**
 * Handles Escape key press to dismiss mobile drawer.
 */
function handleKeyDown(e) {
    if (e.key === 'Escape') {
        const drawer = document.getElementById('mobile-nav-drawer') || document.querySelector('.mobile-nav-drawer');
        if (drawer && !drawer.classList.contains('hidden')) {
            collapseSidebar(true);
            const toggleBtn = document.getElementById('sidebar-toggle-btn');
            if (toggleBtn) toggleBtn.focus();
        }
    }
}

/**
 * Initializes the workspace navigation & mobile drawer component.
 */
export function initSidebar() {
    const toggleBtns = document.querySelectorAll('.mobile-nav-toggle-btn, .sidebar-toggle-btn, #sidebar-toggle-btn');
    const closeBtns = document.querySelectorAll('#mobile-nav-close-btn, .mobile-nav-close-btn');
    const backdrops = document.querySelectorAll('#mobile-nav-backdrop, .mobile-nav-backdrop');
    const drawerLinks = document.querySelectorAll('.mobile-nav-link');

    // 1. Initial State: Always ensure mobile drawer starts closed
    collapseSidebar(false);

    // Prevent duplicate listener binding
    if (document.documentElement.dataset.workspaceNavInitialized === 'true') {
        return;
    }
    document.documentElement.dataset.workspaceNavInitialized = 'true';

    // 2. Bind mobile hamburger toggle buttons
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleSidebar();
        });
    });

    // 3. Bind drawer close buttons
    closeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            collapseSidebar(true);
        });
    });

    // 4. Bind backdrop tap to dismiss
    backdrops.forEach(backdrop => {
        backdrop.addEventListener('click', () => {
            collapseSidebar(true);
        });
    });

    // 5. Auto-collapse drawer on mobile nav link click
    drawerLinks.forEach(link => {
        link.addEventListener('click', () => {
            collapseSidebar(true);
        });
    });

    // 6. Bind global Escape key handler
    document.addEventListener('keydown', handleKeyDown);

    // 7. Sync active navigation link with current URL hash
    updateSidebarActiveLink(window.location.hash);
}

/**
 * Updates the active link in both desktop horizontal navigation and mobile drawer.
 * @param {string} hash - The active hash route (e.g., "#/recruiter/dashboard")
 */
export function updateSidebarActiveLink(hash) {
    const activeHash = hash || "";

    // Clear active class from all desktop links
    Object.values(sidebarLinkIds).forEach(id => {
        const link = document.getElementById(id);
        if (link) {
            link.classList.remove('active');
        }
    });

    // Clear active class from all mobile drawer links
    const mobileLinks = document.querySelectorAll('.mobile-nav-link');
    mobileLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Activate the current hash link on desktop
    const targetId = sidebarLinkIds[activeHash];
    if (targetId) {
        const activeLink = document.getElementById(targetId);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        // Activate matching mobile drawer link
        const activeMobileLink = document.querySelector(`.mobile-nav-link[data-nav-target="${targetId}"]`) ||
                                 document.querySelector(`.mobile-nav-link[href="${activeHash}"]`);
        if (activeMobileLink) {
            activeMobileLink.classList.add('active');
        }
    }
}
