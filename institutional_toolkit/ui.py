"""Streamlit UI for the existing final Checklist tab only."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json, re
from html import escape
from unified_brand import header_html
import streamlit as st
from . import evidence as ev, reports, updates, rag, domain_views

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'data'
RESPONSES=("Yes, with official documentation", "Yes, based on my knowledge", "Partially / needs updating",
           "I believe it does not exist", "Not applicable to this jurisdiction", "I do not know")


def _slug(country: str)->str:
    return re.sub(r'[^A-Za-z0-9]+','_',country).strip('_') or 'Country'


def _context_changed(kind: str) -> None:
    """Record a country or mode switch before Streamlit's automatic rerun.

    Each rerun derives the page from the CURRENT country and comparison
    selection. A monotonic revision makes the switch explicit and supports QA.
    Existing country-specific user drafts are intentionally preserved.
    """
    st.session_state['rs_context_revision'] = st.session_state.get('rs_context_revision', 0) + 1
    if kind == 'country':
        st.session_state['rs_previous_primary_country'] = st.session_state.get('rs_context_country')
        st.session_state['rs_context_country'] = st.session_state.get('rs_toolkit_country')
        st.session_state.pop('rs_open_legacy', None)
    elif kind == 'mode':
        st.session_state['rs_context_mode'] = st.session_state.get('rs_toolkit_mode')
    elif kind == 'comparison':
        st.session_state['rs_context_comparison'] = st.session_state.get('rs_compare_country_active')


def _choose_peer(choices: list[str], selected: str | None, previous_primary: str | None) -> str:
    """Keep the selected peer valid after changing the primary country."""
    if not choices:
        raise ValueError('Pairwise comparison requires at least two countries.')
    if selected in choices:
        return selected
    if previous_primary in choices:
        return previous_primary
    for preferred in ('Sweden', 'Estonia'):
        if preferred in choices:
            return preferred
    return choices[0]


def _link(link: str, text: str='View original source'):
    link=ev.url(link)
    if link: st.markdown(f'[{text}]({link})')


def _light_notice(message: str, kind: str = 'info') -> None:
    """Accessible, light-background notices independent of Streamlit's dark-alert internals.

    Native Streamlit alerts can include a dark BaseWeb notification child even
    when the outer stAlert element is set to a light background. This is why
    the previous CSS-only fix did not address the user's screenshot.
    """
    variants = {
        'info': ('#edf7fb', '#087e96', 'Information'),
        'warning': ('#fff9eb', '#98630d', 'Attention'),
        'error': ('#fff2f0', '#a23b36', 'Error'),
        'success': ('#eef9f3', '#197553', 'Success'),
    }
    bg, accent, heading = variants.get(kind, variants['info'])
    content = escape(str(message))
    st.markdown(
        f'<div class="rs-light-notice" role="status" '
        f'style="background-color:{bg}!important;color:#17324a!important;'
        f'border:1px solid #cbdde5;border-left:4px solid {accent};'
        f'border-radius:8px;padding:14px 17px;margin:10px 0 18px;'
        f'font-size:14px;line-height:1.58;">'
        f'<span style="font-weight:700;color:{accent}!important;">{heading}.</span> '
        f'<span style="color:#17324a!important;">{content}</span></div>',
        unsafe_allow_html=True,
    )


def _boundary():
    st.caption('Evidence and source coverage are not assessments of road safety performance. Missing information does not mean a body or intervention does not exist. User responses are not independently verified.')


def _display_grounded_result(result: dict, hits: list[dict], label: str):
    """Only link real research-record URLs, never model-authored sources."""
    st.caption('**'+result.get('status','Draft')+'**')
    if not result.get('claims'):
        _light_notice('No AI-generated factual answer is available for these retrieved records. Review the linked excerpts below, or obtain additional official evidence.', 'info')
    for item in result.get('claims',[]):
        st.write(item['text'])
        for ref in item.get('references',[]):
            _link(ref['url'], 'Evidence '+ref['evidence_id'])
    if result.get('limitations'):
        with st.expander('Limitations and unanswered evidence questions',expanded=True):
            for note in result['limitations']:st.write('• '+note)
            for note in result.get('questions_for_verification',[]):st.write('Verification question: '+note)
    st.caption('AI-assisted interpretation of indexed research, not an independently audited government finding.')
    st.download_button('Download cited evidence and analysis (JSON)',
                       json.dumps({'analysis':result,'retrieved':hits},indent=2,ensure_ascii=False),
                       file_name=_slug(label)+'_RAG_evidence_DRAFT.json',mime='application/json',
                       key='rag_json_'+_slug(label))
    if st.button('Prepare source-grounded analysis report (Word)',key='rag_word_prepare_'+_slug(label)):
        st.session_state['rag_word_'+_slug(label)]=reports.word_rag(
            title=label, question=st.session_state.get('rag_question_'+_slug(label),''),
            hits=hits,result=result)
    doc=st.session_state.get('rag_word_'+_slug(label))
    if doc:
        st.download_button('Download cited analysis (Word)',doc,
                           file_name=_slug(label)+'_cited_analysis_DRAFT.docx',
                           mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           key='rag_word_download_'+_slug(label))


def _display_retrieved(hits: list[dict]):
    if not hits:
        _light_notice('No relevant source-linked excerpt was found in the reviewed records for this request. The system will not invent a finding.', 'warning')
        return
    for i,hit in enumerate(hits,1):
        label=f"{hit['country']} · {hit['domain'] or hit['record_type']} · {hit['evidence_id']}"
        with st.expander(f'Evidence {i} • {label}'):
            st.write(hit['excerpt'])
            st.caption('Jurisdiction: '+(hit.get('jurisdiction') or 'Not specified')+
                       ' | Source locator: '+(hit.get('locator') or 'Not supplied')+
                       ' | Review date: '+(hit.get('checked_on') or 'Not supplied'))
            if hit.get('limitations'):st.write('**Evidence limitation:** '+hit['limitations'])
            st.caption(hit['provenance'])
            _link(hit['source_url'],'Open original source')


def _official_source_records(ctx: dict) -> list[dict]:
    """Freshness search uses original records marked as official/primary sources.

    Historical secondary law transcriptions are useful research leads but must
    not expand the allowed web-search domain list.
    """
    trusted = []
    for record in ctx.get('institutional', []):
        source_type = (record.get('evidence_type') or '').lower()
        link = ev.url(record.get('source_url', ''))
        if link and 'official agency' in source_type:
            trusted.append({'url':link, 'checked_on':record.get('checked_on') or ''})
    for record in ctx.get('findings', []):
        source_type = (record.get('source_class') or '').lower()
        link = ev.url(record.get('source_url', ''))
        if link and ('government' in source_type or 'official agency' in source_type):
            trusted.append({'url':link, 'checked_on':record.get('checked_on') or ''})
    return trusted


def _update_check(country: str, ctx: dict, focus: str, key: str):
    with st.expander('Check for newer official information',expanded=False):
        st.caption('Optional, targeted freshness check. Uses known source links first and checks for changes, not a new deep search. Available with an OpenAI API key.')
        if st.button('Run limited update check',key='freshness_'+key):
            with st.spinner('Checking recent official updates...'):
                source_records=_official_source_records(ctx)
                sources=[r['url'] for r in source_records]
                checked_dates=[r['checked_on'] for r in source_records if r.get('checked_on')]
                since=max(checked_dates) if checked_dates else ''
                st.session_state['freshness_result_'+key]=updates.check_updates(country,sources,focus,since=since)
        result=st.session_state.get('freshness_result_'+key)
        if result:
            st.write('**'+result['status']+'**')
            if result.get('allowed_domains'):
                st.caption('Search restricted to: '+', '.join(result['allowed_domains']))
            st.write(result['text'])
            if result['utc']:st.caption('Checked at '+result['utc'])
            for u in result['sources']:_link(u,'Candidate update source')
            st.caption('Candidate updates do not overwrite existing data or automatically change checklist statuses.')


def _country_findings(data:dict,country:str):
    ctx=ev.country_context(data,country);m=ev.coverage(data,country)
    c1,c2,c3=st.columns(3)
    c1.metric('Reviewed coordinating mechanisms',m['Reviewed mechanisms'])
    c2.metric('Institutional domains with sources',f"{m['Institutional domains with sources']} / {m['Total domains']}")
    c3.metric('Interventions with specific sources',f"{m['Source-linked checklist items']} / {m['Total eligible interventions']}")
    _boundary()
    indexed = rag.corpus(data,country,DATA)
    distinct_links = len({r.source_url for r in indexed})
    st.caption(f'Controlled retrieval index: {len(indexed)} source-linked excerpts from {distinct_links} distinct source URL(s) for {country}. '
               'No full-document coverage is implied by these counts.')
    if not ctx['mechanisms']:
        _light_notice('This country has no detailed mechanism in the reviewed research subset. This is not evidence that it has no coordinating body. The global Atlas may contain additional findings.', 'warning')
    else:
        st.subheader('Coordinating institutions in our reviewed research')
        for p in ctx['mechanisms']:
            st.write(f"**{p['coordinating_body']}**  ")
            st.caption('Jurisdiction: '+p['jurisdiction']+' | Profile: '+p['profile_id'])
        _render_country_domain_grid(data,country)
        st.subheader('Specific interventions with documented sources')
        items=[r for r in ev.checklist_prefill(data,country) if r['source_urls']]
        if not items:_light_notice('No intervention-specific sources in the detailed research subset.')
        for r in items:
            with st.expander(r['matrix_id']+' • '+r['ideal_intervention']):
                st.write('**Classification**: '+r['research_status'])
                st.write(r['documented_action'] or 'No intervention details recorded')
                if r['evidence_note']:st.caption('Research limitation: '+r['evidence_note'])
                for u in r['source_urls']:_link(u)
    if not ctx['mechanisms']:
        _render_country_domain_grid(data,country)
    st.divider()
    st.subheader('Ask the reviewed country evidence (controlled RAG)')
    st.caption('The system retrieves source-linked research excerpts from the selected country only. '
               'It does not search the open web when answering. The current corpus contains reviewed source notes, '
               'not complete copies of every official document.')
    with st.form('research_question_form'):
        question=st.text_input('Your evidence question',placeholder='For example, what sources establish the coordinating body and its mandate?')
        submitted=st.form_submit_button('Retrieve relevant evidence')
    if submitted:
        if len(question.strip())<5:
            _light_notice('Enter a more specific question.', 'warning')
        else:
            st.session_state['toolkit_retrieval_'+country]={
                'question':question,
                'hits':rag.retrieve(data,country,question,data_dir=DATA,limit=8),
            }
            st.session_state.pop('rag_summary_'+country,None)
            st.session_state.pop('rag_word_'+_slug(country),None)
    retrieval=st.session_state.get('toolkit_retrieval_'+country)
    if retrieval:
        st.write('**Question:** '+retrieval['question'])
        hits=retrieval['hits']
        _display_retrieved(hits)
        if hits and updates.api_key() and st.button('Generate citation-checked AI synthesis',key='rag_'+country):
            with st.spinner('Synthesizing the indexed evidence...'):
                st.session_state['rag_summary_'+country]=rag.synthesis(retrieval['question'],hits)
        if hits and not updates.api_key():
            st.caption('Add an OpenAI API key in Streamlit Secrets to enable AI synthesis. Indexed evidence search works without it.')
        if st.session_state.get('rag_summary_'+country):
            st.session_state['rag_question_'+_slug(country)]=retrieval['question']
            st.subheader('Cited synthesis')
            _display_grounded_result(st.session_state['rag_summary_'+country],hits,country)
    _update_check(country,ctx,'recent changes to coordinating institutions, mandates, membership and national strategies','find_'+country)
    if st.button('Prepare printable country findings report',key='word_'+country):
        st.session_state['doc_country_'+country]=reports.word_country(data,country)
    if st.session_state.get('doc_country_'+country):
        st.download_button('Download country findings (Word)',st.session_state['doc_country_'+country],
                           file_name=_slug(country)+'_country_evidence_DRAFT.docx',mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')


def _benchmark(data:dict,country:str):
    st.write('Compare **how much institutional evidence we have documented** across countries, without confusing documentation coverage with institutional quality.')
    table=ev.all_coverage(data)
    scope=st.radio('Country set',['All 195 countries','Countries with reviewed mechanisms'],horizontal=True)
    if scope!='All 195 countries':table=[r for r in table if r['Reviewed mechanisms']>0]
    chosen=ev.coverage(data,country)
    st.write(f"**{country}** has {chosen['Reviewed mechanisms']} mechanism(s) in the reviewed detailed dataset, "
             f"with {chosen['Institutional domains with sources']} source-linked institutional domains "
             f"and {chosen['Source-linked checklist items']} source-linked intervention requirements.")
    _light_notice('Countries with zero detailed records have not been assessed in this subset. Do not interpret zeros as lack of institutions. We cannot derive country performance rankings from these research counts.')
    table.sort(key=lambda r:(r['Country']!=country,r['Country']))
    st.dataframe(table,hide_index=True,use_container_width=True)
    if st.button('Prepare printable benchmarking brief',key='benchmark_report_'+_slug(country)):
        st.session_state['benchmark_doc_'+_slug(country)]=reports.word_benchmark(data,country,table)
    if st.session_state.get('benchmark_doc_'+_slug(country)):
        st.download_button('Download benchmarking summary (Word)',st.session_state['benchmark_doc_'+_slug(country)],
                           file_name=_slug(country)+'_benchmark_brief_DRAFT.docx',
                           mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    st.download_button('Download benchmarking table (CSV)',reports.as_csv(table),
                       file_name=_slug(country)+'_benchmark_coverage.csv',mime='text/csv')
    st.download_button('Download benchmarking table (Excel)',reports.excel_export({'Coverage':table}),
                       file_name=_slug(country)+'_benchmark_coverage.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


def _domain_grid_html(rows: list[dict], country: str, second: str) -> str:
    """Source-grounded responsive comparison cards, four across on desktop."""
    return domain_views.comparison_view(rows, country, second)


def _render_domain_grid(rows: list[dict], country: str, second: str) -> None:
    """A self-contained browser grid that does not collapse into accordions."""
    import streamlit.components.v1 as components
    st.subheader('Institutional comparison by domain')
    st.caption('All 17 domains are shown in a grid. Select one to open its full comparison table below the cards. Membership fields are omitted.')
    components.html(_domain_grid_html(rows, country, second), height=1010, scrolling=True)


def _render_country_domain_grid(data:dict, country:str)->None:
    """Native Streamlit 4-column card grid for Explore Country Findings.

    This intentionally does NOT use expanders or an embedded iframe. Selecting
    a card reruns only the Toolkit fragment, then shows that domain's research
    records in one full-width detail table. Selection is namespaced by country.
    """
    st.subheader('Institutional information')
    st.caption('Choose one of the 17 institutional domains. Four cards appear per row on desktop; select a card to see the supporting institutions, responsibilities, and sources below. Source coverage is not evidence of implementation.')
    ctx = ev.country_context(data, country)
    domains = list(data['domains'])
    by_domain = {domain: [r for r in ctx['institutional'] if r.get('domain') == domain]
                 for domain in domains}
    selected_key = 'rs_evidence_domain_selected_' + _slug(country)
    if st.session_state.get(selected_key) not in domains:
        st.session_state[selected_key] = next(
            (domain for domain in domains if any(ev.url(r.get('source_url', '')) for r in by_domain[domain])),
            domains[0] if domains else None,
        )

    # The grid is native Streamlit, not an HTML snapshot. The selected card and
    # its details are keyed to the currently selected country.
    st.markdown("""<style>
      .st-key-rs_country_domain_grid [data-testid="stHorizontalBlock"] {align-items:stretch!important}
      .st-key-rs_country_domain_grid [class*="st-key-rs_domain_card_"] {
        background:#fff!important;border:1px solid #cfdde8!important;
        border-radius:12px!important;padding:10px 11px!important;
        height:100%;box-shadow:0 2px 10px rgba(7,45,84,.045)!important;
      }
      .st-key-rs_country_domain_grid [class*="st-key-rs_domain_card_"] [data-testid="stButton"] button {
        width:100%!important;min-height:83px!important;height:auto!important;
        white-space:normal!important;text-align:left!important;justify-content:flex-start!important;
        color:#123b60!important;-webkit-text-fill-color:#123b60!important;
        background:#fff!important;border:1px solid transparent!important;
        font-weight:730!important;font-size:13px!important;line-height:1.35!important;
      }
      .st-key-rs_country_domain_grid [class*="st-key-rs_domain_card_"] [data-testid="stButton"] button:hover {
        border-color:#3e8ede!important;background:#eef6ff!important;
      }
      .st-key-rs_country_domain_grid [class*="st-key-rs_domain_card_"] [data-testid="stCaptionContainer"] p {
        color:#506a7d!important;font-size:11px!important;line-height:1.3!important;
      }
      .st-key-rs_country_domain_grid [class*="st-key-rs_domain_card_selected_"] {
        border:2px solid #3e8ede!important;background:#edf5ff!important;
        padding:9px 10px!important;
      }
      .st-key-rs_country_domain_grid [class*="st-key-rs_domain_card_selected_"] [data-testid="stButton"] button {
        background:#edf5ff!important;color:#073b71!important;
        -webkit-text-fill-color:#073b71!important;
      }
      @media(max-width:800px) {
        .st-key-rs_country_domain_grid [data-testid="stHorizontalBlock"] {
          flex-wrap:wrap!important;
        }
        .st-key-rs_country_domain_grid [data-testid="column"] {
          min-width:calc(50% - 14px)!important;flex:1 1 calc(50% - 14px)!important;
        }
      }
      @media(max-width:480px) {
        .st-key-rs_country_domain_grid [data-testid="column"] {
          min-width:100%!important;flex:1 1 100%!important;
        }
      }
    </style>""", unsafe_allow_html=True)

    with st.container(key='rs_country_domain_grid'):
        for start in range(0, len(domains), 4):
            columns = st.columns(4, gap='small')
            for offset, col in enumerate(columns):
                index = start + offset
                if index >= len(domains):
                    continue
                domain = domains[index]
                source_count = sum(bool(ev.url(r.get('source_url', '')))
                                   for r in by_domain[domain])
                selected = st.session_state[selected_key] == domain
                with col:
                    key = ('rs_domain_card_selected_' if selected else 'rs_domain_card_') + _slug(country) + '_' + str(index)
                    with st.container(key=key):
                        if st.button(f'{index + 1:02d}  ·  {domain}',
                                     key='rs_choose_domain_' + _slug(country) + '_' + str(index),
                                     use_container_width=True):
                            st.session_state[selected_key] = domain
                            st.rerun(scope='fragment')
                        st.caption(f'{source_count} linked research record' +
                                   ('' if source_count == 1 else 's') if source_count
                                   else 'No linked research records')

    selected_domain = st.session_state[selected_key]
    if not selected_domain:
        return
    records = by_domain[selected_domain]
    linked = [r for r in records if ev.url(r.get('source_url', ''))]
    st.markdown('### ' + selected_domain)
    st.caption(f'{country} · {len(linked)} source-linked institutional record(s) in this domain')
    if not linked:
        _light_notice('No source-linked institutional record was identified for this domain in the reviewed subset. This does not mean the institution or function is absent.')
        return
    table = []
    for r in linked:
        table.append({
            'Institution': r.get('responsible_institution') or 'Not specified',
            'Institutional role': r.get('functional_responsibility') or 'Not documented',
            'Implementation evidence': r.get('implementation_evidence') or 'Not verified',
            'Original source': ev.url(r.get('source_url', '')),
        })
    st.dataframe(table, use_container_width=True, hide_index=True,
                 column_config={'Original source': st.column_config.LinkColumn('Original source')})
    for r in linked:
        if r.get('classification_rationale'):
            st.caption('Research qualification: ' + r['classification_rationale'])
    st.caption('These are source-linked research findings, not confirmation of formal membership, operational implementation, or road safety outcomes.')


def _pairwise(data:dict,country:str):
    choices=[c for c in data['countries'] if c!=country]
    # A shared comparison selector needs a valid value when the PRIMARY country
    # changes (for example Sweden -> Estonia). Reset invalid or self-comparisons.
    if st.session_state.get('rs_compare_country_active') not in choices:
        st.session_state['rs_compare_country_active'] = _choose_peer(
            choices,st.session_state.get('rs_compare_country_active'),
            st.session_state.get('rs_previous_primary_country'))
    second=st.selectbox('Select the comparison country', choices,
                        key='rs_compare_country_active',
                        on_change=_context_changed, args=('comparison',))
    st.caption(f'Active comparison: {country} versus {second}. The tables below reflect this selection.')
    a=ev.coverage(data,country);b=ev.coverage(data,second)
    st.subheader(f'{country} and {second}')
    c1,c2=st.columns(2)
    c1.metric(country+' • source-linked domains',f"{a['Institutional domains with sources']} / {a['Total domains']}")
    c2.metric(second+' • source-linked domains',f"{b['Institutional domains with sources']} / {b['Total domains']}")
    st.write(f"The reviewed dataset has {a['Source-linked checklist items']} intervention-specific source-linked items for {country} "
             f"and {b['Source-linked checklist items']} for {second}. This is **not** a ranking of road safety performance.")
    comparison_rows = ev.compare(data,country,second)
    _render_domain_grid(comparison_rows,country,second)
    st.subheader('Intervention-level differences in documented evidence')
    first=ev.checklist_prefill(data,country);other=ev.checklist_prefill(data,second)
    available=[(x,y) for x,y in zip(first,other) if x['source_urls'] or y['source_urls']]
    if not available:_light_notice(f'No source-linked intervention records found for {country} or {second} in this reviewed subset. This does not establish that either country lacks these interventions.')
    for x,y in available:
        with st.expander(x['matrix_id']+' • '+x['ideal_intervention']):
            cols=st.columns(2)
            for col,n,r in ((cols[0],country,x),(cols[1],second,y)):
                with col:
                    st.markdown('**'+n+'**')
                    st.write(r['research_status'])
                    st.write(r['documented_action'] or 'Not verified in reviewed source-specific data')
                    for u in r['source_urls']:_link(u)
    st.divider()
    st.subheader('Generate a source-grounded analytical comparison')
    st.caption('The retriever selects separate country-specific excerpts before any model call. '
               'Neither country borrows evidence from the other.')
    topics={
        'Coordination and mandates':'coordination national road safety institution mandate strategy government',
        'Membership and representation':'membership coordination council agencies ministry government participation',
        'Strategies and action plans':'national road safety strategy programme action plan implementation',
        'Accountability and monitoring':'coordination responsibilities implementation evidence monitoring accountability',
    }
    topic=st.selectbox('Comparison focus',list(topics),key='rag_pair_topic_'+_slug(country)+'_'+_slug(second))
    pairkey=_slug(country+'_vs_'+second)
    query=f"Compare {country} and {second} regarding {topics[topic]}, distinguishing the documented governance arrangements and evidence limitations."
    if st.button('Retrieve comparable source excerpts',key='rag_pair_retrieve_'+pairkey):
        with st.spinner('Retrieving independently from both country records...'):
            hits=rag.retrieve_pair(data,country,second,query,data_dir=DATA,per_country=5)
        st.session_state['rag_pair_'+pairkey]={'question':query,'hits':hits}
        st.session_state.pop('rag_pair_answer_'+pairkey,None)
        st.session_state.pop('rag_word_'+pairkey,None)
    retrieved_pair=st.session_state.get('rag_pair_'+pairkey)
    # Each focus requires its own retrieval. Never show an answer produced for a
    # different prompt merely because the same country pair is selected.
    if retrieved_pair and retrieved_pair.get('question')!=query:
        st.session_state.pop('rag_pair_'+pairkey,None)
        st.session_state.pop('rag_pair_answer_'+pairkey,None)
        st.session_state.pop('rag_word_'+pairkey,None)
        retrieved_pair=None
        st.caption('Comparison focus changed. Select Retrieve comparable source excerpts to update the RAG evidence.')
    if retrieved_pair:
        hits=retrieved_pair['hits']
        n1=sum(x['country']==country for x in hits)
        n2=sum(x['country']==second for x in hits)
        st.write(f'Retrieved {n1} evidence excerpts for {country} and {n2} for {second}.')
        _display_retrieved(hits)
        if n1 and n2 and updates.api_key() and st.button('Generate citation-checked pairwise analysis',key='rag_pair_generate_'+pairkey):
            with st.spinner('Preparing evidence-grounded comparison...'):
                st.session_state['rag_pair_answer_'+pairkey]=rag.synthesis(retrieved_pair['question'],hits)
        elif not n1 or not n2:
            _light_notice('This dataset cannot support a source-grounded pairwise analysis of the selected topic for both countries. Compare the available records, and gather missing evidence first.', 'warning')
        elif not updates.api_key():
            st.caption('AI comparison needs an OpenAI API key. Source retrieval and the detailed tables above work without it.')
        if st.session_state.get('rag_pair_answer_'+pairkey):
            st.session_state['rag_question_'+pairkey]=retrieved_pair['question']
            _display_grounded_result(st.session_state['rag_pair_answer_'+pairkey],hits,pairkey)
    st.caption('Adaptation of practices to a different country requires national legal, financial, institutional and operational review.')
    pairrows=[]
    for item in comparison_rows:
        pairrows.append({'Domain':item['domain'],country+' institution':item[country]['responsible_institution'],
                         country+' function':item[country]['functional_responsibility'],
                         country+' source':item[country]['source_url'],
                         second+' institution':item[second]['responsible_institution'],
                         second+' function':item[second]['functional_responsibility'],
                         second+' source':item[second]['source_url']})
    st.download_button('Export pairwise table (Excel)',reports.excel_export({'Domains':pairrows}),
                       file_name=_slug(country)+'_vs_'+_slug(second)+'_domains.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if st.button('Prepare detailed comparison dossier',key='make_pair_doc'):
        st.session_state['pairdoc_'+country+'_'+second]=reports.word_comparison(data,country,second)
    doc=st.session_state.get('pairdoc_'+country+'_'+second)
    if doc:
        st.download_button('Download detailed comparison (Word)',doc,file_name=_slug(country)+'_vs_'+_slug(second)+'_DRAFT.docx',
                           mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    _update_check(country,ev.country_context(data,country),'institutional changes relevant to comparison with '+second,
                  'compare_'+country+'_'+second)


def _checklist(data:dict,country:str):
    st.subheader('Step 1 • Share what you already know')
    st.write('We have already collected research evidence. Before preparing your checklist, please answer any questions where you can add current local knowledge. All questions are optional.')
    prompts=ev.questionnaire(data,country)
    key=_slug(country)
    with st.form('rs_questionnaire_'+key):
        run_freshness = st.checkbox('Check recent official updates when generating (optional API call)',
                                   value=False,
                                   help='Targeted short web search. Results are added as provisional leads and never change research classifications without review.')
        for i,r in enumerate(prompts,1):
            st.markdown(f"**{i}. {r['ideal_intervention']}**")
            st.caption('Domain: '+r['domain']+' | pillar: '+r['pillar'])
            st.radio('What do you know?',RESPONSES,index=None,key='rs_choice_'+key+'_'+r['matrix_id'],horizontal=False)
            st.text_input('Optional official link / document reference',key='rs_src_'+key+'_'+r['matrix_id'])
            st.text_input('Optional explanation',key='rs_note_'+key+'_'+r['matrix_id'])
            if i<len(prompts):st.divider()
        submitted=st.form_submit_button('Generate my prefilled checklist',type='primary')
    if submitted:
        answers={}
        for r in prompts:
            rid=r['matrix_id'];choice=st.session_state.get('rs_choice_'+key+'_'+rid)
            src=st.session_state.get('rs_src_'+key+'_'+rid,'').strip();note=st.session_state.get('rs_note_'+key+'_'+rid,'').strip()
            if choice or src or note:
                answers[rid]={'choice':choice or 'I do not know','source':src,'note':note}
        candidate_updates = {'status':'Not requested', 'text':'', 'sources':[], 'utc':''}
        if run_freshness:
            with st.spinner('Checking for recent official updates before drafting...'):
                candidate_updates=updates.check_updates(
                    country,[s['url'] for s in _official_source_records(ev.country_context(data,country))],
                    'institutional mandates, coordination, strategy and policy details relevant to checklist requirements',
                    since=max((r.get('checked_on','') for r in _official_source_records(ev.country_context(data,country))),default=''))
        st.session_state['rs_assessment_'+key]={'country':country,'answers':answers,
                    'created':datetime.now(timezone.utc).isoformat(timespec='seconds'),
                    'candidate_updates':candidate_updates,
                    'items':ev.checklist_prefill(data,country,answers)}
        # Any earlier drill-down selection must not be mistaken for the new
        # response-specific assessment after the form is resubmitted.
        st.session_state.pop('rs_checklist_item_'+key, None)
        st.session_state.pop('rs_checklist_domain_'+key, None)
    saved=st.session_state.get('rs_assessment_'+key)
    if not saved:
        st.caption('You may skip all questions and still generate a checklist using the published research records.')
    else:
        st.divider();st.subheader('Step 2 • Your prefilled checklist and recommended actions')
        items=saved['items'];cited=sum(bool(x['source_urls']) for x in items)
        x,y,z=st.columns(3)
        x.metric('Interventions',len(items));y.metric('Research-supported evidence leads',cited);z.metric('Your answered questions',len(saved['answers']))
        _light_notice('Private working draft. Source-linked plans are not proof of delivery. User answers are recorded separately and have not been approved or independently verified.', 'warning')
        update_info=saved.get('candidate_updates',{})
        if update_info.get('status') not in ('Not requested',None):
            with st.expander('New information identified during this assessment',expanded=True):
                st.write('**'+update_info['status']+'**')
                st.write(update_info.get('text') or 'No new evidence available')
                for source in update_info.get('sources',[]):_link(source,'Candidate official update')
                st.caption('New findings require human review before they can amend the original evidence or checklist status.')
        st.write('**Research-first assessment summary:** '+str(cited)+' requirements have direct source links; '+
                 str(len(items)-cited)+' requirements require source-specific verification in the present dataset. This does not establish how many interventions are actually missing.')
        domains=['All domains']+list(dict.fromkeys(r['domain'] for r in items))
        selected=st.selectbox('Filter the checklist by institutional domain',domains,
                              key='rs_checklist_domain_'+key)
        eligible=[r for r in items if selected=='All domains' or r['domain']==selected]
        st.dataframe([{'ID':r['matrix_id'],'Domain':r['domain'],'Intervention':r['ideal_intervention'],
                       'Research assessment':r['research_status'],'Your answer':r['respondent_answer']}
                      for r in eligible],hide_index=True,use_container_width=True)
        chosen=st.selectbox('View detailed evidence and recommended intervention',eligible,
                            key='rs_checklist_item_'+key,
                            format_func=lambda r:r['matrix_id']+' • '+r['ideal_intervention'])
        st.write('**Research classification:** '+chosen['research_status'])
        st.write('**Documented action:** '+(chosen['documented_action'] or 'No intervention-specific documented action in the reviewed sources'))
        if chosen['evidence_note']:st.write('**Evidence limitation:** '+chosen['evidence_note'])
        st.write('**Your response:** '+chosen['respondent_answer'])
        if chosen['respondent_note']:st.caption('Your information: '+chosen['respondent_note'])
        st.write('**Recommended verification / improvement step:** '+chosen['recommended_next_step'])
        for source in chosen['source_urls']:_link(source)
        with st.expander('Trace indexed evidence for this checklist intervention'):
            matched=rag.retrieve(data,country,chosen['ideal_intervention'],data_dir=DATA,
                                 limit=5,matrix_id=chosen['matrix_id'])
            if matched:
                st.write('**Direct requirement-specific source excerpts**')
                _display_retrieved(matched)
            else:
                st.write('No citable intervention-specific excerpt was indexed for this requirement.')
                related=rag.retrieve(data,country,chosen['ideal_intervention'],data_dir=DATA,
                                     limit=4,domain=chosen['domain'])
                if related:
                    st.caption('Related institutional context follows, but it does NOT establish implementation of the selected intervention.')
                    _display_retrieved(related)
        st.caption('Exported documents contain the complete list of 72 interventions, supporting links, limitations, questionnaire responses and proposed next actions.')
        st.download_button('Download complete checklist (Excel)',reports.excel_export({
            'Checklist':reports.checklist_export_rows(items),
            'Responses':[{'ID':rid,**rec} for rid,rec in saved['answers'].items()],
            'Update check':[{'Status':update_info.get('status','Not requested'),
                             'Checked UTC':update_info.get('utc',''),
                             'Candidate notes':update_info.get('text',''),
                             'Candidate source URLs':' | '.join(update_info.get('sources',[]))}]}),
            file_name=key+'_prefilled_checklist_DRAFT.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        st.download_button('Download complete checklist (CSV)',reports.as_csv(reports.checklist_export_rows(items)),
                           file_name=key+'_prefilled_checklist_DRAFT.csv',mime='text/csv')
        if st.button('Prepare full Word checklist and action plan'):
            st.session_state['rs_word_'+key]=reports.word_assessment(data,country,items,saved['answers'], update_info)
        if st.session_state.get('rs_word_'+key):
            st.download_button('Download full checklist and recommendations (Word)',st.session_state['rs_word_'+key],
                               file_name=key+'_checklist_action_plan_DRAFT.docx',
                               mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        st.download_button('Backup answers and findings (JSON)',json.dumps(saved,ensure_ascii=False,indent=2),
                           file_name=key+'_checklist_DRAFT.json',mime='application/json')
        st.caption('You should download your files before closing your browser. This version does not include authenticated persistent storage or institutional approval.')
    st.divider()
    st.subheader('Step 3 • Optional detailed self-assessment and action tracking')
    st.write('The original planner is preserved for a full 17-domain assessment, managing actions, and its existing Word/Excel exports. It requires explicit human review.')
    if st.toggle('Open the original detailed action planner',key='rs_open_legacy'):
        import planner
        planner.render()
    _update_check(country,ev.country_context(data,country),'recent changes affecting the prefilled checklist','checklist_'+country)


TOOLKIT_INTRO_HTML = '<style id="rs-lab-toolkit-v3">\n/* Road Safety Lab inspired information architecture with original artwork and assets. */\n.st-key-road_safety_toolkit{font-family:Inter,\'Segoe UI\',Arial,sans-serif!important;color:#142d42!important}\n.st-key-road_safety_toolkit :is(.rst-mast,.rst-hero,.rst-areas,.rst-workflow,.rst-how),\n.st-key-road_safety_toolkit :is(.rst-mast,.rst-hero,.rst-areas,.rst-workflow,.rst-how) *{box-sizing:border-box}\n.st-key-road_safety_toolkit :is(.rst-mast,.rst-hero){margin-left:-24px!important;margin-right:-24px!important}\n.st-key-road_safety_toolkit .rst-mast{background:#fff!important;height:70px;border-bottom:1px solid #d9e6ea!important;display:flex;align-items:center;justify-content:space-between;padding:0 max(28px,calc((100% - 1440px)/2));gap:15px}\n.st-key-road_safety_toolkit .rst-brand{display:flex;align-items:center;gap:12px;font-size:14px;font-weight:850;letter-spacing:.065em;color:#11364b!important;-webkit-text-fill-color:#11364b!important;text-transform:uppercase}\n.st-key-road_safety_toolkit .rst-brand-mark{height:39px;width:39px;display:grid;place-items:center;border-radius:12px;background:#def3f2!important;color:#096e76!important;border:1px solid #b1d9d7!important;flex-shrink:0}\n.st-key-road_safety_toolkit .rst-brand-mark svg{height:28px;width:28px;stroke:#087e84!important}\n.st-key-road_safety_toolkit .rst-mast-nav{display:flex;gap:20px;color:#3c6070!important;-webkit-text-fill-color:#3c6070!important;font-size:12px;font-weight:750;letter-spacing:.035em}\n.st-key-road_safety_toolkit .rst-mast-nav span{white-space:nowrap}\n.st-key-road_safety_toolkit .rst-hero{height:405px!important;min-height:405px!important;max-height:405px!important;overflow:hidden;position:relative;isolation:isolate;background:linear-gradient(110deg,#08283a 0%,#0b5268 62%,#0c8a8d 145%)!important}\n.st-key-road_safety_toolkit .rst-hero:before{content:"";position:absolute;inset:0;pointer-events:none;background:radial-gradient(circle at 85% 18%,rgba(91,216,211,.17),transparent 39%)}\n.st-key-road_safety_toolkit .rst-hero-inner{height:100%;max-width:1490px;margin:auto;display:grid;grid-template-columns:minmax(0,1fr) minmax(370px,.83fr);gap:35px;align-items:center;padding:32px 36px;position:relative;z-index:1}\n.st-key-road_safety_toolkit .rst-hero-copy{max-width:815px;position:relative;z-index:2}\n.st-key-road_safety_toolkit .rst-overline{display:inline-flex;align-items:center;gap:9px;color:#a7e6df!important;-webkit-text-fill-color:#a7e6df!important;letter-spacing:.15em;font-size:12px;font-weight:800;text-transform:uppercase;margin-bottom:19px}\n.st-key-road_safety_toolkit .rst-overline:before{content:"";display:inline-block;width:34px;height:3px;background:#e7bd54;border-radius:3px}\n.st-key-road_safety_toolkit .rst-hero h1{font-family:Inter,\'Segoe UI\',Arial,sans-serif!important;color:#fff!important;-webkit-text-fill-color:#fff!important;font-size:clamp(36px,3.4vw,57px)!important;line-height:1.075!important;letter-spacing:-.045em!important;font-weight:850!important;margin:0 0 17px!important;max-width:770px!important}\n.st-key-road_safety_toolkit .rst-hero h1 em{font-style:normal!important;color:#8ce0d4!important;-webkit-text-fill-color:#8ce0d4!important}\n.st-key-road_safety_toolkit .rst-hero p{font-size:16px!important;color:#ecf7f8!important;-webkit-text-fill-color:#ecf7f8!important;line-height:1.65!important;max-width:670px!important;margin:0!important}\n.st-key-road_safety_toolkit .rst-hero-tags{display:flex;gap:10px;flex-wrap:wrap;margin-top:25px}\n.st-key-road_safety_toolkit .rst-hero-tags span{font-size:11px;color:#e7f6f5!important;-webkit-text-fill-color:#e7f6f5!important;border:1px solid rgba(224,251,247,.38);border-radius:22px;padding:7px 12px;letter-spacing:.03em}\n.st-key-road_safety_toolkit .rst-hero-art{width:100%;height:355px;display:flex;align-items:center;justify-content:center;opacity:.98;pointer-events:none}\n.st-key-road_safety_toolkit .rst-hero-art svg{width:100%;max-height:355px;filter:drop-shadow(0 22px 25px rgba(0,24,37,.18))}\n.st-key-road_safety_toolkit .rst-main{max-width:1450px;padding:34px 8px 6px;margin:0 auto}\n.st-key-road_safety_toolkit .rst-eyebrow{font-size:11px;color:#07817d!important;-webkit-text-fill-color:#07817d!important;text-transform:uppercase;letter-spacing:.135em;font-weight:850;margin:0 0 11px}\n.st-key-road_safety_toolkit .rst-main h2{font-size:clamp(24px,2.5vw,32px)!important;font-weight:850!important;color:#153349!important;-webkit-text-fill-color:#153349!important;letter-spacing:-.03em!important;line-height:1.16!important;margin:0 0 12px!important}\n.st-key-road_safety_toolkit .rst-deck{font-size:14px;color:#566f7e!important;-webkit-text-fill-color:#566f7e!important;line-height:1.62!important;margin:0 0 23px!important;max-width:980px}\n.st-key-road_safety_toolkit .rst-areas{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:17px;margin:0 0 25px}\n.st-key-road_safety_toolkit .rst-area{border:1px solid #d7e5e8!important;border-radius:14px;overflow:hidden;background:#fff!important;box-shadow:0 8px 24px rgba(12,52,67,.055);min-height:299px;display:flex;flex-direction:column;transition:transform .15s,border-color .15s}\n.st-key-road_safety_toolkit .rst-area:hover{transform:translateY(-3px);border-color:#88c8c6!important}\n.st-key-road_safety_toolkit .rst-area-art{height:113px;display:grid;place-items:center;position:relative;overflow:hidden}\n.st-key-road_safety_toolkit .rst-area-art svg{width:120px;height:95px;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;fill:none;position:relative;z-index:1}\n.st-key-road_safety_toolkit .rst-area-art:before{content:"";position:absolute;width:210px;height:210px;border-radius:50%;right:-95px;top:-123px;border:28px solid rgba(255,255,255,.13)}\n.st-key-road_safety_toolkit .rst-a1 .rst-area-art{background:linear-gradient(130deg,#0e6070,#178b93)}\n.st-key-road_safety_toolkit .rst-a2 .rst-area-art{background:linear-gradient(130deg,#163f60,#32708d)}\n.st-key-road_safety_toolkit .rst-a3 .rst-area-art{background:linear-gradient(130deg,#16545b,#329b91)}\n.st-key-road_safety_toolkit .rst-a4 .rst-area-art{background:linear-gradient(130deg,#0a414c,#226d76)}\n.st-key-road_safety_toolkit .rst-area-body{padding:19px 19px 20px;display:flex;flex-direction:column;flex:1}\n.st-key-road_safety_toolkit .rst-area-num{color:#087982!important;-webkit-text-fill-color:#087982!important;letter-spacing:.11em;font-weight:850;font-size:10px;margin:0 0 7px}\n.st-key-road_safety_toolkit .rst-area h3{font-size:17px!important;color:#16354b!important;-webkit-text-fill-color:#16354b!important;font-weight:830!important;line-height:1.3!important;margin:0 0 9px!important}\n.st-key-road_safety_toolkit .rst-area p{font-size:12.5px;color:#526e7b!important;-webkit-text-fill-color:#526e7b!important;line-height:1.58!important;margin:0 0 13px!important;flex:1}\n.st-key-road_safety_toolkit .rst-area-end{font-size:11px;color:#087987!important;-webkit-text-fill-color:#087987!important;font-weight:800;border-top:1px solid #e8eff1;padding-top:11px}\n.st-key-road_safety_toolkit .rst-how{display:grid;grid-template-columns:1.2fr 1fr;gap:25px;align-items:center;padding:18px 22px;margin-bottom:15px;background:#eaf6f5!important;border:1px solid #c6e3e0!important;border-left:4px solid #038a89!important;border-radius:12px}\n.st-key-road_safety_toolkit .rst-how h3{font-size:15px!important;color:#124b54!important;-webkit-text-fill-color:#124b54!important;margin:0 0 6px!important;font-weight:820!important}\n.st-key-road_safety_toolkit .rst-how p{font-size:12.5px!important;color:#345d63!important;-webkit-text-fill-color:#345d63!important;margin:0!important;line-height:1.55!important}\n.st-key-road_safety_toolkit .rst-how-steps{display:flex;justify-content:space-between;gap:8px;align-items:center}\n.st-key-road_safety_toolkit .rst-how-step{font-size:11px;font-weight:800;color:#14636b!important;-webkit-text-fill-color:#14636b!important;background:#fff!important;border:1px solid #d1e7e5;border-radius:8px;padding:12px 9px;text-align:center;flex:1}\n.st-key-road_safety_toolkit .rst-how-arrow{font-weight:900;color:#13818c!important;-webkit-text-fill-color:#13818c!important}\n.st-key-road_safety_toolkit .rst-workflow{padding:18px 0 9px;border-top:1px solid #dbe8e8;margin-top:7px}\n.st-key-road_safety_toolkit .rst-workflow h2{font-size:23px!important;margin:0 0 6px!important}\n.st-key-road_safety_toolkit .rst-workflow p{font-size:13px!important;color:#587381!important;-webkit-text-fill-color:#587381!important;margin:0!important}\n.st-key-road_safety_toolkit .rst-mode-brief{max-width:1450px;padding:16px 19px 15px;background:#fff!important;border:1px solid #d6e6e6;border-left:4px solid #078d91;border-radius:10px;margin:12px 0 20px}\n.st-key-road_safety_toolkit .rst-mode-brief h3{color:#1a4455!important;-webkit-text-fill-color:#1a4455!important;margin:0 0 5px!important;font-size:17px!important}\n.st-key-road_safety_toolkit .rst-mode-brief p{color:#526c78!important;-webkit-text-fill-color:#526c78!important;font-size:13px!important;line-height:1.58!important;margin:0!important}\n@media(max-width:1160px){.st-key-road_safety_toolkit .rst-hero-inner{grid-template-columns:minmax(0,1fr) minmax(260px,.6fr)}.st-key-road_safety_toolkit .rst-areas{grid-template-columns:repeat(2,minmax(0,1fr))}.st-key-road_safety_toolkit .rst-area{min-height:270px}}\n@media(max-width:790px){.st-key-road_safety_toolkit :is(.rst-mast,.rst-hero){margin-left:-12px!important;margin-right:-12px!important}.st-key-road_safety_toolkit .rst-mast{padding:0 15px!important}.st-key-road_safety_toolkit .rst-mast-nav{display:none}.st-key-road_safety_toolkit .rst-hero{height:auto!important;min-height:355px!important;max-height:none!important}.st-key-road_safety_toolkit .rst-hero-inner{display:block!important;padding:38px 22px 37px!important}.st-key-road_safety_toolkit .rst-hero h1{font-size:clamp(30px,8vw,43px)!important}.st-key-road_safety_toolkit .rst-hero p{font-size:14px!important}.st-key-road_safety_toolkit .rst-hero-art{display:none}.st-key-road_safety_toolkit .rst-main{padding:27px 0 5px}}\n@media(max-width:640px){.st-key-road_safety_toolkit .rst-areas{grid-template-columns:1fr!important;gap:12px}.st-key-road_safety_toolkit .rst-area{min-height:0}.st-key-road_safety_toolkit .rst-area-art{height:82px}.st-key-road_safety_toolkit .rst-area-art svg{height:72px}.st-key-road_safety_toolkit .rst-area-body{padding:17px}.st-key-road_safety_toolkit .rst-how{display:block}.st-key-road_safety_toolkit .rst-how-steps{margin-top:14px}.st-key-road_safety_toolkit .rst-hero-tags{gap:5px}}\n</style>\n<div class="rst-mast" role="banner">\n  <div class="rst-brand"><span class="rst-brand-mark" aria-hidden="true">\n    <svg viewBox="0 0 36 36" aria-hidden="true"><path d="M10 30 C8 19 21 16 24 6" stroke="currentColor" fill="none" stroke-width="7" stroke-linecap="round"/><path d="M13 27l2-4m3-4 2-4m2-4 2-4" stroke="white" stroke-width="1.9" stroke-linecap="round"/></svg>\n  </span>Road Safety Toolkit</div>\n  <div class="rst-mast-nav"><span>COUNTRY EVIDENCE</span><span>INTERNATIONAL LEARNING</span><span>INSTITUTIONAL ACTION</span></div>\n</div>\n<section class="rst-hero" aria-labelledby="rst-title">\n  <div class="rst-hero-inner">\n    <div class="rst-hero-copy">\n      <span class="rst-overline">Global knowledge and action workspace</span>\n      <h1 id="rst-title">Road Safety<br><em>Institutional Toolkit</em></h1>\n      <p>Bring country research, international experience, and government knowledge together to strengthen how road safety institutions coordinate and deliver action.</p>\n      <div class="rst-hero-tags"><span>Evidence-led</span><span>Cross-country learning</span><span>Action-oriented</span></div>\n    </div>\n    <div class="rst-hero-art" aria-hidden="true">\n      <svg viewBox="0 0 570 385" xmlns="http://www.w3.org/2000/svg" role="img">\n        <defs><linearGradient id="road" x1="0" x2="1"><stop stop-color="#77D8C9"/><stop offset="1" stop-color="#D5EBC9"/></linearGradient><linearGradient id="card" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#276E80"/><stop offset="1" stop-color="#103A54"/></linearGradient></defs>\n        <circle cx="350" cy="185" r="158" fill="#d5ffff" opacity=".075"/>\n        <circle cx="350" cy="185" r="120" fill="none" stroke="#bdeee7" opacity=".18" stroke-width="1.4" stroke-dasharray="5 9"/>\n        <path d="M96 362C119 270 196 281 238 207S324 117 432 33" fill="none" stroke="#194A59" stroke-width="80" stroke-linecap="round"/>\n        <path d="M96 362C119 270 196 281 238 207S324 117 432 33" fill="none" stroke="url(#road)" stroke-width="3" stroke-dasharray="17 15" stroke-linecap="round"/>\n        <path d="M112 360C131 302 210 306 258 229S342 130 432 47" fill="none" stroke="#98EAE2" opacity=".28" stroke-width="1.5"/>\n        <path d="M73 343C100 263 177 248 219 187S304 87 406 17" fill="none" stroke="#98EAE2" opacity=".28" stroke-width="1.5"/>\n        <g fill="#0E6574" stroke="#C5F8EE" stroke-width="3"><circle cx="116" cy="319" r="13"/><circle cx="244" cy="204" r="13"/><circle cx="349" cy="113" r="13"/><circle cx="419" cy="40" r="13"/></g>\n        <g><rect x="310" y="167" width="213" height="135" rx="12" fill="url(#card)" stroke="#8fcfce" opacity=".97"/><rect x="326" y="186" width="66" height="7" rx="3" fill="#91D8CF"/><rect x="326" y="205" width="115" height="6" rx="3" fill="#DAF7F4" opacity=".7"/><rect x="326" y="245" width="19" height="35" rx="3" fill="#A5E7D7"/><rect x="354" y="228" width="19" height="52" rx="3" fill="#78CBCD"/><rect x="382" y="216" width="19" height="64" rx="3" fill="#E6C26F"/><rect x="410" y="199" width="19" height="81" rx="3" fill="#8ED8D8"/><path d="M450 259h52" stroke="#B9E9E2" stroke-width="3" stroke-linecap="round"/><path d="M450 274h40" stroke="#B9E9E2" opacity=".6" stroke-width="3" stroke-linecap="round"/></g>\n        <g transform="translate(120 48)"><rect width="126" height="62" rx="9" fill="#EAF8F4"/><path d="M15 18h38M15 29h61" stroke="#0C6776" stroke-width="6" stroke-linecap="round"/><path d="M16 46l13-6 13 4 13-11 13 2" fill="none" stroke="#169C9C" stroke-width="3"/><circle cx="99" cy="35" r="15" fill="#0B6575"/><path d="M94 35l4 4 8-9" stroke="#fff" stroke-width="3" fill="none"/></g>\n        <g fill="#EBD78A"><circle cx="172" cy="220" r="4"/><circle cx="292" cy="78" r="4"/><circle cx="479" cy="89" r="4"/></g>\n      </svg>\n    </div>\n  </div>\n</section>\n<div class="rst-main">\n  <p class="rst-eyebrow">What would you like to achieve?</p>\n  <h2>From knowledge to country-specific action</h2>\n  <p class="rst-deck">Choose one of four services. You can start with existing research, examine international evidence, compare institutions, or create an editable improvement checklist informed by your own knowledge.</p>\n  <section class="rst-areas" aria-label="Four institutional toolkit services">\n    <article class="rst-area rst-a1"><div class="rst-area-art" aria-hidden="true"><svg viewBox="0 0 120 96" stroke="#EBFFFA"><rect x="20" y="13" width="80" height="70" rx="7"/><path d="M35 30h50M35 42h25M35 58h30"/><circle cx="81" cy="62" r="10"/><path d="M88 69l12 12"/></svg></div><div class="rst-area-body"><span class="rst-area-num">01 / KNOWLEDGE</span><h3>Explore country findings</h3><p>Review identified institutions, mandates, responsibilities, strategies and source links for your selected country.</p><span class="rst-area-end">Output · Country evidence report</span></div></article>\n    <article class="rst-area rst-a2"><div class="rst-area-art" aria-hidden="true"><svg viewBox="0 0 120 96" stroke="#EBFFFA"><path d="M20 80h85M30 70V40M48 70V52M66 70V29M84 70V17"/><path d="M17 28l20-10 20 7 23-9 15 4"/><circle cx="97" cy="20" r="7"/></svg></div><div class="rst-area-body"><span class="rst-area-num">02 / BENCHMARKING</span><h3>Benchmark internationally</h3><p>See how published evidence coverage differs across countries, with clear limits on what can be concluded.</p><span class="rst-area-end">Output · Benchmarking brief</span></div></article>\n    <article class="rst-area rst-a3"><div class="rst-area-art" aria-hidden="true"><svg viewBox="0 0 120 96" stroke="#EBFFFA"><rect x="10" y="21" width="43" height="51" rx="6"/><rect x="67" y="21" width="43" height="51" rx="6"/><path d="M24 39h16M24 51h16M80 39h16M80 51h16M51 44h18"/><path d="M62 37l7 7-7 7"/></svg></div><div class="rst-area-body"><span class="rst-area-num">03 / PEER LEARNING</span><h3>Compare two countries</h3><p>Investigate institutional arrangements side by side across 17 domains, with clickable evidence tables.</p><span class="rst-area-end">Output · Comparative dossier</span></div></article>\n    <article class="rst-area rst-a4"><div class="rst-area-art" aria-hidden="true"><svg viewBox="0 0 120 96" stroke="#EBFFFA"><rect x="28" y="15" width="66" height="70" rx="7"/><path d="M43 29l4 4 7-9M60 30h21M43 48l4 4 7-9M60 49h21M44 68h37"/></svg></div><div class="rst-area-body"><span class="rst-area-num">04 / INSTITUTIONAL ACTION</span><h3>Generate a tailored checklist</h3><p>Answer a few optional questions and receive a prefilled 72-intervention assessment with next steps.</p><span class="rst-area-end">Output · Editable action plan</span></div></article>\n  </section>\n  <section class="rst-how" aria-label="How the evidence engine works">\n    <div><h3>How the Toolkit works</h3><p>It retrieves source-linked country records first, distinguishes verified evidence from unknowns, and can check recent official changes on request. AI summaries require an API key and must cite retrieved sources. Your answers never overwrite the reviewed research automatically.</p></div>\n    <div class="rst-how-steps" aria-hidden="true"><span class="rst-how-step">RETRIEVE<br>EVIDENCE</span><span class="rst-how-arrow">→</span><span class="rst-how-step">VERIFY<br>CHANGES</span><span class="rst-how-arrow">→</span><span class="rst-how-step">PLAN<br>ACTION</span></div>\n  </section>\n  <section class="rst-workflow"><p class="rst-eyebrow">Your workspace</p><h2>Begin with your country</h2><p>Select a country, choose your task, and use the evidence and guidance below.</p></section>\n</div>\n'


def _render_toolkit_intro() -> None:
    """Use the SAME UNITAR-informed header as all six embedded HTML pages."""
    # Retain the original four service cards, retrieval explanation, and styling,
    # but discard the outdated, separate Toolkit masthead and hero.
    before_main, after_main = TOOLKIT_INTRO_HTML.split('<div class="rst-main">', 1)
    existing_styles = before_main.split('<div class="rst-mast"', 1)[0]
    standard_header = header_html(
        section='Road Safety Institutional Toolkit',
        eyebrow='COUNTRY EVIDENCE AND INSTITUTIONAL ACTION',
        title_html='Road Safety <em>Institutional Toolkit</em>',
        description=(
            'Explore institutional evidence, compare national arrangements, '
            'and develop a country-specific road safety coordination improvement plan.'
        ),
        meta='195 countries · 17 institutional domains · 72 defined interventions',
        legacy_mast='grs-fixed-banner',
    )
    # This content is trusted, repository-authored HTML (never user input).
    # Do not pass it through st.markdown: the indented lines inside the shared
    # masthead are parsed as a Markdown CODE BLOCK, displaying raw <div> tags.
    # st.html uses Streamlit's HTML renderer and preserves the shared hero.
    st.html(existing_styles + standard_header + '<div class="rst-main">' + after_main)


def render():
    with st.container(key='road_safety_toolkit'):
        try:data=ev.load_data(str(DATA))
        except (FileNotFoundError,ValueError) as err:
            _light_notice('The Toolkit could not load its research data: '+str(err), 'error');return
        _render_toolkit_intro()
        st.markdown('<div class="rs-workspace-head"><strong>Start your country assessment</strong>'
                    '<p>Select a country and one of the four services below. The comparison country is only requested when needed.</p>'
                    '</div>',unsafe_allow_html=True)
        country=st.selectbox('Select your country',data['countries'],
                             index=data['countries'].index('Estonia') if 'Estonia' in data['countries'] else 0,
                             key='rs_toolkit_country',
                             on_change=_context_changed,args=('country',))
        if 'rs_context_country' not in st.session_state:
            st.session_state['rs_context_country']=country
        mode=st.radio('What would you like to do?',(
            'Explore country findings','Benchmark internationally','Compare with another country','Generate my institutional checklist'),
            key='rs_toolkit_mode',horizontal=True,
            on_change=_context_changed,args=('mode',))
        # Unlike a static iframe, Streamlit reruns when country/mode changes.
        # Displaying the active country makes the selected data context explicit.
        st.markdown(
            '<div class="rs-toolkit-context-status" role="status" aria-live="polite">'
            '<strong>Currently viewing:</strong> '+escape(country)+' &nbsp; | &nbsp; '+escape(mode)+'</div>',
            unsafe_allow_html=True,
        )
        info = {
            'Explore country findings':('Understand the evidence',
                'Review identified coordinating bodies, institutional roles and original sources. Select a domain in the 17-card grid to inspect its records. You can then retrieve source-linked research excerpts and export a country brief.'),
            'Benchmark internationally':('Benchmark documentation coverage',
                'Compare the coverage of reviewed institutional evidence across the country directory. This is not a ranking of road safety performance. Download an executive brief or an Excel table.'),
            'Compare with another country':('Learn from another country',
                'Select one peer country to see all 17 domains in a four-column grid. Clicking a domain shows a real side-by-side source table, followed by intervention-level evidence and an optional analytical report.'),
            'Generate my institutional checklist':('Create your country-specific action plan',
                'First answer eight optional multiple-choice questions selected from areas where evidence is limited. The Toolkit then prefills 72 interventions from research plus your responses and proposes verification and improvement steps.'),
        }
        heading, description = info[mode]
        st.markdown('<div class="rst-mode-brief"><h3>'+escape(heading)+'</h3><p>'+escape(description)+'</p></div>',unsafe_allow_html=True)
        if mode=='Explore country findings':_country_findings(data,country)
        elif mode=='Benchmark internationally':_benchmark(data,country)
        elif mode=='Compare with another country':_pairwise(data,country)
        else:_checklist(data,country)
