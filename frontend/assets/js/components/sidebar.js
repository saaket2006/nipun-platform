/**
 * Sidebar component that manages link highlights, titles, and collapsed-by-default
 * hover-delayed expansion in recruiter and candidate workspaces.
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

// Timing constants
const EXPAND_DELAY_MS = 500;
const COLLAPSE_DELAY_MS = 350;

let expandTimeout = null;
let collapseTimeout = null;
let isPointerOverSidebar = false;

/**
 * Checks whether the sidebar is currently collapsed.
 * @returns {boolean}
 */
export function isSidebarCollapsed() {
    const sidebar = document.querySelector('.rec-sidebar');
    if (sidebar) {
        return sidebar.classList.contains('collapsed') || !sidebar.classList.contains('expanded');
    }
    try {
        return localStorage.getItem(SIDEBAR_STORAGE_KEY) !== "false";
    } catch (e) {
        return true;
    }
}

/**
 * Clears any pending hover-intent or collapse grace period timers.
 */
function clearSidebarTimers() {
    if (expandTimeout) {
        clearTimeout(expandTimeout);
        expandTimeout = null;
    }
    if (collapseTimeout) {
        clearTimeout(collapseTimeout);
        collapseTimeout = null;
    }
}

/**
 * Expands the sidebar overlay layout.
 * @param {boolean} [animate=true]
 */
export function expandSidebar(animate = true) {
    clearSidebarTimers();

    const layout = document.querySelector('.rec-layout');
    const sidebar = document.querySelector('.rec-sidebar');
    const toggleBtns = document.querySelectorAll('.sidebar-toggle-btn, #sidebar-toggle-btn');

    if (!sidebar) return;

    if (!animate) {
        if (layout) layout.classList.add('no-sidebar-transition');
        sidebar.classList.add('no-sidebar-transition');
    }

    sidebar.classList.remove('collapsed');
    sidebar.classList.add('expanded');
    if (layout) {
        layout.classList.remove('sidebar-collapsed');
        layout.classList.add('sidebar-expanded');
    }
    document.documentElement.classList.remove('sidebar-pref-collapsed');

    toggleBtns.forEach(btn => {
        btn.setAttribute('aria-expanded', 'true');
        btn.setAttribute('title', 'Collapse sidebar');
        btn.setAttribute('aria-label', 'Collapse sidebar');
    });

    try {
        localStorage.setItem(SIDEBAR_STORAGE_KEY, "false");
    } catch (e) {}

    if (!animate) {
        void sidebar.offsetWidth;
        requestAnimationFrame(() => {
            if (layout) layout.classList.remove('no-sidebar-transition');
            sidebar.classList.remove('no-sidebar-transition');
        });
    }
}

/**
 * Collapses the sidebar to its compact rail state.
 * @param {boolean} [animate=true]
 */
export function collapseSidebar(animate = true) {
    clearSidebarTimers();

    const layout = document.querySelector('.rec-layout');
    const sidebar = document.querySelector('.rec-sidebar');
    const toggleBtns = document.querySelectorAll('.sidebar-toggle-btn, #sidebar-toggle-btn');

    if (!sidebar) return;

    if (!animate) {
        if (layout) layout.classList.add('no-sidebar-transition');
        sidebar.classList.add('no-sidebar-transition');
    }

    sidebar.classList.add('collapsed');
    sidebar.classList.remove('expanded');
    if (layout) layout.classList.add('sidebar-collapsed');
    document.documentElement.classList.add('sidebar-pref-collapsed');

    toggleBtns.forEach(btn => {
        btn.setAttribute('aria-expanded', 'false');
        btn.setAttribute('title', 'Expand sidebar');
        btn.setAttribute('aria-label', 'Expand sidebar');
    });

    try {
        localStorage.setItem(SIDEBAR_STORAGE_KEY, "true");
    } catch (e) {}

    if (!animate) {
        void sidebar.offsetWidth;
        requestAnimationFrame(() => {
            if (layout) layout.classList.remove('no-sidebar-transition');
            sidebar.classList.remove('no-sidebar-transition');
        });
    }
}

/**
 * Collapses or expands the sidebar layout.
 * @param {boolean} collapsed - Whether to collapse the sidebar
 * @param {boolean} [animate=true] - Whether to use smooth CSS transitions
 */
export function setSidebarCollapsed(collapsed, animate = true) {
    if (collapsed) {
        collapseSidebar(animate);
    } else {
        expandSidebar(animate);
    }
}

/**
 * Toggles the sidebar between collapsed and expanded states.
 */
export function toggleSidebar() {
    const nextState = isSidebarCollapsed();
    setSidebarCollapsed(!nextState, true);
}

/**
 * Handles pointer enter event on the sidebar.
 * Starts a 500ms hover-intent delay before expanding.
 */
function handlePointerEnter(e) {
    if (e.pointerType === 'touch') return;

    isPointerOverSidebar = true;

    // Grace period re-entry: cancel pending collapse immediately
    if (collapseTimeout) {
        clearTimeout(collapseTimeout);
        collapseTimeout = null;
    }

    const sidebar = document.querySelector('.rec-sidebar');
    if (!sidebar || sidebar.classList.contains('expanded')) {
        return;
    }

    // Start 500ms hover-intent timer
    expandTimeout = setTimeout(() => {
        if (isPointerOverSidebar) {
            expandSidebar(true);
        }
        expandTimeout = null;
    }, EXPAND_DELAY_MS);
}

/**
 * Handles pointer leave event on the sidebar.
 * Cancels pending expansion or starts a 350ms collapse grace period.
 */
function handlePointerLeave(e) {
    if (e.pointerType === 'touch') return;

    isPointerOverSidebar = false;

    // If leaving before 500ms expansion completes, cancel expansion immediately
    if (expandTimeout) {
        clearTimeout(expandTimeout);
        expandTimeout = null;
    }

    const sidebar = document.querySelector('.rec-sidebar');
    if (!sidebar || !sidebar.classList.contains('expanded')) {
        return;
    }

    // Start collapse grace period (350ms)
    collapseTimeout = setTimeout(() => {
        // Do not collapse if keyboard focus is still inside the sidebar
        if (!isPointerOverSidebar && !sidebar.contains(document.activeElement)) {
            collapseSidebar(true);
        }
        collapseTimeout = null;
    }, COLLAPSE_DELAY_MS);
}

/**
 * Handles focus entering the sidebar (keyboard navigation).
 */
function handleFocusIn(e) {
    if (collapseTimeout) {
        clearTimeout(collapseTimeout);
        collapseTimeout = null;
    }
    const sidebar = document.querySelector('.rec-sidebar');
    if (sidebar && !sidebar.classList.contains('expanded')) {
        expandSidebar(true);
    }
}

/**
 * Handles focus leaving the sidebar (keyboard navigation).
 */
function handleFocusOut(e) {
    const sidebar = document.querySelector('.rec-sidebar');
    if (!sidebar) return;

    requestAnimationFrame(() => {
        if (!sidebar.contains(document.activeElement) && !isPointerOverSidebar) {
            collapseSidebar(true);
        }
    });
}

/**
 * Handles keydown events within the sidebar (e.g. Escape to collapse).
 */
function handleKeyDown(e) {
    if (e.key === 'Escape') {
        const sidebar = document.querySelector('.rec-sidebar');
        if (sidebar && sidebar.classList.contains('expanded')) {
            collapseSidebar(true);
            const activeLink = sidebar.querySelector('.sidebar-link.active') || sidebar.querySelector('.sidebar-link');
            if (activeLink) activeLink.focus();
        }
    }
}

/**
 * Outside tap detection for touch devices.
 */
function handleOutsidePointerDown(e) {
    const sidebar = document.querySelector('.rec-sidebar');
    if (!sidebar) return;

    if (sidebar.classList.contains('expanded') && !sidebar.contains(e.target) && !isPointerOverSidebar) {
        collapseSidebar(true);
    }
}

/**
 * Initializes the sidebar:
 * - Starts collapsed on fresh dashboard load
 * - Binds delayed hover-intent expansion and collapse grace period
 * - Binds keyboard focus and accessibility handlers
 * - Supports touch/tap toggles
 */
export function initSidebar() {
    const sidebar = document.querySelector('.rec-sidebar');
    if (!sidebar) return;

    // 1. Initial State: Always start collapsed on fresh dashboard load
    collapseSidebar(false);

    // Prevent duplicate event listener registration if initSidebar() is called multiple times
    if (sidebar.dataset.sidebarInitialized === 'true') {
        return;
    }
    sidebar.dataset.sidebarInitialized = 'true';

    // 2. Attach hover-intent listeners (desktop pointer)
    sidebar.addEventListener('pointerenter', handlePointerEnter);
    sidebar.addEventListener('pointerleave', handlePointerLeave);

    // 3. Attach keyboard focus and keydown listeners (accessibility)
    sidebar.addEventListener('focusin', handleFocusIn);
    sidebar.addEventListener('focusout', handleFocusOut);
    sidebar.addEventListener('keydown', handleKeyDown);

    // 4. Bind click handlers to toggle buttons (keyboard & touch fallback)
    const toggleBtns = document.querySelectorAll('.sidebar-toggle-btn, #sidebar-toggle-btn');
    toggleBtns.forEach(btn => {
        btn.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleSidebar();
        };
    });

    // 5. Outside tap detection for touch devices
    document.addEventListener('pointerdown', handleOutsidePointerDown);

    // 6. Auto-collapse on navigation link click for touch/mobile
    const navLinks = sidebar.querySelectorAll('.sidebar-link');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 800 || window.matchMedia('(hover: none)').matches) {
                collapseSidebar(true);
            }
        });
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
