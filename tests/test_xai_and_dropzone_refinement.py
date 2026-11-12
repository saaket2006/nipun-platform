import os
import json
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
RECRUITER_HTML = os.path.join(FRONTEND_DIR, "recruiter.html")
CANDIDATE_HTML = os.path.join(FRONTEND_DIR, "candidate.html")
RECRUITER_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "recruiter.css")
BASE_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "base.css")
RECRUITER_JS = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "recruiter.js")
CANDIDATE_JS = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "candidate.js")


# ==============================================================================
# 1. BACKEND & STATIC VERIFICATION TESTS
# ==============================================================================

def test_backend_xai_engine_suppresses_skills_supporting_evidence():
    """Verify that backend XaiEngine suppresses per-skill supporting_evidence dictionaries."""
    from backend.services.xai.engine import XaiEngine
    from backend.services.xai.models import ScoreComponent, Evidence

    engine = XaiEngine()
    skills_comp = ScoreComponent(
        name="Technical Skills",
        raw_score=75.0,
        weight=0.5,
        weighted_score=37.5,
        max_score=100.0,
        status="partially_met",
        details="Technical skill evaluation",
        evidence=[
            Evidence(type="exact_match", category="Technical Skills", title="Exact Match: Python", description="Exact match", importance="high", related_skill="python", confidence=1.0),
            Evidence(type="unmatched", category="Technical Skills", title="Missing Skill: Docker", description="Missing skill", importance="low", related_skill="docker", confidence=0.0)
        ]
    )

    exp_comp = ScoreComponent(
        name="Work Experience",
        raw_score=80.0,
        weight=0.25,
        weighted_score=20.0,
        max_score=100.0,
        status="met",
        details="Work experience evaluation",
        evidence=[
            Evidence(type="experience_record", category="Work Experience", title="Industry Experience Level", description="Candidate has 5 years of professional experience", importance="high", confidence=1.0)
        ]
    )

    explanations = engine.generate_explanations([skills_comp, exp_comp])

    # Technical Skills supporting_evidence must be empty (suppressed in favor of consolidated overview)
    assert explanations["skills"]["summary"]["supporting_evidence"] == []
    assert explanations["skills"]["detailed"]["supporting_evidence"] == []

    # Non-skills component (Work Experience) retains its summary evidence
    assert len(explanations["experience"]["summary"]["supporting_evidence"]) == 1
    assert explanations["experience"]["summary"]["supporting_evidence"][0]["title"] == "Industry Experience Level"


def test_recruiter_js_omits_supporting_evidence_for_technical_skills():
    """Verify that recruiter.js explicitly suppresses per-skill Supporting Evidence cards in XAI."""
    with open(RECRUITER_JS, "r", encoding="utf-8") as f:
        js = f.read()

    # The filter logic in renderXaiContent must set evidenceItems to [] for skills
    assert '!lowerCompName.includes("skill")' in js or 'evidenceItems = [];' in js
    assert 'renderTechnicalSkillsOverview' in js


def test_candidate_js_omits_supporting_evidence_for_technical_skills():
    """Verify that candidate.js also suppresses per-skill Supporting Evidence cards in XAI."""
    with open(CANDIDATE_JS, "r", encoding="utf-8") as f:
        js = f.read()

    assert 'comp.name.toLowerCase().includes("skill")' in js or '!lowerCompName.includes("skill")' in js


def test_dropzone_html_and_css_structure():
    """Verify dropzones in recruiter and candidate have unified .drop-zone-content and centered styling."""
    with open(RECRUITER_HTML, "r", encoding="utf-8") as f:
        r_html = f.read()
    with open(CANDIDATE_HTML, "r", encoding="utf-8") as f:
        c_html = f.read()
    with open(BASE_CSS, "r", encoding="utf-8") as f:
        b_css = f.read()

    assert 'id="rec-drop-zone"' in r_html
    assert 'class="drop-zone-content"' in r_html
    assert 'class="drop-zone-icon-wrap"' in r_html

    assert 'id="cand-drop-zone"' in c_html
    assert 'class="drop-zone-content"' in c_html
    assert 'class="drop-zone-icon-wrap"' in c_html

    assert '.file-upload-box' in b_css
    assert '.drop-zone-content' in b_css
    assert '.drop-zone-icon-wrap' in b_css


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
    "resume_count": 2,
    "job_description": "Seeking Lead Infrastructure Architect for Kubernetes & Terraform multi-cloud deployment.",
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
            "analysis_metadata": {
                "xai": {
                    "enabled": True,
                    "overall_summary": "Strong overall candidate with stellar infrastructure qualifications.",
                    "components": [
                        {
                            "name": "Technical Skills",
                            "raw_score": 95,
                            "weight": 0.5,
                            "status": "exceeded",
                            "evidence": [
                                {"title": "Exact Match: kubernetes", "importance": "high", "description": "Candidate has exact match"},
                                {"title": "Exact Match: aws", "importance": "high", "description": "Candidate has exact match"},
                                {"title": "Missing Skill: gcp", "importance": "low", "description": "No match found"}
                            ]
                        },
                        {
                            "name": "Work Experience",
                            "raw_score": 90,
                            "weight": 0.25,
                            "status": "met",
                            "evidence": [
                                {"title": "Industry Experience Level", "importance": "high", "description": "Candidate has 8 years of professional experience"}
                            ]
                        }
                    ],
                    "explanations": {
                        "skills": {
                            "summary": {
                                "why_awarded": "Points awarded for exceptional core mastery of Kubernetes, AWS, and Terraform.",
                                "why_deducted": "Points deducted for missing GCP cloud platform experience."
                            }
                        },
                        "experience": {
                            "summary": {
                                "why_awarded": "Candidate has 8 years of relevant architecture tenure.",
                                "why_deducted": "No deductions applied."
                            }
                        }
                    }
                }
            }
        }
    ]
}

def setup_page_mock(page):
    page.route("**/firebase-auth.js*", lambda r: r.fulfill(
        status=200,
        content_type="application/javascript",
        body=MOCK_AUTH_JS
    ))
    page.route("**/api/auth/me", lambda r: r.fulfill(json={
        "id": 1, "email": "sarah.connor@apex.com", "display_name": "Sarah Connor",
        "role": "RECRUITER", "profile_completed": True
    }))
    page.route("**/api/recruiter/profile", lambda r: r.fulfill(json={
        "id": 1, "email": "sarah.connor@apex.com", "display_name": "Sarah Connor",
        "role": "RECRUITER", "profile_completed": True,
        "recruiter_profile": {
            "company_name": "Apex Tech Solutions",
            "company_type": "Enterprise",
            "hiring_domain": "Cloud Infrastructure"
        }
    }))
    page.route("**/api/recruiter/stats", lambda r: r.fulfill(json={
        "total_screened": 10, "average_score": 85.0, "average_experience": 5.0,
        "common_education": "B.Tech", "common_missing_skills": [], "common_matched_skills": [], "common_improvements": []
    }))
    page.route("**/api/recruiter/profiles*", lambda r: r.fulfill(json=[]))
    page.route("**/api/recruiter/jobs*", lambda r: r.fulfill(json=[]))
    page.route("**/api/recruiter/screening-tasks*", lambda r: r.fulfill(json=[]))
    page.route("**/api/profile*", lambda r: r.fulfill(json={
        "id": 1, "email": "sarah.connor@apex.com", "display_name": "Sarah Connor",
        "role": "RECRUITER", "profile_completed": True,
        "recruiter_profile": {
            "company_name": "Apex Tech Solutions",
            "company_type": "Enterprise",
            "hiring_domain": "Cloud Infrastructure"
        }
    }))
    page.route("**/api/recruiter/history", lambda r: r.fulfill(json=[{"id": 42, "role": "Lead Infrastructure Architect", "created_at": "2026-11-10T14:30:00Z", "resume_count": 2}]))
    page.route("**/api/recruiter/history/*", lambda r: r.fulfill(json=MOCK_TASK_DETAIL))


def test_browser_quick_view_no_redundant_skills_evidence():
    """Verify Quick View modal displays consolidated Skills Overview and NO per-skill Supporting Evidence cards."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        setup_page_mock(page)

        page.goto("http://localhost:8085/recruiter.html#/recruiter/history?id=42", wait_until="domcontentloaded")
        page.wait_for_selector(".quick-view-btn", state="visible", timeout=10000)

        # Click Quick View on first candidate
        qv_btn = page.locator(".quick-view-btn").first
        assert qv_btn.is_visible()
        qv_btn.click()
        page.wait_for_selector("#rec-quick-view-modal", state="visible", timeout=5000)

        modal = page.locator("#rec-quick-view-modal")
        assert modal.is_visible(), "Quick View modal must open"

        # Check Consolidated Technical Skills Overview
        skills_overview = page.locator("#qv-skills-overview-section")
        assert skills_overview.is_visible(), "Technical Skills Overview must be visible"

        matched_chips = page.locator("#qv-cand-matched-skills .skill-chip").all()
        assert len(matched_chips) == 4, f"Expected 4 matched skill chips, got {len(matched_chips)}"

        missing_chips = page.locator("#qv-cand-missing-skills .skill-chip").all()
        assert len(missing_chips) == 1, f"Expected 1 missing skill chip, got {len(missing_chips)}"

        # Open Technical Skills XAI accordion
        skills_accordion = page.locator(".xai-accordion-item").filter(has_text="Technical Skills").first
        assert skills_accordion.is_visible()
        
        # Click header to expand accordion
        skills_header = skills_accordion.locator(".xai-accordion-header")
        skills_header.click()
        page.wait_for_timeout(300)

        # Points Awarded and Deductions must be present
        awarded_text = skills_accordion.locator(".xai-text-awarded")
        assert awarded_text.is_visible()
        assert "Points awarded for exceptional core mastery" in awarded_text.text_content()

        deducted_text = skills_accordion.locator(".xai-text-deducted")
        assert deducted_text.is_visible()
        assert "Points deducted for missing GCP" in deducted_text.text_content()

        # CRITICAL ASSERTION: No Supporting Evidence header and no per-skill evidence cards in Technical Skills!
        skills_content_text = skills_accordion.locator(".xai-accordion-content").inner_text()
        assert "SUPPORTING EVIDENCE" not in skills_content_text.upper()
        assert "Exact Match: kubernetes" not in skills_content_text
        assert "Missing Skill: gcp" not in skills_content_text

        browser.close()


def test_browser_dropzone_and_action_button_alignment():
    """Verify dropzone and action button have matching widths and perfectly centered icon and text."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        
        # Test across Desktop (1440), Tablet (768), and Mobile (390)
        for vp_width in [1440, 768, 390]:
            page = browser.new_page(viewport={"width": vp_width, "height": 900})
            setup_page_mock(page)

            page.goto("http://localhost:8085/recruiter.html#/recruiter/screen", wait_until="domcontentloaded")
            page.wait_for_selector("#rec-drop-zone", state="visible", timeout=10000)

            dropzone = page.locator("#rec-drop-zone")
            process_btn = page.locator("#rec-process-btn")

            assert dropzone.is_visible()
            assert process_btn.is_visible()

            dz_box = dropzone.bounding_box()
            btn_box = process_btn.bounding_box()

            # Equal width check (within 2px tolerance)
            assert abs(dz_box["width"] - btn_box["width"]) <= 2.0, \
                f"Width mismatch at {vp_width}px: Dropzone={dz_box['width']}px, Button={btn_box['width']}px"

            # Horizontal centering of dropzone icon wrap
            icon_wrap = dropzone.locator(".drop-zone-icon-wrap")
            assert icon_wrap.is_visible()
            icon_box = icon_wrap.bounding_box()

            dz_center_x = dz_box["x"] + dz_box["width"] / 2
            icon_center_x = icon_box["x"] + icon_box["width"] / 2
            assert abs(dz_center_x - icon_center_x) <= 5.0, \
                f"Dropzone icon not centered at {vp_width}px: dz={dz_center_x}, icon={icon_center_x}"

            # Text centering check
            primary_text = dropzone.locator(".drop-zone-primary")
            assert primary_text.is_visible()
            text_align = primary_text.evaluate("el => window.getComputedStyle(el).textAlign")
            assert text_align == "center"

            page.close()

        browser.close()
