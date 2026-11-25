"""Ensure end-user naming is consistent without touching the evidence engine."""
from io import BytesIO
from docx import Document
from institutional_toolkit import reports
from pathlib import Path


def test_visible_agent_name_and_stable_technical_engine():
    rendered_ui_source = (Path(__file__).resolve().parents[1] / 'institutional_toolkit' / 'ui.py').read_text(encoding='utf-8')
    assert '<h2>Road Safety Intelligence Agent</h2>' in rendered_ui_source
    assert '<h2>Road Safety Intelligence Agent</h2>' in rendered_ui_source
    assert "st.form('rs_agent_question_form'" in rendered_ui_source
    assert 'controlled RAG' not in rendered_ui_source


def test_cited_report_uses_agent_brand():
    output = reports.word_rag('Estonia', 'What evidence is available?', [], {'status': 'No claims', 'claims': []})
    document = Document(BytesIO(output))
    content = '\n'.join(p.text for p in document.paragraphs)
    assert 'Road Safety Intelligence Agent' in content
    assert 'Controlled RAG' not in content
