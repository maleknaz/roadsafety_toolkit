"""Global Road Safety Planner: data-connected Streamlit MVP.

Drafts live in Streamlit session state and can be exported/imported as JSON.
No user identity, durable multi-user database or publication is implemented.
Research evidence is read-only and never automatically converted to confirmed findings.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from docx import Document
from docx.shared import Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data'
PILLARS = ['P1 Management', 'P2 Roads', 'P3 Vehicles', 'P4 Users', 'P5 Post-crash']
ASSESSMENTS = ['Not assessed', 'Fully aligned', 'Partially aligned', 'Confirmed gap', 'Evidence insufficient', 'Not applicable (reason required)']
STAGES = ['Not verified', 'Planned', 'In progress', 'Implementation reported', 'Completed and verified']
MEMBERSHIPS = ['Not assessed', 'Confirmed member', 'Confirmed not a member', 'Historical member', 'Not verified']
FUNCTIONS = ['Not assessed', 'Documented', 'Partially documented', 'Not documented', 'Not verified']
TASK_STATUSES = ['Not started', 'In progress', 'Blocked', 'Submitted for review', 'Completed and verified']


def rows(name):
    with (DATA / name).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def load():
    return {
        'countries': json.loads((DATA / 'countries_195.json').read_text(encoding='utf-8')),
        'checklist': [r for r in rows('checklist.csv') if r['eligible'].lower() == 'true'],
        'domains': list(dict.fromkeys(r['domain'] for r in rows('checklist.csv'))),
        'institutional': rows('institutional_evidence.csv'),
        'findings': rows('source_findings.csv'),
        'profiles': rows('intervention_evidence.csv'),
    }


def fresh(country, scope, jurisdiction, mechanism):
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    return {'schema':'road-safety-planner-v1', 'country':country, 'scope':scope,
            'jurisdiction':jurisdiction, 'mechanism':mechanism,
            'created':now, 'updated':now, 'domains':{}, 'interventions':{},
            'actions':[], 'review_state':'Private draft'}


def key_for(a):
    return '|'.join([a['country'],a['scope'],a['jurisdiction'],a['mechanism']])


def set_cell(a, category, index, field, value):
    a[category].setdefault(index,{})[field] = value
    a['updated'] = datetime.now(timezone.utc).isoformat(timespec='seconds')


def word_bytes(a, d):
    doc = Document()
    section = doc.sections[0];section.top_margin=Inches(.7);section.bottom_margin=Inches(.7)
    doc.add_heading('Road Safety Governance Gap Analysis',0)
    doc.add_paragraph(a['country'] + (' | '+a['jurisdiction'] if a['jurisdiction'] else ''), style='Subtitle')
    doc.add_paragraph('PRIVATE DRAFT | Not reviewed, approved or published')
    doc.add_paragraph('Assessment scope: '+a['scope']+'\nResearch mechanism: '+(a['mechanism'] or 'No linked mechanism')+'\nSaved: '+a['updated'])
    doc.add_heading('Executive summary',level=1)
    iv = a['interventions']; assessed = sum(x.get('assessment','Not assessed') != 'Not assessed' for x in iv.values())
    doc.add_paragraph(f'{assessed} of 72 applicable interventions have an entered assessment. This is assessment completion, not implemented road safety performance.')
    doc.add_paragraph('A confirmed gap requires explicit supporting evidence. An evidence gap means the available information is insufficient to determine alignment.')
    doc.add_heading('Institutional assessment: 17 domains',level=1)
    for domain in d['domains']:
        rec = a['domains'].get(domain,{})
        doc.add_heading(domain,level=2)
        doc.add_paragraph('Formal membership: '+rec.get('membership','Not assessed')+'\nFunctional responsibility: '+rec.get('functional','Not assessed')+'\nResponsible institution: '+rec.get('institution','N/A')+'\nSource: '+rec.get('source','N/A'))
    doc.add_heading('Intervention assessment: 72 requirements',level=1)
    for r in d['checklist']:
        rec = iv.get(r['matrix_id'],{})
        doc.add_heading(r['matrix_id']+' | '+r['ideal_intervention'],level=2)
        doc.add_paragraph('Domain: '+r['domain']+'; pillar: '+r['pillar']+'\nFinding: '+rec.get('assessment','Not assessed')+'; stage: '+rec.get('stage','Not verified')+'\nInstitution: '+rec.get('institution','N/A')+'\nSource: '+rec.get('source','N/A')+'\nNotes: '+rec.get('notes','N/A'))
    doc.add_heading('Actions and decisions',level=1)
    if not a['actions']:doc.add_paragraph('No actions entered.')
    for item in a['actions']:
        doc.add_paragraph(f"{item.get('requirement','')} | {item.get('title','')} | {item.get('status','')} | Owner: {item.get('owner','N/A')} | Due: {item.get('due','N/A')}")
    doc.add_heading('Data integrity and review status',level=1)
    doc.add_paragraph('The country research register provides candidate evidence, not self-assessment answers. Private drafts are not approved country statements. Publication and shared editing require authenticated server-side services.')
    b=io.BytesIO();doc.save(b);return b.getvalue()


def excel_bytes(a, d):
    """Create an Excel workbook using openpyxl (Streamlit Cloud friendly)."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    wb.remove(wb.active)
    sheets = [
        ('Summary', [
            ['Field', 'Value'], ['Country', a['country']], ['Scope', a['scope']],
            ['Jurisdiction', a['jurisdiction']], ['Research mechanism', a['mechanism']],
            ['Review status', a['review_state']], ['Updated', a['updated']],
            ['Interventions assessed', sum(v.get('assessment', 'Not assessed') != 'Not assessed'
                                           for v in a['interventions'].values())],
            ['Total defined requirements', 72],
        ]),
        ('Institutions', [['Domain', 'Membership', 'Functional role', 'Responsible institution', 'Evidence URL', 'Notes']] + [
            [name, rec.get('membership', 'Not assessed'), rec.get('functional', 'Not assessed'),
             rec.get('institution', ''), rec.get('source', ''), rec.get('notes', '')]
            for name in d['domains'] for rec in [a['domains'].get(name, {})]
        ]),
        ('Checklist', [['ID', 'Pillar', 'Domain', 'Ideal intervention', 'Assessment',
                        'Implementation stage', 'Responsible institution', 'Evidence URL', 'Notes']] + [
            [r['matrix_id'], r['pillar'], r['domain'], r['ideal_intervention'],
             rec.get('assessment', 'Not assessed'), rec.get('stage', 'Not verified'),
             rec.get('institution', ''), rec.get('source', ''), rec.get('notes', '')]
            for r in d['checklist'] for rec in [a['interventions'].get(r['matrix_id'], {})]
        ]),
        ('Action Tracker', [['Requirement', 'Action', 'Owner', 'Due date', 'Priority', 'Status', 'Evidence']] + [
            [x.get(k, '') for k in ['requirement', 'title', 'owner', 'due', 'priority', 'status', 'evidence']]
            for x in a['actions']
        ]),
    ]
    for sheet_name, values in sheets:
        ws = wb.create_sheet(sheet_name)
        for row in values:
            ws.append([str(v) if v is not None and not isinstance(v, (int, float)) else v for v in row])
        ws.freeze_panes = 'A2'
        ws.auto_filter.ref = ws.dimensions
        for cell in ws[1]:
            cell.fill = PatternFill('solid', fgColor='123B57')
            cell.font = Font(color='FFFFFF', bold=True)
            cell.alignment = Alignment(wrap_text=True, vertical='center')
        ws.row_dimensions[1].height = 28
        for i, heading in enumerate(values[0], start=1):
            width = 42 if heading in ('Ideal intervention', 'Domain') else 25
            ws.column_dimensions[get_column_letter(i)].width = width
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def render():
    with st.container(key="road_safety_planner"):
        d=load()
        st.markdown('''<div class="rs-planner-band"><div class="rs-planner-kicker">GLOBAL ROAD SAFETY · GOVERNANCE TOOLS</div><h1>Road Safety Governance Action Planner</h1><p>195 countries · 17 institutional domains · 72 defined interventions · Private self-assessments</p></div>''', unsafe_allow_html=True)
        # A native st.info() inherits an opaque dark background in certain hosted themes.
        # Render this scoped, light callout instead; no global app styling is changed.
        st.markdown("""
        <div style="background-color:#edf6fa; border:1px solid #cbdfe8;
                    border-left:4px solid #188aa1; border-radius:8px;
                    padding:14px 18px; margin:10px 0 22px; color:#17324a;">
          <p style="margin:0; font-size:14px; line-height:1.6; color:#17324a;">
            <strong style="color:#12334a;">Connected research evidence · Private assessment draft.</strong>
            The planner uses the Atlas research as reference material. Your entries are saved only
            in this browser session; please export a JSON backup before leaving.
            Secure user accounts, cloud storage and publication approvals are not yet enabled.
          </p>
        </div>
        """, unsafe_allow_html=True)
        if 'planner_drafts' not in st.session_state:st.session_state.planner_drafts={}
        if 'planner_active' not in st.session_state:st.session_state.planner_active=None
        if 'planner_flash' in st.session_state:
            st.success(st.session_state.pop('planner_flash'))
        with st.expander('Create or import a country assessment',expanded=not bool(st.session_state.planner_active)):
            c1,c2=st.columns([2,1])
            country=c1.selectbox('Country',d['countries'],index=d['countries'].index('Canada'))
            scope=c2.selectbox('Assessment scope',['National','Federal / central','Province / state / territory','City / municipality'])
            jurisdiction=''
            if scope in ['Province / state / territory','City / municipality']:
                jurisdiction=st.text_input('Name of province, state, territory or municipality',placeholder='Specify the jurisdiction for this assessment')
            available=sorted({(r['profile_id'],r['jurisdiction'],r['coordinating_body']) for r in d['profiles'] if r['country']==country})
            labels={'': 'New self-assessment (no preselected mechanism)'}
            labels.update({pid: f'{name} | {jur or "national"}' for pid,jur,name in available})
            mechanism=st.selectbox('Optional research mechanism to consult',list(labels),format_func=lambda x:labels[x])
            if st.button('Create or open private draft',type='primary'):
                if scope in ['Province / state / territory','City / municipality'] and not jurisdiction.strip():
                    st.error('Please enter the province, state, territory or municipality.')
                else:
                    t=fresh(country,scope,jurisdiction.strip(),mechanism)
                    k=key_for(t)
                    if k not in st.session_state.planner_drafts:st.session_state.planner_drafts[k]=t
                    st.session_state.planner_active=k
                    st.rerun()
            up=st.file_uploader('Import a previously exported draft (.json)',type=['json'])
            if up and st.button('Import draft'):
                try:
                    incoming=json.load(up)
                    if incoming.get('schema')!='road-safety-planner-v1' or incoming.get('country') not in d['countries'] or not isinstance(incoming.get('interventions'),dict):
                        raise ValueError('Unsupported or invalid draft')
                    k=key_for(incoming);st.session_state.planner_drafts[k]=incoming;st.session_state.planner_active=k
                    st.session_state.planner_flash='Draft imported successfully.';st.rerun()
                except Exception as e:st.error(str(e))
        if not st.session_state.planner_active:return
        a=st.session_state.planner_drafts[st.session_state.planner_active]
        st.markdown(f"### {a['country']} · {a['scope']}" + (f" · {a['jurisdiction']}" if a['jurisdiction'] else ''))
        if a['mechanism']:
            match=[r for r in d['profiles'] if r['profile_id']==a['mechanism']]
            if match:st.caption('Linked research mechanism: '+match[0]['coordinating_body']+' (research reference, not government validation)')
        assessed=sum(rec.get('assessment','Not assessed')!='Not assessed' for rec in a['interventions'].values())
        institutions=sum(bool(rec.get('membership','Not assessed')!='Not assessed' or rec.get('functional','Not assessed')!='Not assessed') for rec in a['domains'].values())
        k1,k2,k3=st.columns(3)
        k1.metric('Interventions assessed',f'{assessed} / 72')
        k2.metric('Domains assessed',f'{institutions} / 17')
        k3.metric('Actions created',len(a['actions']))
        st.progress(assessed/72)
        sections=st.tabs(['Research evidence','17 domains','72 interventions','Actions','Reports & backup'])
        with sections[0]:
            st.markdown('#### Available source-linked research')
            if not a['mechanism']:
                st.info('No specific coordinating mechanism selected. You can still assess the full framework. To see published source findings, start another draft linked to a researched mechanism.')
            else:
                institutional=[r for r in d['institutional'] if r['profile_id']==a['mechanism'] and r.get('source_url')]
                findings=[r for r in d['findings'] if r['profile_id']==a['mechanism']]
                st.caption(f'{len(institutional)} institutional records with citations and {len(findings)} source-specific intervention findings. These are research leads, not endorsed answers.')
                for r in institutional:
                    with st.expander(r['domain']+' | '+r['institutional_relationship']):
                        st.write('**Institution:** '+(r['responsible_institution'] or 'Not established'))
                        st.write('**Formal membership:** '+r['formal_membership'])
                        st.write('**Functional responsibility:** '+r['functional_responsibility'])
                        st.write('**Reported implementation:** '+r['implementation_evidence'])
                        st.write('**Rationale:** '+r['classification_rationale'])
                        st.markdown('[Official source]('+r['source_url']+')')
                for r in findings:
                    with st.expander(r['matrix_id']+' | '+r['assessment']):
                        st.write(r['documented_action'])
                        st.write('**Responsible institution:** '+r['responsible_institution'])
                        st.write('**Stage:** '+r['activity_stage'])
                        st.write('**Limitation:** '+r['verification_boundary'])
                        if r['source_url']:st.markdown('[Source]('+r['source_url']+')')
        with sections[1]:
            domain=st.selectbox('Institutional domain',d['domains'])
            rec=a['domains'].get(domain,{})
            research=[r for r in d['institutional'] if r['profile_id']==a['mechanism'] and r['domain']==domain] if a['mechanism'] else []
            if research:
                r=research[0]
                st.caption('Research lead: '+r['institutional_relationship']+' | '+(r['responsible_institution'] or 'No named institution'))
                if r['source_url']:st.markdown('[Research source]('+r['source_url']+')')
            with st.form('domain_form'):
                membership=st.selectbox('Formal membership',MEMBERSHIPS,index=MEMBERSHIPS.index(rec.get('membership','Not assessed')))
                functional=st.selectbox('Documented functional responsibility',FUNCTIONS,index=FUNCTIONS.index(rec.get('functional','Not assessed')))
                institution=st.text_input('Responsible institution (name and jurisdiction)',value=rec.get('institution',''))
                source=st.text_input('Evidence URL or official document identifier',value=rec.get('source',''))
                notes=st.text_area('Assessment rationale and limitations',value=rec.get('notes',''))
                submitted=st.form_submit_button('Save institutional assessment')
            if submitted:
                a['domains'][domain]={'membership':membership,'functional':functional,'institution':institution,'source':source,'notes':notes}
                a['updated']=datetime.now(timezone.utc).isoformat(timespec='seconds')
                st.success('Saved in current session.')
        with sections[2]:
            pillar=st.selectbox('Filter by Safe System pillar', ['All pillars']+PILLARS)
            domain_filter=st.selectbox('Filter by institution', ['All domains']+d['domains'])
            valid=[r for r in d['checklist'] if (pillar=='All pillars' or r['pillar']==pillar) and (domain_filter=='All domains' or r['domain']==domain_filter)]
            req=st.selectbox('Checklist requirement',valid,format_func=lambda x:x['matrix_id']+' · '+x['ideal_intervention'])
            code=req['matrix_id'];rec=a['interventions'].get(code,{})
            st.markdown('**'+req['ideal_intervention']+'**')
            st.caption(req['domain']+' · '+req['pillar'])
            research=[r for r in d['findings'] if r['profile_id']==a['mechanism'] and r['matrix_id']==code] if a['mechanism'] else []
            if research:
                e=research[0]
                st.info('**Published research lead, not verified self-assessment:** '+e['assessment']+' | '+e['documented_action'])
                if e['source_url']:st.markdown('[Evidence link]('+e['source_url']+')')
            with st.form('intervention_form'):
                assessment=st.selectbox('Assessment finding',ASSESSMENTS,index=ASSESSMENTS.index(rec.get('assessment','Not assessed')))
                stage=st.selectbox('Implementation stage',STAGES,index=STAGES.index(rec.get('stage','Not verified')))
                institution=st.text_input('Accountable implementing institution',value=rec.get('institution',''))
                source=st.text_input('Official source URL or document identifier',value=rec.get('source',''))
                notes=st.text_area('Exact source provision, reasoning and unresolved gaps',value=rec.get('notes',''))
                submitted=st.form_submit_button('Save checklist entry')
            if submitted:
                if assessment in ['Fully aligned','Confirmed gap'] and not (source.strip() and notes.strip()):
                    st.error('A fully aligned or confirmed-gap conclusion requires a source and rationale.')
                elif assessment.startswith('Not applicable') and not notes.strip():
                    st.error('Please explain why the requirement is not applicable.')
                else:
                    set_cell(a,'interventions',code,'assessment',assessment)
                    a['interventions'][code].update({'stage':stage,'institution':institution,'source':source,'notes':notes})
                    st.success('Saved in current session. Assessment progress does not imply intervention completion.')
        with sections[3]:
            st.markdown('#### Action tracking')
            with st.form('new_action',clear_on_submit=True):
                req=st.selectbox('Related requirement',d['checklist'],format_func=lambda x:x['matrix_id']+' · '+x['ideal_intervention'])
                title=st.text_input('Action to take')
                owner=st.text_input('Accountable owner')
                due=st.date_input('Target date',value=None)
                priority=st.selectbox('Priority',['To be determined','High','Medium','Low'])
                new=st.form_submit_button('Add action')
            if new:
                if not title.strip():st.error('Enter an action description.')
                else:
                    a['actions'].append({'requirement':req['matrix_id'],'title':title,'owner':owner,'due':str(due or ''),'priority':priority,'status':'Not started','evidence':''})
                    st.success('Action added.')
            for i,x in enumerate(a['actions']):
                with st.expander(f"{i+1}. {x['title']} ({x['status']})"):
                    st.caption(f"Requirement {x['requirement']} | {x['priority']} | Due {x['due'] or 'unscheduled'}")
                    new_status=st.selectbox('Progress',TASK_STATUSES,index=TASK_STATUSES.index(x['status']),key=f'action_status_{i}')
                    ev=st.text_input('Completion evidence or source',value=x.get('evidence',''),key=f'action_evidence_{i}')
                    if st.button('Save task',key=f'action_save_{i}'):
                        if new_status=='Completed and verified' and not ev.strip():st.error('Add evidence before marking a task verified complete.')
                        else:x.update({'status':new_status,'evidence':ev});st.success('Task saved.')
        with sections[4]:
            st.warning('This is an **unapproved draft**. Word/Excel files are internal working reports, not validated government findings. Shared publishing is intentionally disabled until authentication, independent review and country-approver permissions exist.')
            name=''.join(ch if ch.isalnum() or ch in '-_' else '_' for ch in a['country'])
            st.download_button('Download draft backup (.json)',json.dumps(a,indent=2,ensure_ascii=False),file_name=name+'_draft.json',mime='application/json')
            st.download_button('Download Word executive report (.docx)',word_bytes(a,d),file_name=name+'_Gap_Analysis_DRAFT.docx',mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            try:
                content=excel_bytes(a,d)
                st.download_button('Download Excel action tracker (.xlsx)',content,file_name=name+'_Action_Tracker_DRAFT.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            except Exception as e:
                st.error('Excel export unavailable: '+str(e))
            st.button('Submit for shared publication (requires secure backend)',disabled=True)
