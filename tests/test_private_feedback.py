"""Private CSV feedback must be correct, persistent, anonymous by default and private."""
import base64
import csv
import io
import json
from pathlib import Path
import re

import pytest
from institutional_toolkit import feedback


@pytest.fixture
def output():
    return {
        'first': 'Estonia', 'second': 'Sweden',
        'question': 'Compare the documented coordination arrangements.',
        'result': {'status': 'AI-assisted draft', 'claims': [
            {'text': 'Both sources describe road safety coordination.', 'evidence_ids': ['e1','s1'],
             'references': [{'url':'https://example.org/e','evidence_id':'e1'},
                            {'url':'https://example.org/s','evidence_id':'s1'}]}],
                   'limitations': ['Membership remains unconfirmed.'],
                   'questions_for_verification': ['Which meeting records are available?']},
        'hits': [{'evidence_id': 'e1', 'source_url': 'https://example.org/e', 'country': 'Estonia'},
                 {'evidence_id': 's1', 'source_url': 'https://example.org/s', 'country': 'Sweden'}],
    }


def test_records_contain_question_answer_and_sources(output):
    record = feedback.build_feedback(output, feedback.RATINGS[0], feedback_id='known-1')
    assert record['optional_name'] == ''
    assert record['question'] == output['question']
    assert 'Both sources describe road safety coordination' in record['answer_text']
    assert json.loads(record['evidence_ids']) == ['e1','s1']
    assert json.loads(record['source_urls']) == ['https://example.org/e','https://example.org/s']
    assert record['comparison_country'] == 'Sweden'
    assert record['review_status'] == 'Pending review'
    assert record['submitted_at_utc'].endswith('+00:00')


def test_no_requires_explanation_and_preserves_optional_name(output):
    with pytest.raises(feedback.FeedbackError, match='explain'):
        feedback.build_feedback(output, feedback.RATINGS[1], '  ')
    record = feedback.build_feedback(output, feedback.RATINGS[1], 'This source is outdated.', 'Researcher')
    assert record['optional_name'] == 'Researcher'
    assert record['feedback_text'] == 'This source is outdated.'


def test_unfamiliar_is_valid_without_name(output):
    row = feedback.build_feedback(output, feedback.RATINGS[2])
    assert row['rating'] == feedback.RATINGS[2]
    assert row['optional_name'] == ''


def test_rejects_missing_response_or_untrusted_link(output):
    with pytest.raises(feedback.FeedbackError):
        feedback.build_feedback({**output,'result': None}, feedback.RATINGS[0])
    with pytest.raises(feedback.FeedbackError):
        feedback.build_feedback(output, feedback.RATINGS[1], 'Issue', '', 'javascript:alert(1)')


def test_csv_round_trip_and_idempotence(output):
    row = feedback.build_feedback(output, feedback.RATINGS[0], feedback_id='same-record')
    first = feedback.append_csv(b'', row)
    assert first.startswith(b'\xef\xbb\xbf')
    second = feedback.append_csv(first, row)
    assert first == second
    contents = list(csv.DictReader(io.StringIO(first.decode('utf-8-sig'))))
    assert len(contents) == 1
    assert contents[0]['question'] == output['question']
    row2 = feedback.build_feedback(output, feedback.RATINGS[1], 'Correction', feedback_id='another')
    contents2 = list(csv.DictReader(io.StringIO(feedback.append_csv(first,row2).decode('utf-8-sig'))))
    assert len(contents2) == 2
    assert contents2[1]['feedback_text'] == 'Correction'


def test_csv_formula_injection_is_escaped(output):
    row = feedback.build_feedback({**output,'question': '=cmd|whoami'}, feedback.RATINGS[0])
    text = feedback.append_csv(b'',row).decode('utf-8-sig')
    assert "'=cmd|whoami" in text


def test_private_repo_enforced(output):
    record = feedback.build_feedback(output,feedback.RATINGS[0])
    def public_api(method,url,token,payload=None):
        return (200, {'private': False})
    with pytest.raises(feedback.FeedbackError, match='not private'):
        feedback.save_private_csv(record,repository='owner/public',token='test',api_call=public_api)


def test_private_repo_creation_append_and_no_duplicate(output):
    record1 = feedback.build_feedback(output,feedback.RATINGS[0],feedback_id='record-1')
    record2 = feedback.build_feedback(output,feedback.RATINGS[1],'Issue found',feedback_id='record-2')
    store = {}
    def fake_api(method,url,token,payload=None):
        assert token == 'token'
        if method == 'GET' and url.endswith('/repos/org/private-reviews'):
            return 200, {'private': True}
        if method == 'GET':
            if 'bytes' not in store:
                return 404, {}
            return 200, {'type': 'file', 'sha': store['sha'],
                         'content': base64.b64encode(store['bytes']).decode()}
        if method == 'PUT':
            if 'bytes' in store and payload.get('sha') != store.get('sha'):
                return 409, {}
            store['bytes'] = base64.b64decode(payload['content'])
            store['sha'] = str(len(store['bytes']))
            return (200 if payload.get('sha') else 201), {}
        raise AssertionError('Unexpected API call')
    for row in (record1,record2,record2):
        feedback.save_private_csv(row,repository='org/private-reviews',token='token',api_call=fake_api)
    contents = list(csv.DictReader(io.StringIO(store['bytes'].decode('utf-8-sig'))))
    assert len(contents) == 2
    assert contents[0]['feedback_id'] == 'record-1'
    assert contents[1]['feedback_id'] == 'record-2'


def test_feedback_widget_is_after_response_and_conditional():
    src = (Path(__file__).resolve().parents[1]/'institutional_toolkit'/'ui.py').read_text()
    start = src.index('def _agent_feedback_form(')
    end = src.index('def _agent_workspace(',start)
    fragment = src[start:end]
    assert "rating = st.radio(" in fragment
    assert fragment.index("rating = st.radio(") < fragment.index("with st.form(")
    assert "if rating == feedback.RATINGS[1]" in fragment
    assert 'Your name (optional)' in fragment
    assert 'consent' in fragment
    assert 'feedback.save_private_csv(data)' in fragment
    assert src.index('_agent_feedback_form(output)') > src.index('def _agent_workspace(')
