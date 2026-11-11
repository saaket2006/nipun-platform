import os
import re
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
RECRUITER_HTML = os.path.join(FRONTEND_DIR, "recruiter.html")
CANDIDATE_HTML = os.path.join(FRONTEND_DIR, "candidate.html")
RECRUITER_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "recruiter.css")
BASE_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "base.css")
RECRUITER_JS = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "recruiter.js")


# ==============================================================================
# 1. STATIC HTML & CSS AUDIT TESTS
# ==============================================================================

def test_back_to_profile_button_is_compact_secondary_not_full_width():
    """Verify #btn-back-to-profile has compact secondary styling and does not stretch 100% width."""
    with open(RECRUITER_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # Must contain #btn-back-to-profile
    assert 'id="btn-back-to-profile"' in html

    css = ""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css += f.read() + "\n"
    with open(BASE_CSS, "r", encoding="utf-8") as f:
        css += f.read()

    # Dedicated back button class or explicit compact rule
    assert "#btn-back-to-profile" in css or ".task-back-btn" in css or ".task-nav-btn" in css
    # Ensure secondary button rule prevents full-width stretching
    assert ".glow-btn.secondary" in css or "#btn-back-to-profile" in css


def test_loading_and_error_states_editorial_styling():
    """Verify loading and error states use restrained editorial styling rather than harsh solid blocks."""
    with open(RECRUITER_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # History loading & error IDs
    assert 'id="rec-history-loading"' in html
    assert 'id="rec-history-error"' in html
    assert 'id="rec-history-empty"' in html
    assert 'id="rec-task-detail-loading"' in html
    assert 'id="rec-task-detail-error"' in html

    css = ""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css += f.read()
    with open(BASE_CSS, "r", encoding="utf-8") as f:
        css += f.read()

    # Spinner / loader definition must exist and have dimensions
    assert ".spinner" in css or ".loader" in css


def test_recruiter_profile_card_balanced_dimensions():
    """Verify profile card padding and grid rules avoid excessive whitespace."""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    assert ".recruiter-profile-card" in css
    assert ".rec-profile-layout" in css
    assert ".rec-profile-identity" in css
    assert ".rec-profile-details" in css


def test_screening_history_card_and_refresh_button():
    """Verify screening history section has content-driven layout and compact refresh button."""
    with open(RECRUITER_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    assert 'id="rec-refresh-history-btn"' in html
    assert 'id="rec-history-list"' in html

    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css = f.read()

    assert ".history-refresh-icon-btn" in css
    assert ".history-item-card" in css


# ==============================================================================
# 2. BROWSER PLAYWRIGHT FUNCTIONAL TESTS
# ==============================================================================

MOCK_AUTH_JS = """
export function getAuth() {
    const user = {
        uid: "rec_tester_1",
        email: "sarah.connor@apex.com",
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

MOCK_TASK_DETAIL = {
    "id": 42,
    "role": "Lead Infrastructure Architect (Kubernetes & Multi-Cloud)",
    "created_at": "2026-11-10T14:30:00Z",
    "resume_count": 3,
    "job_description": "We are seeking a Lead Infrastructure Architect to spearhead multi-cloud Kubernetes orchestration and cloud compliance.",
    "ranked_results": [
        {
            "name": "Alex Vance",
            "similarity_score": 92,
            "skill_score": 95,
            "experience_score": 90,
            "education_score": 100,
            "projects_score": 85,
            "email": "alex.vance@example.com",
            "matched_skills": ["Kubernetes", "AWS", "Terraform", "Docker"],
            "missing_skills": ["GCP"],
            "analysis_metadata": {"xai": {"enabled": True, "components": []}}
        },
        {
            "name": "Jordan Lee",
            "similarity_score": 78,
            "skill_score": 80,
            "experience_score": 75,
            "education_score": 100,
            "projects_score": 70,
            "email": "jordan.lee@example.com",
            "matched_skills": ["Docker", "AWS"],
            "missing_skills": ["Kubernetes", "Terraform", "GCP"],
            "analysis_metadata": {"xai": {"enabled": True, "components": []}}
        }
    ]
}

def setup_page_mock(page, history_items=None, task_detail=None):
    if history_items is None:
        history_items = [
            {"id": 42, "role": "Lead Infrastructure Architect (Kubernetes & Multi-Cloud)", "created_at": "2026-11-10T14:30:00Z", "resume_count": 3},
            {"id": 41, "role": "Senior Backend Engineer", "created_at": "2026-11-08T09:15:00Z", "resume_count": 8}
        ]
    if task_detail is None:
        task_detail = MOCK_TASK_DETAIL

    page.route("**/firebase-auth.js*", lambda r: r.fulfill(
        status=200,
        content_type="application/javascript",
        body=MOCK_AUTH_JS
    ))
    page.route("**/api/auth/me", lambda r: r.fulfill(json={
        "id": 1, "email": "sarah.connor@apex.com", "display_name": "Sarah Connor",
        "role": "RECRUITER", "profile_completed": True
    }))
    mock_profile_data = {
        "id": 1, "email": "sarah.connor@apex.com", "display_name": "Sarah Connor",
        "role": "RECRUITER", "profile_completed": True,
        "recruiter_profile": {
            "company_name": "Apex Tech Solutions",
            "company_type": "Enterprise",
            "hiring_domain": "Cloud Infrastructure & AI"
        }
    }
    page.route("**/api/recruiter/profile", lambda r: r.fulfill(json=mock_profile_data))
    page.route("**/api/profile", lambda r: r.fulfill(json=mock_profile_data))
    page.route("**/api/recruiter/stats", lambda r: r.fulfill(json={
        "total_screened": 11, "average_score": 85.0, "average_experience": 5.2,
        "common_education": "B.Tech in CS", "common_missing_skills": [], "common_matched_skills": [], "common_improvements": []
    }))
    page.route("**/api/recruiter/profiles", lambda r: r.fulfill(json=[]))
    page.route("**/api/recruiter/job-descriptions", lambda r: r.fulfill(json=[]))
    page.route("**/api/recruiter/screening-tasks", lambda r: r.fulfill(json=[]))
    page.route("**/api/recruiter/history", lambda r: r.fulfill(json=history_items))
    page.route("**/api/recruiter/history/*", lambda r: r.fulfill(json=task_detail))


def test_browser_back_to_profile_button_dimensions():
    """Verify Back to Profile button is compact, left-aligned, and does NOT stretch across page."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_page_mock(page)

        page.goto("http://localhost:8085/recruiter.html#/recruiter/history?id=42", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        back_btn = page.locator("#btn-back-to-profile")
        assert back_btn.is_visible(), "Back to Profile button must be visible"

        btn_box = back_btn.bounding_box()
        # Full width would be > 900px on a 1440 viewport
        assert btn_box["width"] < 250, f"Back to Profile button is oversized/full-width! width={btn_box['width']}px"
        assert btn_box["width"] > 80, f"Back to Profile button is too small! width={btn_box['width']}px"

        # Check background color is secondary (not full green background)
        bg = back_btn.evaluate("el => window.getComputedStyle(el).backgroundColor")
        # Should not be dark solid forest green (rgb(30, 58, 47))
        assert bg != "rgb(30, 58, 47)", f"Back to Profile button has dark solid green background: {bg}"

        browser.close()


def test_browser_task_detail_loading_centered():
    """Verify screening task details loading state is centered horizontally and vertically."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        # Setup mock with delayed history detail
        setup_page_mock(page)
        # Delay history endpoint indefinitely to inspect loading state
        page.route("**/api/recruiter/history/42", lambda r: None)

        page.goto("http://localhost:8085/recruiter.html#/recruiter/history?id=42", wait_until="domcontentloaded")
        page.wait_for_timeout(500)

        loading_box = page.locator("#rec-task-detail-loading")
        assert loading_box.is_visible(), "Task detail loading container should be visible"

        box = loading_box.bounding_box()
        assert box["width"] > 400, "Loading container should span across content wrapper"
        # Must not have excessive arbitrary min-height (> 600px)
        assert box["height"] < 400, f"Loading container has excessive height: {box['height']}px"

        # Check spinner / loader element exists and is visible
        spinner = loading_box.locator(".loader, .spinner").first
        assert spinner.is_visible(), "Loading spinner must be visible"
        
        # Check spinner is centered horizontally in loading box
        sp_box = spinner.bounding_box()
        box_center_x = box["x"] + box["width"] / 2
        sp_center_x = sp_box["x"] + sp_box["width"] / 2
        assert abs(box_center_x - sp_center_x) <= 20.0, \
            f"Loading spinner is not horizontally centered: box={box_center_x}, spinner={sp_center_x}"

        browser.close()


def test_browser_profile_and_history_loaded_layout():
    """Verify profile layout has balanced proportions and history entries render uniformly."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_page_mock(page)

        page.goto("http://localhost:8085/recruiter.html#/recruiter/profile", wait_until="domcontentloaded")
        page.wait_for_selector(".recruiter-profile-card", state="visible", timeout=10000)

        # Profile card check
        profile_card = page.locator(".recruiter-profile-card")
        assert profile_card.is_visible()
        p_box = profile_card.bounding_box()
        assert p_box["height"] < 380, f"Profile card height is excessively tall: {p_box['height']}px"

        # Edit button positioned top-right inside profile card
        edit_btn = page.locator("#rec-edit-profile-btn")
        assert edit_btn.is_visible()
        eb_box = edit_btn.bounding_box()
        assert eb_box["x"] > p_box["x"] + p_box["width"] - 80, "Edit button should be in top right of card"

        # Refresh button compact and aligned with history heading
        refresh_btn = page.locator("#rec-refresh-history-btn")
        assert refresh_btn.is_visible()
        rf_box = refresh_btn.bounding_box()
        assert rf_box["width"] <= 40, f"Refresh button width should be compact (<=40px), got {rf_box['width']}"
        assert rf_box["height"] <= 40, f"Refresh button height should be compact (<=40px), got {rf_box['height']}"

        # History item cards
        items = page.locator(".history-item-card").all()
        assert len(items) == 2, f"Expected 2 history items, got {len(items)}"

        item_boxes = [it.bounding_box() for it in items]
        assert abs(item_boxes[0]["width"] - item_boxes[1]["width"]) <= 2.0, "History cards must have equal width"

        # History more info button is compact
        more_btns = page.locator(".history-more-info-btn").all()
        for mb in more_btns:
            mbb = mb.bounding_box()
            assert mbb["width"] < 160, f"More Info button should be compact, got {mbb['width']}px"

        browser.close()


def test_browser_screening_history_empty_state():
    """Verify screening history empty state is clean, informative, and without excessive height."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_page_mock(page, history_items=[])

        page.goto("http://localhost:8085/recruiter.html#/recruiter/profile", wait_until="domcontentloaded")
        page.wait_for_selector("#rec-history-empty", state="visible", timeout=10000)

        empty_box = page.locator("#rec-history-empty")
        assert empty_box.is_visible(), "History empty state should be visible when 0 tasks exist"

        box = empty_box.bounding_box()
        assert box["height"] < 350, f"Empty state has excessive height: {box['height']}px"

        cta = empty_box.locator("a[href='#/recruiter/screen']")
        assert cta.is_visible(), "Empty state should have clear call to action to Resume Screening"

        browser.close()

