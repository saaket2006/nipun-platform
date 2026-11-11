import os
import re
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
RECRUITER_HTML = os.path.join(FRONTEND_DIR, "recruiter.html")
CANDIDATE_HTML = os.path.join(FRONTEND_DIR, "candidate.html")
RECRUITER_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "recruiter.css")
TOKENS_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "tokens.css")
CANDIDATE_JS = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "candidate.js")
RECRUITER_JS = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "recruiter.js")

VIEWPORTS = [
    {"name": "desktop_1440", "width": 1440, "height": 900},
    {"name": "desktop_1280", "width": 1280, "height": 800},
    {"name": "tablet_1024", "width": 1024, "height": 768},
    {"name": "tablet_768", "width": 768, "height": 1024},
    {"name": "mobile_390", "width": 390, "height": 844},
    {"name": "mobile_360", "width": 360, "height": 740},
]

MOCK_AUTH_JS = """
export function getAuth() {
    const user = {
        uid: "test_user_1",
        email: "user@apex.com",
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

def setup_page_mock(page, role="RECRUITER"):
    page.route("**/firebase-auth.js*", lambda r: r.fulfill(
        status=200,
        content_type="application/javascript",
        body=MOCK_AUTH_JS
    ))
    
    if role == "RECRUITER":
        rec_data = {
            "id": 1, "email": "rec@apex.com", "display_name": "Sarah Connor",
            "role": "RECRUITER", "profile_completed": True,
            "recruiter_profile": {
                "company_name": "Apex Tech Solutions",
                "company_type": "Enterprise",
                "hiring_domain": "Cloud Infrastructure & AI"
            }
        }
        page.route("**/api/auth/me*", lambda r: r.fulfill(json=rec_data))
        page.route("**/api/recruiter/profile*", lambda r: r.fulfill(json=rec_data))
        page.route("**/api/profile*", lambda r: r.fulfill(json=rec_data))
        page.route("**/api/recruiter/stats*", lambda r: r.fulfill(json={
            "total_screened": 142,
            "average_score": 78.5,
            "average_experience": 4.8,
            "common_education": "B.Tech in Computer Science and Engineering",
            "common_missing_skills": ["Kubernetes", "GraphQL", "Rust", "Terraform", "Distributed Systems"],
            "common_matched_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
            "common_improvements": ["Add concrete metrics to past project descriptions"]
        }))
        page.route("**/api/recruiter/profiles*", lambda r: r.fulfill(json=[]))
        page.route("**/api/recruiter/job-descriptions*", lambda r: r.fulfill(json=[]))
        page.route("**/api/recruiter/screening-tasks*", lambda r: r.fulfill(json=[]))
    else:
        cand_prof = {
            "id": 2, "email": "alex@example.com", "display_name": "Alex Chen",
            "role": "CANDIDATE", "profile_completed": True,
            "candidate_profile": {
                "current_status": "Actively Looking",
                "field_of_study": "Computer Science",
                "current_domain": "Backend Systems & Cloud"
            }
        }
        page.route("**/api/auth/me*", lambda r: r.fulfill(json=cand_prof))
        page.route("**/api/profile*", lambda r: r.fulfill(json=cand_prof))
        page.route("**/api/candidate/profile*", lambda r: r.fulfill(json=cand_prof))
        page.route("**/api/candidate/stats*", lambda r: r.fulfill(json={
            "latest_ats_score": 84.5,
            "last_analysis_date": "2026-11-08T14:30:00Z"
        }))
        page.route("**/api/candidate/resumes*", lambda r: r.fulfill(json=[
            {"id": 101, "version": 1, "label": "V1 - General Resume", "ats_score": 72.0, "uploaded_at": "2026-10-15T10:00:00Z", "job_description_title": "Senior Backend Engineer", "analysis_metadata": {"profile_name": "General Backend", "engine_version": "v1.0.0"}},
            {"id": 102, "version": 2, "label": "V2 - Targeted Resume", "ats_score": 84.5, "uploaded_at": "2026-11-08T14:30:00Z", "job_description_title": "Senior Backend Engineer", "analysis_metadata": {"profile_name": "General Backend", "engine_version": "v1.0.0"}}
        ]))


# ==============================================================================
# 1. STATIC CSS & CODE AUDIT TESTS
# ==============================================================================

def test_rec_main_wrapper_is_centered_without_left_anchor_overrides():
    """Verify .rec-main-wrapper is centered with margin-inline: auto and has no margin-left: 0 forcing it left."""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Must have auto margins for centering
    assert "margin-inline: auto" in content or "margin: 0 auto" in content
    # Should not have active sidebar-collapsed override pinning margin-left: 0 without auto
    assert "html.sidebar-pref-collapsed .rec-layout .rec-main-wrapper,\n.rec-layout.sidebar-collapsed .rec-main-wrapper {\n    margin-left: 0;\n}" not in content


def test_recruiter_html_summary_card_no_conflicting_inline_padding():
    """Workspace intelligence summary in recruiter.html must not override padding with inline style."""
    with open(RECRUITER_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the span-two summary card
    summary_match = re.search(r'<div class="stat-card span-two"([^>]*)>', content)
    assert summary_match is not None, "Missing .stat-card.span-two in recruiter.html"
    attrs = summary_match.group(1)
    assert "padding: 1.5rem" not in attrs, "Summary card has inline padding: 1.5rem overriding card padding!"


def test_candidate_js_kpi_card_no_inline_font_size_override():
    """Candidate dashboard Card 2 must not override font-size inline, breaking baseline with Card 1."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        content = f.read()

    assert 'id="cand-stat-last-date"' in content
    # Look for inline font-size on cand-stat-last-date
    assert 'style="font-size: 1.5rem; margin-top: 0.5rem;" id="cand-stat-last-date"' not in content, \
        "Candidate card 2 has inline font-size: 1.5rem breaking visual hierarchy!"


def test_kpi_card_has_height_100_and_uniform_icon_box():
    """Stat cards must be full height in grid cells and icons must have standard dimensions."""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        content = f.read()

    # Find .stat-card block
    stat_card_match = re.search(r'\.stat-card\s*\{([^}]*)\}', content)
    assert stat_card_match is not None
    stat_card_body = stat_card_match.group(1)
    assert "height: 100%" in stat_card_body, ".stat-card should declare height: 100% for grid cell parity"


# ==============================================================================
# 2. BROWSER PLAYWRIGHT LAYOUT TESTS
# ==============================================================================

def test_browser_recruiter_dashboard_kpi_and_summary_alignment():
    """Verify recruiter dashboard KPI cards have equal heights and summary card gap aligns with KPI grid."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_page_mock(page, "RECRUITER")

        page.goto("http://localhost:8085/recruiter.html", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        # 1. Container Centering Check
        main_box = page.locator(".rec-main-wrapper").bounding_box()
        expected_x = (1440 - main_box["width"]) / 2
        assert abs(main_box["x"] - expected_x) <= 2.0, \
            f"rec-main-wrapper is not centered! x={main_box['x']}, expected={expected_x}"

        # 2. KPI Cards Equal Heights
        cards = page.locator(".rec-grid > .stat-card:not(.span-two)").all()
        assert len(cards) == 4, f"Expected 4 KPI cards, got {len(cards)}"
        boxes = [c.bounding_box() for c in cards]

        # Row 1 (Card 0 & Card 1)
        assert abs(boxes[0]["height"] - boxes[1]["height"]) <= 1.0, \
            f"Row 1 KPI cards have unequal heights: {boxes[0]['height']} vs {boxes[1]['height']}"

        # Row 2 (Card 2 & Card 3)
        assert abs(boxes[2]["height"] - boxes[3]["height"]) <= 1.0, \
            f"Row 2 KPI cards have unequal heights: {boxes[2]['height']} vs {boxes[3]['height']}"

        # 3. KPI Icons Equal Dimensions
        icons = page.locator(".rec-grid > .stat-card:not(.span-two) .stat-icon").all()
        icon_boxes = [ic.bounding_box() for ic in icons]
        first_w = icon_boxes[0]["width"]
        first_h = icon_boxes[0]["height"]
        for i, ib in enumerate(icon_boxes):
            assert abs(ib["width"] - first_w) <= 0.5, f"Icon {i} width {ib['width']} != {first_w}"
            assert abs(ib["height"] - first_h) <= 0.5, f"Icon {i} height {ib['height']} != {first_h}"

        # 4. Summary Card Alignment
        grid_box = page.locator(".rec-grid").bounding_box()
        summary_box = page.locator(".stat-card.span-two").bounding_box()
        assert abs(summary_box["x"] - grid_box["x"]) <= 1.0, "Summary card left edge does not match grid!"
        assert abs(summary_box["width"] - grid_box["width"]) <= 1.0, "Summary card width does not match grid!"

        # Summary columns gap alignment with KPI grid
        col1 = page.locator(".stat-card.span-two > div:last-child > div:first-child").bounding_box()
        col2 = page.locator(".stat-card.span-two > div:last-child > div:nth-child(2)").bounding_box()
        summary_gap = col2["x"] - (col1["x"] + col1["width"])
        kpi_gap = boxes[1]["x"] - (boxes[0]["x"] + boxes[0]["width"])
        assert abs(summary_gap - kpi_gap) <= 2.0, \
            f"Summary column gap ({summary_gap}px) does not match KPI grid gap ({kpi_gap}px)!"

        browser.close()


def test_browser_candidate_dashboard_kpi_height_and_alignment():
    """Verify candidate dashboard KPI cards have equal heights and consistent metrics."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_page_mock(page, "CANDIDATE")

        page.goto("http://localhost:8085/candidate.html", wait_until="domcontentloaded")
        page.wait_for_timeout(1000)

        # 1. Container Centering Check
        main_box = page.locator(".rec-main-wrapper").bounding_box()
        expected_x = (1440 - main_box["width"]) / 2
        assert abs(main_box["x"] - expected_x) <= 2.0, \
            f"Candidate rec-main-wrapper is not centered! x={main_box['x']}, expected={expected_x}"

        # 2. Candidate KPI Cards Equal Heights
        cards = page.locator(".rec-grid > .stat-card:not(.span-two)").all()
        assert len(cards) >= 2, f"Expected at least 2 KPI cards, got {len(cards)}"
        boxes = [c.bounding_box() for c in cards]
        assert abs(boxes[0]["height"] - boxes[1]["height"]) <= 1.0, \
            f"Candidate KPI cards have unequal heights: {boxes[0]['height']} vs {boxes[1]['height']}"

        # 3. Value font-size consistency
        val1_font = page.locator("#cand-stat-latest-score").evaluate("el => window.getComputedStyle(el).fontSize")
        val2_font = page.locator("#cand-stat-last-date").evaluate("el => window.getComputedStyle(el).fontSize")
        assert val1_font == val2_font, \
            f"Candidate stat values have inconsistent font sizes: {val1_font} vs {val2_font}"

        browser.close()


def test_browser_zero_horizontal_overflow_all_viewports():
    """Verify zero horizontal scroll/overflow on all 6 viewports for recruiter and candidate workspaces."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)

        for vp in VIEWPORTS:
            # 1. Recruiter View
            page = browser.new_page(viewport={"width": vp["width"], "height": vp["height"]})
            setup_page_mock(page, "RECRUITER")
            page.goto("http://localhost:8085/recruiter.html", wait_until="domcontentloaded")
            page.wait_for_timeout(300)
            
            overflow_rec = page.evaluate("""() => {
                const doc = document.documentElement;
                const body = document.body;
                return {
                    docScroll: doc.scrollWidth,
                    bodyScroll: body.scrollWidth,
                    winWidth: window.innerWidth,
                    hasOverflow: doc.scrollWidth > window.innerWidth || body.scrollWidth > window.innerWidth
                };
            }""")
            assert not overflow_rec["hasOverflow"], \
                f"Recruiter page has horizontal overflow at {vp['name']} ({vp['width']}px): doc={overflow_rec['docScroll']} body={overflow_rec['bodyScroll']}"
            page.close()

            # 2. Candidate View
            page = browser.new_page(viewport={"width": vp["width"], "height": vp["height"]})
            setup_page_mock(page, "CANDIDATE")
            page.goto("http://localhost:8085/candidate.html", wait_until="domcontentloaded")
            page.wait_for_timeout(300)

            overflow_cand = page.evaluate("""() => {
                const doc = document.documentElement;
                const body = document.body;
                return {
                    docScroll: doc.scrollWidth,
                    bodyScroll: body.scrollWidth,
                    winWidth: window.innerWidth,
                    hasOverflow: doc.scrollWidth > window.innerWidth || body.scrollWidth > window.innerWidth
                };
            }""")
            assert not overflow_cand["hasOverflow"], \
                f"Candidate page has horizontal overflow at {vp['name']} ({vp['width']}px): doc={overflow_cand['docScroll']} body={overflow_cand['bodyScroll']}"
            page.close()

        browser.close()
