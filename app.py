"""Global Road Safety dashboard, consolidated static HTML and research datasets."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import planner

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="Global Road Safety Atlas",page_icon="🚦",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
header[data-testid="stHeader"]{height:0!important;visibility:hidden!important}
#MainMenu,footer[data-testid="stFooter"],[data-testid="stDecoration"]{display:none!important}
[data-testid="stMainBlockContainer"],section.main>div.block-container{max-width:none!important;padding:0!important}
/* All Streamlit-native planner areas use a consistent light canvas. */
[data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"]{background:#f3f8fb!important;color:#17324a!important}
/* Strong contrast for native Streamlit headings, metrics, captions and form labels.
   The HTML research dashboards are isolated inside iframes and are unchanged. */
[data-testid="stHeading"] :is(h1,h2,h3,h4,h5,h6),
[data-testid="stMarkdownContainer"] :is(h1,h2,h3,h4,h5,h6),
[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"] *,
[data-testid="stMetricDelta"] *,
[data-testid="stWidgetLabel"] *,
[data-testid="stCaptionContainer"] *,
label[data-testid="stWidgetLabel"] *{
  color:#17324a!important;-webkit-text-fill-color:#17324a!important;opacity:1!important;
}
[data-testid="stMarkdownContainer"] :is(h1,h2,h3,h4,h5,h6){
  font-weight:750!important;line-height:1.25!important;
}
/* Keep body text readable on pale panels; avoid changing dark info banners. */
[data-testid="stMarkdownContainer"] > p,
[data-testid="stMarkdownContainer"] > div > p,
[data-testid="stMarkdownContainer"] > ul,
[data-testid="stMarkdownContainer"] > ol{
  color:#17324a!important;-webkit-text-fill-color:#17324a!important;
}
[data-testid="stExpander"]{border:1px solid #cbd9e4!important;background:#fff!important;border-radius:8px!important}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary *{color:#17324a!important;-webkit-text-fill-color:#17324a!important;opacity:1!important}
/* Clean white controls and readable input text in either user OS theme. */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input{
  background:#fff!important;color:#17324a!important;-webkit-text-fill-color:#17324a!important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder{
  color:#35536b!important;-webkit-text-fill-color:#35536b!important;
}
[data-testid="stMetric"]{background:#fff!important;border:1px solid #cfdae4!important;border-radius:10px!important;padding:12px 16px!important}
[data-testid="stProgress"]{margin-top:8px!important;margin-bottom:16px!important}
/* Native planner buttons, only; the top navigation has its own blue/white rule. */
[data-testid="stButton"] button[kind="primary"]{background:#155c7e!important;color:#fff!important;border-color:#155c7e!important}
[data-testid="stButton"] button[kind="secondary"]{background:#fff!important;color:#17324a!important;border:1px solid #8eaabd!important}

[data-testid="stTabs"] [role="tablist"]{background:#0e2b48!important;padding:12px!important;gap:6px!important;flex-wrap:wrap!important;border-bottom:3px solid #09a7d5!important}
[data-testid="stTabs"] [role="tab"]{background:#21516f!important;color:#fff!important;-webkit-text-fill-color:#fff!important;border:1px solid #85aec3!important;border-radius:6px!important;padding:10px 14px!important;min-height:42px!important;font-size:13px!important;font-weight:750!important;opacity:1!important;white-space:normal!important}
[data-testid="stTabs"] [role="tab"] *{color:#fff!important;-webkit-text-fill-color:#fff!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:#fff!important;color:#0e2b48!important;-webkit-text-fill-color:#0e2b48!important;border:2px solid #09a7d5!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] *{color:#0e2b48!important;-webkit-text-fill-color:#0e2b48!important}
[data-testid="stTabs"] [role="tab"]:focus-visible{outline:3px solid #f0c766!important}
[data-testid="stTabs"] [role="tabpanel"]{padding:0!important}
iframe{border:0!important}
</style>""",unsafe_allow_html=True)

def show(filename,height=1550):
    path=ROOT/filename
    if not path.is_file():st.error(f"Missing: {filename}");return
    components.html(path.read_text(encoding="utf-8"),height=height,scrolling=True)

# The checklist is the final tab. Research datasets are not exposed for download.
labels=[
    "Start here",
    "Atlas",
    "Taskforces",
    "Existing documents",
    "Bodies & strategies",
    "Country case studies",
    "Checklists for your taskforce",
]
files=[
    "Dashboard_Overview.html",
    "road_safety_atlas.html",
    "who_has_task_forces.html",
    "Existing_road_safety_documents.html",
    "Bodies_Their_Road_Safety_Strategies.html",
    "Case_Studies.html",
    "Checklists_for_Your_Task_Force.html",
]

tabs=st.tabs(labels)
for label, filename, tab in zip(labels, files, tabs):
    with tab:
        if filename == "Checklists_for_Your_Task_Force.html":
            planner.render()
        else:
            show(filename, 1500 if filename == "Dashboard_Overview.html" else 2000)
