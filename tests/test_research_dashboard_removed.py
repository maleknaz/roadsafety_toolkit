from pathlib import Path
from unified_brand import header_html

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'Dashboard_Overview.html',
    'road_safety_atlas.html',
    'who_has_task_forces.html',
    'Existing_road_safety_documents.html',
    'Bodies_Their_Road_Safety_Strategies.html',
    'Case_Studies.html',
)


def test_shared_header_has_no_research_dashboard_label():
    header = header_html('Road Safety Institutional Toolkit', 'TEST', 'Example', 'Description')
    assert 'Research dashboard' not in header
    assert 'rsu-date' not in header
    assert 'Road Safety Toolkit' in header


def test_all_embedded_pages_remove_right_header_label():
    for name in FILES:
        source = (ROOT / name).read_text(encoding='utf-8')
        assert 'Research dashboard' not in source, name
        assert 'rsu-date"' not in source, name
        assert 'rsu-masthead' in source, name
