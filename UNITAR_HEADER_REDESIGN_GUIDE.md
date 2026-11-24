# Road Safety Toolkit: UNITAR-informed unified headers

## Purpose

Bring all seven views into one accessible, coherent visual system based on the uploaded **Existing documents** reference screenshot. This is a toolkit-specific visual design inspired by UNITAR materials. It is **not an official UNITAR branding certification** and does not reproduce UNITAR or United Nations logos.

## References reviewed

1. CIFAL Branding Policy (2019), publicly accessible PDF, pages discussing UNITAR's use of UN Blue. The policy specifies **RGB 62/142/222**, equivalent to **#3E8EDE**, as the key blue. https://bauglobal.com/wp-content/uploads/2019/06/CIFAL-Branding-Policy-2019.pdf
2. UNITAR's official publication on sport and diplomacy, which uses a white-page presentation, institutional blue, thin rules and restrained typographic structure. https://unitar.org/sites/default/files/media/file/UNITAR%27s%20Activities%20in%20Harnessing%20the%20Power%20of%20Sports%20for%20Global%20Diplomacy.pdf
3. Current UNITAR website for general institutional communication approach. https://unitar.org/
4. User-provided screenshot of the Existing documents page, 24 November 2026, used as the **layout reference** for the new masthead and hero.

These sources do not provide a complete current public UNITAR digital design system. The darker hero blue is an **accessibility-oriented design adaptation**, not a claimed official UNITAR swatch.

## What is unified

Across `Start here`, `Atlas`, `Taskforces`, `Existing documents`, `Bodies & strategies`, `Country case studies`, and `Road Safety Institutional Toolkit`:

- **74 px desktop / 64 px mobile** white breadcrumb/masthead with a thin UN Blue top rule.
- **405 px desktop** navy-blue hero, responsive height on phones where long titles must wrap.
- Same title font, white/cyan text hierarchy, spacing, road-themed SVG and metadata treatment.
- UN Blue (`#3E8EDE`) for accents; navy hero (`#07345F` to `#0A619C`); pale blue surfaces and dark ink.
- Consistent Streamlit tab accents and light theme, with no gold or teal mixed stripes in the page headers.
- The research descriptions from each original page are preserved. No country records, RAG service, app logic, or assessment data were edited.

## Files changed

```
unified_brand.py                 # Single reusable style + header renderer
portal_theme.py                 # Streamlit-wide shared blue navigation palette
institutional_toolkit/ui.py    # Shares masthead/hero renderer with 6 HTML pages
.streamlit/config.toml          # Light theme and UN Blue accent
Dashboard_Overview.html
road_safety_atlas.html
who_has_task_forces.html
Existing_road_safety_documents.html
Bodies_Their_Road_Safety_Strategies.html
Case_Studies.html
```

`apply_unified_brand.py` is included as an optional reproducibility script. The embedded HTML pages contain self-contained styles so exports remain consistent when opened independently.

## Deploy

1. Download the **full repository ZIP** and unzip it locally.
2. In your existing repository, preserve directory structure and replace existing files with the new versions. GitHub's web interface can upload extracted files, but be sure nested `.streamlit`, `institutional_toolkit`, and `tests` paths remain intact.
3. Commit. If deployed on Streamlit Community Cloud, the linked branch normally redeploys automatically.
4. Refresh the browser (Ctrl+Shift+R) and verify each of the seven tabs.
5. Test Estonia and Sweden country selection and the comparison grid, not only the headers.

## Quality checks

- Six standalone HTML pages plus a rendered Toolkit preview checked in Chromium at **1440, 960, and 390 px** widths.
- Identical desktop header dimensions for all seven views and no horizontal overflow in tested widths.
- No JavaScript console errors in the tested header/page interactions.
- Source HTML JavaScript blocks compared byte for byte with the previous release and found identical.
- Five research datasets and RAG/assessment service files unchanged.
- Regression tests in `tests/` passed in separate test groups.
- Limitations: this environment does not include the deployed Streamlit server; production iframe sizing and nav should be verified on the live site after committing.

## Developer note

For future design changes, update `unified_brand.py` first. It is the single design reference for Streamlit Toolkit rendering and the six source HTML pages. Avoid adding new, independent hero styles for individual pages. Always test actual rendered desktop and mobile header geometry after regeneration.
