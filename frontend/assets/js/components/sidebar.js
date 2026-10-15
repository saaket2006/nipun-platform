/**
 * Sidebar component that manages link highlights, titles, and collapsible rail state in recruiter/candidate workspaces.
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
 * Checks whether the sidebar is currently collapsed.
 * @returns {boolean}
 */
export function isSidebarCollapsed() {
    try {
        return localStorage.getItem(SIDEBAR_STORAGE_KEY) === "true";
    } catch (e) {
        return false;
    }
}

/**
 * Collapses or expands the sidebar layout.
 * @param {boolean} collapsed - Whether to collapse the sidebar
 * @param {boolean} [animate=true] - Whether to use smooth CSS transitions
 */
export function setSidebarCollapsed(collapsed, animate = true) {
    const layout = document.querySelector('.rec-layout');
    const sidebar = document.querySelector('.rec-sidebar');
    const toggleBtns = document.querySelectorAll('.sidebar-toggle-btn, #sidebar-toggle-btn');

    if (!animate) {
        if (layout) layout.classList.add('no-sidebar-transition');
        if (sidebar) sidebar.classList.add('no-sidebar-transition');
    }

    if (collapsed) {
        if (layout) layout.classList.add('sidebar-collapsed');
        if (sidebar) sidebar.classList.add('collapsed');
        document.documentElement.classList.add('sidebar-pref-collapsed');
        toggleBtns.forEach(btn => {
            btn.setAttribute('aria-expanded', 'false');
            btn.setAttribute('title', 'Expand sidebar');
            btn.setAttribute('aria-label', 'Expand sidebar');
        });
        try {
            localStorage.setItem(SIDEBAR_STORAGE_KEY, "true");
        } catch (e) {}
    } else {
        if (layout) layout.classList.remove('sidebar-collapsed');
        if (sidebar) sidebar.classList.remove('collapsed');
        document.documentElement.classList.remove('sidebar-pref-collapsed');
        toggleBtns.forEach(btn => {
            btn.setAttribute('aria-expanded', 'true');
            btn.setAttribute('title', 'Collapse sidebar');
            btn.setAttribute('aria-label', 'Collapse sidebar');
        });
        try {
            localStorage.setItem(SIDEBAR_STORAGE_KEY, "false");
        } catch (e) {}
    }

    if (!animate && sidebar) {
        // Force reflow and clean up no-transition class on next animation frame
        void sidebar.offsetWidth;
        requestAnimationFrame(() => {
            if (layout) layout.classList.remove('no-sidebar-transition');
            if (sidebar) sidebar.classList.remove('no-sidebar-transition');
        });
    }
}

/**
 * Toggles the sidebar between collapsed and expanded states.
 */
export function toggleSidebar() {
    const nextState = !isSidebarCollapsed();
    setSidebarCollapsed(nextState, true);
}

/**
 * Initializes the sidebar toggle button and restores persisted user preference.
 */
export function initSidebar() {
    // 1. Restore persisted state
    const savedCollapsed = isSidebarCollapsed();
    setSidebarCollapsed(savedCollapsed, false);

    // 2. Bind click handlers to toggle buttons
    const toggleBtns = document.querySelectorAll('.sidebar-toggle-btn, #sidebar-toggle-btn');
    toggleBtns.forEach(btn => {
        btn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleSidebar();
        };
    });
}

/**
 * Updates the active link in the sidebar based on the current hash route.
 * @param {string} hash - The active hash route
 */
export function updateSidebarActiveLink(hash) {
    const activeHash = hash || "";

    // Remove active class from all links
    Object.values(sidebarLinkIds).forEach(id => {
        const link = document.getElementById(id);
        if (link) {
            link.classList.remove('active');
        }
    });

    // Add active class to current hash link
    const targetId = sidebarLinkIds[activeHash];
    const activeLink = document.getElementById(targetId);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}
