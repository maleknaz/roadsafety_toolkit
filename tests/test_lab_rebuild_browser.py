"""Chromium regression of new homepage, country grid and pairwise grid.

Tests real DOM positions, selections, 17 visible cards and country isolation;
static asserts of CSS strings alone are insufficient for this UI.
"""
from __future__ import annotations
import ast
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright
from institutional_toolkit import evidence, domain_views

ROOT=Path(__file__).resolve().parents[1]


def _intro():
    tree=ast.parse((ROOT/'institutional_toolkit/ui.py').read_text())
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='TOOLKIT_INTRO_HTML' for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError('Missing intro')


@pytest.mark.parametrize('viewport,cols',[(1440,4),(960,3),(680,2),(390,1)])
def test_both_domain_modes_are_17_card_interactive_grids(viewport,cols):
    data=evidence.load_data(str(ROOT/'data'))
    views=[domain_views.country_view(data,'Estonia'),
           domain_views.comparison_view(evidence.compare(data,'Estonia','Sweden'),'Estonia','Sweden')]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'],headless=True)
        for html in views:
            page=browser.new_page(viewport={'width':viewport,'height':1100})
            errors=[]
            page.on('pageerror',lambda exc:errors.append(str(exc)))
            page.set_content(html)
            buttons=page.locator('button.domain-card')
            assert buttons.count()==17
            assert page.locator('.domain-grid').evaluate('el=>getComputedStyle(el).gridTemplateColumns.split(" ").length')==cols
            if cols==4:
                first_y=[round(buttons.nth(i).bounding_box()['y']) for i in range(4)]
                assert len(set(first_y))==1
            buttons.nth(11).click()
            expected=buttons.nth(11).locator('.card-heading').inner_text()
            assert page.locator('#domain-detail h3').inner_text()==expected
            assert page.locator('button.domain-card[aria-pressed="true"]').count()==1
            assert page.locator('#domain-detail table').count()<=1
            assert not errors
            assert page.locator('body').evaluate('el=>el.scrollWidth')<=viewport+2
            page.close()
        browser.close()


@pytest.mark.parametrize('viewport,cols',[(1440,4),(960,2),(390,1)])
def test_home_and_toolkit_have_consistent_illustrated_four_area_layouts(viewport,cols):
    intro=('<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">'
           '<style>body{margin:0;background:#f7fafb}.st-key-road_safety_toolkit{padding:0 24px 20px;background:#f7fafb}</style>'
           '</head><body><div class="st-key-road_safety_toolkit">'+_intro()+'</div></body></html>')
    homepage=(ROOT/'Dashboard_Overview.html').read_text()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'],headless=True)
        for html,card_selector,grid_selector,graphic_selector in [
            (intro,'.rst-area','.rst-areas','.rst-hero-art svg'),
            (homepage,'.rs-lab-home-area','.rs-lab-home-area-grid','.rs-lab-home-art svg')
        ]:
            page=browser.new_page(viewport={'width':viewport,'height':950})
            errors=[];page.on('pageerror',lambda exc:errors.append(str(exc)))
            page.set_content(html)
            assert page.locator(card_selector).count()==4
            assert page.locator(grid_selector).evaluate('el=>getComputedStyle(el).gridTemplateColumns.split(" ").length')==cols
            assert page.locator(graphic_selector).count()==1
            assert page.locator('body').evaluate('el=>el.scrollWidth')<=viewport+2
            assert not errors
            page.close()
        browser.close()
