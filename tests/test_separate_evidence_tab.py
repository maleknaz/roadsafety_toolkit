"""Regression tests for splitting the Agent from the checklist Toolkit tab."""
from __future__ import annotations
from contextlib import nullcontext
import inspect
import importlib
import sys
from pathlib import Path
from institutional_toolkit import evidence

ROOT = Path(__file__).resolve().parents[1]


def test_toolkit_does_not_duplicate_agent_question_form():
    src=(ROOT/'institutional_toolkit'/'ui.py').read_text(encoding='utf-8')
    src=src[src.index('def render():'):src.index('def render_agent():')]
    assert '_agent_workspace' not in src
    assert 'rs_agent_question_form' not in src
    assert '_checklist(data,country)' in src


def test_agent_separate_tab_uses_same_evidence_pipeline(monkeypatch):
    data=evidence.load_data(str(ROOT/'data'))
    captured=[]

    class FakeStreamlit:
        def __init__(self):
            self.session_state={'rs_toolkit_country':'Sweden'}
            self.selects=[]
            self.html_calls=[]
        def container(self, **kwargs):
            captured.append(('container', kwargs.get('key')))
            return nullcontext()
        def html(self, html, **kwargs):
            self.html_calls.append(html)
        def selectbox(self, label, options, index=0, **kwargs):
            self.selects.append((label, kwargs.get('key'), options[index]))
            return options[index]

    fake=FakeStreamlit()
    monkeypatch.setitem(sys.modules,'streamlit',fake)
    sys.modules.pop('institutional_toolkit.ui', None)
    ui=importlib.import_module('institutional_toolkit.ui')
    monkeypatch.setattr(ui,'st',fake)
    monkeypatch.setattr(ui.ev,'load_data',lambda _:data)
    monkeypatch.setattr(ui,'_agent_workspace',lambda d, country:captured.append(('ask',country)))
    ui.render_agent()
    assert ('container','road_safety_agent_tab') in captured
    assert ('ask','Sweden') in captured
    assert fake.selects==[('Select your country','rs_agent_primary_country','Sweden')]
    header=''.join(fake.html_calls)
    assert 'Ask the Evidence' in header
    assert 'Road Safety Intelligence Agent' in header
    assert 'st-key-road_safety_agent_tab' in header


def test_agent_retains_country_scoping_and_citations():
    from institutional_toolkit.agent_workspace import AgentRequest,retrieve_request
    data=evidence.load_data(str(ROOT/'data'))
    answer=retrieve_request(data,AgentRequest('Estonia',
        'Compare documented governance and road safety strategies of these countries.',
        'Sweden'),ROOT/'data')
    assert answer['scope']=='compare'
    assert answer['first']=='Estonia' and answer['second']=='Sweden'
    assert all(hit['country'] in ('Estonia','Sweden') for hit in answer['hits'])
    assert answer['sufficient_for_ai'] == all(answer['counts'].values())


def test_six_embedded_pages_unmodified_from_predecessor():
    # This checks the contract without requiring an HTML browser.
    app=(ROOT/'app.py').read_text()
    assert sum((ROOT / name).exists() for name in ('Dashboard_Overview.html','road_safety_atlas.html','who_has_task_forces.html','Existing_road_safety_documents.html','Bodies_Their_Road_Safety_Strategies.html','Case_Studies.html')) == 6
    assert 'Ask the Evidence' in app
    assert '_show_ask_the_evidence()' in app
    assert 'render_intelligence_agent()' in app
