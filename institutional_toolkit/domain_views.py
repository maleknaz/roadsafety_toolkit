"""Original, browser-native institutional domain cards and source tables.

One HTML grid is embedded by Streamlit, not 17 nested st.expander widgets.
Country and pairwise views share the same 4/3/2/1-column responsive layout.
Only source-linked research evidence may be shown as source-linked.
"""
from __future__ import annotations
from html import escape
from . import evidence as ev

CSS = r"""<style>
:root{color-scheme:light}*{box-sizing:border-box}
html,body{margin:0;background:#f7fafb;color:#16364c;font-family:Inter,'Segoe UI',Arial,sans-serif}
.domain-toolbar{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:2px 2px 15px;flex-wrap:wrap}
.domain-toolbar strong{font-size:17px;color:#16364c;font-weight:800}
.domain-toolbar span{font-size:12px;color:#607583}
.domain-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;padding:0 2px 12px}
.domain-card{position:relative;display:flex;flex-direction:column;gap:9px;min-height:141px;width:100%;padding:15px 16px 13px;text-align:left;background:#fff;border:1px solid #d5e4e7;border-radius:11px;color:#16384f;box-shadow:0 3px 14px rgba(9,45,63,.04);cursor:pointer;transition:transform .12s,border .12s,box-shadow .12s}
.domain-card:hover{transform:translateY(-2px);border-color:#0c8f99;box-shadow:0 9px 22px rgba(11,66,76,.09)}
.domain-card[aria-pressed=true]{background:#edf8f7;border:2px solid #078b91;padding:14px 15px 12px;box-shadow:inset 0 0 0 1px #c6e7e3}
.domain-card:focus-visible{outline:3px solid #08778e;outline-offset:2px}
.card-top{display:flex;align-items:center;justify-content:space-between;gap:8px}
.card-index{font-size:11px;color:#07858a;font-weight:850;letter-spacing:.13em}
.card-mark{width:25px;height:25px;display:grid;place-items:center;border-radius:50%;background:#e7f3f3;color:#0d7c82;font-size:13px;font-weight:900}
.card-heading{font-size:14px;font-weight:790;line-height:1.35;overflow-wrap:anywhere;flex:1}
.card-meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:10px;color:#527184;line-height:1.25}
.card-meta em{font-style:normal;border-radius:4px;padding:4px 6px;background:#f0f4f6;color:#577083;font-weight:740}
.card-meta em.linked{background:#e1f4f0;color:#096d66}
.card-meta em.missing{background:#f0f4f6;color:#5b6e7d}
.view-hint{font-size:11px;color:#087a83;font-weight:760;padding-top:3px}
#domain-detail{border:1px solid #cfe2e4;background:#fff;border-radius:12px;padding:22px 22px 18px;margin:8px 2px 18px;scroll-margin-top:16px;box-shadow:0 5px 22px rgba(8,52,63,.045)}
#domain-detail h3{font-size:22px;color:#13344a;font-weight:830;line-height:1.2;margin:0 0 7px}
.detail-sub{color:#54717d;font-size:12px;margin:0 0 16px;line-height:1.5}
.table-scroll{overflow-x:auto;border:1px solid #d9e5e9;border-radius:9px}
table{border-collapse:collapse;width:100%;min-width:560px;table-layout:auto;color:#213d4f;font-size:12.5px}
thead th{background:#eaf4f6;color:#12435b;font-weight:800;text-align:left;padding:12px 14px;border-bottom:1px solid #cfdfdf}
tbody th{background:#f7fafb;width:21%;font-weight:760;color:#284b60;text-align:left}
td,tbody th{padding:11px 13px;vertical-align:top;border-bottom:1px solid #e0e9eb;overflow-wrap:anywhere}
tr:last-child td,tr:last-child th{border-bottom:0}
a{color:#027c8a;text-decoration:underline;text-underline-offset:2px}
.evidence-note{font-size:12px;color:#566f79;line-height:1.5;margin:12px 0 2px;border-left:3px solid #0a9a97;padding-left:11px}
.empty-note{background:#f4f8fa;color:#456577;border:1px solid #dae6e9;border-radius:7px;padding:15px;font-size:13px;line-height:1.5}
@media(max-width:1100px){.domain-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:790px){.domain-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.domain-card{min-height:132px}}
@media(max-width:480px){.domain-grid{grid-template-columns:1fr}.domain-card{min-height:100px;gap:6px}#domain-detail{padding:16px 12px}}
</style>"""

JS = r"""<script>
(function(){
  'use strict';
  const cards=[...document.querySelectorAll('button.domain-card')];
  const detail=document.getElementById('domain-detail');
  function resize(){
    try{window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:setFrameHeight',height:Math.ceil(document.documentElement.scrollHeight+12)},'*');}catch(_e){}
  }
  function select(n,scroll){
    const template=document.getElementById('domain-template-'+n);
    if(!template)return;
    detail.replaceChildren(template.content.cloneNode(true));
    cards.forEach(card=>{
      const active=card.dataset.domainIndex===String(n);
      card.setAttribute('aria-pressed',active?'true':'false');
      card.querySelector('.view-hint').textContent=active?'Selected · Details below':'View evidence';
    });
    resize();
    if(scroll){detail.scrollIntoView({behavior:'smooth',block:'nearest'});}
  }
  cards.forEach(card=>card.addEventListener('click',()=>select(card.dataset.domainIndex,true)));
  select(FIRST_DOMAIN,false);
  if('ResizeObserver' in window){new ResizeObserver(resize).observe(document.body)}
  window.addEventListener('resize',resize);
  resize();
})();
</script>"""


def _text(value: object, default: str = 'Not established in reviewed records') -> str:
    return escape(str(value).strip()) if value is not None and str(value).strip() else escape(default)


def _link(raw: str) -> str:
    u=ev.url(raw)
    return ('<a href="'+escape(u,quote=True)+'" target="_blank" rel="noopener noreferrer">Open source ↗</a>') if u else 'No linked source'


def _frame(cards: list[str], details: list[str], selected: int, subtitle: str) -> str:
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'+CSS+'</head>'
            '<body><div class="domain-toolbar"><strong>Explore all '+str(len(cards))+' institutional domains</strong>'
            '<span>'+escape(subtitle)+'</span></div>'
            '<div class="domain-grid" role="group" aria-label="Select a road safety institutional domain">'
            +''.join(cards)+'</div><section id="domain-detail" role="region" aria-live="polite"></section>'
            +''.join(details)+JS.replace('FIRST_DOMAIN',str(selected))+'</body></html>')


def _button(i: int, label: str, markers: list[tuple[str, bool]], selected: int) -> str:
    badges=''.join('<em class="'+('linked' if active else 'missing')+'">'+escape(n)+' '+('· linked' if active else '· unverified')+'</em>' for n,active in markers)
    return ('<button type="button" class="domain-card" aria-pressed="'+('true' if i==selected else 'false')+'" '
            'aria-controls="domain-detail" data-domain-index="'+str(i)+'">'
            '<div class="card-top"><span class="card-index">'+str(i+1).zfill(2)+'</span>'
            '<span class="card-mark" aria-hidden="true">+</span></div>'
            '<span class="card-heading">'+_text(label)+'</span>'
            '<span class="card-meta">'+badges+'</span>'
            '<span class="view-hint">'+('Selected · Details below' if i==selected else 'View evidence')+'</span></button>')


def comparison_view(rows: list[dict], first: str, second: str) -> str:
    """Four-column cards, each opens a real side-by-side evidence table."""
    selected=next((i for i,r in enumerate(rows) if ev.url(r[first].get('source_url','')) or ev.url(r[second].get('source_url',''))),0)
    cards=[];details=[]
    fields=[('Evidence status','evidence'),('Coordinating institution','responsible_institution'),
            ('Institutional responsibility','functional_responsibility'),('Implementation evidence','implementation_evidence'),
            ('Research qualification','rationale')]
    for i,r in enumerate(rows):
        a,b=r[first],r[second]
        cards.append(_button(i,r['domain'],[(first,bool(ev.url(a.get('source_url','')))),(second,bool(ev.url(b.get('source_url',''))))],selected))
        table=''.join('<tr><th scope="row">'+escape(lab)+'</th><td>'+_text(a.get(key))+'</td><td>'+_text(b.get(key))+'</td></tr>' for lab,key in fields)
        table+='<tr><th scope="row">Supporting source</th><td>'+_link(a.get('source_url',''))+'</td><td>'+_link(b.get('source_url',''))+'</td></tr>'
        details.append('<template id="domain-template-'+str(i)+'"><h3>'+_text(r['domain'])+'</h3>'
                       '<p class="detail-sub">Documented institutional arrangements for '+escape(first)+' and '+escape(second)+'.</p>'
                       '<div class="table-scroll"><table><thead><tr><th>Evidence field</th><th>'+escape(first)+'</th><th>'+escape(second)+'</th></tr></thead>'
                       '<tbody>'+table+'</tbody></table></div><p class="evidence-note">Linked research sources indicate documentation coverage, not institutional effectiveness. Unlinked records do not establish absence.</p></template>')
    return _frame(cards,details,selected,'Select a card to see a side-by-side comparison')


def country_view(data: dict, country: str) -> str:
    """The same four-column grid for one country, replacing 17 vertical expanders.

    Each selected domain reveals ALL reviewed institutional source records within
    that domain (not an arbitrary first record). Formal membership is omitted.
    """
    ctx=ev.country_context(data,country)
    records=ctx['institutional']
    by_domain={d:[r for r in records if r.get('domain')==d] for d in data['domains']}
    selected=next((i for i,d in enumerate(data['domains']) if any(ev.url(r.get('source_url','')) for r in by_domain[d])),0)
    cards=[];details=[]
    for i,d in enumerate(data['domains']):
        rs=by_domain[d];linked=[r for r in rs if ev.url(r.get('source_url',''))]
        cards.append(_button(i,d,[(str(len(linked))+' source'+('s' if len(linked)!=1 else ''),bool(linked))],selected))
        if linked:
            table=''.join('<tr><td>'+_text(r.get('responsible_institution'),'Not specified')+'</td>'
                          '<td>'+_text(r.get('functional_responsibility'),'Not documented')+'</td>'
                          '<td>'+_text(r.get('implementation_evidence'),'Not verified')+'</td>'
                          '<td>'+_link(r.get('source_url',''))+'</td></tr>' for r in linked)
            content='<div class="table-scroll"><table><thead><tr><th>Institution</th><th>Role</th><th>Implementation evidence</th><th>Source</th></tr></thead><tbody>'+table+'</tbody></table></div>'
        else:
            content='<div class="empty-note">No source-linked institutional record was identified for this domain in the reviewed subset. This is not evidence that an institution or function is absent.</div>'
        details.append('<template id="domain-template-'+str(i)+'"><h3>'+_text(d)+'</h3>'
                       '<p class="detail-sub">'+escape(country)+' · '+str(len(linked))+' linked research record(s) in this institutional domain.</p>'
                       +content+'<p class="evidence-note">Displayed records are research leads; verify current legal mandates and operational status with official sources.</p></template>')
    return _frame(cards,details,selected,'Choose a domain to inspect roles and sources')
