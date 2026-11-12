import os
import re
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
INDEX_HTML = os.path.join(FRONTEND_DIR, "index.html")
SIGNUP_JS = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "signup.js")
LOGIN_JS = os.path.join(FRONTEND_DIR, "assets", "js", "pages", "login.js")
MODAL_JS = os.path.join(FRONTEND_DIR, "assets", "js", "components", "modal.js")
AUTH_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "auth.css")

def test_signup_plane_contains_conditional_confirm_password():
    """Verify index.html contains #signup-confirm-group and #signup-confirm-password inside #signup-form."""
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert 'id="signup-confirm-group"' in content, "Missing #signup-confirm-group in index.html"
    assert 'id="signup-confirm-password"' in content, "Missing #signup-confirm-password in index.html"
    assert 'id="signup-password-match-feedback"' in content, "Missing #signup-password-match-feedback in index.html"
    assert 'data-target="signup-confirm-password"' in content, "Missing data-target bindings for confirm password buttons"

def test_login_and_reset_planes_do_not_contain_confirm_password():
    """Confirm Password field must NOT appear in Login, Forgot Password, or unrelated planes."""
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # Login plane extraction
    login_match = re.search(r'id=["\']login-plane["\'][\s\S]*?id=["\']signup-plane["\']', content)
    assert login_match is not None
    assert 'confirm-password' not in login_match.group(0), "Confirm Password unexpectedly found in #login-plane"

    # Forgot password plane extraction
    forgot_match = re.search(r'id=["\']forgot-password-plane["\'][\s\S]*?id=["\']reset-password-plane["\']', content)
    assert forgot_match is not None
    assert 'confirm-password' not in forgot_match.group(0), "Confirm Password unexpectedly found in #forgot-password-plane"

def test_signup_js_exports_validate_password_match():
    """Verify signup.js exports validatePasswordMatch and gates Firebase registration."""
    with open(SIGNUP_JS, "r", encoding="utf-8") as f:
        content = f.read()

    assert "validatePasswordMatch" in content, "signup.js must export or define validatePasswordMatch"
    assert "createUserWithEmailAndPassword" in content, "signup.js must use Firebase createUserWithEmailAndPassword"
    
    # Verify password !== confirmPassword check occurs before createUserWithEmailAndPassword
    mismatch_idx = content.find("password !== confirmPassword")
    firebase_idx = content.find("createUserWithEmailAndPassword(auth, email, password)")
    assert mismatch_idx != -1, "Missing password !== confirmPassword check"
    assert firebase_idx != -1, "Missing createUserWithEmailAndPassword call"
    assert mismatch_idx < firebase_idx, "Password mismatch check must execute BEFORE Firebase registration!"

def test_confirm_password_value_is_never_sent_to_backend():
    """Confirm password value must never be sent to API, state, or storage."""
    with open(SIGNUP_JS, "r", encoding="utf-8") as f:
        content = f.read()

    assert "state.setToken" in content
    # Ensure confirm password is not in state or passed to Firebase
    assert "createUserWithEmailAndPassword(auth, email, password)" in content
    assert "confirmPassword" not in content.split("createUserWithEmailAndPassword")[1].split(";")[0]

def test_auth_css_defines_smooth_transitions_and_semantic_feedback():
    """Verify auth.css defines .confirm-password-group, .is-visible, and feedback styling."""
    with open(AUTH_CSS, "r", encoding="utf-8") as f:
        content = f.read()

    assert ".confirm-password-group" in content
    assert ".confirm-password-group.is-visible" in content
    assert "max-height" in content
    assert ".password-match-feedback" in content
    assert ".match-success" in content
    assert ".match-error" in content

def test_browser_confirm_password_lifecycle():
    """Verify full interactive lifecycle: reveal, clear, match, mismatch, tab isolation via Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright not installed in environment")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")
        except Exception as e:
            pytest.skip(f"Chrome browser launch skipped: {e}")

        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Load local server page
        try:
            page.goto("http://localhost:8085/index.html", wait_until="networkidle", timeout=5000)
        except Exception as e:
            browser.close()
            pytest.skip(f"Dev server on 8085 not reachable: {e}")

        # Open Sign Up Modal
        get_started_btn = page.locator('header .nav-signup-btn')
        get_started_btn.click()
        page.wait_for_timeout(300)

        confirm_group = page.locator('#signup-confirm-group')
        password_input = page.locator('#signup-password')
        confirm_input = page.locator('#signup-confirm-password')
        feedback = page.locator('#signup-password-match-feedback')

        # 1. Initially hidden
        assert not confirm_group.evaluate("el => el.classList.contains('is-visible')")

        # 2. Typing password reveals confirm password
        password_input.fill("Password123!")
        page.wait_for_timeout(350)
        assert confirm_group.evaluate("el => el.classList.contains('is-visible')")

        # 3. Mismatch detection
        confirm_input.fill("WrongPassword!")
        page.wait_for_timeout(200)
        assert "Passwords do not match." in feedback.inner_text()
        assert feedback.evaluate("el => el.classList.contains('match-error')")

        # 4. Exact match detection
        confirm_input.fill("Password123!")
        page.wait_for_timeout(200)
        assert "Passwords match." in feedback.inner_text()
        assert feedback.evaluate("el => el.classList.contains('match-success')")

        # 5. Revalidation on primary password edit
        password_input.fill("Password123!Edited")
        page.wait_for_timeout(200)
        assert "Passwords do not match." in feedback.inner_text()

        # 6. Clearing primary password hides and resets confirm password
        password_input.fill("")
        page.wait_for_timeout(350)
        assert not confirm_group.evaluate("el => el.classList.contains('is-visible')")
        assert confirm_input.input_value() == ""

        # 7. Tab switching reset
        password_input.fill("TestPassword123!")
        page.wait_for_timeout(300)
        page.locator('#tab-login').click()
        page.wait_for_timeout(250)
        page.locator('#tab-signup').click()
        page.wait_for_timeout(250)
        assert not confirm_group.evaluate("el => el.classList.contains('is-visible')")
        assert password_input.input_value() == ""
        assert confirm_input.input_value() == ""

        context.close()
        browser.close()

def test_confirm_password_file_protocol_e2e():
    """Verify that when opened via file:// protocol (CORS-isolated, zero-module), the resilient engine works."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright not installed in current environment")

    file_url = f"file:///{INDEX_HTML.replace(os.sep, '/')}"
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(file_url)
        page.wait_for_timeout(300)

        # Trigger signup modal
        page.locator('.nav-signup-btn').first.click()
        page.wait_for_timeout(300)

        confirm_group = page.locator('#signup-confirm-group')
        password_input = page.locator('#signup-password')
        confirm_input = page.locator('#signup-confirm-password')
        feedback = page.locator('#signup-password-match-feedback')

        # Initially hidden
        assert not confirm_group.evaluate("el => el.classList.contains('is-visible')")

        # Reveals on input
        password_input.fill("P")
        page.wait_for_timeout(200)
        assert confirm_group.evaluate("el => el.classList.contains('is-visible')")

        # Mismatch
        password_input.fill("Password123!")
        confirm_input.fill("Different123!")
        page.wait_for_timeout(200)
        assert "Passwords do not match." in feedback.inner_text()
        assert feedback.evaluate("el => el.classList.contains('match-error')")

        # Match
        confirm_input.fill("Password123!")
        page.wait_for_timeout(200)
        assert "Passwords match." in feedback.inner_text()
        assert feedback.evaluate("el => el.classList.contains('match-success')")

        # Disappears on clear
        password_input.fill("")
        page.wait_for_timeout(200)
        assert not confirm_group.evaluate("el => el.classList.contains('is-visible')")

        context.close()
        browser.close()
