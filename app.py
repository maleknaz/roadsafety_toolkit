"""Road Safety Toolkit, consolidated static HTML and institutional analysis."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
# Import Toolkit screens when their tabs render, not at process startup.
# This keeps all public research pages working if a GitHub upload updates
# app.py before the institutional_toolkit package has been fully updated.
def render_institutional_toolkit():
    try:
        from institutional_toolkit import render as handler
        return handler()
    except ImportError as exc:
        st.error("The Institutional Toolkit files are missing or out of sync. Upload the complete institutional_toolkit folder from the latest release.")
        st.exception(exc)


def render_intelligence_agent():
    try:
        from institutional_toolkit import render_agent as handler
    except ImportError:
        # Backward compatibility: the previous package __init__.py exposed
        # only `render`, even if ui.py had already been upgraded.
        try:
            from institutional_toolkit.ui import render_agent as handler
        except ImportError as exc:
            st.error("Ask the Evidence needs the updated institutional_toolkit/ui.py and __init__.py files. Upload the complete institutional_toolkit folder.")
            st.exception(exc)
            return
    try:
        return handler()
    except ImportError as exc:
        st.error("Ask the Evidence could not load its dependencies. Check the complete institutional_toolkit folder and requirements.txt.")
        st.exception(exc)

from portal_theme import PORTAL_CSS

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="Road Safety Toolkit",page_icon="🚦",layout="wide",initial_sidebar_state="collapsed")
st.markdown("""<style>
/* The native Streamlit multipage top navigation stays visible. Embedded HTML pages remain independent. */
header[data-testid="stHeader"]{visibility:visible!important;height:auto!important;min-height:64px!important;background:#ffffff!important;border-top:4px solid #3E8EDE!important;border-bottom:1px solid #d9e4e8!important;box-shadow:0 2px 12px rgba(17,54,79,.04)!important}
#MainMenu,footer[data-testid="stFooter"],[data-testid="stDecoration"]{display:none!important}
[data-testid="stMainBlockContainer"],section.main>div.block-container{max-width:none!important;padding:0!important}
[data-testid="stTabs"] [role="tablist"]{background:#eef5f8!important;padding:12px!important;gap:6px!important;flex-wrap:wrap!important;border-bottom:3px solid #1593a9!important}
[data-testid="stTabs"] [role="tab"]{background:#ffffff!important;color:#17324a!important;-webkit-text-fill-color:#17324a!important;border:1px solid #c6d8e2!important;border-radius:6px!important;padding:10px 14px!important;min-height:42px!important;font-size:13px!important;font-weight:700!important;opacity:1!important}
[data-testid="stTabs"] [role="tab"] *{color:inherit!important;-webkit-text-fill-color:inherit!important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:#e1f1f5!important;color:#103b54!important;-webkit-text-fill-color:#103b54!important;border:2px solid #1593a9!important}
[data-testid="stTabs"] [role="tabpanel"]{padding:0!important}
iframe{border:0!important}

/* PLANNER ONLY. Other six pages are separate HTML iframes and are not changed. */
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab){background:#f8fbfd!important;color:#17324a!important;padding:0 24px 36px!important;font-family:"Segoe UI",Arial,sans-serif!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stMarkdownContainer"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stMarkdownContainer"] :is(p,li,strong,em),
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stWidgetLabel"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stWidgetLabel"] *,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stMetricLabel"] *,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stMetricValue"] *,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stCaptionContainer"] *,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) label,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) label *{color:#17324a!important;-webkit-text-fill-color:#17324a!important;opacity:1!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stCaptionContainer"] *,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stMetricLabel"] *{color:#607588!important;-webkit-text-fill-color:#607588!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stMarkdownContainer"] :is(h1,h2,h3,h4,h5,h6){color:#12334a!important;-webkit-text-fill-color:#12334a!important;letter-spacing:-.02em!important;font-family:"Segoe UI",Arial,sans-serif!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stHeading"] :is(h1,h2,h3,h4,h5,h6){color:#12334a!important;-webkit-text-fill-color:#12334a!important}
/* White/light surfaces, never dark panels in this workspace. */
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stAlert"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stNotification"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stExpander"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stFileUploader"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stMetric"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stForm"]{background:#ffffff!important;color:#17324a!important;border:1px solid #d8e4eb!important;border-radius:9px!important;box-shadow:none!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stAlert"]{background:#eef6fa!important;border-left:4px solid #168a9f!important;padding:12px 16px!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stAlert"] *,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stNotification"] *,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stExpander"] summary,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stExpander"] summary *,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stFileUploader"] *,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stMetric"] *{color:#17324a!important;-webkit-text-fill-color:#17324a!important;opacity:1!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stFileUploaderDropzone"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stFileUploaderDropzone"] *{background:#f8fbfd!important;color:#17324a!important;-webkit-text-fill-color:#17324a!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stExpander"] details,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stExpander"] summary{background:#fff!important;color:#17324a!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-baseweb="select"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-baseweb="select"] > div,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-baseweb="input"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-baseweb="textarea"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stDateInput"] input,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) input,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) textarea{background:#fff!important;color:#17324a!important;-webkit-text-fill-color:#17324a!important;border-color:#afc4d1!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-baseweb="select"] *,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) input::placeholder,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) textarea::placeholder{color:#35546b!important;-webkit-text-fill-color:#35546b!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) :is(input,textarea):disabled{background:#f0f4f6!important;color:#7b8e9e!important;-webkit-text-fill-color:#7b8e9e!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stButton"] button,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stFormSubmitButton"] button,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stDownloadButton"] button,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stFileUploader"] button{background:#fff!important;color:#13506c!important;-webkit-text-fill-color:#13506c!important;border:1px solid #91b0c0!important;border-radius:7px!important;font-weight:650!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stButton"] button[kind="primary"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stFormSubmitButton"] button[kind="primary"]{background:#e8f4f7!important;color:#123c54!important;-webkit-text-fill-color:#123c54!important;border-color:#8bbac7!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stButton"] button:hover,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stDownloadButton"] button:hover{background:#e9f4f8!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stProgress"]{margin:10px 0 16px!important}
/* Planner's second-level tabs are a light subnavigation, not another dark banner. */
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stTabs"] [role="tablist"]{background:#eff5f8!important;padding:7px!important;border:1px solid #d8e4eb!important;border-bottom:2px solid #cbdde6!important;gap:5px!important;border-radius:8px 8px 0 0!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stTabs"] [role="tab"]{background:#fff!important;color:#284a60!important;-webkit-text-fill-color:#284a60!important;border:1px solid #cbdde6!important;border-radius:6px!important;padding:9px 13px!important;min-height:38px!important;font-size:13px!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:#e1f1f5!important;color:#103b54!important;-webkit-text-fill-color:#103b54!important;border:1px solid #81b6c5!important;border-bottom:3px solid #0796ad!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stTabs"] [role="tabpanel"]{background:#fff!important;padding:16px 18px!important;border:1px solid #d8e4eb!important;border-top:0!important;border-radius:0 0 9px 9px!important}
/* HIGH-CONTRAST LIGHT THEME: Toolkit and nested original planner only.
   Streamlit's stAlert background is NOT sufficient. Some Streamlit versions
   render a second dark [data-baseweb=notification] inside its frame. Keep both
   the outer notification and every inner layer light, and force readable ink. */
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab){
  background-color:#f8fbfd!important;
  color:#17324a!important;
  color-scheme:light!important;
}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) :is([data-testid="stAlert"],[data-baseweb="notification"],[data-testid="stNotification"],[role="alert"]),
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) :is([data-testid="stAlert"],[data-baseweb="notification"],[data-testid="stNotification"],[role="alert"]) > div,
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) :is([data-testid="stAlert"],[data-baseweb="notification"],[data-testid="stNotification"],[role="alert"]) [data-testid="stMarkdownContainer"]{
  background-color:#eef6fa!important;
  color:#17324a!important;
  -webkit-text-fill-color:#17324a!important;
  border-color:#bdd4df!important;
  opacity:1!important;
}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) :is([data-testid="stAlert"],[data-baseweb="notification"],[data-testid="stNotification"],[role="alert"]) :is(div,span,p,li,strong,em,svg){
  color:#17324a!important;
  -webkit-text-fill-color:#17324a!important;
  opacity:1!important;
}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) .rs-light-notice{
  color:#17324a!important;
  background-color:#edf7fb!important;
  -webkit-text-fill-color:#17324a!important;
  opacity:1!important;
}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) :is([data-testid="stExpanderDetails"],[data-testid="stExpander"],details,details > div,[data-testid="stForm"],[data-testid="stMetric"],[data-testid="stDataFrame"],[data-testid="stDataEditor"]){
  background-color:#fff!important;
  color:#17324a!important;
  color-scheme:light!important;
}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stExpander"] :is(summary,summary > div,summary > div > div){
  background-color:#fff!important;
  color:#17324a!important;
  -webkit-text-fill-color:#17324a!important;
}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stCaptionContainer"],
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) [data-testid="stCaptionContainer"] *{
  color:#4d6478!important;
  -webkit-text-fill-color:#4d6478!important;
  opacity:1!important;
}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) :is([data-testid="stRadio"],[data-testid="stCheckbox"],[data-testid="stSelectbox"],[data-testid="stTextInput"],[data-testid="stTextArea"]){
  color:#17324a!important;
  color-scheme:light!important;
}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) :is([data-testid="stRadio"],[data-testid="stCheckbox"]) label *{
  color:#17324a!important;
  -webkit-text-fill-color:#17324a!important;
}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) :is([data-testid="stButton"],[data-testid="stDownloadButton"],[data-testid="stFormSubmitButton"]) button *{
  color:#13506c!important;
  -webkit-text-fill-color:#13506c!important;
  opacity:1!important;
}

/* Compact, editorial heading akin to the other UN-style Atlas pages. */
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) .rs-planner-band{margin:0 -24px 22px!important;padding:17px 28px!important;background:#fff!important;border-top:5px solid #078da0!important;border-bottom:1px solid #d8e4eb!important;color:#10334b!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) .rs-planner-kicker{font-size:12px!important;font-weight:750!important;letter-spacing:.10em!important;color:#16647a!important;text-transform:uppercase!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) .rs-planner-band h1{font-size:30px!important;font-weight:760!important;line-height:1.2!important;margin:8px 0 6px!important;color:#10334b!important}
:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) .rs-planner-band p{margin:0!important;color:#607588!important;font-size:13px!important}
@media(max-width:720px){:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab){padding:0 12px 22px!important}:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) .rs-planner-band{margin:0 -12px 18px!important;padding:15px 16px!important}:is(.st-key-road_safety_planner,.st-key-road_safety_toolkit,.st-key-road_safety_agent_tab) .rs-planner-band h1{font-size:25px!important}}
</style>""",unsafe_allow_html=True)

# Editorial Lab-inspired app navigation; appended last to win older tab CSS.
st.markdown('<style>'+PORTAL_CSS+'</style>',unsafe_allow_html=True)

@st.cache_data(show_spinner=False, max_entries=16)
def _read_embedded_html(filename: str, modified_ns: int) -> str:
    """Cache large embedded pages across Streamlit widget reruns.

    Including the file modification timestamp ensures changed HTML is reloaded
    on the next request, rather than retaining a stale cached copy.
    """
    return (ROOT / filename).read_text(encoding="utf-8")


def show(filename, height=1550):
    path = ROOT / filename
    if not path.is_file():
        st.error(f"Missing: {filename}")
        return
    components.html(_read_embedded_html(filename, path.stat().st_mtime_ns),
                    height=height, scrolling=True)

@st.fragment
# Keep country/mode widgets reactive without reconstructing the six heavy
# static HTML iframes on each interaction. This is supported by Streamlit 1.40+.
def _show_institutional_toolkit():
    render_institutional_toolkit()

@st.fragment
def _show_ask_the_evidence():
    """Agent tab reruns independently of six large HTML pages and the Toolkit."""
    render_intelligence_agent()

# Each section is a real Streamlit page. Unlike st.tabs, st.Page gives each
# section an individual, shareable pathname and renders ONLY the active page.
# The homepage remains at /, and the existing research HTML and toolkit logic
# are not modified by the router.

def _page_home():
    show("Dashboard_Overview.html", height=1500)


def _page_atlas():
    show("road_safety_atlas.html", height=2000)


def _page_taskforces():
    show("who_has_task_forces.html", height=2000)


def _page_documents():
    show("Existing_road_safety_documents.html", height=2000)


def _page_bodies_strategies():
    show("Bodies_Their_Road_Safety_Strategies.html", height=2000)


def _page_case_studies():
    show("Case_Studies.html", height=2000)


def _page_institutional_toolkit():
    _show_institutional_toolkit()


def _page_ask_evidence():
    _show_ask_the_evidence()


# Keep URLs stable and explicit. Streamlit serves the default page at /.
# st.navigation(position="top") requires Streamlit >= 1.46.
PAGES = [
    st.Page(_page_home, title="Start here", default=True),
    st.Page(_page_atlas, title="Atlas", url_path="atlas"),
    st.Page(_page_taskforces, title="Taskforces", url_path="taskforces"),
    st.Page(_page_documents, title="Existing documents", url_path="documents"),
    st.Page(_page_bodies_strategies, title="Bodies & strategies", url_path="bodies-strategies"),
    st.Page(_page_case_studies, title="Country case studies", url_path="case-studies"),
    st.Page(_page_institutional_toolkit,
            title="Road Safety Institutional Toolkit", url_path="institutional-toolkit"),
    st.Page(_page_ask_evidence, title="Ask the Evidence", url_path="ask-the-evidence"),
]

selected_page = st.navigation(PAGES, position="top")
selected_page.run()
