"""Visible DOM contract shared by all seven research/toolkit tabs."""
from __future__ import annotations
import ast
import re
import hashlib
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from unified_brand import HEADER_CSS, header_html, UN_BLUE

ROOT=Path(__file__).resolve().parents[1]
PAGES=[
    'Dashboard_Overview.html',
    'road_safety_atlas.html',
    'who_has_task_forces.html',
    'Existing_road_safety_documents.html',
    'Bodies_Their_Road_Safety_Strategies.html',
    'Case_Studies.html',
]


def toolkit_rendered():
    tree=ast.parse((ROOT/'institutional_toolkit/ui.py').read_text())
    raw=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and
             any(isinstance(target,ast.Name) and target.id=='TOOLKIT_INTRO_HTML' for target in n.targets))
    prefix,main=raw.split('<div class="rst-main">',1)
    styles=prefix.split('<div class="rst-mast"',1)[0]
    header=header_html('Road Safety Institutional Toolkit','COUNTRY EVIDENCE AND INSTITUTIONAL ACTION',
                       'Road Safety <em>Institutional Toolkit</em>',
                       'Explore institutional evidence, compare countries and prepare improvement plans.',
                       '195 countries · 17 institutional domains · 72 defined interventions')
    return '<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}.st-key-road_safety_toolkit{padding:0 24px}</style></head><body><div class="st-key-road_safety_toolkit">'+styles+header+'<div class="rst-main">'+main+'</div></body></html>'


@pytest.mark.parametrize('viewport,hero_height,mast_height',[(1440,405,74),(960,405,74),(390,None,64)])
def test_all_seven_headers_share_geometry_palette_and_clean_dom(viewport,hero_height,mast_height):
    sources=[]
    for name in PAGES:
        raw=(ROOT/name).read_text()
        # Test header geometry without rendering the multi-megabyte source dataset
        # repeatedly; the separate browser suites cover full HTML interactions.
        fragment=re.search(r'<style id="rsu-unitar-brand-system">.*?</header>',raw,re.S)
        assert fragment, name
        sources.append((name,'<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0">'+fragment.group(0)+'</body></html>'))
    sources.append(('Toolkit',toolkit_rendered()))
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for name,src in sources:
            page=browser.new_page(viewport={'width':viewport,'height':960})
            errors=[]
            page.on('pageerror',lambda exc:errors.append(str(exc)))
            page.set_content(src,wait_until='domcontentloaded',timeout=45000)
            assert page.locator('.rsu-masthead').count()==1, name
            assert page.locator('header.rsu-hero').count()==1, name
            assert page.locator('.rsu-hero .rsu-art svg').count()==1, name
            assert page.locator('.rsu-hero h1').first.inner_text().strip(), name
            mast=round(page.locator('.rsu-masthead').bounding_box()['height'])
            assert mast==mast_height, (name,viewport,mast)
            hero=round(page.locator('.rsu-hero').bounding_box()['height'])
            if hero_height: assert hero==hero_height,(name,viewport,hero)
            else: assert hero>=360,(name,viewport,hero)
            blue=page.locator('.rsu-masthead .rsu-mark').evaluate('el => getComputedStyle(el).backgroundColor')
            assert blue=='rgb(62, 142, 222)',(name,blue)
            body_width=page.evaluate('document.body.scrollWidth')
            assert body_width<=viewport+1,(name,viewport,body_width)
            assert not errors,(name,errors)
            page.close()
        browser.close()


def test_embedded_research_unchanged_beyond_header_and_styles():
    # Frozen hashes from the source repository. Edits to evidence scripts or
    # embedded country data must be separate, explicitly reviewed releases.
    hashes = {'Dashboard_Overview.html': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'road_safety_atlas.html': '52d767fa6e8dba0e2c7a627e723ac3dfa08abc20771e357cce96dc105b935f06', 'who_has_task_forces.html': 'dec7ed58e4535bf2f51362f8d3748abac155d7da7bd69b13eebda21c447a5564', 'Existing_road_safety_documents.html': '1c7ffb46f1c003acefe67e724f1d5bef877d6ae22ec00d88bfb45219c153f822', 'Bodies_Their_Road_Safety_Strategies.html': 'de3424b2a955631a6d2b46dfa2b1b85a152e45f8ae3161cbb81fd0c49345ddfb', 'Case_Studies.html': '64d1d25c43768952ea2b563f7ff9a9c63edbfb4c558a6a9be022615167d0a8c1'}
    for fn in PAGES:
        raw=(ROOT/fn).read_text(encoding='utf-8')
        scripts=''.join(re.findall(r'<script\b[^>]*>.*?</script>',raw,flags=re.I|re.S))
        assert hashlib.sha256(scripts.encode()).hexdigest()==hashes[fn],fn
    assert UN_BLUE == '#3E8EDE'


def test_streamlit_uses_shared_header_and_blue_theme():
    ui=(ROOT/'institutional_toolkit/ui.py').read_text()
    assert 'standard_header = header_html(' in ui
    assert 'TOOLKIT_INTRO_HTML.split(' in ui
    assert '#3E8EDE' in (ROOT/'.streamlit/config.toml').read_text()
    assert 'PORTAL_CSS +=' in (ROOT/'portal_theme.py').read_text()
    assert 'render_institutional_toolkit' in (ROOT/'app.py').read_text()
