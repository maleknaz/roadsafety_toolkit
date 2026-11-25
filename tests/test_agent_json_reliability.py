"""Regression tests for empty/incomplete structured output and evidence relevance."""
from pathlib import Path
from types import SimpleNamespace
import json

from institutional_toolkit import agent_workspace, evidence, rag

ROOT = Path(__file__).resolve().parents[1]
DATA = evidence.load_data(str(ROOT/'data'))
HITS = rag.retrieve(DATA,'Estonia','government traffic commission',data_dir=ROOT/'data')


class Client:
    def __init__(self, result):
        self.result = result
        self.requests = []
        self.responses = self

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return self.result


def test_empty_ai_output_is_handled_and_sources_retained():
    client = Client(SimpleNamespace(status='completed', output_text=''))
    answer = rag.synthesis('What is happening?', HITS, client=client)
    assert not answer['claims']
    assert answer['status'] == 'AI answer not generated; retrieved evidence remains available'
    assert 'complete structured answer' in answer['limitations'][0]
    assert set(answer['retrieved_evidence_ids']) == {h['evidence_id'] for h in HITS}
    assert client.requests[0]['max_output_tokens'] >= 2500
    assert client.requests[0]['reasoning'] == {'effort':'low'}
    assert len(client.requests) == 1  # prevent silent extra billable requests


def test_truncated_json_has_a_friendly_message_not_jsondecodeerror():
    client = Client(SimpleNamespace(status='incomplete',
                  incomplete_details=SimpleNamespace(reason='max_output_tokens'),
                  output_text='{"claims": [ {'))
    answer = rag.synthesis('What is documented?',HITS,client=client)
    assert not answer['claims']
    assert 'token budget' in answer['limitations'][0]
    assert 'JSONDecodeError' not in str(answer)


def test_completed_but_malformed_json_fails_closed():
    client = Client(SimpleNamespace(status='completed', output_text='{"claims":'))
    answer = rag.synthesis('What is documented?', HITS,client=client)
    assert not answer['claims']
    assert 'unreadable structured answer' in answer['limitations'][0]


def test_valid_json_remains_citation_verified():
    valid = {'summary':'Short','claims':[{'text':'Review describes coordination',
             'evidence_ids':[HITS[0]['evidence_id']]}],
             'limitations':[], 'questions_for_verification':[]}
    client=Client(SimpleNamespace(status='completed', output_text=json.dumps(valid)))
    answer=rag.synthesis('What is documented?',HITS,client=client)
    assert len(answer['claims']) == 1
    assert answer['claims'][0]['references'][0]['evidence_id'] == HITS[0]['evidence_id']


def test_unrecognized_evidence_citation_is_never_displayed():
    invalid = {'summary':'Short','claims':[{'text':'Invented','evidence_ids':['FAKE']}],
               'limitations':[], 'questions_for_verification':[]}
    answer = rag.synthesis('What is documented?', HITS,
                           client=Client(SimpleNamespace(status='completed',output_text=json.dumps(invalid))))
    assert answer['claims'] == []
    assert 'validation' in answer['limitations'][0]


def test_emergency_preparedness_not_compared_to_unrelated_swedish_records():
    req=agent_workspace.AgentRequest('Estonia',
         'How do Estonia and Sweden compare in terms of emergency preparedness presence?','Sweden')
    payload=agent_workspace.retrieve_request(DATA,req,ROOT/'data')
    assert payload['focus_domains'] == ['Civil defence & disaster preparedness','Fire protection & rescue']
    assert payload['counts']['Estonia'] > 0
    assert payload['counts']['Sweden'] == 0
    assert payload['sufficient_for_ai'] is False
    assert all(h['country']=='Estonia' for h in payload['hits'])


def test_regular_multi_country_governance_question_still_works():
    req=agent_workspace.AgentRequest('Estonia',
        'Compare governance leadership and strategies in Estonia and Sweden','Sweden')
    payload=agent_workspace.retrieve_request(DATA,req,ROOT/'data')
    assert payload['focus_domains'] == []
    assert payload['sufficient_for_ai'] is True
    assert set(payload['counts'])== {'Estonia','Sweden'}


def test_emergency_gap_never_triggers_comparative_model_call():
    class NoClient:
        @property
        def responses(self):
            raise AssertionError('No AI call is permitted for one-sided topic evidence')
    request = agent_workspace.AgentRequest('Estonia',
        'Does emergency preparedness differ between Estonia and Sweden?', 'Sweden')
    output = agent_workspace.ask(DATA,request,ROOT/'data',run_ai=True,client=NoClient())
    assert output['result'] is None
    assert output['sufficient_for_ai'] is False
    assert output['counts']['Sweden'] == 0
