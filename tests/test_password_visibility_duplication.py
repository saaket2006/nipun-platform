import os
import re
import pytest

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
INDEX_HTML = os.path.join(FRONTEND_DIR, "index.html")
AUTH_CSS = os.path.join(FRONTEND_DIR, "assets", "css", "auth.css")

def test_css_suppresses_native_ms_reveal_and_clear():
    """Verify auth.css suppresses Microsoft Edge & IE native password reveal/clear controls."""
    with open(AUTH_CSS, "r", encoding="utf-8") as f:
        content = f.read()

    # Must contain ::-ms-reveal suppression with display: none !important
    assert "::-ms-reveal" in content, "auth.css must define suppression for ::-ms-reveal"
    assert "::-ms-clear" in content, "auth.css must define suppression for ::-ms-clear"
    
    # Must ensure display: none is applied to ::-ms-reveal
    reveal_match = re.search(r'::-ms-reveal[\s\S]*?\{[\s\S]*?display:\s*none', content)
    assert reveal_match is not None, "auth.css must set display: none on ::-ms-reveal"

def test_dom_has_exactly_one_toggle_per_password_wrapper():
    """Verify that every password-input-wrapper in index.html contains exactly ONE .toggle-password-btn."""
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all password-input-wrapper blocks
    wrappers = re.findall(r'<div class="password-input-wrapper">([\s\S]*?)</div>', content)
    assert len(wrappers) >= 3, f"Expected at least 3 password wrappers (login, signup, confirm), found {len(wrappers)}"

    for idx, wrapper in enumerate(wrappers):
        toggle_matches = re.findall(r'class="[^"]*toggle-password-btn[^"]*"', wrapper)
        clear_matches = re.findall(r'class="[^"]*clear-password-btn[^"]*"', wrapper)
        assert len(toggle_matches) == 1, f"Wrapper #{idx} has {len(toggle_matches)} toggle buttons (expected exactly 1)"
        assert len(clear_matches) == 1, f"Wrapper #{idx} has {len(clear_matches)} clear buttons (expected exactly 1)"

def test_playwright_password_field_single_eye_toggle():
    """Test interactive focus, typing, blur, refocus, and toggling in Chromium/Edge."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright not installed in current environment")

    with sync_playwright() as p:
        # Prefer msedge channel if available, fallback to chrome/chromium
        channel = "msedge"
        try:
            browser = p.chromium.launch(channel=channel, headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)

        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.goto("http://localhost:8085/index.html")
        page.wait_for_timeout(300)

        # Open sign up modal
        page.locator(".nav-signup-btn").first.click()
        page.wait_for_timeout(300)

        pass_input = page.locator("#signup-password")
        pass_wrapper = page.locator("#signup-form .password-input-wrapper").first
        toggle_btn = pass_wrapper.locator(".toggle-password-btn")
        clear_btn = pass_wrapper.locator(".clear-password-btn")

        # 1. Initial State: Exactly one toggle button, one clear button
        assert toggle_btn.count() == 1
        assert clear_btn.count() == 1
        assert toggle_btn.locator(".icon-eye:not(.hidden)").count() == 1
        assert toggle_btn.locator(".icon-eye-off.hidden").count() == 1

        # 2. Focus but empty
        pass_input.focus()
        page.wait_for_timeout(100)
        assert toggle_btn.count() == 1

        # 3. Type multiple characters
        pass_input.type("MySecret123!", delay=20)
        page.wait_for_timeout(100)
        assert toggle_btn.count() == 1
        assert toggle_btn.locator(".icon-eye:not(.hidden)").count() == 1

        # Check native reveal is suppressed in computed style
        computed_reveal = page.evaluate("""() => {
            const el = document.getElementById('signup-password');
            const style = window.getComputedStyle(el, '::-ms-reveal');
            return style ? style.display : 'none';
        }""")
        assert computed_reveal in ('none', ''), f"Computed ::-ms-reveal display is {computed_reveal}, expected 'none'"

        # 4. Toggle visibility -> switches to text
        toggle_btn.click()
        page.wait_for_timeout(100)
        assert pass_input.get_attribute("type") == "text"
        assert toggle_btn.locator(".icon-eye.hidden").count() == 1
        assert toggle_btn.locator(".icon-eye-off:not(.hidden)").count() == 1

        # 5. Blur
        page.locator("#signup-email").click()
        page.wait_for_timeout(100)
        assert toggle_btn.count() == 1

        # 6. Refocus
        pass_input.focus()
        page.wait_for_timeout(100)
        assert toggle_btn.count() == 1

        # 7. Toggle back to password
        toggle_btn.click()
        page.wait_for_timeout(100)
        assert pass_input.get_attribute("type") == "password"
        assert toggle_btn.locator(".icon-eye:not(.hidden)").count() == 1
        assert toggle_btn.locator(".icon-eye-off.hidden").count() == 1

        context.close()
        browser.close()

def test_playwright_confirm_password_field_single_eye_toggle():
    """Test Confirm Password field focus, typing, blur, refocus, and toggling in Chromium/Edge."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright not installed in current environment")

    with sync_playwright() as p:
        channel = "msedge"
        try:
            browser = p.chromium.launch(channel=channel, headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)

        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.goto("http://localhost:8085/index.html")
        page.wait_for_timeout(300)

        # Open sign up modal
        page.locator(".nav-signup-btn").first.click()
        page.wait_for_timeout(300)

        # Type password to reveal confirm password
        page.locator("#signup-password").fill("MySecret123!")
        page.wait_for_timeout(300)

        confirm_input = page.locator("#signup-confirm-password")
        confirm_wrapper = page.locator("#signup-confirm-group .password-input-wrapper")
        toggle_btn = confirm_wrapper.locator(".toggle-password-btn")
        clear_btn = confirm_wrapper.locator(".clear-password-btn")

        # 1. Exactly one toggle button, one clear button
        assert toggle_btn.count() == 1
        assert clear_btn.count() == 1

        # 2. Focus and type in confirm password
        confirm_input.focus()
        confirm_input.type("MySecret123!", delay=20)
        page.wait_for_timeout(100)
        assert toggle_btn.count() == 1
        assert toggle_btn.locator(".icon-eye:not(.hidden)").count() == 1

        # 3. Blur and refocus
        page.locator("#signup-email").click()
        page.wait_for_timeout(100)
        confirm_input.focus()
        page.wait_for_timeout(100)
        assert toggle_btn.count() == 1

        # 4. Toggle visibility on confirm password
        toggle_btn.click()
        page.wait_for_timeout(100)
        assert confirm_input.get_attribute("type") == "text"
        # Primary password remains password type (independent)
        assert page.locator("#signup-password").get_attribute("type") == "password"

        # 5. Toggle back
        toggle_btn.click()
        page.wait_for_timeout(100)
        assert confirm_input.get_attribute("type") == "password"

        context.close()
        browser.close()

def test_independent_visibility_toggles_and_clear():
    """Verify that Password and Confirm Password visibility toggles and clear buttons operate independently."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright not installed in current environment")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="msedge", headless=True)
        except Exception:
            browser = p.chromium.launch(headless=True)

        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto("http://localhost:8085/index.html")
        page.wait_for_timeout(300)

        page.locator(".nav-signup-btn").first.click()
        page.wait_for_timeout(300)

        pass_input = page.locator("#signup-password")
        confirm_input = page.locator("#signup-confirm-password")

        pass_input.fill("PasswordA123!")
        page.wait_for_timeout(200)
        confirm_input.fill("PasswordA123!")
        page.wait_for_timeout(200)

        pass_toggle = page.locator(".toggle-password-btn[data-target='signup-password']")
        confirm_toggle = page.locator(".toggle-password-btn[data-target='signup-confirm-password']")
        pass_clear = page.locator(".clear-password-btn[data-target='signup-password']")
        confirm_clear = page.locator(".clear-password-btn[data-target='signup-confirm-password']")

        # Toggle only password
        pass_toggle.click()
        page.wait_for_timeout(100)
        assert pass_input.get_attribute("type") == "text"
        assert confirm_input.get_attribute("type") == "password"

        # Toggle only confirm password
        confirm_toggle.click()
        page.wait_for_timeout(100)
        assert pass_input.get_attribute("type") == "text"
        assert confirm_input.get_attribute("type") == "text"

        # Clear confirm password
        confirm_clear.click()
        page.wait_for_timeout(100)
        assert confirm_input.input_value() == ""
        assert pass_input.input_value() == "PasswordA123!"

        browser.close()

