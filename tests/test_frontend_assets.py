import os
import re
import json
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_firebase_config_exists_and_valid():
    """Verify frontend/firebase-config.js exists and is valid JavaScript exporting firebaseConfig."""
    config_path = os.path.join(FRONTEND_DIR, "firebase-config.js")
    assert os.path.exists(config_path), "frontend/firebase-config.js must exist"

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "export const firebaseConfig" in content or "export { firebaseConfig" in content
    assert "apiKey" in content
    assert "authDomain" in content
    assert "projectId" in content
    assert "appId" in content

def test_firebase_config_not_ignored_in_gitignore():
    """Verify that frontend/firebase-config.js is not ignored by .gitignore."""
    gitignore_path = os.path.join(ROOT_DIR, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if not line.startswith("#")]
        assert "frontend/firebase-config.js" not in lines, "frontend/firebase-config.js must not be in .gitignore"

def test_firebase_json_configuration():
    """Verify firebase.json hosting settings, headers, and rewrite safety."""
    firebase_json_path = os.path.join(ROOT_DIR, "firebase.json")
    assert os.path.exists(firebase_json_path), "firebase.json must exist"

    with open(firebase_json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    hosting = config.get("hosting", {})
    assert hosting.get("public") == "frontend", "Hosting public directory must be 'frontend'"

    # Verify rewrites do not catch static assets
    rewrites = hosting.get("rewrites", [])
    assert len(rewrites) > 0, "At least one rewrite rule must be defined"
    for rw in rewrites:
        source = rw.get("source", "")
        # Rewrites must either exclude extensions or not be a raw catch-all for JS
        if rw.get("destination") == "/index.html":
            assert source != "**", "Catch-all rewrite must not hijack static JS modules"
            assert "!" in source or "js" not in source

def test_html_entrypoints_reference_existing_scripts():
    """Verify that all script tags in HTML files reference files that exist on disk."""
    html_files = [f for f in os.listdir(FRONTEND_DIR) if f.endswith(".html")]
    assert len(html_files) >= 4, "Must have index.html, candidate.html, recruiter.html, onboarding.html"

    script_src_pattern = re.compile(r'<script[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)

    for html_file in html_files:
        html_path = os.path.join(FRONTEND_DIR, html_file)
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        for match in script_src_pattern.finditer(content):
            src = match.group(1)
            # Ignore external CDN scripts
            if src.startswith("http://") or src.startswith("https://") or src.startswith("//"):
                continue

            # Strip query strings (e.g. ?v=2.1)
            clean_path = src.split("?")[0]
            disk_path = os.path.normpath(os.path.join(FRONTEND_DIR, clean_path))
            assert os.path.exists(disk_path), f"File {clean_path} referenced in {html_file} does not exist at {disk_path}"

def test_javascript_relative_imports_resolve():
    """Verify that static relative imports in local frontend JS files resolve to actual files."""
    import_pattern = re.compile(r'(?:import|export)\s+(?:.*?from\s+)?["\'](\.[^"\']+)["\']')

    js_files = []
    for root, _, files in os.walk(FRONTEND_DIR):
        for file in files:
            if file.endswith(".js"):
                js_files.append(os.path.join(root, file))

    assert len(js_files) > 0

    for js_file in js_files:
        with open(js_file, "r", encoding="utf-8") as f:
            content = f.read()

        for match in import_pattern.finditer(content):
            specifier = match.group(1)
            clean_specifier = specifier.split("?")[0]
            resolved_path = os.path.normpath(os.path.join(os.path.dirname(js_file), clean_specifier))
            assert os.path.exists(resolved_path), f"Import '{specifier}' in {os.path.relpath(js_file, ROOT_DIR)} failed to resolve to {resolved_path}"


def test_logo_elements_and_navbar_navigation():
    """Verify logo elements exist in recruiter.html, candidate.html, index.html and navbar.js wires navigation."""
    recruiter_html = os.path.join(FRONTEND_DIR, "recruiter.html")
    candidate_html = os.path.join(FRONTEND_DIR, "candidate.html")
    index_html = os.path.join(FRONTEND_DIR, "index.html")
    navbar_js = os.path.join(FRONTEND_DIR, "assets", "js", "components", "navbar.js")

    with open(recruiter_html, "r", encoding="utf-8") as f:
        rec_content = f.read()
    assert 'id="recruiter-sidebar-logo"' in rec_content, "recruiter.html must have id='recruiter-sidebar-logo'"

    with open(candidate_html, "r", encoding="utf-8") as f:
        cand_content = f.read()
    assert 'id="candidate-sidebar-logo"' in cand_content, "candidate.html must have id='candidate-sidebar-logo'"

    with open(index_html, "r", encoding="utf-8") as f:
        index_content = f.read()
    assert 'id="landing-logo"' in index_content, "index.html must have id='landing-logo'"

    with open(navbar_js, "r", encoding="utf-8") as f:
        nav_content = f.read()
    assert "handleLogoNavigation" in nav_content, "navbar.js must implement handleLogoNavigation"
    assert "recruiter-sidebar-logo" in nav_content
    assert "candidate-sidebar-logo" in nav_content
    assert "landing-logo" in nav_content


def test_recruiter_quick_view_modal_dom_structure():
    """Verify recruiter.html contains the full quick view modal and candidate.html does not duplicate it."""
    recruiter_html = os.path.join(FRONTEND_DIR, "recruiter.html")
    candidate_html = os.path.join(FRONTEND_DIR, "candidate.html")

    with open(recruiter_html, "r", encoding="utf-8") as f:
        rec_content = f.read()

    required_ids = [
        "rec-quick-view-modal",
        "close-quick-view-btn",
        "qv-cand-name",
        "qv-cand-score-badge",
        "qv-cand-email",
        "qv-cand-phone",
        "qv-cand-linkedin",
        "qv-cand-github",
        "qv-xai-container",
        "qv-recommendations-container",
        "qv-cand-extracted-skills",
        "qv-cand-matched-skills",
        "qv-cand-missing-skills",
    ]

    for req_id in required_ids:
        assert f'id="{req_id}"' in rec_content, f"recruiter.html must contain id='{req_id}'"

    with open(candidate_html, "r", encoding="utf-8") as f:
        cand_content = f.read()
    assert 'id="rec-quick-view-modal"' not in cand_content, "candidate.html must not contain duplicate rec-quick-view-modal"
    assert 'id="cand-analysis-view-modal"' in cand_content, "candidate.html must retain cand-analysis-view-modal"


def test_candidate_card_and_recruiter_quick_view_integration():
    """Verify candidate card renders quick view button with data attributes and recruiter.js binds them."""
    card_js = os.path.join(FRONTEND_DIR, "assets", "js", "components", "candidateCard.js")
    recruiter_js = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "recruiter.js")

    with open(card_js, "r", encoding="utf-8") as f:
        card_content = f.read()
    assert "quick-view-btn" in card_content
    assert "data-candidate-index" in card_content
    assert "getRecruiterCandidateCardHTML(cand, index" in card_content

    with open(recruiter_js, "r", encoding="utf-8") as f:
        rec_content = f.read()
    assert "showCandidateQuickView" in rec_content
    assert "window.showCandidateQuickView = showCandidateQuickView" in rec_content
    assert "renderRecruiterResults" in rec_content
    assert "closeQuickViewBtn" in rec_content


def test_recruiter_profile_card_horizontal_layout_and_pencil_btn():
    """Verify recruiter profile has horizontal side-by-side layout, pencil icon button, and candidate profile is unchanged."""
    recruiter_html = os.path.join(FRONTEND_DIR, "recruiter.html")
    candidate_html = os.path.join(FRONTEND_DIR, "candidate.html")
    recruiter_css = os.path.join(FRONTEND_DIR, "assets", "css", "recruiter.css")

    with open(recruiter_html, "r", encoding="utf-8") as f:
        rec_content = f.read()

    # Recruiter Profile DOM checks
    assert 'class="glass-card profile-details-card recruiter-profile-card"' in rec_content
    assert 'id="rec-edit-profile-btn"' in rec_content
    assert 'class="profile-edit-icon-btn"' in rec_content
    assert 'aria-label="Edit Profile"' in rec_content
    assert 'title="Edit Profile"' in rec_content
    assert 'class="rec-profile-layout"' in rec_content
    assert 'class="rec-profile-identity"' in rec_content
    assert 'class="rec-profile-divider"' in rec_content
    assert 'class="rec-profile-details"' in rec_content
    assert 'class="rec-profile-grid"' in rec_content
    assert 'id="profile-rec-name"' in rec_content
    assert 'id="profile-rec-email"' in rec_content
    assert 'id="profile-comp-name"' in rec_content
    assert 'id="profile-comp-type"' in rec_content
    assert 'id="profile-hiring-domain"' in rec_content
    assert 'id="rec-profile-edit-form"' in rec_content

    # Candidate Profile isolation checks (must remain unchanged)
    with open(candidate_html, "r", encoding="utf-8") as f:
        cand_content = f.read()

    assert 'id="cand-edit-profile-btn"' in cand_content
    assert 'id="cand-profile-display"' in cand_content
    assert 'rec-profile-layout' not in cand_content
    assert 'profile-edit-icon-btn' not in cand_content

    # Recruiter CSS rules check
    with open(recruiter_css, "r", encoding="utf-8") as f:
        css_content = f.read()

    assert ".recruiter-profile-card" in css_content
    assert ".profile-edit-icon-btn" in css_content
    assert ".rec-profile-layout" in css_content
    assert ".rec-profile-identity" in css_content
    assert ".rec-profile-meta h3#profile-rec-name" in css_content
    assert ".rec-profile-meta p#profile-rec-email" in css_content


def test_recruiter_screening_history_refresh_icon_btn():
    """Verify recruiter screening history has a compact icon-only refresh button with tooltip, aria-label, spinning animation, and concurrency protection."""
    recruiter_html = os.path.join(FRONTEND_DIR, "recruiter.html")
    candidate_html = os.path.join(FRONTEND_DIR, "candidate.html")
    recruiter_css = os.path.join(FRONTEND_DIR, "assets", "css", "recruiter.css")
    recruiter_js = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "recruiter.js")

    with open(recruiter_html, "r", encoding="utf-8") as f:
        rec_html = f.read()

    # Recruiter HTML checks
    assert 'id="rec-refresh-history-btn"' in rec_html
    assert 'class="history-refresh-icon-btn"' in rec_html
    assert 'aria-label="Refresh screening history"' in rec_html
    assert 'title="Refresh screening history"' in rec_html
    assert 'class="refresh-icon"' in rec_html
    assert '🔄 Refresh' not in rec_html

    # Candidate profile isolation check
    with open(candidate_html, "r", encoding="utf-8") as f:
        cand_html = f.read()
    assert 'history-refresh-icon-btn' not in cand_html

    # Recruiter CSS checks
    with open(recruiter_css, "r", encoding="utf-8") as f:
        css = f.read()
    assert '.history-refresh-icon-btn' in css
    assert '.history-refresh-icon-btn:hover' in css
    assert '.history-refresh-icon-btn:focus-visible' in css
    assert '.history-refresh-icon-btn.is-refreshing .refresh-icon' in css
    assert '@keyframes spin-refresh' in css

    # Recruiter JS checks
    with open(recruiter_js, "r", encoding="utf-8") as f:
        js = f.read()
    assert 'isRefreshingHistory' in js
    assert 'refreshBtn.classList.add(\'is-refreshing\')' in js
    assert 'aria-busy' in js
    assert 'loadRecruiterScreeningHistory(true)' in js


def test_recruiter_recommendations_restricted_and_hidden():
    """Verify recruiter pages hide candidate recommendations while candidate views retain them."""
    recruiter_html = os.path.join(FRONTEND_DIR, "recruiter.html")
    candidate_html = os.path.join(FRONTEND_DIR, "candidate.html")
    recruiter_js = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "recruiter.js")
    candidate_js = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "candidate.js")

    with open(recruiter_html, "r", encoding="utf-8") as f:
        rec_html = f.read()

    # Recruiter HTML: qv-recommendations-section must be hidden
    assert 'id="qv-recommendations-section" style="display: none;"' in rec_html or 'class="qv-section hidden" id="qv-recommendations-section"' in rec_html
    # Recruiter Dashboard: Top recommendations list header removed from 2-column grid
    assert '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1rem;">' in rec_html

    # Candidate HTML: retains recommendations section
    with open(candidate_html, "r", encoding="utf-8") as f:
        cand_html = f.read()
    assert 'id="cav-recommendations-section"' in cand_html
    assert 'Resume Improvement Recommendations' in cand_html

    # Candidate JS: preserves candidate recommendations rendering with action buttons
    with open(candidate_js, "r", encoding="utf-8") as f:
        cand_js = f.read()
    assert 'renderRecommendations(details.recommendations' in cand_js
    assert 'updateRecommendationStatus' in cand_js
    assert 'COMPLETED' in cand_js
    assert 'DISMISSED' in cand_js

    # Recruiter JS: renderRecommendations returns empty string and quick view clears recommendations
    with open(recruiter_js, "r", encoding="utf-8") as f:
        rec_js = f.read()
    assert 'export function renderRecommendations' in rec_js
    assert 'qv-recommendations-section' in rec_js
    assert 'recsSection.style.display = \'none\'' in rec_js


def test_screening_workflow_state_reset_controls():
    """Verify recruiter screening has explicit reset controls and state reset mechanism."""
    recruiter_html = os.path.join(FRONTEND_DIR, "recruiter.html")
    recruiter_js = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "recruiter.js")

    with open(recruiter_html, "r", encoding="utf-8") as f:
        rec_html = f.read()
    assert 'id="btn-new-screening"' in rec_html
    assert 'id="btn-reset-screening"' in rec_html
    assert 'Start New Screening' in rec_html

    with open(recruiter_js, "r", encoding="utf-8") as f:
        rec_js = f.read()
    assert 'resetScreeningWorkflowState' in rec_js
    assert 'recResumesInput.value = \'\'' in rec_js
    assert 'activeScreeningRunId++' in rec_js
    assert 'btnNewScreening' in rec_js
    assert 'btnResetScreening' in rec_js


def test_advanced_scoring_customization_controls():
    """Verify recruiter screening includes optional advanced customizable scoring controls."""
    recruiter_html = os.path.join(FRONTEND_DIR, "recruiter.html")
    recruiter_js = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "recruiter.js")

    with open(recruiter_html, "r", encoding="utf-8") as f:
        rec_html = f.read()

    # Structural UI controls
    assert 'id="advanced-scoring-container"' in rec_html
    assert 'id="btn-toggle-advanced-scoring"' in rec_html
    assert 'id="scoring-mode-default"' in rec_html
    assert 'id="scoring-mode-custom"' in rec_html
    assert 'id="btn-reset-scoring-defaults"' in rec_html
    assert 'id="btn-autobalance-weights"' in rec_html
    assert 'id="crit-skills-weight"' in rec_html
    assert 'id="crit-exp-weight"' in rec_html
    assert 'id="crit-edu-weight"' in rec_html
    assert 'id="crit-proj-weight"' in rec_html
    assert 'id="thresh-exp-years"' in rec_html
    assert 'id="thresh-proj-count"' in rec_html
    assert 'id="scoring-applied-banner"' in rec_html
    assert 'id="custom-scoring-status-badge"' in rec_html

    with open(recruiter_js, "r", encoding="utf-8") as f:
        rec_js = f.read()

    # Client-side validation and state management
    assert 'initAdvancedScoringControls' in rec_js
    assert 'getCustomScoringPayload' in rec_js
    assert 'resetAdvancedScoringState' in rec_js
    assert 'syncScoringControlsWithSelectedProfile' in rec_js
    assert 'autoBalanceActiveWeights' in rec_js
    assert 'custom_scoring_config' in rec_js
    assert 'scoring-applied-banner' in rec_js


def test_sidebar_toggle_button_and_collapsible_rail():
    """Verify shared recruiter and candidate layouts include the sidebar toggle button and collapsible rail styles."""
    recruiter_html = os.path.join(FRONTEND_DIR, "recruiter.html")
    candidate_html = os.path.join(FRONTEND_DIR, "candidate.html")
    sidebar_js = os.path.join(FRONTEND_DIR, "assets", "js", "components", "sidebar.js")
    recruiter_css = os.path.join(FRONTEND_DIR, "assets", "css", "recruiter.css")

    for html_path, page_name in [(recruiter_html, "recruiter.html"), (candidate_html, "candidate.html")]:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Sidebar header wrapper and toggle button
        assert 'class="sidebar-header"' in content, f"{page_name} must contain .sidebar-header wrapper"
        assert 'id="sidebar-toggle-btn"' in content, f"{page_name} must contain #sidebar-toggle-btn"
        assert 'aria-label="Toggle sidebar"' in content or 'aria-label="Collapse sidebar"' in content, f"{page_name} toggle must have accessible aria-label"
        assert 'title="Toggle sidebar"' in content or 'title="Collapse sidebar"' in content, f"{page_name} toggle must have title tooltip"
        assert 'aria-expanded="true"' in content, f"{page_name} toggle must default to aria-expanded='true'"

        # SVG icon geometry
        assert 'class="sidebar-toggle-icon"' in content, f"{page_name} must contain .sidebar-toggle-icon"
        assert 'toggle-icon-collapse' in content, f"{page_name} must contain collapse icon state"
        assert 'toggle-icon-expand' in content, f"{page_name} must contain expand icon state"

        # Early restoration script to prevent layout jumps/FOUC
        assert 'sidebar-pref-collapsed' in content, f"{page_name} must have early restoration script"

    # JS Component exports & state logic
    with open(sidebar_js, "r", encoding="utf-8") as f:
        js_content = f.read()

    assert "export function initSidebar" in js_content
    assert "export function toggleSidebar" in js_content
    assert "export function setSidebarCollapsed" in js_content
    assert "export function isSidebarCollapsed" in js_content
    assert "nipun_sidebar_collapsed" in js_content
    assert "sidebar-collapsed" in js_content
    assert "sidebar-pref-collapsed" in js_content

    # CSS styles and transitions
    with open(recruiter_css, "r", encoding="utf-8") as f:
        css_content = f.read()

    assert ".sidebar-header" in css_content
    assert ".sidebar-toggle-btn" in css_content
    assert ".sidebar-collapsed" in css_content
    assert ".sidebar-pref-collapsed" in css_content
    assert "margin-left: 68px" in css_content
    assert "width: 68px" in css_content
    assert "@media (max-width: 800px)" in css_content
    assert ".sidebar-toggle-btn" in css_content


def test_candidate_xai_and_dashboard_frontend_lifecycle():
    """Verify that candidate frontend JS and HTML implement XAI breakdown, status badges, and cache-safe dashboard refresh."""
    candidate_js_path = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "candidate.js")
    candidate_html_path = os.path.join(FRONTEND_DIR, "candidate.html")

    assert os.path.exists(candidate_js_path), "candidate.js must exist"
    assert os.path.exists(candidate_html_path), "candidate.html must exist"

    with open(candidate_js_path, "r", encoding="utf-8") as f:
        cand_js = f.read()

    with open(candidate_html_path, "r", encoding="utf-8") as f:
        cand_html = f.read()

    # 1. HTML containers for dashboard and analysis
    assert 'id="cand-stats-container"' in cand_html
    assert 'id="candidate-timeline-list"' in cand_html
    assert 'id="cand-results-container"' in cand_html
    assert 'id="cand-results-details"' in cand_html

    # 2. Cache invalidation upon candidate analysis completion
    assert "state.setCandidateStats(null)" in cand_js
    assert "state.setCandidateResumes(null)" in cand_js

    # 3. Monotonic request ID guarding against stale response overwrites in dashboard
    assert "currentDashboardReqId" in cand_js
    assert "reqId !== currentDashboardReqId" in cand_js

    # 4. Distinct dashboard loading indicators avoiding premature empty states
    assert "Loading your dashboard data..." in cand_js
    assert "Loading analysis history..." in cand_js

    # 5. Dashboard error states with retry functionality
    assert "Could not load dashboard statistics." in cand_js
    assert "Could not load analysis history." in cand_js
    assert 'onclick="initializeCandidateDashboard()"' in cand_js

    # 6. Inline XAI Breakdown and Recommendations rendering in results
    assert 'cand-results-xai-section' in cand_js
    assert 'cand-results-recs-section' in cand_js
    assert 'renderXaiContent(xaiData)' in cand_js
    assert 'renderRecommendations(recsData' in cand_js

    # 7. Grounded AI vs Rule Fallback badges and strengths/gaps cards in renderXaiContent
    assert "Grounded AI Insights (Gemini" in cand_js
    assert "Deterministic Matching (Rule-Based Fallback)" in cand_js
    assert "Key Strengths" in cand_js
    assert "Skill Gaps &amp; Missing Qualifications" in cand_js



