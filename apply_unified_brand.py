"""Idempotently apply the shared, screenshot-matched header to bundled HTML.

Run from repository root. This script edits only top masthead and hero sections
and applies standalone styles. The original data and page scripts are untouched.
"""
from pathlib import Path
from bs4 import BeautifulSoup
from unified_brand import header_html
import re

BASE = Path(__file__).resolve().parent

PAGES = {
    'Dashboard_Overview.html': ('Research overview','GLOBAL KNOWLEDGE AND ACTION WORKSPACE', '195-country research · Institutional coordination · Practical guidance'),
    'road_safety_atlas.html': ('Initiative atlas', 'GLOBAL ROAD SAFETY INITIATIVES', 'National, subnational and local initiatives · Source-linked records'),
    'who_has_task_forces.html': ('Coordinating bodies','GLOBAL INSTITUTIONAL DIRECTORY', 'Institutions · Membership evidence · Government responsibilities'),
    'Existing_road_safety_documents.html': ('Existing documents','GLOBAL DOCUMENTATION OVERVIEW', '195 countries · National and subnational records · Sources reviewed 9 November 2026'),
    'Bodies_Their_Road_Safety_Strategies.html': ('Bodies & strategies','INSTITUTIONS AND POLICY OUTPUTS', 'Coordinating bodies · Strategies and action plans · Evidence links'),
    'Case_Studies.html': ('Country case studies','COUNTRY CASE STUDIES', '26 countries · 27 coordinating mechanisms · 17 domains and 72 interventions'),
}

for fname, (section, eyebrow, meta) in PAGES.items():
    file_path = BASE / fname
    original = file_path.read_text(encoding='utf-8')
    soup = BeautifulSoup(original, 'html.parser')
    mast = soup.select_one('body > .grs-fixed-banner, body > .grs-consistent-masthead')
    hero = soup.select_one('body > header.hero')
    assert mast is not None and hero is not None, f'{fname} is missing its original banner or hero'
    title = hero.find('h1')
    description = hero.find('p')
    assert title is not None and description is not None
    title_html = title.decode_contents()
    description_text = description.get_text(' ', strip=True)
    # Maintain the same relevant existing title, description, and any atlas anchor.
    new = header_html(section,eyebrow,title_html,description_text,meta,
                      legacy_mast='grs-consistent-masthead' if 'grs-consistent-masthead' in mast.get('class',[]) else 'grs-fixed-banner',
                      hero_id=hero.get('id',''))
    # Span-based exact replace preserves all inline dataset JavaScript and filters byte for byte.
    mast_start = str(mast)
    hero_end = str(hero)
    # BeautifulSoup will normalize attribute syntax, so locate via source regexp instead.
    banner_pattern = re.compile(r'<div\b[^>]*class="[^"]*(?:grs-fixed-banner|grs-consistent-masthead)[^"]*"[^>]*>')
    m = banner_pattern.search(original)
    h = re.search(r'<header\s+class="[^"]*\bhero\b[^"]*"[^>]*>', original)
    assert m and h and h.start() > m.start(), fname
    # Find matching tag closures robustly, without reserializing scripts/data.
    def element_end(start: int, tag: str) -> int:
        matcher = re.compile(r'</?'+tag+r'(?=[\s>/])[^>]*>',re.I)
        depth=0
        for z in matcher.finditer(original,start):
            if original[z.start():z.start()+2] == '</':
                depth-=1
                if depth==0: return z.end()
            else: depth+=1
        raise RuntimeError(f'Could not find end of {tag} from offset {start} in {fname}')
    # Banner is nested divs; handle arbitrary nested wrappers.
    mast_end = element_end(m.start(),'div')
    # Hero contains nested divs and SVG, but its header tag is never nested.
    hm = re.search(r'</header\s*>',original[h.end():],re.I)
    assert hm, fname
    hero_end = h.end() + hm.end()
    assert original[mast_end:h.start()].strip() == '', f'Unexpected content between masthead and hero in {fname}'
    new_doc = original[:m.start()] + new + original[hero_end:]
    file_path.write_text(new_doc,encoding='utf-8')
    print(fname, 'original',len(original),'modified',len(new_doc))
