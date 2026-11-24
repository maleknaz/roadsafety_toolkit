"""Regression: the Toolkit masthead must be rendered as HTML, not Markdown code.

This catches the production screenshot failure where indented <div> tags in
`header_html()` were parsed as a Markdown code block in the Streamlit tab.
"""
from pathlib import Path
from types import SimpleNamespace
import importlib
import sys

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class HeaderSink:
    def __init__(self):
        self.rendered = []

    def html(self, body):
        self.rendered.append(body)

    def markdown(self, *args, **kwargs):
        raise AssertionError("Toolkit masthead HTML must not be sent to st.markdown")


def make_markup(monkeypatch):
    sink = HeaderSink()
    monkeypatch.setitem(sys.modules, "streamlit", sink)
    sys.modules.pop("institutional_toolkit.ui", None)
    ui = importlib.import_module("institutional_toolkit.ui")
    ui._render_toolkit_intro()
    assert len(sink.rendered) == 1
    return sink.rendered[0]


def test_toolkit_hero_is_sent_to_html_renderer(monkeypatch):
    content = make_markup(monkeypatch)
    doc = BeautifulSoup(content, "html.parser")
    assert len(doc.select(".rsu-masthead")) == 1
    assert len(doc.select("header.rsu-hero")) == 1
    assert "Road Safety Institutional Toolkit" in doc.select_one("header.rsu-hero h1").get_text(" ", strip=True)
    assert len(doc.select(".rst-area")) == 4
    assert len(doc.select(".rsu-art svg")) == 1


def test_toolkit_header_renders_at_desktop_and_mobile(monkeypatch):
    content = make_markup(monkeypatch)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        for width in [1440, 390]:
            page = browser.new_page(viewport={"width": width, "height": 1050})
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.set_content('<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">'
                             '<style>body{margin:0;background:#F5F9FC}.st-key-road_safety_toolkit{padding:0 24px;}</style>'
                             '</head><body><div class="st-key-road_safety_toolkit">' + content + '</div></body></html>')
            assert page.locator("header.rsu-hero h1").is_visible()
            assert page.locator(".rsu-masthead").is_visible()
            assert page.locator(".rst-area").count() == 4
            assert page.locator("pre:has-text('<div')").count() == 0
            assert page.locator("code:has-text('<div')").count() == 0
            assert not errors, errors
            assert page.locator("body").evaluate("el => el.scrollWidth") <= width + 1
            page.close()
        browser.close()
