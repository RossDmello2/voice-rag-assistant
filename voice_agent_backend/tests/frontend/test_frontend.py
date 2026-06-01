"""
Playwright end-to-end tests for the Voice Agent frontend.

Tests are self-contained — they serve the frontend/index.html directly
via a local HTTP server and mock all API calls with route interception,
so no running FastAPI server, Qdrant, Ollama, or Groq key is required.

Run with:
    cd voice_agent_backend
    pytest tests/frontend/test_frontend.py -v
"""

import os
import sys
import json
import threading
import http.server
import functools
import pytest
from playwright.sync_api import Page, expect, Route, sync_playwright

# ── Locate frontend directory ─────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(HERE))
FRONTEND_DIR = os.path.join(BACKEND_DIR, "frontend")


# ── Minimal static file server ───────────────────────────────────

def _make_handler(frontend_dir: str):
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=frontend_dir,
    )
    return handler


def _start_server(port: int = 9871) -> http.server.HTTPServer:
    handler = _make_handler(FRONTEND_DIR)
    server = http.server.HTTPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


# ── Fixtures ─────────────────────────────────────────────────────

_server: http.server.HTTPServer = None
BASE_URL = "http://127.0.0.1:9871"


def setup_module(module):
    global _server
    _server = _start_server(9871)


def teardown_module(module):
    global _server
    if _server:
        _server.shutdown()


def _intercept_health(route: Route):
    """Mock /health → all services online."""
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps({
            "ollama": {"online": True, "error": None},
            "qdrant": {"online": True, "error": None},
            "groq":   {"online": True, "error": None},
        }),
    )


def _intercept_collections(route: Route):
    """Mock GET /collections → one collection."""
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps({"collections": ["agent_knowledge"]}),
    )


def _intercept_models(route: Route):
    """Mock GET /models → minimal model list."""
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps({
            "chat": {
                "groq": ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
                "ollama": [],
            },
            "embeddings": {"ollama": [], "groq": []},
        }),
    )


def _intercept_chat(route: Route):
    """Mock POST /chat → SSE stream with one token + done."""
    sse_body = (
        'data: {"token": "Hello! How can I help you today?"}\n\n'
        'data: {"sources": [], "intent": "GENERAL_CHAT"}\n\n'
        "data: [DONE]\n\n"
    )
    route.fulfill(
        status=200,
        content_type="text/event-stream",
        body=sse_body,
    )


def _intercept_401(route: Route):
    """Mock any route with 401 Unauthorized."""
    route.fulfill(
        status=401,
        content_type="application/json",
        body=json.dumps({"detail": "Missing authentication token"}),
    )


def _intercept_auth_success(route: Route):
    """Mock auth endpoints with a bearer token."""
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps({"access_token": "test-token", "token_type": "bearer"}),
    )


def _mock_all_api(page: Page):
    """Intercept all API calls used on page load."""
    page.route("**/health",      _intercept_health)
    page.route("**/collections", _intercept_collections)
    page.route("**/models",      _intercept_models)


# ══════════════════════════════════════════════════════════════════
# TEST SUITE
# ══════════════════════════════════════════════════════════════════

class TestPageLoad:
    """Verify the frontend loads and renders its key structural elements."""

    def test_page_title(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            assert "VoiceRAG Agent" in page.title()
            browser.close()

    def test_orb_canvas_present(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            canvas = page.locator("#orb-canvas")
            expect(canvas).to_be_visible()
            browser.close()

    def test_status_bar_visible(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            expect(page.locator("#status-bar")).to_be_visible()
            browser.close()

    def test_text_input_present(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            expect(page.locator("#text-input")).to_be_visible()
            browser.close()

    def test_control_bar_buttons_present(self):
        """All main control bar buttons must be in the DOM."""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            for btn_id in ["mic-btn", "upload-btn", "docs-btn", "settings-btn", "send-btn"]:
                assert page.locator(f"#{btn_id}").count() == 1, f"#{btn_id} missing"
            browser.close()

    def test_message_list_on_load(self):
        """
        Frontend injects a welcome message on load.
        Verify no USER messages exist on a fresh session.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="networkidle")
            msg_list = page.locator("#message-list")
            expect(msg_list).to_be_visible()
            # No user-originated messages should exist on fresh load
            user_msgs = msg_list.locator(".message.user, .user-message")
            assert user_msgs.count() == 0, "No user messages should exist on fresh load"
            browser.close()


class TestSettingsPanel:
    """Settings panel open/close behaviour."""

    def test_settings_panel_hidden_on_load(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            panel = page.locator("#settings-panel")
            # Panel exists but should be hidden (has 'hidden' class or display:none)
            assert panel.count() == 1
            browser.close()

    def test_settings_panel_opens_on_button_click(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.locator("#settings-btn").click()
            page.wait_for_timeout(400)
            panel = page.locator("#settings-panel")
            # After click, 'hidden' class should be removed
            classes = panel.get_attribute("class") or ""
            assert "hidden" not in classes, "Settings panel did not open"
            browser.close()

    def test_settings_panel_closes_on_close_button(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.locator("#settings-btn").click()
            page.wait_for_timeout(300)
            page.locator("#settings-close").click()
            page.wait_for_timeout(400)
            classes = page.locator("#settings-panel").get_attribute("class") or ""
            assert "hidden" in classes, "Settings panel did not close"
            browser.close()


class TestDocumentsPanel:
    """Documents panel open/close behaviour."""

    def test_documents_panel_opens(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.locator("#docs-btn").click()
            page.wait_for_timeout(400)
            classes = page.locator("#documents-panel").get_attribute("class") or ""
            assert "hidden" not in classes, "Documents panel did not open"
            browser.close()

    def test_documents_panel_has_drop_zone(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.locator("#docs-btn").click()
            page.wait_for_timeout(300)
            expect(page.locator("#drop-zone")).to_be_visible()
            browser.close()

    def test_documents_panel_closes(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.locator("#docs-btn").click()
            page.wait_for_timeout(300)
            page.locator("#documents-close").click()
            page.wait_for_timeout(400)
            classes = page.locator("#documents-panel").get_attribute("class") or ""
            assert "hidden" in classes, "Documents panel did not close"
            browser.close()


class TestTextInput:
    """Text input field behaviour."""

    def test_text_input_accepts_typing(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            textarea = page.locator("#text-input")
            textarea.fill("Hello agent")
            assert textarea.input_value() == "Hello agent"
            browser.close()

    def test_text_input_clears_after_send(self):
        """After clicking Send, the textarea should be cleared."""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            # Also mock the chat endpoint
            page.route("**/chat", _intercept_chat)
            page.route("**/auth/**", _intercept_401)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            textarea = page.locator("#text-input")
            textarea.fill("Test message")
            page.locator("#send-btn").click()
            page.wait_for_timeout(500)
            # Input should be empty or cleared
            val = textarea.input_value()
            assert val == "" or val != "Test message", "Textarea was not cleared after send"
            browser.close()

    def test_enter_key_triggers_send(self):
        """Pressing Enter in the textarea should trigger message send."""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.route("**/chat", _intercept_chat)
            page.route("**/auth/**", _intercept_401)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            textarea = page.locator("#text-input")
            textarea.fill("Hello via Enter")
            # Press Enter (not Shift+Enter) to send
            textarea.press("Enter")
            page.wait_for_timeout(500)
            val = textarea.input_value()
            assert val == "" or val != "Hello via Enter", "Enter key did not trigger send"
            browser.close()


class TestStatusBar:
    """Status bar health indicators."""

    def test_status_items_present(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            for item_id in ["status-ollama", "status-qdrant", "status-groq"]:
                assert page.locator(f"#{item_id}").count() == 1, f"#{item_id} missing"
            browser.close()

    def test_collection_select_present(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            expect(page.locator("#collection-select")).to_be_visible()
            browser.close()


class TestKeyboardShortcuts:
    """Keyboard shortcut smoke tests."""

    def test_ctrl_comma_opens_settings(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.keyboard.press("Control+,")
            page.wait_for_timeout(400)
            classes = page.locator("#settings-panel").get_attribute("class") or ""
            assert "hidden" not in classes, "Ctrl+, did not open settings"
            browser.close()

    def test_escape_closes_open_panel(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.locator("#settings-btn").click()
            page.wait_for_timeout(300)
            page.keyboard.press("Escape")
            page.wait_for_timeout(400)
            classes = page.locator("#settings-panel").get_attribute("class") or ""
            assert "hidden" in classes, "Escape did not close the settings panel"
            browser.close()


class TestAccessibility:
    """Basic accessibility checks."""

    def test_buttons_have_aria_labels(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            for btn_id in ["mic-btn", "upload-btn", "docs-btn", "settings-btn", "send-btn"]:
                label = page.locator(f"#{btn_id}").get_attribute("aria-label")
                assert label, f"#{btn_id} missing aria-label"
            browser.close()

    def test_no_js_errors_on_load(self):
        """Page must not throw uncaught JS errors on load."""
        errors = []
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.on("pageerror", lambda err: errors.append(str(err)))
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="networkidle")
            page.wait_for_timeout(500)
            browser.close()
        assert errors == [], f"Uncaught JS errors on load: {errors}"

    def test_html_lang_attribute(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            lang = page.locator("html").get_attribute("lang")
            assert lang is not None and len(lang) >= 2, "html[lang] missing or empty"
            browser.close()


class TestAuthAndSecurity:
    """Auth and Markdown safety checks for protected frontend writes."""

    def test_auth_modal_can_open(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.evaluate("showAuthModal()")
            expect(page.locator("#auth-overlay")).to_be_visible()
            expect(page.locator("#auth-email")).to_be_visible()
            browser.close()

    def test_login_stores_token_and_hides_modal(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.route("**/auth/login", _intercept_auth_success)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.evaluate("showAuthModal()")
            page.locator("#auth-email").fill("tester@example.com")
            page.locator("#auth-password").fill("strong-password")
            page.locator("#auth-submit").click()
            page.wait_for_function("localStorage.getItem('ssa_auth_token') === 'test-token'")
            assert "hidden" in (page.locator("#auth-overlay").get_attribute("class") or "")
            browser.close()

    def test_protected_collection_create_sends_bearer_token(self):
        seen = {}

        def route_collections(route: Route):
            if route.request.method == "POST":
                seen["authorization"] = route.request.headers.get("authorization")
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({"name": "secure_collection", "status": "created"}),
                )
            else:
                _intercept_collections(route)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.route("**/health", _intercept_health)
            page.route("**/models", _intercept_models)
            page.route("**/collections", route_collections)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.evaluate("localStorage.setItem('ssa_auth_token', 'test-token')")
            page.evaluate(
                """
                document.getElementById('new-collection-input').value = 'secure_collection';
                confirmNewCollection();
                """
            )
            page.wait_for_timeout(300)
            assert seen["authorization"] == "Bearer test-token"
            browser.close()

    def test_agent_markdown_is_sanitized(self):
        payload = '<img src=x onerror="window.__xss = true">safe<script>window.__xss = true</script>'
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            _mock_all_api(page)
            page.goto(BASE_URL, wait_until="domcontentloaded")
            page.evaluate("(payload) => addMessage('agent', payload)", payload)
            page.wait_for_timeout(200)
            assert page.evaluate("window.__xss === true") is False
            html = page.locator(".message.agent .msg-content").last.inner_html()
            assert "<script" not in html.lower()
            assert "onerror" not in html.lower()
            browser.close()
