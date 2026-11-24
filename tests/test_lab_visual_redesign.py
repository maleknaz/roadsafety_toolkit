"""Live Chromium visual regression for redesigned portal UI, not just source CSS."""
from __future__ import annotations
import ast
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright
from portal_theme import PORTAL_CSS, EMBEDDED_CSS

ROOT=Path(__file__).resolve().parents[1]


def toolkit_intro_html() -> str:
    tree=ast.parse((ROOT/'institutional_toolkit'/'ui.py').read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TOOLKIT_INTRO_HTML' for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError('Missing Toolkit intro')


def toolkit_fixture() -> str:
    return ('<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<style>body{margin:0;background:#f7fafb;} .st-key-road_safety_toolkit{background:#f7fafb;padding:0 24px 25px;}</style>'
            '</head><body><div class="st-key-road_safety_toolkit"><div data-testid="stMarkdownContainer">'
            +toolkit_intro_html()+'</div><div style="max-width:1450px;margin:auto;color:#17384b;font-family:Arial">'
            '<div class="rs-workspace-head"><strong>Start your country assessment</strong>'
            '<p>Select a country and one of the four services below.</p></div>'
            '<label for="country">Select your country</label><br><select id="country" style="width:100%;padding:14px;background:#fff;border:1px solid #cdd;">'
            '<option>Estonia</option><option>Sweden</option></select></div></div></body></html>')


@pytest.mark.parametrize('width,columns',[(1440,4),(960,2),(390,1)])
def test_toolkit_editorial_header_layout_in_chromium(width,columns):
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'],headless=True)
        page=b.new_page(viewport={'width':width,'height':950},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(toolkit_fixture())
        assert page.get_by_role('heading',name='Road Safety Institutional Toolkit').is_visible()
        assert page.locator('.rst-area').count()==4
        count=page.locator('.rst-areas').evaluate('el=>getComputedStyle(el).gridTemplateColumns.split(" ").length')
        assert count==columns
        assert page.locator('.rst-mast').evaluate('el=>Math.round(el.getBoundingClientRect().height)')==70
        if width>=740:
            assert page.locator('.rst-hero').evaluate('el=>Math.round(el.getBoundingClientRect().height)')==405
        assert page.locator('body').evaluate('el=>el.scrollWidth')<=width+1
        assert page.locator('.rst-area').first.evaluate('el=>getComputedStyle(el).backgroundColor')=='rgb(255, 255, 255)'
        assert not errors
        if width==1440:
            (ROOT/'qa').mkdir(exist_ok=True)
            page.screenshot(path=str(ROOT/'qa'/'toolkit_desktop.png'),full_page=True)
        if width==390:
            page.screenshot(path=str(ROOT/'qa'/'toolkit_mobile.png'),full_page=True)
        b.close()


@pytest.mark.parametrize('width,columns',[(1440,4),(960,2),(390,1)])
def test_overview_lab_style_and_mobile(width,columns):
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'],headless=True)
        page=b.new_page(viewport={'width':width,'height':1050},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content((ROOT/'Dashboard_Overview.html').read_text(encoding='utf-8'))
        assert page.title()=='Road Safety Toolkit | Overview'
        assert page.get_by_role('heading',name='Road Safety Toolkit',exact=True).is_visible()
        assert page.locator('.rs-lab-home-area').count()==4
        count=page.locator('.rs-lab-home-area-grid').evaluate('el=>getComputedStyle(el).gridTemplateColumns.split(" ").length')
        assert count==columns
        assert page.locator('.rs-lab-home-area').first.evaluate('el=>getComputedStyle(el).backgroundColor')=='rgb(255, 255, 255)'
        assert page.locator('body').evaluate('el=>el.scrollWidth')<=width+1
        assert not errors
        if width==1440:
            page.screenshot(path=str(ROOT/'qa'/'overview_desktop.png'),full_page=True)
        if width==390:
            page.screenshot(path=str(ROOT/'qa'/'overview_mobile.png'),full_page=True)
        b.close()


def test_seven_tabs_still_use_streamlit_and_shared_theme():
    app=(ROOT/'app.py').read_text(encoding='utf-8')
    assert 'from portal_theme import PORTAL_CSS' in app
    assert 'st.markdown(\'<style>\'+PORTAL_CSS+\'</style>\'' in app
    assert 'labels=[' in app
    assert 'render_institutional_toolkit' in app
    assert '[role="tablist"]' in PORTAL_CSS
    assert 'overflow-x:auto' in PORTAL_CSS


def test_all_embedded_pages_styled_once_without_touching_data_files():
    files=['Dashboard_Overview.html','road_safety_atlas.html','who_has_task_forces.html',
           'Existing_road_safety_documents.html','Bodies_Their_Road_Safety_Strategies.html','Case_Studies.html']
    assert len(files)==6
    for name in files:
        html=(ROOT/name).read_text(encoding='utf-8')
        assert html.count('id="rs-lab-inspired-theme"')==1
        assert '<title>Road Safety Toolkit' in html
    assert 'position:relative!important' in EMBEDDED_CSS
