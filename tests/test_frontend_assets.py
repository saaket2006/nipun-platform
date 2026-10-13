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
