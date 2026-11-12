import os
import re
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
RECRUITER_HTML = os.path.join(FRONTEND_DIR, "recruiter.html")
RECRUITER_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "recruiter.css")
BASE_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "base.css")
RECRUITER_JS = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "recruiter.js")


# ==============================================================================
# 1. STATIC HTML & CSS AUDIT TESTS
# ==============================================================================

def test_dropzone_html_structure_and_ids():
    """Verify #rec-drop-zone has centered content wrapper, icon badge, primary & secondary text, and preserves IDs."""
    with open(RECRUITER_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # Drop zone container
    assert 'id="rec-drop-zone"' in content, "Missing #rec-drop-zone ID"
    assert 'id="rec-resumes"' in content, "Missing #rec-resumes file input ID"
    assert 'id="rec-resumes-header"' in content, "Missing #rec-resumes-header ID"
    assert 'id="rec-resumes-count"' in content, "Missing #rec-resumes-count ID"
    assert 'id="rec-file-list"' in content, "Missing #rec-file-list ID"
    assert 'id="rec-process-btn"' in content, "Missing #rec-process-btn ID"

    # Centered content group wrapper
    assert 'drop-zone-content' in content, "Missing .drop-zone-content wrapper inside dropzone"
    assert 'drop-zone-icon-wrap' in content, "Missing .drop-zone-icon-wrap for circular icon container"
    assert 'drop-zone-primary' in content, "Missing .drop-zone-primary for main instruction text"
    assert 'drop-zone-secondary' in content, "Missing .drop-zone-secondary for helper/supported formats text"


def test_dropzone_css_alignment_and_states():
    """Verify dropzone CSS enforces centered group alignment, min-height, hover/drag states, and collapsed mode."""
    css_content = ""
    with open(RECRUITER_CSS, "r", encoding="utf-8") as f:
        css_content += f.read() + "\n"
    with open(BASE_CSS, "r", encoding="utf-8") as f:
        css_content += f.read()

    # Must define .drop-zone-content centering
    assert ".drop-zone-content" in css_content
    # Must style .drop-zone-icon-wrap
    assert ".drop-zone-icon-wrap" in css_content
    # Collapsed state must hide .drop-zone-content
    assert ".file-upload-box.collapsed .drop-zone-content" in css_content or \
           "#rec-drop-zone.collapsed .drop-zone-content" in css_content


def test_quick_view_modal_html_structure():
    """Verify recruiter.html quick view modal structure supports the refined architecture."""
    with open(RECRUITER_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    assert 'id="rec-quick-view-modal"' in content
    assert 'id="qv-xai-section"' in content
    assert 'id="qv-xai-container"' in content
    assert 'id="qv-cand-name"' in content


# ==============================================================================
# 2. STATIC JS AUDIT TESTS
# ==============================================================================

def test_render_xai_content_removes_summary_detailed_toggle():
    """renderXaiContent must NOT render summary/detailed toggle buttons (.xai-level-btn)."""
    with open(RECRUITER_JS, "r", encoding="utf-8") as f:
        content = f.read()

    xai_render_match = re.search(r'export function renderXaiContent[\s\S]*?^}', content, re.MULTILINE)
    assert xai_render_match is not None, "renderXaiContent function not found"
    xai_code = xai_render_match.group(0)

    assert "xai-level-btn" not in xai_code, "renderXaiContent should not generate .xai-level-btn toggle buttons"
    assert "toggleXaiLevel" not in xai_code, "renderXaiContent should not contain toggleXaiLevel calls"


def test_recruiter_js_consolidates_skills_overview():
    """recruiter.js must provide a consolidated Technical Skills Overview and eliminate per-skill evidence cards."""
    with open(RECRUITER_JS, "r", encoding="utf-8") as f:
        content = f.read()

    # Must contain logic to render Technical Skills Overview with matched and missing skills
    assert "Matched Skills" in content
    assert "Missing Skills" in content


def test_recruiter_js_consolidates_overall_score_and_scoring_breakdown():
    """showCandidateQuickView / renderXaiContent must render Overall Score & ATS Overview with scoring breakdown."""
    with open(RECRUITER_JS, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Scoring Breakdown" in content or "scoring-breakdown" in content or "score-breakdown" in content


# ==============================================================================
# 3. PLAYWRIGHT BROWSER FUNCTIONAL TESTS
# ==============================================================================

MOCK_AUTH_JS = """
export function getAuth() {
    const user = {
        uid: "test_rec_1",
        email: "recruiter@apex.com",
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

def setup_page_mock(page):
    page.route("**/firebase-auth.js*", lambda r: r.fulfill(
        status=200,
        content_type="application/javascript",
        body=MOCK_AUTH_JS
    ))
    page.route("**/api/auth/me", lambda r: r.fulfill(json={
        "id": 1, "email": "recruiter@apex.com", "display_name": "Sarah Connor",
        "role": "RECRUITER", "profile_completed": True
    }))
    mock_prof = {
        "id": 1, "email": "recruiter@apex.com", "display_name": "Sarah Connor",
        "role": "RECRUITER", "profile_completed": True,
        "recruiter_profile": {
            "company_name": "Apex Tech Solutions",
            "company_type": "Enterprise",
            "hiring_domain": "Cloud Infrastructure & AI"
        }
    }
    page.route("**/api/recruiter/profile*", lambda r: r.fulfill(json=mock_prof))
    page.route("**/api/profile*", lambda r: r.fulfill(json=mock_prof))
    page.route("**/api/recruiter/stats*", lambda r: r.fulfill(json={
        "total_screened": 10,
        "average_score": 82.0,
        "average_experience": 5.0,
        "common_education": "B.Tech in CS",
        "common_missing_skills": ["Kubernetes"],
        "common_matched_skills": ["Python", "FastAPI"],
        "common_improvements": []
    }))
    page.route("**/api/recruiter/profiles*", lambda r: r.fulfill(json=[]))
    page.route("**/api/recruiter/jobs*", lambda r: r.fulfill(json=[]))
    page.route("**/api/recruiter/job-descriptions*", lambda r: r.fulfill(json=[]))
    page.route("**/api/recruiter/screening-tasks*", lambda r: r.fulfill(json=[]))
    page.route("**/api/recruiter/history*", lambda r: r.fulfill(json=[]))


@pytest.fixture(scope="module")
def web_server():
    return "http://localhost:8085"


def test_browser_dropzone_centered_layout(web_server):
    """Verify dropzone content group (icon, primary text, helper) is visually and horizontally centered."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_page_mock(page)

        page.goto(f"{web_server}/recruiter.html#/recruiter/screen", wait_until="domcontentloaded")
        page.wait_for_selector("#rec-drop-zone", state="visible", timeout=15000)

        dropzone = page.locator("#rec-drop-zone")
        assert dropzone.is_visible(), "#rec-drop-zone must be visible in screen view"

        dz_box = dropzone.bounding_box()
        assert dz_box["width"] > 400, "Dropzone should span across screening form"
        assert dz_box["height"] >= 160, f"Dropzone deliberate height should be at least 160px, got {dz_box['height']}"

        # Check .drop-zone-content is centered inside dropzone
        content_box = page.locator("#rec-drop-zone .drop-zone-content").bounding_box()
        dz_center_x = dz_box["x"] + dz_box["width"] / 2
        content_center_x = content_box["x"] + content_box["width"] / 2
        assert abs(dz_center_x - content_center_x) <= 15.0, \
            f"Dropzone content is not horizontally centered: dz={dz_center_x}, content={content_center_x}"

        # Check vertical order: icon wrap -> primary text -> secondary text
        icon_box = page.locator("#rec-drop-zone .drop-zone-icon-wrap").bounding_box()
        primary_box = page.locator("#rec-drop-zone .drop-zone-primary").bounding_box()
        sec_box = page.locator("#rec-drop-zone .drop-zone-secondary").bounding_box()

        assert icon_box["y"] < primary_box["y"], "Icon must be vertically above primary instruction"
        assert primary_box["y"] < sec_box["y"], "Primary instruction must be vertically above secondary text"

        browser.close()


def test_browser_quick_view_xai_and_skills_consolidation(web_server):
    """Verify quick view modal displays consolidated overall score, skills overview, and simplified XAI without toggle buttons."""
    from playwright.sync_api import sync_playwright

    mock_candidate = {
        "id": 101,
        "name": "Alex Vance",
        "email": "alex.vance@example.com",
        "phone": "+1 (555) 234-5678",
        "linkedin": "https://linkedin.com/in/alexvance",
        "github": "https://github.com/alexvance",
        "similarity_score": 88,
        "skill_score": 90,
        "experience_score": 85,
        "education_score": 100,
        "projects_score": 80,
        "matched_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        "missing_skills": ["Kubernetes", "GraphQL"],
        "extracted_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "Kubernetes", "GraphQL", "Git"],
        "analysis_metadata": {
            "profile_name": "Senior Cloud Backend Engineer",
            "profile_version": "1.2.0",
            "engine_version": "v1.0.0",
            "xai": {
                "enabled": True,
                "overall_summary": "Alex demonstrates an outstanding match with deep backend expertise in Python and AWS.",
                "components": [
                    {
                        "name": "Overall Score",
                        "raw_score": 88,
                        "weight": 1.0,
                        "status": "met",
                        "evidence": [
                            {"title": "Exact Match: python", "description": "Matched directly", "importance": "high"},
                            {"title": "Missing Skill: kubernetes", "description": "Not found in resume", "importance": "medium"}
                        ]
                    },
                    {
                        "name": "Technical Skills",
                        "raw_score": 90,
                        "weight": 0.50,
                        "status": "met",
                        "evidence": [
                            {"title": "Exact Match: python", "description": "Direct keyword match", "importance": "high"},
                            {"title": "Exact Match: fastapi", "description": "Direct keyword match", "importance": "high"},
                            {"title": "Missing Skill: kubernetes", "description": "Required infrastructure skill absent", "importance": "high"}
                        ]
                    },
                    {
                        "name": "Work Experience",
                        "raw_score": 85,
                        "weight": 0.25,
                        "status": "met",
                        "evidence": [
                            {"title": "Senior Engineer Role", "description": "Over 5 years in production environments", "importance": "high"}
                        ]
                    },
                    {
                        "name": "Education",
                        "raw_score": 100,
                        "weight": 0.15,
                        "status": "met",
                        "evidence": [
                            {"title": "Degree Alignment", "description": "B.S. in Computer Science", "importance": "info"}
                        ]
                    },
                    {
                        "name": "Projects",
                        "raw_score": 80,
                        "weight": 0.10,
                        "status": "met",
                        "evidence": [
                            {"title": "Open Source Contributions", "description": "Active FastAPI libraries", "importance": "info"}
                        ]
                    }
                ],
                "explanations": {
                    "skills": {
                        "summary": {
                            "why_awarded": "Candidate matched 5 of 7 required skills including core languages and backend frameworks.",
                            "why_deducted": "Candidate lacked Kubernetes orchestration experience which caused a 10% deduction in skills scoring."
                        }
                    },
                    "experience": {
                        "summary": {
                            "why_awarded": "5 years of relevant backend development exceeds the 3 year minimum requirement.",
                            "why_deducted": "No deductions applied."
                        }
                    },
                    "education": {
                        "summary": {
                            "why_awarded": "B.S. in Computer Science fully satisfies the educational baseline.",
                            "why_deducted": "No deductions applied."
                        }
                    },
                    "projects": {
                        "summary": {
                            "why_awarded": "Projects demonstrate hands-on application of backend architectural principles.",
                            "why_deducted": "Limited high-scale distributed systems projects."
                        }
                    }
                }
            }
        }
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_page_mock(page)

        page.goto(f"{web_server}/recruiter.html", wait_until="domcontentloaded")
        page.wait_for_selector("#recruiter-container", state="visible", timeout=10000)
        page.wait_for_function("() => typeof window.showCandidateQuickView === 'function'", timeout=10000)

        # Trigger showCandidateQuickView with the mock candidate
        page.evaluate("(cand) => window.showCandidateQuickView(cand)", mock_candidate)
        page.wait_for_timeout(500)

        modal = page.locator("#rec-quick-view-modal")
        assert modal.is_visible(), "Candidate Quick View modal must be visible"

        # 1. Verify absence of Summary/Detailed toggle buttons
        level_buttons = page.locator(".xai-level-btn").all()
        assert len(level_buttons) == 0, f"Expected 0 .xai-level-btn buttons, but found {len(level_buttons)}"

        # 2. Verify consolidated Technical Skills Overview
        # Matched skills group
        matched_tags = page.locator(".skills-overview-group.matched .skill-chip, #qv-skills-matched .skill-chip, .skill-tag.matched").all()
        assert len(matched_tags) >= 5, f"Expected at least 5 matched skill tags, got {len(matched_tags)}"

        # Missing skills group
        missing_tags = page.locator(".skills-overview-group.missing .skill-chip, #qv-skills-missing .skill-chip, .skill-tag.missing").all()
        assert len(missing_tags) >= 2, f"Expected at least 2 missing skill tags, got {len(missing_tags)}"

        # 3. Verify no repetitive per-skill evidence cards in the XAI accordion
        # In Technical Skills accordion, individual "Exact Match: python", "Missing Skill: kubernetes" should NOT be rendered
        xai_container_text = page.locator("#qv-xai-container").inner_text()
        assert "Missing Skill: kubernetes" not in xai_container_text, \
            "Found raw 'Missing Skill: kubernetes' evidence card in XAI container! Per-skill evidence should be consolidated."
        assert "Exact Match: python" not in xai_container_text, \
            "Found raw 'Exact Match: python' evidence card in XAI container! Per-skill evidence should be consolidated."

        # 4. Verify Overall Score & ATS Overview at top
        # Must show Overall Match Score
        assert "88% Match" in page.locator("#rec-quick-view-modal").inner_text() or \
               "88.0% Match" in page.locator("#rec-quick-view-modal").inner_text()
        
        # Must show Scoring Breakdown rows/table
        modal_text = page.locator("#rec-quick-view-modal").inner_text()
        assert "Technical Skills" in modal_text
        assert "Work Experience" in modal_text
        assert "Education" in modal_text
        assert "Projects" in modal_text

        # 5. Verify accordion expand / collapse behavior
        first_accordion_header = page.locator(".xai-accordion-header").first
        first_accordion_content = page.locator(".xai-accordion-content").first
        assert not first_accordion_content.is_visible(), "Accordion should start collapsed"
        
        first_accordion_header.click()
        page.wait_for_timeout(200)
        assert first_accordion_content.is_visible(), "Accordion should be visible after click"

        first_accordion_header.click()
        page.wait_for_timeout(200)
        assert not first_accordion_content.is_visible(), "Accordion should collapse after second click"

        browser.close()


def test_browser_dropzone_drag_and_file_handling(web_server, tmp_path):
    """Verify dropzone drag events, file input, and collapsed state transition."""
    from playwright.sync_api import sync_playwright

    # Create dummy pdf file
    dummy_pdf = tmp_path / "resume_jane_doe.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 mock resume content")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_page_mock(page)

        page.goto(f"{web_server}/recruiter.html#/recruiter/screen", wait_until="domcontentloaded")
        page.wait_for_selector("#rec-drop-zone", state="visible", timeout=15000)

        dropzone = page.locator("#rec-drop-zone")
        assert dropzone.is_visible()

        # 1. Dragover and dragleave states
        dropzone.dispatch_event("dragover")
        assert "drag-over" in (dropzone.get_attribute("class") or "")

        dropzone.dispatch_event("dragleave")
        assert "drag-over" not in (dropzone.get_attribute("class") or "")

        # 2. File attachment
        file_input = page.locator("#rec-resumes")
        file_input.set_input_files(str(dummy_pdf))
        page.wait_for_timeout(500)

        # File list should render resume item
        file_list = page.locator("#rec-file-list")
        assert file_list.is_visible() or page.locator(".rec-file-item").count() > 0
        assert "resume_jane_doe.pdf" in page.locator("#rec-file-list").inner_text()

        # 3. Remove file
        remove_btn = page.locator(".rec-file-remove-btn").first
        remove_btn.click()
        page.wait_for_timeout(500)
        assert page.locator(".rec-file-item").count() == 0

        browser.close()


