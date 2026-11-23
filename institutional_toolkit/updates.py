"""Opt-in, time-bounded update checks and grounded generation.

The API is only called on a user click. Results are provisional leads and are
never written back into the dataset or treated as verified government facts.
"""
from __future__ import annotations
from datetime import datetime, timezone
import os, re


def api_key() -> str:
    if os.getenv('OPENAI_API_KEY'):
        return os.environ['OPENAI_API_KEY']
    try:
        import streamlit as st
        return str(st.secrets.get('OPENAI_API_KEY', ''))
    except Exception:
        return ''


def check_updates(country: str, known_links: list[str], focus: str) -> dict:
    key=api_key()
    if not key:
        return {'status':'Not checked: no OpenAI API key configured', 'text':'Existing research is still available. No currentness claim is made.', 'sources':[], 'utc':''}
    from openai import OpenAI
    client=OpenAI(api_key=key,timeout=20.0,max_retries=0)
    prompt=f"""Do a SHORT and TARGETED official-source update check only. Do not start a general deep country research project.
Country: {country}. Focus: {focus}.
Known official source links from our reviewed research: {', '.join(known_links[:8]) or 'none available'}.
Search for changes to named institutions, mandates, membership, strategies, action plans since the available source dates, including local-language updates. Prioritize authoritative official primary sources. Give source titles, URLs, effective or published dates and uncertainty. Only mention novel or changed information actually supported by accessible links.
If no relevant update found, say exactly: 'No relevant update identified in this limited check.' Never imply everything was verified current. Do not infer implementation from a planned action. Respond concisely."""
    try:
        response=client.responses.create(model=os.getenv('ROAD_SAFETY_OPENAI_MODEL','gpt-5-mini'),
            tools=[{'type':'web_search','search_context_size':'low'}],
            input=prompt,max_output_tokens=1100)
        cites=[]
        for item in getattr(response,'output',[]) or []:
            for part in getattr(item,'content',[]) or []:
                for ann in getattr(part,'annotations',[]) or []:
                    u=getattr(ann,'url',None)
                    if u and u.startswith(('https://','http://')) and u not in cites:cites.append(u)
        return {'status':'Candidate updates only; manual verification required',
                'text':response.output_text,'sources':cites,
                'utc':datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
    except Exception as exc:
        return {'status':'Update check unavailable: '+type(exc).__name__,
                'text':'No currentness inference made. Existing research remains unchanged.', 'sources':[], 'utc':''}


def synthesize(country: str,question: str, snippets: list[dict]) -> str:
    key=api_key()
    if not key or not snippets:return ''
    from openai import OpenAI
    lines=[f"SOURCE {i+1}: {r['source_url']} | {r['snippet']}" for i,r in enumerate(snippets[:8])]
    prompt=(f"For {country}, answer this question: {question}\n\n"
            "Use only the following retrieved evidence. Cite source URLs precisely. Clearly distinguish planned activities from implemented ones and say when evidence is insufficient. "
            "No unsourced factual statements, fabricated sources or assumptions about absent institutions.\n\n"+'\n'.join(lines))
    try:
        r=OpenAI(api_key=key,timeout=20,max_retries=0).responses.create(
            model=os.getenv('ROAD_SAFETY_OPENAI_MODEL','gpt-5-mini'),input=prompt,max_output_tokens=850)
        return r.output_text
    except Exception:return ''
