"""Private CSV feedback capture for Ask the Evidence.

Production storage lives in a separate *private* GitHub repository, NOT the
public Streamlit app repository or its ephemeral local filesystem. A scoped
GitHub fine-grained token is configured only through Streamlit Secrets.

The evidence corpus is never updated by user feedback.
"""
from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import os
import re
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from uuid import uuid4

SCHEMA = (
    'feedback_id', 'submitted_at_utc', 'primary_country', 'comparison_country',
    'question', 'answer_text', 'answer_json', 'evidence_ids', 'source_urls',
    'rating', 'feedback_text', 'suggested_source_url', 'optional_name',
    'review_status',
)
RATINGS = (
    'Yes, matches my understanding',
    'No, does not match my understanding',
    'Not familiar with the topic',
)
CSV_PATH = 'feedback/ask_the_evidence_feedback.csv'
MAX_FILE_BYTES = 900_000  # GitHub Contents API base64 payloads are reliable below 1 MB


class FeedbackError(Exception):
    """Friendly, non-secret-bearing error suitable for UI."""


def _clean_str(value: Any, limit: int) -> str:
    if value is None:
        return ''
    return str(value).replace('\x00', '')[:limit]


def display_answer(result: dict[str, Any]) -> str:
    """Preserve the exact user-visible source-grounded claim texts and caveats."""
    parts: list[str] = []
    if result.get('claims'):
        for claim in result['claims']:
            ids = ', '.join(claim.get('evidence_ids', []))
            parts.append(f"{claim.get('text', '')}" + (f' [Evidence: {ids}]' if ids else ''))
    else:
        parts.append(result.get('status', 'No cited answer available'))
    if result.get('limitations'):
        parts.append('Limitations: ' + '; '.join(result['limitations']))
    if result.get('questions_for_verification'):
        parts.append('Verification questions: ' + '; '.join(result['questions_for_verification']))
    return '\n\n'.join(parts)


def response_fingerprint(output: dict[str, Any]) -> str:
    """Identify the exact prompt, analysis, evidence and scope for submission UI."""
    subset = {
        'question': output.get('question', ''),
        'first': output.get('first', ''),
        'second': output.get('second', ''),
        'result': output.get('result'),
        'ids': [h.get('evidence_id', '') for h in output.get('hits', [])],
    }
    return hashlib.sha256(json.dumps(subset, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:24]


def build_feedback(output: dict[str, Any], rating: str,
                   comment: str = '', optional_name: str = '',
                   suggested_source_url: str = '', feedback_id: str | None = None) -> dict[str, str]:
    """Reject incomplete feedback; retain question + answer + source provenance."""
    if rating not in RATINGS:
        raise FeedbackError('Choose Yes, No, or Not familiar.')
    if not output.get('question') or not isinstance(output.get('result'), dict):
        raise FeedbackError('A generated Agent response is required before submitting feedback.')
    comment = _clean_str(comment.strip(), 3000)
    if rating == RATINGS[1] and not comment:
        raise FeedbackError('Please explain what is incorrect or missing before submitting No.')
    name = _clean_str(optional_name.strip(), 160)
    if suggested_source_url:
        from urllib.parse import urlparse
        link = urlparse(suggested_source_url.strip())
        if link.scheme not in ('https', 'http') or not link.netloc or any(c.isspace() for c in suggested_source_url):
            raise FeedbackError('The optional supporting source must be a valid http(s) link.')
    links = sorted({h.get('source_url', '') for h in output.get('hits', [])
                    if h.get('source_url', '').startswith(('https://', 'http://'))})
    ids = list(dict.fromkeys(h.get('evidence_id', '') for h in output.get('hits', []) if h.get('evidence_id')))
    result = output['result']
    # All CSV cells are treated as untrusted when opened in spreadsheet tools;
    # formula-prefixed values are escaped *only on CSV serialization*.
    return {
        'feedback_id': feedback_id or str(uuid4()),
        'submitted_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'primary_country': _clean_str(output.get('first', ''), 160),
        'comparison_country': _clean_str(output.get('second', ''), 160),
        'question': _clean_str(output['question'], 1000),
        'answer_text': _clean_str(display_answer(result), 50000),
        'answer_json': json.dumps(result, ensure_ascii=False),
        'evidence_ids': json.dumps(ids, ensure_ascii=False),
        'source_urls': json.dumps(links, ensure_ascii=False),
        'rating': rating,
        'feedback_text': comment,
        'suggested_source_url': _clean_str(suggested_source_url.strip(), 1000),
        'optional_name': name,
        'review_status': 'Pending review',
    }


def _safe_csv_cell(value: str) -> str:
    """Prevent spreadsheet formula injection while preserving ordinary text."""
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value


def append_csv(raw_bytes: bytes, record: dict[str, str]) -> bytes:
    """Append one feedback row, rejecting incompatible schemas and duplicates."""
    if len(raw_bytes) > MAX_FILE_BYTES:
        raise FeedbackError('Feedback CSV is too large; an administrator must archive it.')
    if raw_bytes:
        existing_text = raw_bytes.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(existing_text))
        if tuple(reader.fieldnames or ()) != SCHEMA:
            raise FeedbackError('The private CSV schema does not match this version of the app.')
        rows = list(reader)
    else:
        rows = []
    if any(row.get('feedback_id') == record['feedback_id'] for row in rows):
        return raw_bytes  # same id is safe to retry without duplicating it
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=SCHEMA, extrasaction='ignore', lineterminator='\n')
    writer.writeheader()
    for row in rows:
        # Existing rows were already escaped when first written.
        writer.writerow({k: row.get(k, '') for k in SCHEMA})
    writer.writerow({k: _safe_csv_cell(record.get(k, '')) for k in SCHEMA})
    encoded = stream.getvalue().encode('utf-8-sig')
    if len(encoded) > MAX_FILE_BYTES:
        raise FeedbackError('Feedback CSV is full; an administrator must archive it.')
    return encoded


def _api(method: str, url: str, token: str, payload: dict | None = None) -> tuple[int, dict]:
    body = json.dumps(payload).encode('utf-8') if payload is not None else None
    request = Request(url, data=body, method=method, headers={
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'road-safety-toolkit-private-feedback',
        'Content-Type': 'application/json',
    })
    try:
        with urlopen(request, timeout=12) as response:
            return response.status, json.loads(response.read())
    except HTTPError as e:
        # Do not log or show provider messages as they may contain request text.
        return e.code, {}
    except (OSError, URLError):
        raise FeedbackError('Private feedback storage is temporarily unreachable. Please try again.') from None


def github_settings(secrets: Any = None) -> tuple[str, str]:
    """Credentials are never stored in source control or user-visible state."""
    if secrets is None:
        try:
            import streamlit as st
            secrets = st.secrets
        except Exception:
            secrets = {}
    try:
        repository = secrets.get('FEEDBACK_GITHUB_REPO', '') or os.getenv('FEEDBACK_GITHUB_REPO', '')
        token = secrets.get('FEEDBACK_GITHUB_TOKEN', '') or os.getenv('FEEDBACK_GITHUB_TOKEN', '')
    except Exception:
        repository, token = os.getenv('FEEDBACK_GITHUB_REPO', ''), os.getenv('FEEDBACK_GITHUB_TOKEN', '')
    return str(repository).strip(), str(token).strip()


def is_configured(secrets: Any = None) -> bool:
    repository, token = github_settings(secrets)
    return bool(token and re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository))


def save_private_csv(record: dict[str, str], *, repository: str | None = None,
                     token: str | None = None,
                     api_call: Callable = _api) -> None:
    """Write an append-only row to a separate GitHub repo (must be private).

    Optimistic concurrency uses GitHub file SHA and retries only on conflicts.
    We never silently fall back to the public repository or a local file.
    """
    if repository is None or token is None:
        configured_repo, configured_token = github_settings()
        repository = repository if repository is not None else configured_repo
        token = token if token is not None else configured_token
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository or '') or not token:
        raise FeedbackError('Private CSV storage is not configured yet. Ask an administrator to configure Streamlit Secrets.')
    base = f'https://api.github.com/repos/{repository}'
    status, meta = api_call('GET', base, token)
    if status != 200:
        raise FeedbackError('Could not access the configured feedback repository. Check repository access and token permissions.')
    if meta.get('private') is not True:
        raise FeedbackError('Feedback storage is blocked because the configured repository is not private.')
    file_url = base + '/contents/' + quote(CSV_PATH, safe='/')
    for _ in range(3):
        status, current = api_call('GET', file_url, token)
        if status == 404:
            previous, sha = b'', None
        elif status == 200 and current.get('type') == 'file':
            try:
                previous = base64.b64decode(current['content'].replace('\n', ''), validate=True)
                sha = current['sha']
            except (KeyError, ValueError):
                raise FeedbackError('Could not read the existing private CSV file.') from None
        else:
            raise FeedbackError('The feedback CSV could not be retrieved from private storage.')
        updated = append_csv(previous, record)
        if updated == previous:
            return  # duplicate retry already persisted
        payload = {
            'message': 'Record Road Safety Intelligence Agent feedback',
            'content': base64.b64encode(updated).decode('ascii'),
        }
        if sha:
            payload['sha'] = sha
        status, _ = api_call('PUT', file_url, token, payload)
        if status in (200, 201):
            return
        if status not in (409, 422):
            raise FeedbackError('Could not save feedback in the private repository. Check write permissions.')
    raise FeedbackError('Someone else updated the feedback file at the same time. Please submit again.')
