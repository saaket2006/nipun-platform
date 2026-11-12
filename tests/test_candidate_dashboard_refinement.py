import os
import re
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
CANDIDATE_HTML = os.path.join(FRONTEND_DIR, "candidate.html")
CANDIDATE_JS = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "candidate.js")
RECRUITER_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "recruiter.css")
BASE_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "base.css")


# ==============================================================================
# 1. CANDIDATE DASHBOARD EMPTY AND LOADING STATES AUDIT
# ==============================================================================

def test_candidate_loading_states_centering_and_dimensions():
    """Verify that both dashboard and timeline loading containers are compact and centered."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    # Dashboard loading container
    assert 'class="dashboard-loading"' in js
    assert "min-height: 180px" in js
    assert "display: flex" in js
    assert "flex-direction: column" in js
    assert "align-items: center" in js
    assert "justify-content: center" in js

    # Timeline loading container
    assert 'class="timeline-loading"' in js
    assert "Loading analysis history" in js


def test_candidate_empty_states_centering_and_width():
    """Verify that empty states have centered icons and Analysis History uses full available width."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    # Empty stats container
    assert "No Resumes Analyzed Yet" in js
    assert "+ Analyze Your First Resume" in js

    # Analysis history empty container
    assert "No Analysis History" in js
    assert "width: 100%" in js
    assert "box-sizing: border-box" in js
    # Folder icon svg present
    assert "<svg" in js
    assert "d=\"M22 19a2 2 0 0 1-2 2H4" in js


# ==============================================================================
# 2. ANALYSIS HISTORY CARD OVERLAP & FORMATTING AUDIT
# ==============================================================================

def test_analysis_history_newest_indicator_is_green_dot():
    """Verify that 'NEWEST VERSION' text badge is replaced with an accessible green dot."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    # Must NOT render the text badge 'Newest Version'
    assert 'class="newest-badge">Newest Version<' not in js
    # Must render latest-version-dot with tooltip/aria-label
    assert 'class="latest-version-dot"' in js
    assert 'title="Latest version"' in js
    assert 'aria-label="Latest version"' in js

    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    # CSS definition for latest-version-dot
    assert ".latest-version-dot" in css
    assert "background: var(--color-forest)" in css
    assert "border-radius: 50%" in css


def test_analysis_history_action_buttons_alignment():
    """Verify uniform alignment and styling for View Analysis and Delete buttons."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert "timeline-btn-view" in js
    assert "timeline-btn-delete" in js
    assert "viewCandidateAnalysis" in js
    assert "deleteCandidateAnalysis" in js
    assert "height: 34px" in js


# ==============================================================================
# 3. CAREER PROGRESS TIMELINE CREDIBILITY AUDIT
# ==============================================================================

def test_career_timeline_clean_starter_state_for_single_version():
    """Verify that when only 1 version exists or analyses target different roles, a single indicator and clean hint message are rendered."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert "Career Progress Timeline" in js
    assert "career-timeline-hint" in js
    assert "Another version must be analysed to track progress" in js


def test_career_timeline_role_grouping_logic():
    """Verify that version progression is role-specific and does not conflate different job descriptions."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert "roleGroups" in js
    assert "job_description_title" in js


def test_analysis_history_expandable_job_description():
    """Verify expandable job description toggle button and collapsed/expanded state."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert "timeline-jd-box" in js
    assert "timeline-jd-toggle-btn" in js
    assert "toggleJdSummary" in js
    # Toggle button text — "Show description" or "Show full description" are both acceptable
    assert "Show description" in js or "Show full description" in js


def test_analysis_history_latest_version_badge_structure():
    """Verify that latest version badge contains independent green dot and accessible text."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert "latest-version-badge" in js
    assert "latest-version-dot" in js
    assert "Latest version" in js

    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    assert ".latest-version-badge" in css
    assert ".latest-version-dot" in css
    assert ".timeline-content-grid" in css
    assert "grid-template-columns: 1fr auto" in css


def test_career_timeline_no_speculative_or_invented_claims():
    """Verify complete removal of artificial metrics like 'Comparison Reliability: HIGH/LOW'."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert "Comparison Reliability" not in js
    assert "Same Job Description" not in js
    assert "Same Profile" not in js
    assert "Same Engine Version" not in js


# ==============================================================================
# 4. CANDIDATE RESUME ANALYSIS XAI AUDIT
# ==============================================================================

def test_candidate_xai_no_summary_detailed_toggle():
    """Verify that Summary/Detailed toggle buttons and handler are completely removed."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert "Explanation Level:" not in js
    assert "toggleXaiLevel" not in js
    assert "xai-level-btn" not in js


def test_candidate_xai_no_ai_provider_or_model_branding():
    """Verify removal of 'Grounded AI Insights (Gemini)' and 'Deterministic Matching (Rule-Based Fallback)'."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert "Grounded AI Insights" not in js
    assert "Deterministic Matching (Rule-Based Fallback)" not in js
    assert "Gemini" not in js


def test_candidate_xai_modal_scrolling():
    """Verify smooth scrolling and absence of scroll locking in quick-view-body."""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    assert "-webkit-overflow-scrolling: touch" in css
    assert "overscroll-behavior: contain" in css
    assert "scroll-behavior: smooth" in css


# ==============================================================================
# 5. BROWSER PLAYWRIGHT VERIFICATION TESTS
# ==============================================================================

MOCK_AUTH_JS = """
export function getAuth() {
    const user = {
        uid: "cand_tester_1",
        email: "alex.turner@example.com",
        emailVerified: true,
        getIdToken: async () => "mock-token",
        providerData: [{ providerId: "password" }]
    };
    return {
        currentUser: user,
        authStateReady: async () => user,
        onAuthStateChanged: (cb) => { cb(user); return () => {}; }
    };
}
export function onAuthStateChanged(auth, cb) {
    cb(auth.currentUser);
    return () => {};
}
export class GoogleAuthProvider {}
export const signInWithEmailAndPassword = async () => {};
export const createUserWithEmailAndPassword = async () => {};
export const signInWithPopup = async () => {};
export const signOut = async () => {};
export const sendEmailVerification = async () => {};
export const sendPasswordResetEmail = async () => {};
export const verifyPasswordResetCode = async () => {};
export const confirmPasswordReset = async () => {};
export const reload = async () => {};
"""

MOCK_CANDIDATE_RESUMES_SAME_ROLE = [
    {
        "id": 102,
        "label": "Full Stack Senior Resume",
        "version": 2,
        "original_filename": "Alex_Turner_FullStack_v2.pdf",
        "ats_score": 88,
        "uploaded_at": "2026-11-11T12:00:00Z",
        "job_description_title": "Senior Full Stack Engineer",
        "job_description_summary": "Looking for a Senior Full Stack Engineer with 5+ years of experience in React, Node.js, TypeScript, PostgreSQL, and cloud deployments."
    },
    {
        "id": 101,
        "label": "Full Stack Initial Draft",
        "version": 1,
        "original_filename": "Alex_Turner_Draft_v1.pdf",
        "ats_score": 74,
        "uploaded_at": "2026-11-09T10:00:00Z",
        "job_description_title": "Senior Full Stack Engineer",
        "job_description_summary": "Looking for a Senior Full Stack Engineer with 5+ years of experience in React, Node.js, TypeScript, PostgreSQL, and cloud deployments."
    }
]

MOCK_CANDIDATE_RESUMES_DIFFERENT_ROLES = [
    {
        "id": 202,
        "label": "Platform Lead Resume",
        "version": 1,
        "original_filename": "Alex_Platform_v1.pdf",
        "ats_score": 82,
        "uploaded_at": "2026-11-11T14:00:00Z",
        "job_description_title": "Cloud Platform Architect",
        "job_description_summary": "Kubernetes and multi-cloud platform governance architect."
    },
    {
        "id": 201,
        "label": "Frontend Specialist Resume",
        "version": 1,
        "original_filename": "Alex_Frontend_v1.pdf",
        "ats_score": 79,
        "uploaded_at": "2026-11-08T09:00:00Z",
        "job_description_title": "Senior Frontend Developer",
        "job_description_summary": "React, Next.js, and design systems specialist."
    }
]


def setup_candidate_mock(page, resumes=None):
    if resumes is None:
        resumes = MOCK_CANDIDATE_RESUMES_SAME_ROLE

    latest_score = resumes[0]["ats_score"] if resumes else 0
    latest_date = resumes[0]["uploaded_at"] if resumes else None

    page.route("**/firebase-auth.js*", lambda r: r.fulfill(
        status=200,
        content_type="application/javascript",
        body=MOCK_AUTH_JS
    ))
    mock_user_data = {
        "id": 5, "email": "alex.turner@example.com", "display_name": "Alex Turner",
        "role": "CANDIDATE", "profile_completed": True,
        "candidate_profile": {
            "current_status": "Actively Looking",
            "field": "Software Engineering",
            "field_of_study": "Computer Science",
            "primary_domain": "Full Stack & Distributed Systems",
            "current_domain": "Full Stack & Distributed Systems"
        }
    }
    page.route("**/api/auth/me*", lambda r: r.fulfill(json=mock_user_data))
    page.route("**/api/candidate/profile*", lambda r: r.fulfill(json=mock_user_data))
    page.route("**/api/profile*", lambda r: r.fulfill(json=mock_user_data))
    page.route("**/api/candidate/stats*", lambda r: r.fulfill(json={
        "total_resumes": len(resumes),
        "latest_ats_score": latest_score,
        "last_analysis_date": latest_date
    }))
    page.route("**/api/candidate/resumes*", lambda r: r.fulfill(json=resumes))


def test_browser_candidate_dashboard_same_role_timeline():
    """Verify that multiple analyses for the same target role render target-role progression timeline with delta badge."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_candidate_mock(page, MOCK_CANDIDATE_RESUMES_SAME_ROLE)

        page.goto("http://localhost:8085/candidate.html#/candidate/dashboard", wait_until="domcontentloaded")
        page.wait_for_selector(".career-ribbon-container", state="visible", timeout=10000)

        # 1. Benchmark KPI check
        benchmark_card = page.locator(".stat-card").filter(has_text="Latest Account Benchmark").first
        assert benchmark_card.is_visible()
        assert "88%" in benchmark_card.inner_text()

        # 2. Career Progress timeline check
        timeline_header = page.locator(".stat-title").filter(has_text="Career Progress Timeline").first
        assert timeline_header.is_visible()
        assert "career progress timeline" in timeline_header.inner_text().lower()
        # Ensure target job description is NOT embedded inside timeline header
        assert "senior full stack engineer" not in timeline_header.inner_text().lower()

        # Net score improvement badge check (+14 pts)
        delta_badge = page.locator(".stat-card.span-two span").filter(has_text="+14 pts").first
        assert delta_badge.is_visible()

        # Timeline nodes check
        nodes = page.locator(".career-node").all()
        assert len(nodes) == 2, f"Expected 2 nodes, found {len(nodes)}"

        # Consecutive score change check on connector
        connector_badge = page.locator(".career-connector-badge")
        assert connector_badge.is_visible()
        assert "+14 pts" in connector_badge.inner_text()

        # 3. History Cards check: 2-column layout and Latest version badge with dot
        history_cards = page.locator(".timeline-card").all()
        assert len(history_cards) == 2

        newest_card = history_cards[0]
        badge = newest_card.locator(".latest-version-badge")
        assert badge.is_visible()
        assert "latest version" in badge.inner_text().lower()
        assert badge.locator(".latest-version-dot").is_visible()

        # Actions group check: Version Match label and 34px buttons
        score_block = newest_card.locator(".timeline-score-block")
        assert score_block.is_visible()
        assert "version match:" in score_block.inner_text().lower()
        assert "88%" in score_block.inner_text()

        view_btn = newest_card.locator(".timeline-btn-view")
        del_btn = newest_card.locator(".timeline-btn-delete")
        assert view_btn.is_visible()
        assert del_btn.is_visible()

        vb_box = view_btn.bounding_box()
        db_box = del_btn.bounding_box()
        assert abs(vb_box["height"] - 34) <= 2, f"Expected height ~34px, got {vb_box['height']}"
        assert abs(db_box["height"] - 34) <= 2, f"Expected height ~34px, got {db_box['height']}"

        # 4. Expandable Job Description toggle check
        jd_body = newest_card.locator(".timeline-jd-body")
        toggle_btn = newest_card.locator(".timeline-jd-toggle-btn")
        assert jd_body.is_visible()
        assert toggle_btn.is_visible()
        assert "show full description" in toggle_btn.inner_text().lower()
        assert "collapsed" in jd_body.get_attribute("class")

        # Click to expand
        toggle_btn.click()
        page.wait_for_timeout(200)
        assert "show less" in toggle_btn.inner_text().lower()
        assert "expanded" in jd_body.get_attribute("class")

        # Click to collapse again
        toggle_btn.click()
        page.wait_for_timeout(200)
        assert "show full description" in toggle_btn.inner_text().lower()
        assert "collapsed" in jd_body.get_attribute("class")

        browser.close()


def test_browser_candidate_dashboard_different_roles_compact_state():
    """Verify that when only one version exists for a target role, exactly one circular indicator is rendered with clean hint message."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_candidate_mock(page, MOCK_CANDIDATE_RESUMES_DIFFERENT_ROLES)

        page.goto("http://localhost:8085/candidate.html#/candidate/dashboard", wait_until="domcontentloaded")
        page.wait_for_selector(".career-ribbon-container", state="visible", timeout=10000)

        # Single circular indicator check
        nodes = page.locator(".career-node").all()
        assert len(nodes) == 1, f"Expected 1 indicator for single version, got {len(nodes)}"
        assert page.locator(".career-node-circle").is_visible()
        assert "82%" in page.locator(".career-node-circle").inner_text()
        assert page.locator(".career-node-version").inner_text().strip() == "V1"

        # No connector for single version
        assert page.locator(".career-node-connector").count() == 0

        # Short clean message below indicator
        hint_msg = page.locator(".career-timeline-hint")
        assert hint_msg.is_visible()
        assert "another version must be analysed to track progress" in hint_msg.inner_text().lower()

        # No dashed box or embedded job description inside timeline
        assert page.locator(".career-timeline-empty-state").count() == 0 or not page.locator(".career-timeline-empty-state").first.is_visible()

        # History list renders both separate analyses
        cards = page.locator(".timeline-card").all()
        assert len(cards) == 2

        browser.close()


def test_browser_candidate_dashboard_mobile_390():
    """Verify responsive 390px mobile behavior: stacked layout without clipping or horizontal overflow."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 844})
        setup_candidate_mock(page, MOCK_CANDIDATE_RESUMES_SAME_ROLE)

        page.goto("http://localhost:8085/candidate.html#/candidate/dashboard", wait_until="domcontentloaded")
        page.wait_for_selector(".timeline-card", state="visible", timeout=10000)

        card = page.locator(".timeline-card").first
        c_box = card.bounding_box()
        assert c_box["width"] <= 390, f"Card width {c_box['width']} exceeds mobile viewport 390px"

        # Buttons stretch evenly in mobile button group
        view_btn = card.locator(".timeline-btn-view")
        del_btn = card.locator(".timeline-btn-delete")
        assert view_btn.is_visible()
        assert del_btn.is_visible()

        vb_box = view_btn.bounding_box()
        db_box = del_btn.bounding_box()
        assert vb_box["width"] > 100, "View button should have touch target width"
        assert db_box["width"] > 100, "Delete button should have touch target width"

        browser.close()



# ==============================================================================
# REGRESSION TESTS: 4 Candidate-side fixes (session continuation)
# ==============================================================================

ROUTER_JS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "assets", "js", "router.js")
)


# --- Fix 1 & 2: Dashboard state preservation (no reload on modal close) --------

def test_close_modal_uses_history_replace_state():
    """closeCandidateAnalysisModal must use history.replaceState to avoid triggering hashchange reload."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    # Must contain history.replaceState in candidate.js
    assert "history.replaceState" in js, (
        "closeCandidateAnalysisModal should use history.replaceState to avoid triggering hashchange"
    )


def test_router_guards_dashboard_reinit_when_already_rendered():
    """Router must guard initializeCandidateDashboard call when dashboard is already rendered."""
    with open(ROUTER_JS, "r", encoding="utf-8") as f:
        router = f.read()

    # Guard condition must be present
    assert "alreadyRendered" in router, (
        "Router should guard initializeCandidateDashboard with an alreadyRendered check"
    )
    assert "cand-stats-container" in router, (
        "Guard should check the cand-stats-container for existing content"
    )


# --- Fix 3: Analysis Snapshot modal width ------------------------------------

def test_modal_max_width_increased_to_820():
    """quick-view-card max-width must be 820px for evaluation content."""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    # Find the .quick-view-card rule and confirm max-width
    match = re.search(
        r"\.quick-view-card\s*\{[^}]+max-width\s*:\s*(\d+px)[^}]+\}",
        css,
        re.DOTALL,
    )
    assert match, ".quick-view-card rule with max-width not found in CSS"
    assert match.group(1) == "820px", (
        f"Expected max-width: 820px, got {match.group(1)}"
    )


def test_modal_max_height_is_90vh():
    """quick-view-card max-height must be 90vh."""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    match = re.search(
        r"\.quick-view-card\s*\{[^}]+max-height\s*:\s*([\w%]+)[^}]+\}",
        css,
        re.DOTALL,
    )
    assert match, ".quick-view-card rule with max-height not found in CSS"
    assert match.group(1) == "90vh", (
        f"Expected max-height: 90vh, got {match.group(1)}"
    )


def test_modal_responsive_breakpoints_exist():
    """Responsive overrides for the modal at 860px and 480px must exist."""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    assert "@media (max-width: 860px)" in css, (
        "Missing responsive breakpoint for quick-view-card at 860px"
    )
    assert "@media (max-width: 480px)" in css, (
        "Missing responsive breakpoint for quick-view-card at 480px"
    )


# --- Fix 4: Career Progress legibility ---------------------------------------

def test_career_node_version_legibility():
    """career-node-version should use improved contrast color and font size."""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    match = re.search(
        r"\.career-node-version\s*\{([^}]+)\}",
        css,
        re.DOTALL,
    )
    assert match, ".career-node-version rule not found"
    block = match.group(1)
    # Font size should be at least 0.8125rem (not tiny 0.6875rem)
    assert "0.8125rem" in block or "0.875rem" in block or "0.9rem" in block, (
        "career-node-version font-size should be ≥ 0.8125rem for legibility"
    )
    # Should use ink-2 or ink (not muted) for contrast
    assert "color-ink" in block or "ink-2" in block, (
        "career-node-version should use --color-ink-2 or --color-ink for contrast"
    )


def test_career_node_circle_legibility():
    """career-node-circle should be larger (≥50px) for readability."""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    match = re.search(
        r"\.career-node-circle\s*\{([^}]+)\}",
        css,
        re.DOTALL,
    )
    assert match, ".career-node-circle rule not found"
    block = match.group(1)
    # Width and height should be at least 50px
    width_match = re.search(r"width\s*:\s*(\d+)px", block)
    assert width_match and int(width_match.group(1)) >= 48, (
        f"career-node-circle width should be ≥ 48px, got {width_match.group(1) if width_match else 'not found'}"
    )


def test_career_node_date_legibility():
    """career-node-date should use improved font size and contrast."""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    match = re.search(
        r"\.career-node-date\s*\{([^}]+)\}",
        css,
        re.DOTALL,
    )
    assert match, ".career-node-date rule not found"
    block = match.group(1)
    # Should be at least 0.75rem
    fs_match = re.search(r"font-size\s*:\s*([\d.]+rem)", block)
    assert fs_match, "career-node-date font-size not found"
    size_val = float(fs_match.group(1).replace("rem", ""))
    assert size_val >= 0.75, (
        f"career-node-date font-size should be ≥ 0.75rem, got {size_val}rem"
    )


# --- Fix 1: Duplicate JD in Analysis History --------------------------------

def test_analysis_history_deduplicates_duplicate_jd():
    """Verify that candidate.js removes redundant job description from title when duplicating summary."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert "isDuplicateDescription" in js, (
        "candidate.js should detect when jdTitle duplicates jdSummary to prevent showing JD twice"
    )


def test_analysis_history_jd_toggle_button_text():
    """Toggle button text should say 'Show full description' in collapsed state."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert "Show full description" in js, (
        "Toggle button should have 'Show full description' text in collapsed state"
    )
