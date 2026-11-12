import os
import re
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
INDEX_HTML = os.path.join(FRONTEND_DIR, "index.html")
MODAL_JS = os.path.join(FRONTEND_DIR, "assets", "js", "components", "modal.js")
APP_JS = os.path.join(FRONTEND_DIR, "assets", "js", "app.js")
ROUTER_JS = os.path.join(FRONTEND_DIR, "assets", "js", "router.js")

def test_single_auth_modal_instance():
    """Verify index.html contains exactly one #auth-modal element."""
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    matches = re.findall(r'id=["\']auth-modal["\']', content)
    assert len(matches) == 1, f"Expected exactly 1 #auth-modal, found {len(matches)}"

def test_auth_modal_has_required_planes_and_tabs():
    """Verify #auth-modal has login and signup tabs and planes."""
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    assert 'id="login-plane"' in content, "Missing #login-plane in index.html"
    assert 'id="signup-plane"' in content, "Missing #signup-plane in index.html"
    assert 'id="tab-login"' in content, "Missing #tab-login in index.html"
    assert 'id="tab-signup"' in content, "Missing #tab-signup in index.html"

def test_landing_buttons_have_data_auth_modal_contract():
    """
    Verify all key CTA buttons in index.html possess resilient data-auth-modal attributes:
    1. Header Sign In (data-auth-modal="login")
    2. Header Get Started (data-auth-modal="signup")
    3. Mobile Drawer Sign In (data-auth-modal="login")
    4. Mobile Drawer Get Started (data-auth-modal="signup")
    5. Hero Start Screening Free (data-auth-modal="signup")
    6. Bottom Start Free Screening (data-auth-modal="signup")
    7. Bottom Candidate Portal (data-auth-modal="login")
    """
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # Header Sign In
    header_login = re.search(r'<button[^>]*class="[^"]*nav-login-btn[^"]*"[^>]*>[\s\S]*?Sign[\s\S]*?In[\s\S]*?</button>', content)
    assert header_login is not None, "Header Sign In button not found"
    assert 'data-auth-modal="login"' in header_login.group(0), "Header Sign In missing data-auth-modal='login'"

    # Header Get Started
    header_signup = re.search(r'<button[^>]*class="[^"]*nav-signup-btn[^"]*"[^>]*>[\s\S]*?Get[\s\S]*?Started[\s\S]*?</button>', content)
    assert header_signup is not None, "Header Get Started button not found"
    assert 'data-auth-modal="signup"' in header_signup.group(0), "Header Get Started missing data-auth-modal='signup'"

    # Hero Start Screening Free
    hero_cta = re.search(r'<button[^>]*class="[^"]*hero-cta-primary[^"]*"[^>]*>[\s\S]*?Start Screening Free[\s\S]*?</button>', content)
    assert hero_cta is not None, "Hero Start Screening Free CTA not found"
    assert 'data-auth-modal="signup"' in hero_cta.group(0), "Hero CTA missing data-auth-modal='signup'"

    # Bottom CTA Start Free Screening
    bottom_cta_signup = re.search(r'<button[^>]*class="[^"]*nav-signup-btn[^"]*"[^>]*>[\s\S]*?Start Free Screening[\s\S]*?</button>', content)
    assert bottom_cta_signup is not None, "Bottom CTA Start Free Screening not found"
    assert 'data-auth-modal="signup"' in bottom_cta_signup.group(0), "Bottom CTA missing data-auth-modal='signup'"

    # Bottom CTA Candidate Portal
    bottom_cta_login = re.search(r'<button[^>]*class="[^"]*nav-login-btn[^"]*"[^>]*>[\s\S]*?Candidate Portal[\s\S]*?</button>', content)
    assert bottom_cta_login is not None, "Bottom CTA Candidate Portal not found"
    assert 'data-auth-modal="login"' in bottom_cta_login.group(0), "Bottom CTA Candidate Portal missing data-auth-modal='login'"

    # Mobile Drawer buttons
    drawer_section = re.search(r'id=["\']landing-mobile-drawer["\'][\s\S]*?</div>\s*</div>\s*</div>', content)
    assert drawer_section is not None, "landing-mobile-drawer section not found"
    drawer_text = drawer_section.group(0)
    assert 'data-auth-modal="login"' in drawer_text, "Mobile drawer missing data-auth-modal='login'"
    assert 'data-auth-modal="signup"' in drawer_text, "Mobile drawer missing data-auth-modal='signup'"

def test_modal_js_exports_open_and_close_auth_modal():
    """Verify modal.js exports explicit openAuthModal and closeAuthModal functions."""
    with open(MODAL_JS, "r", encoding="utf-8") as f:
        content = f.read()

    assert re.search(r'export\s+function\s+openAuthModal\s*\(', content) is not None, \
        "modal.js must export openAuthModal(mode)"
    assert re.search(r'export\s+function\s+closeAuthModal\s*\(', content) is not None, \
        "modal.js must export closeAuthModal()"

def test_modal_js_attaches_event_delegation():
    """Verify modal.js attaches event delegation on document to handle auth triggers dynamically."""
    with open(MODAL_JS, "r", encoding="utf-8") as f:
        content = f.read()

    assert "data-auth-modal" in content, "modal.js must handle [data-auth-modal] triggers"
    assert "closest" in content, "modal.js must use event delegation with .closest()"

def test_app_js_invokes_init_modals():
    """Verify app.js actively calls initModals() during page initialization."""
    with open(APP_JS, "r", encoding="utf-8") as f:
        content = f.read()

    assert re.search(r'\binitModals\(\)', content) is not None, \
        "app.js must explicitly call initModals()"

def test_app_js_handles_dom_ready_race_condition():
    """Verify app.js handles readyState interactive/complete so module execution never misses DOM readiness."""
    with open(APP_JS, "r", encoding="utf-8") as f:
        content = f.read()

    assert "readyState" in content or "DOMContentLoaded" in content
    # Specifically ensure it doesn't just blindly wait on DOMContentLoaded without checking readyState
    assert "readyState" in content, "app.js must check document.readyState before attaching DOMContentLoaded"

def test_router_js_integrates_modal_api():
    """Verify router.js integrates with modal.js for auth routing."""
    with open(ROUTER_JS, "r", encoding="utf-8") as f:
        content = f.read()

    assert "openAuthModal" in content or "closeAuthModal" in content or "resetAuthModalToTabs" in content

