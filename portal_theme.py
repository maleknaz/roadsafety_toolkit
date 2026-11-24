"""Shared visual direction for the Road Safety Toolkit.

Inspired by the UN Road Safety Lab's editorial information architecture:
white navigation, topic-led cards, calm blue/teal accents and accessible filters.
No Lab trademarks, logos, photographic assets or website code are reused.
"""

PORTAL_CSS = r"""
:root{color-scheme:light;--rs-navy:#102f48;--rs-ink:#19384e;--rs-muted:#5e7281;
  --rs-teal:#087f8f;--rs-cyan:#d9f1f2;--rs-border:#dce6e9;--rs-bg:#f7fafb;}
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{
  background:#f7fafb!important;color:#19384e!important;}
/* Clear, lab-like primary navigation. Streamlit still manages every tab. */
[data-testid="stTabs"] > div > [role="tablist"],
[data-testid="stTabs"] [role="tablist"]{
  background:#ffffff!important;padding:9px clamp(12px,2.4vw,42px)!important;
  border-top:4px solid #078a99!important;border-bottom:1px solid #d9e4e8!important;
  gap:2px!important;display:flex!important;flex-wrap:nowrap!important;
  overflow-x:auto!important;overflow-y:hidden!important;scrollbar-width:thin!important;
  width:100%!important;}
[data-testid="stTabs"] [role="tablist"] [role="tab"]{
  background:#fff!important;white-space:nowrap!important;min-height:48px!important;
  border:0!important;border-bottom:3px solid transparent!important;
  border-radius:0!important;padding:11px 17px!important;
  font-family:Arial,'Segoe UI',sans-serif!important;font-size:13px!important;
  font-weight:700!important;letter-spacing:.01em!important;
  color:#365167!important;-webkit-text-fill-color:#365167!important;
  transition:color .15s,background .15s,border-color .15s!important;}
[data-testid="stTabs"] [role="tablist"] [role="tab"]:hover{
  background:#f0f7f8!important;color:#0b5668!important;-webkit-text-fill-color:#0b5668!important;}
[data-testid="stTabs"] [role="tablist"] [role="tab"][aria-selected="true"]{
  background:#edf7f7!important;color:#0a5969!important;-webkit-text-fill-color:#0a5969!important;
  border:0!important;border-bottom:3px solid #098996!important;}
[data-testid="stTabs"] [role="tablist"] [role="tab"] *{color:inherit!important;-webkit-text-fill-color:inherit!important;}
[data-testid="stTabs"] > div > [role="tabpanel"]{padding:0!important;}
/* Streamlit Toolkit (not the six independently rendered HTML research pages). */
.st-key-road_safety_toolkit{background:#f7fafb!important;}
.st-key-road_safety_toolkit [data-testid="stVerticalBlock"]{gap:1.0rem;}
.st-key-road_safety_toolkit [data-testid="stMetric"]{
  border:1px solid #dce6e9!important;border-radius:14px!important;
  box-shadow:0 8px 28px rgba(9,51,67,.035)!important;padding:13px 17px!important;}
.st-key-road_safety_toolkit [data-testid="stExpander"]{
  border:1px solid #dde6e9!important;border-radius:11px!important;
  box-shadow:0 1px 4px rgba(19,63,79,.025)!important;}
.st-key-road_safety_toolkit [data-testid="stExpander"]:hover{border-color:#abd3d7!important;}
.st-key-road_safety_toolkit [data-testid="stDataFrame"]{
  border:1px solid #dce6e9!important;border-radius:12px!important;overflow:hidden!important;}
.st-key-road_safety_toolkit [data-testid="stButton"] button,
.st-key-road_safety_toolkit [data-testid="stDownloadButton"] button,
.st-key-road_safety_toolkit [data-testid="stFormSubmitButton"] button{
  border-radius:8px!important;min-height:41px!important;background:#fff!important;
  color:#075668!important;-webkit-text-fill-color:#075668!important;
  border:1px solid #9abfc6!important;font-weight:700!important;
  transition:background .15s,border-color .15s!important;}
.st-key-road_safety_toolkit [data-testid="stButton"] button:hover,
.st-key-road_safety_toolkit [data-testid="stDownloadButton"] button:hover{
  background:#e5f5f5!important;border-color:#087f8f!important;}
.st-key-road_safety_toolkit [data-testid="stFormSubmitButton"] button[kind="primary"],
.st-key-road_safety_toolkit [data-testid="stButton"] button[kind="primary"]{
  color:#fff!important;-webkit-text-fill-color:#fff!important;
  background:#087c8d!important;border-color:#087c8d!important;}
.st-key-road_safety_toolkit [data-testid="stFormSubmitButton"] button[kind="primary"] *,
.st-key-road_safety_toolkit [data-testid="stButton"] button[kind="primary"] *{
  color:#fff!important;-webkit-text-fill-color:#fff!important;}
.st-key-road_safety_toolkit [data-testid="stForm"]{border-radius:14px!important;padding:22px!important;}
.st-key-road_safety_toolkit [data-testid="stMarkdownContainer"] a{color:#087083!important;}
.st-key-road_safety_toolkit [data-testid="stMarkdownContainer"] h2{
  font-size:clamp(21px,2vw,27px)!important;letter-spacing:-.025em!important;}
.st-key-road_safety_toolkit [data-testid="stMarkdownContainer"] h3{
  font-size:19px!important;letter-spacing:-.015em!important;}
/* Horizontal mode selector looks like an accessible set of Lab-style category chips. */
.st-key-road_safety_toolkit [data-testid="stRadio"] > div[role="radiogroup"]{
  display:flex;flex-wrap:wrap;gap:8px!important;}
.st-key-road_safety_toolkit [data-testid="stRadio"] > div[role="radiogroup"] label{
  background:#fff!important;border:1px solid #d2e2e5!important;border-radius:99px!important;
  padding:9px 13px!important;margin:0!important;}
.st-key-road_safety_toolkit [data-testid="stRadio"] > div[role="radiogroup"] label:has(input:checked){
  background:#e7f6f6!important;border-color:#07919e!important;}
.st-key-road_safety_toolkit .rs-toolkit-context-status{
  border:1px solid #d4e9e9!important;border-radius:11px!important;background:#eef8f8!important;
  padding:14px 17px!important;margin:6px 0 12px!important;color:#21485b!important;}
.st-key-road_safety_toolkit .rs-toolkit-context-status strong{color:#103d50!important;}
@media(max-width:750px){
  [data-testid="stTabs"] [role="tablist"]{padding:7px 8px!important;}
  [data-testid="stTabs"] [role="tablist"] [role="tab"]{padding:9px 12px!important;font-size:12px!important;}
  .st-key-road_safety_toolkit [data-testid="stForm"]{padding:13px!important;}
}
/* Focus indicators and contrast remain visible on the deliberately light UI. */
:where(button,[role="tab"],input,select,textarea):focus-visible{
  outline:3px solid #168c9d!important;outline-offset:2px!important;}
"""

# CSS embedded into each standalone source HTML page so the portal appearance
# survives when a page is exported and opened without the Streamlit wrapper.
EMBEDDED_CSS = r"""
<style id="rs-lab-inspired-theme">
:root{color-scheme:light;--rs-lab-ink:#193a50;--rs-lab-muted:#5b7382;
  --rs-lab-teal:#087d8d;--rs-lab-bg:#f7fafb;--rs-lab-line:#dce7e9;}
html,body{background:#f7fafb!important;color:#193a50;}
body{font-family:Arial,'Segoe UI',sans-serif!important;}
body>.grs-fixed-banner,body>.grs-consistent-masthead{
  background:#fff!important;border-bottom:1px solid #dbe7e8!important;
  box-shadow:0 2px 14px rgba(13,54,69,.025)!important;}
body>.grs-fixed-banner .grs-band,body>.grs-consistent-masthead .grs-stripe{
  height:4px!important;background:linear-gradient(90deg,#078e9a 0 72%,#e3b24b 72% 79%,#143c58 79% 100%)!important;}
body>.grs-fixed-banner .grs-label,body>.grs-consistent-masthead .grs-brand{
  color:#153b50!important;letter-spacing:.075em!important;}
body>.grs-fixed-banner .grs-mark,body>.grs-consistent-masthead .grs-mark{
  background:#0b8798!important;}
body>header.hero{
  position:relative!important;isolation:isolate!important;box-sizing:border-box!important;
  min-height:320px!important;max-height:320px!important;height:320px!important;
  overflow:hidden!important;border-bottom:0!important;
  background:linear-gradient(115deg,#0e304b 0%,#125173 70%,#0b7780 140%)!important;}
body>header.hero::after{
  content:"";position:absolute;pointer-events:none;z-index:0;
  width:620px;height:620px;right:-180px;top:-250px;
  border:1px solid rgba(222,244,246,.14);border-radius:50%;
  box-shadow:0 0 0 70px rgba(211,241,242,.025),0 0 0 135px rgba(211,241,242,.025),0 0 0 200px rgba(211,241,242,.015);}
body>header.hero>*{position:relative;z-index:1;}
body>header.hero h1,body>header.hero h1 strong{
  font-family:Arial,'Segoe UI',sans-serif!important;font-weight:800!important;
  font-size:clamp(27px,3vw,39px)!important;letter-spacing:-.03em!important;
  line-height:1.22!important;color:#fff!important;-webkit-text-fill-color:#fff!important;
  max-width:1140px!important;}
body>header.hero h1 em,body>header.hero h1 .title-accent{
  font-style:normal!important;color:#8ce2df!important;-webkit-text-fill-color:#8ce2df!important;}
body>header.hero p,body>header.hero .lede{
  color:#ebf7f7!important;-webkit-text-fill-color:#ebf7f7!important;
  font-size:15px!important;line-height:1.58!important;max-width:840px!important;}
body>header.hero .eyebrow,body>header.hero .section-label{
  color:#a8ece7!important;-webkit-text-fill-color:#a8ece7!important;}
body .panel,body .card,body .kpi,body .stat-card,body .metric-card{
  border-color:#dce7e9!important;box-shadow:0 6px 24px rgba(10,46,65,.035)!important;}
body .panel,body .card{border-radius:13px!important;}
body .panel h2,body main h2{letter-spacing:-.025em!important;}
body a{color:#08758a;}
body :is(button,select,input):focus-visible,
body :is(a,[role="button"]):focus-visible{
  outline:3px solid #0799a5!important;outline-offset:2px!important;}
@media(max-width:740px){
 body>header.hero{height:auto!important;min-height:300px!important;max-height:none!important;}
 body>header.hero h1{font-size:clamp(24px,7vw,32px)!important;}
 body>.grs-fixed-banner .grs-label,body>.grs-consistent-masthead .grs-brand{letter-spacing:.025em!important;}
}
</style>
"""
