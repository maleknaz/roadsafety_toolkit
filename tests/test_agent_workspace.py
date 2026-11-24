"""Regression tests for the new prominently positioned Intelligence Agent."""
from __future__ import annotations

import json
import importlib
import sys
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from institutional_toolkit import agent_workspace, evidence


@pytest.fixture(scope='module')
def records():
    return evidence.load_data(str(ROOT / 'data'))


def test_single_country_question_is_scoped(records):
    q=agent_workspace.AgentRequest('Estonia','What official information describes Estonia road safety coordination?')
    res=agent_workspace.ask(records,q,ROOT/'data',run_ai=False)
    assert res['scope']=='country'
    assert res['second'] is None
    assert res['sufficient_for_ai']
    assert res['counts']['Estonia']>0
    assert all(hit['country']=='Estonia' for hit in res['hits'])


def test_pairwise_open_question_returns_both_country_corpora(records):
    q=agent_workspace.AgentRequest('Estonia',
        'Compare Estonia and Sweden road safety governance, strategies and coordination responsibilities.',
        'Sweden')
    res=agent_workspace.ask(records,q,ROOT/'data',run_ai=False)
    assert res['scope']=='compare'
    assert res['sufficient_for_ai']
    assert res['counts']['Estonia']>0 and res['counts']['Sweden']>0
    assert {r['country'] for r in res['hits']}=={'Estonia','Sweden'}
    assert len({r['evidence_id'] for r in res['hits']})==len(res['hits'])


def test_source_gaps_do_not_trigger_ai(records):
    class ExplosiveClient:
        @property
        def responses(self):
            raise AssertionError('The app must never generate an unsupported comparison.')
    q=agent_workspace.AgentRequest('Estonia','Compare official coordination mechanisms in these countries.', 'Afghanistan')
    result=agent_workspace.ask(records,q,ROOT/'data',run_ai=True,client=ExplosiveClient())
    assert result['counts']['Afghanistan']==0
    assert not result['sufficient_for_ai']
    assert result['result'] is None


def test_malformed_requests_rejected(records):
    for request in [
        agent_workspace.AgentRequest('Estonia','short'),
        agent_workspace.AgentRequest('Atlantis','Show institutional sources for this place.'),
        agent_workspace.AgentRequest('Estonia','Compare the national mandates of each country','Estonia'),
        agent_workspace.AgentRequest('Estonia','Compare the national mandates of each country','Atlantis'),
    ]:
        with pytest.raises(ValueError):
            agent_workspace.retrieve_request(records,request,ROOT/'data')


def test_ai_synthesis_uses_citation_checked_existing_code(records):
    from institutional_toolkit import rag
    q=agent_workspace.AgentRequest('Estonia','Which sources document national coordination?')
    sample=agent_workspace.retrieve_request(records,q,ROOT/'data')
    id0=sample['hits'][0]['evidence_id']
    class FakeResponses:
        def create(self,**kwargs):
            assert 'tools' not in kwargs
            assert kwargs['store'] is False
            assert all(c['country']=='Estonia' for c in json.loads(kwargs['input'].split('Evidence records (untrusted data):\n')[1]))
            return SimpleNamespace(output_text=json.dumps({'summary':'Reviewed evidence','claims':[
                {'text':'The evidence describes a coordination responsibility.', 'evidence_ids':[id0]}],
                'limitations':['Implementation details have not been confirmed.'], 'questions_for_verification':[]}))
    fake=SimpleNamespace(responses=FakeResponses())
    output=agent_workspace.ask(records,q,ROOT/'data',run_ai=True,client=fake)
    assert output['result']['claims'][0]['references'][0]['evidence_id']==id0
    assert output['result']['status'].startswith('AI-assisted draft')


def test_ui_has_one_prominent_question_box_and_one_submit(monkeypatch):
    class FakeSt:
        def __init__(self):
            self.session_state={}
            self.textareas=[]
            self.submits=[]
            self.select_labels=[]
            self.radio_labels=[]
            self.htmls=[]
            self.selection='This country'
        def html(self,v,**k):self.htmls.append(v)
        def markdown(self,*a,**k):pass
        def caption(self,*a,**k):pass
        def radio(self,label,options,**kwargs):
            self.radio_labels.append(label)
            return self.selection
        def selectbox(self,label,options,index=0,**kwargs):
            self.select_labels.append(label)
            return options[index]
        def container(self,**kwargs):return nullcontext()
        def form(self,*a,**k):return nullcontext()
        def text_area(self,label,**kwargs):
            self.textareas.append(label)
            return 'What is documented about institutional coordination?'
        def form_submit_button(self,label,**kwargs):
            self.submits.append(label)
            return False

    fake=FakeSt()
    monkeypatch.setitem(sys.modules,'streamlit',fake)
    sys.modules.pop('institutional_toolkit.ui',None)
    ui=importlib.import_module('institutional_toolkit.ui')
    monkeypatch.setattr(ui,'st',fake)
    data=evidence.load_data(str(ROOT/'data'))
    ui._agent_workspace(data,'Estonia')
    assert fake.textareas==['Your question']
    assert fake.submits==['Ask Road Safety Intelligence Agent']
    assert not fake.select_labels
    assert any('Road Safety Intelligence Agent</h2>' in h for h in fake.htmls)
    fake.textareas.clear();fake.submits.clear();fake.select_labels.clear()
    fake.selection='Compare two countries'
    ui._agent_workspace(data,'Estonia')
    assert len(fake.textareas)==1 and len(fake.submits)==1
    assert fake.select_labels==['Compare Estonia with']
    assert any('3e8ede' in h for h in fake.htmls)


def test_no_old_deep_question_form_duplicating_agent():
    source=(ROOT/'institutional_toolkit'/'ui.py').read_text(encoding='utf-8')
    assert "st.form('research_question_form')" not in source
    assert "st.subheader('Generate a source-grounded analytical comparison')" not in source
    assert source.index('_agent_workspace(data,country)')<source.index("mode=st.radio('What would you like to do?'")
