"""Toolkit masthead and descriptions: no Streamlit server/API key required."""
from __future__ import annotations
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'institutional_toolkit' / 'ui.py'

def intro_html() -> str:
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'TOOLKIT_INTRO_HTML' for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError('Intro HTML not found')


def test_hero_title_and_fixed_dimensions():
    t = intro_html()
    assert '<h1 id="rst-title">Road Safety<br><em>Institutional Toolkit</em></h1>' in t
    assert 'height:405px!important' in t
    assert 'height:70px' in t
    assert 'linear-gradient(110deg,#08283a' in t
    assert 'max-width:1490px' in t


def test_four_modes_and_honest_intelligence_claims():
    t = intro_html()
    assert t.count('class="rst-area ') == 4
    for label in ('Explore country findings', 'Benchmark internationally', 'Compare two countries',
                  'Generate a tailored checklist'):
        assert label in t
    assert 'source-linked country records' in t
    assert 'AI summaries require an API key' in t
    assert 'never overwrite the reviewed research automatically' in t


def test_responsive_light_theme_and_separation():
    t = intro_html()
    assert '@media(max-width:790px)' in t
    assert 'grid-template-columns:1fr' in t
    assert 'background:#fff!important' in t
    assert '.st-key-road_safety_toolkit .rst-hero' in t
    assert 'unsafe_allow_html=True' in SOURCE.read_text(encoding='utf-8')
