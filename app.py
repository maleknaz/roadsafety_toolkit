"""Global Road Safety dashboard, consolidated static HTML and research datasets."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import planner

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="Global Road Safety Atlas",page_icon="🚦",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
/* Only the outer Atlas navigation is styled here; embedded HTML pages stay untouched. */
header[data-testid="stHeader"]{height:0!important;visibility:hidden!important}
#MainMenu,footer[data-testid="stFooter"],[data-testid="stDecoration"]{display:none!important}
[data-testid="stMainBlockContainer"],section.main>div.block-container{max-width:none!important;padding:0!important}
[data-testid="stTabs"] [role="tablist"]{background:#0e2b48!important;padding:12px!important;gap:6px!important;flex-wrap:wrap!important;border-bottom:3px solid #09a7d5!important}
[data-testid="stTabs"] [role="tab"]{background:#21516f!important;color:#fff!important;-webkit-text-fill-color:#fff!important;border:1px solid #85aec3!important;border-radius:6px!important;padding:10px 14px!important;min-height:42px!important;font-size:13px!important;font-weight:700!important;opacity:1!important}
[data-testid="stTabs"] [role="tab"] *{color:inherit!important;-webkit-text-fill-color:inherit!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:#fff!important;color:#0e2b48!important;-webkit-text-fill-color:#0e2b48!important;border:2px solid #09a7d5!important}
[data-testid="stTabs"] [role="tabpanel"]{padding:0!important}
iframe{border:0!important}

/* PLANNER ONLY. Other six pages are separate HTML iframes and are not changed. */
.st-key-road_safety_planner{background:#f8fbfd!important;color:#17324a!important;padding:0 24px 36px!important;font-family:"Segoe UI",Arial,sans-serif!important}
.st-key-road_safety_planner [data-testid="stMarkdownContainer"],
.st-key-road_safety_planner [data-testid="stMarkdownContainer"] :is(p,li,strong,em),
.st-key-road_safety_planner [data-testid="stWidgetLabel"],
.st-key-road_safety_planner [data-testid="stWidgetLabel"] *,
.st-key-road_safety_planner [data-testid="stMetricLabel"] *,
.st-key-road_safety_planner [data-testid="stMetricValue"] *,
.st-key-road_safety_planner [data-testid="stCaptionContainer"] *,
.st-key-road_safety_planner label,
.st-key-road_safety_planner label *{color:#17324a!important;-webkit-text-fill-color:#17324a!important;opacity:1!important}
.st-key-road_safety_planner [data-testid="stCaptionContainer"] *,
.st-key-road_safety_planner [data-testid="stMetricLabel"] *{color:#607588!important;-webkit-text-fill-color:#607588!important}
.st-key-road_safety_planner [data-testid="stMarkdownContainer"] :is(h1,h2,h3,h4,h5,h6){color:#12334a!important;-webkit-text-fill-color:#12334a!important;letter-spacing:-.02em!important;font-family:"Segoe UI",Arial,sans-serif!important}
.st-key-road_safety_planner [data-testid="stHeading"] :is(h1,h2,h3,h4,h5,h6){color:#12334a!important;-webkit-text-fill-color:#12334a!important}
/* White/light surfaces, never dark panels in this workspace. */
.st-key-road_safety_planner [data-testid="stAlert"],
.st-key-road_safety_planner [data-testid="stNotification"],
.st-key-road_safety_planner [data-testid="stExpander"],
.st-key-road_safety_planner [data-testid="stFileUploader"],
.st-key-road_safety_planner [data-testid="stMetric"],
.st-key-road_safety_planner [data-testid="stForm"]{background:#ffffff!important;color:#17324a!important;border:1px solid #d8e4eb!important;border-radius:9px!important;box-shadow:none!important}
.st-key-road_safety_planner [data-testid="stAlert"]{background:#eef6fa!important;border-left:4px solid #168a9f!important;padding:12px 16px!important}
.st-key-road_safety_planner [data-testid="stAlert"] *,
.st-key-road_safety_planner [data-testid="stNotification"] *,
.st-key-road_safety_planner [data-testid="stExpander"] summary,
.st-key-road_safety_planner [data-testid="stExpander"] summary *,
.st-key-road_safety_planner [data-testid="stFileUploader"] *,
.st-key-road_safety_planner [data-testid="stMetric"] *{color:#17324a!important;-webkit-text-fill-color:#17324a!important;opacity:1!important}
.st-key-road_safety_planner [data-testid="stFileUploaderDropzone"],
.st-key-road_safety_planner [data-testid="stFileUploaderDropzone"] *{background:#f8fbfd!important;color:#17324a!important;-webkit-text-fill-color:#17324a!important}
.st-key-road_safety_planner [data-testid="stExpander"] details,
.st-key-road_safety_planner [data-testid="stExpander"] summary{background:#fff!important;color:#17324a!important}
.st-key-road_safety_planner [data-baseweb="select"],
.st-key-road_safety_planner [data-baseweb="select"] > div,
.st-key-road_safety_planner [data-baseweb="input"],
.st-key-road_safety_planner [data-baseweb="textarea"],
.st-key-road_safety_planner [data-testid="stDateInput"] input,
.st-key-road_safety_planner input,
.st-key-road_safety_planner textarea{background:#fff!important;color:#17324a!important;-webkit-text-fill-color:#17324a!important;border-color:#afc4d1!important}
.st-key-road_safety_planner [data-baseweb="select"] *,
.st-key-road_safety_planner input::placeholder,
.st-key-road_safety_planner textarea::placeholder{color:#35546b!important;-webkit-text-fill-color:#35546b!important}
.st-key-road_safety_planner :is(input,textarea):disabled{background:#f0f4f6!important;color:#7b8e9e!important;-webkit-text-fill-color:#7b8e9e!important}
.st-key-road_safety_planner [data-testid="stButton"] button,
.st-key-road_safety_planner [data-testid="stFormSubmitButton"] button,
.st-key-road_safety_planner [data-testid="stDownloadButton"] button,
.st-key-road_safety_planner [data-testid="stFileUploader"] button{background:#fff!important;color:#13506c!important;-webkit-text-fill-color:#13506c!important;border:1px solid #91b0c0!important;border-radius:7px!important;font-weight:650!important}
.st-key-road_safety_planner [data-testid="stButton"] button[kind="primary"],
.st-key-road_safety_planner [data-testid="stFormSubmitButton"] button[kind="primary"]{background:#e8f4f7!important;color:#123c54!important;-webkit-text-fill-color:#123c54!important;border-color:#8bbac7!important}
.st-key-road_safety_planner [data-testid="stButton"] button:hover,
.st-key-road_safety_planner [data-testid="stDownloadButton"] button:hover{background:#e9f4f8!important}
.st-key-road_safety_planner [data-testid="stProgress"]{margin:10px 0 16px!important}
/* Planner's second-level tabs are a light subnavigation, not another dark banner. */
.st-key-road_safety_planner [data-testid="stTabs"] [role="tablist"]{background:#eff5f8!important;padding:7px!important;border:1px solid #d8e4eb!important;border-bottom:2px solid #cbdde6!important;gap:5px!important;border-radius:8px 8px 0 0!important}
.st-key-road_safety_planner [data-testid="stTabs"] [role="tab"]{background:#fff!important;color:#284a60!important;-webkit-text-fill-color:#284a60!important;border:1px solid #cbdde6!important;border-radius:6px!important;padding:9px 13px!important;min-height:38px!important;font-size:13px!important}
.st-key-road_safety_planner [data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:#e1f1f5!important;color:#103b54!important;-webkit-text-fill-color:#103b54!important;border:1px solid #81b6c5!important;border-bottom:3px solid #0796ad!important}
.st-key-road_safety_planner [data-testid="stTabs"] [role="tabpanel"]{background:#fff!important;padding:16px 18px!important;border:1px solid #d8e4eb!important;border-top:0!important;border-radius:0 0 9px 9px!important}
/* Compact, editorial heading akin to the other UN-style Atlas pages. */
.st-key-road_safety_planner .rs-planner-band{margin:0 -24px 22px!important;padding:17px 28px!important;background:#fff!important;border-top:5px solid #078da0!important;border-bottom:1px solid #d8e4eb!important;color:#10334b!important}
.st-key-road_safety_planner .rs-planner-kicker{font-size:12px!important;font-weight:750!important;letter-spacing:.10em!important;color:#16647a!important;text-transform:uppercase!important}
.st-key-road_safety_planner .rs-planner-band h1{font-size:30px!important;font-weight:760!important;line-height:1.2!important;margin:8px 0 6px!important;color:#10334b!important}
.st-key-road_safety_planner .rs-planner-band p{margin:0!important;color:#607588!important;font-size:13px!important}
@media(max-width:720px){.st-key-road_safety_planner{padding:0 12px 22px!important}.st-key-road_safety_planner .rs-planner-band{margin:0 -12px 18px!important;padding:15px 16px!important}.st-key-road_safety_planner .rs-planner-band h1{font-size:25px!important}}
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
