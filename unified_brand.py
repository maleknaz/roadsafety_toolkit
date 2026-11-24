"""Shared UNITAR-informed visual system for all Road Safety Toolkit sections.

The artwork and wordmark are original Road Safety Toolkit elements, not UNITAR's
protected emblem. Palette uses UN Blue (RGB 62,142,222) from the CIFAL branding
policy and a darker accessible blue for the hero. No affiliation is asserted.
"""
from html import escape

UN_BLUE = '#3E8EDE'  # RGB 62/142/222, UNITAR/CIFAL published branding reference
UN_BLUE_DARK = '#073B71'  # design adaptation for contrast, NOT a claimed official hex
CYAN = '#A6E1EC'  # accent inspired by existing UNITAR publications
TEXT = '#183954'

# Compact self-contained inline artwork. It does not depend on external assets.
ROAD_ART = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 475 338" focusable="false" aria-hidden="true">
 <circle cx="294" cy="155" r="140" fill="none" stroke="#A6E1EC" stroke-opacity=".24" stroke-dasharray="5 10"/>
 <circle cx="294" cy="155" r="105" fill="none" stroke="#A6E1EC" stroke-opacity=".12"/>
 <path d="M45 338C82 254 145 270 191 202S281 112 425 15" stroke="#002F60" stroke-width="84" stroke-linecap="round" fill="none" opacity=".68"/>
 <path d="M45 338C82 254 145 270 191 202S281 112 425 15" stroke="#A6E1EC" stroke-width="3" stroke-dasharray="13 15" fill="none" opacity=".86"/>
 <path d="M65 338C91 285 148 296 200 212S293 130 433 32" stroke="#D6F3FA" stroke-width="1.5" fill="none" opacity=".33"/>
 <g stroke="#A6E1EC" stroke-width="3" fill="#0B5B98"><circle cx="69" cy="304" r="14"/><circle cx="190" cy="204" r="14"/><circle cx="296" cy="110" r="14"/></g>
 <g fill="#A6E1EC"><circle cx="375" cy="221" r="4"/><circle cx="158" cy="80" r="4"/></g>
 </svg>'''

HEADER_CSS = r'''<style id="rsu-unitar-brand-system">
:root{--rsu-blue:#3E8EDE;--rsu-dark:#073B71;--rsu-accent:#A6E1EC;--rsu-ink:#183954;--rsu-line:#DCE8F1;--rsu-bg:#F5F9FC;color-scheme:light;}
html,body{background:var(--rsu-bg)!important;color:var(--rsu-ink)!important;font-family:Arial,'Helvetica Neue','Segoe UI',sans-serif!important;}
/* Identical masthead for the six independent HTML pages and the Streamlit Toolkit */
.rsu-masthead{box-sizing:border-box!important;width:100%!important;height:74px!important;min-height:74px!important;margin:0!important;background:#fff!important;color:var(--rsu-ink)!important;border-bottom:1px solid #DCE8F1!important;box-shadow:none!important;font:inherit!important;position:relative!important;z-index:3!important;}
.rsu-masthead::before{content:""!important;display:block!important;position:absolute!important;top:0;left:0;right:0;height:4px!important;background:#3E8EDE!important;}
body>.grs-fixed-banner.rsu-masthead,body>.grs-consistent-masthead.rsu-masthead{height:74px!important;min-height:74px!important;max-height:74px!important;padding:0!important;}
.rsu-masthead .rsu-mast-inner{box-sizing:border-box!important;height:100%!important;padding:4px clamp(18px,2.2vw,36px) 0!important;display:flex!important;align-items:center!important;justify-content:space-between!important;gap:20px!important;max-width:1780px!important;margin:0 auto!important;}
.rsu-masthead .rsu-breadcrumb{display:flex!important;gap:13px!important;align-items:center!important;min-width:0!important;color:#143A59!important;line-height:1.3!important;}
.rsu-masthead .rsu-mark{width:7px!important;height:27px!important;border-radius:3px!important;background:var(--rsu-blue)!important;flex-shrink:0!important;}
.rsu-masthead .rsu-name{font-size:13px!important;font-weight:850!important;letter-spacing:.1em!important;text-transform:uppercase!important;white-space:nowrap!important;color:#143A59!important;}
.rsu-masthead .rsu-current{font-size:12px!important;font-weight:500!important;color:#54748C!important;white-space:normal!important;}
.rsu-masthead .rsu-date{font-size:12px!important;white-space:nowrap!important;color:#5A7890!important;}
/* Full-width editorial hero with a single fixed desktop height. */
body>header.hero.rsu-hero,header.rsu-hero,.st-key-road_safety_toolkit .rsu-hero{box-sizing:border-box!important;display:block!important;position:relative!important;isolation:isolate!important;width:100%!important;height:405px!important;min-height:405px!important;max-height:405px!important;margin:0!important;padding:0!important;overflow:hidden!important;border:0!important;background:linear-gradient(113deg,#07345F 0%,#08487F 56%,#0A619C 100%)!important;color:#fff!important;}
body>header.hero.rsu-hero::before,header.rsu-hero::before{content:""!important;position:absolute!important;z-index:0!important;right:-215px!important;top:-210px!important;width:595px!important;height:595px!important;border-radius:50%!important;border:1px solid rgba(185,231,248,.18)!important;box-shadow:0 0 0 72px rgba(166,225,236,.035),0 0 0 146px rgba(166,225,236,.025)!important;pointer-events:none!important;}
body>header.hero.rsu-hero::after,header.rsu-hero::after{content:none!important;display:none!important;background:none!important;}
.rsu-hero .rsu-hero-inner{box-sizing:border-box!important;max-width:1780px!important;padding:45px clamp(20px,2.2vw,36px) 42px!important;margin:0 auto!important;height:100%!important;display:flex!important;align-items:center!important;position:relative!important;}
.rsu-hero .rsu-copy{min-width:0!important;max-width:1080px!important;position:relative!important;z-index:2!important;padding-right:30px!important;}
.rsu-hero .rsu-eyebrow{display:block!important;color:#A6E1EC!important;-webkit-text-fill-color:#A6E1EC!important;font-size:12px!important;font-weight:850!important;letter-spacing:.16em!important;line-height:1.4!important;text-transform:uppercase!important;margin:0 0 18px!important;}
.rsu-hero h1,.rsu-hero h1 *{font-family:Arial,'Helvetica Neue',sans-serif!important;}
body>header.hero.rsu-hero h1,.rsu-hero h1,.st-key-road_safety_toolkit .rsu-hero h1{color:#fff!important;-webkit-text-fill-color:#fff!important;font-weight:800!important;font-size:clamp(29px,2.9vw,42px)!important;letter-spacing:-.028em!important;line-height:1.2!important;max-width:1000px!important;margin:0 0 18px!important;text-wrap:balance!important;}
body>header.hero.rsu-hero h1 em,body>header.hero.rsu-hero h1 .title-accent,.rsu-hero h1 em,.rsu-hero h1 .title-accent{color:#A6E1EC!important;-webkit-text-fill-color:#A6E1EC!important;font-style:normal!important;}
body>header.hero.rsu-hero .rsu-description,.rsu-hero .rsu-description{display:block!important;font-size:15px!important;line-height:1.62!important;max-width:920px!important;color:#E6F1FA!important;-webkit-text-fill-color:#E6F1FA!important;margin:0!important;}
.rsu-hero .rsu-meta{display:block!important;margin-top:22px!important;font-size:12px!important;line-height:1.5!important;color:#BFDDEE!important;-webkit-text-fill-color:#BFDDEE!important;}
.rsu-hero .rsu-art{position:absolute!important;right:16px!important;top:28px!important;height:350px!important;width:450px!important;z-index:1!important;opacity:.55!important;pointer-events:none!important;}
.rsu-hero .rsu-art svg{display:block!important;width:100%!important;height:100%!important;}
/* The Toolkit's four area cards share the same UNITAR-informed blue family. */
.st-key-road_safety_toolkit .rst-a1 .rst-area-art,.st-key-road_safety_toolkit .rst-a3 .rst-area-art{background:#084E87!important;}
.st-key-road_safety_toolkit .rst-a2 .rst-area-art,.st-key-road_safety_toolkit .rst-a4 .rst-area-art{background:#176FA9!important;}
.st-key-road_safety_toolkit .rst-eyebrow,.st-key-road_safety_toolkit .rst-area-num,.st-key-road_safety_toolkit .rst-area-end{color:#126AA5!important;-webkit-text-fill-color:#126AA5!important;}
.st-key-road_safety_toolkit .rst-area{border-color:#DCE8F1!important;}
/* Home card artwork also uses blue shades, without changing any data-specific status colors. */
body .rs-home-v3-a1 .rs-home-card-art,body .rs-home-v3-a3 .rs-home-card-art{background:linear-gradient(110deg,#094F88,#106B9F)!important;}
body .rs-home-v3-a2 .rs-home-card-art,body .rs-home-v3-a4 .rs-home-card-art{background:linear-gradient(110deg,#105F9A,#297DB8)!important;}
body .rs-home-card-body>span,body .rs-lab-home-eyebrow{color:#126AA5!important;}
/* Simple UNITAR-informed palette for the rest of the pages. */
body :is(.panel,.card,.kpi,.stat-card,.metric-card){border-color:#DCE8F1!important;}
body a:not([role="button"]){color:#075E9F;}
body a:focus-visible,body button:focus-visible,body select:focus-visible,body input:focus-visible{outline:3px solid #3E8EDE!important;outline-offset:2px!important;}
.st-key-road_safety_toolkit .rsu-masthead,.st-key-road_safety_toolkit .rsu-hero{
  margin-left:-24px!important;margin-right:-24px!important;width:calc(100% + 48px)!important;
}
.st-key-road_safety_toolkit .rsu-masthead{margin-top:0!important;margin-bottom:0!important;}
.st-key-road_safety_toolkit .rsu-hero .rsu-copy{max-width:1000px!important;}
@media(max-width:1100px){.rsu-hero .rsu-art{right:-105px!important;opacity:.23!important;}.rsu-hero .rsu-copy{max-width:900px!important;}}
@media(max-width:720px){
.rsu-masthead,body>.grs-fixed-banner.rsu-masthead,body>.grs-consistent-masthead.rsu-masthead{height:64px!important;min-height:64px!important;max-height:64px!important;}
.rsu-masthead .rsu-date{display:none!important;}
.rsu-masthead .rsu-name{font-size:11px!important;letter-spacing:.04em!important;}
.rsu-masthead .rsu-breadcrumb{gap:8px!important;}
.rsu-masthead .rsu-current{font-size:11px!important;}
body>header.hero.rsu-hero,header.rsu-hero,.st-key-road_safety_toolkit .rsu-hero{height:auto!important;min-height:360px!important;max-height:none!important;}
.rsu-hero .rsu-hero-inner{min-height:360px!important;height:auto!important;padding:38px 20px 45px!important;}
body>header.hero.rsu-hero h1,.rsu-hero h1{font-size:clamp(28px,7vw,35px)!important;line-height:1.16!important;}
.rsu-hero .rsu-description{font-size:14px!important;line-height:1.52!important;}
.rsu-hero .rsu-meta{font-size:11px!important;}
.rsu-hero .rsu-art{right:-205px!important;top:25px!important;opacity:.12!important;}
.st-key-road_safety_toolkit .rsu-masthead,.st-key-road_safety_toolkit .rsu-hero{margin-left:-12px!important;margin-right:-12px!important;width:calc(100% + 24px)!important;}
}
@media(max-width:390px){.rsu-masthead .rsu-name{font-size:10px!important;}.rsu-masthead .rsu-current{font-size:10px!important;}.rsu-hero .rsu-hero-inner{padding:27px 18px 36px!important;}}
@media(prefers-reduced-motion:reduce){.rsu-masthead *,.rsu-hero *{transition:none!important;animation:none!important;}}
</style>'''


def header_html(section: str, eyebrow: str, title_html: str,
                description: str, meta: str = '', legacy_mast: str = 'grs-fixed-banner',
                hero_id: str = '') -> str:
    """One header layout for both original HTML pages and Streamlit.

    title_html is trusted authored HTML from the existing bundled pages, not
    arbitrary external or user-provided content.
    """
    meta_html = f'<p class="rsu-meta">{escape(meta)}</p>' if meta else ''
    mast = f'''<div class="{legacy_mast} rsu-masthead" role="banner">
      <div class="rsu-mast-inner"><div class="rsu-breadcrumb"><span class="rsu-mark" aria-hidden="true"></span>
      <span class="rsu-name">Road Safety Toolkit</span><span class="rsu-current">/ {escape(section)}</span></div>
      <span class="rsu-date">Research dashboard · November 2026</span></div></div>'''
    h_id = f' id="{escape(hero_id,quote=True)}"' if hero_id else ''
    hero = f'''<header class="hero rsu-hero"{h_id}>
      <div class="rsu-hero-inner"><div class="rsu-copy">
      <div class="rsu-eyebrow">{escape(eyebrow)}</div>
      <h1>{title_html}</h1><p class="rsu-description">{escape(description)}</p>{meta_html}
      </div><div class="rsu-art">{ROAD_ART}</div></div></header>'''
    return HEADER_CSS + mast + hero


APP_BRAND_CSS = r'''
/* All seven tabs use UNITAR-informed blue instead of mixed teal and gold. */
:root{--rs-navy:#073B71;--rs-ink:#183954;--rs-muted:#59758C;--rs-teal:#1C78B9;--rs-cyan:#E5F3FA;--rs-border:#DCE8F1;--rs-bg:#F5F9FC;}
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{background:#F5F9FC!important;color:#183954!important;}
[data-testid="stTabs"] [role="tablist"]{border-top:4px solid #3E8EDE!important;border-bottom:1px solid #DCE8F1!important;}
[data-testid="stTabs"] [role="tablist"] [role="tab"]{color:#264D70!important;-webkit-text-fill-color:#264D70!important;}
[data-testid="stTabs"] [role="tablist"] [role="tab"][aria-selected="true"]{background:#E9F4FC!important;color:#084B82!important;-webkit-text-fill-color:#084B82!important;border-bottom:3px solid #3E8EDE!important;}
[data-testid="stTabs"] [role="tablist"] [role="tab"]:hover{background:#F0F7FE!important;color:#084B82!important;-webkit-text-fill-color:#084B82!important;}
.st-key-road_safety_toolkit{background:#F5F9FC!important;}
.st-key-road_safety_toolkit .rs-toolkit-context-status{background:#EAF5FB!important;border-color:#BFDFF2!important;}
.st-key-road_safety_toolkit .rst-mode-brief{border-left-color:#3E8EDE!important;}
.st-key-road_safety_toolkit [data-testid="stButton"] button:hover,
.st-key-road_safety_toolkit [data-testid="stDownloadButton"] button:hover{background:#EAF5FB!important;border-color:#3E8EDE!important;}
.st-key-road_safety_toolkit :is([data-testid="stFormSubmitButton"],[data-testid="stButton"]) button[kind="primary"]{background:#106AA9!important;border-color:#106AA9!important;}
.st-key-road_safety_toolkit .rst-area-num{color:#1971AC!important;}
.st-key-road_safety_toolkit .rst-how{border-top-color:#3E8EDE!important;}
.st-key-road_safety_toolkit .rst-main{padding-top:31px!important;}
.st-key-road_safety_toolkit .rst-area{border-color:#DCE8F1!important;}
.st-key-road_safety_toolkit .rst-area-art{background:#0A4B83!important;}
.st-key-road_safety_toolkit .rst-area:nth-child(even) .rst-area-art{background:#146FA9!important;}
'''
