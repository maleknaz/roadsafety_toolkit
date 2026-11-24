# Road Safety Toolkit visual redesign

## Design direction

The interface adopts the **information architecture and visual patterns** of the [UN Road Safety Lab](https://rsl.adersim.ca/): simple top navigation, four entry areas, editorial section headings, generous white-space, modular white cards, a clear relationship between research and action, and accessible filters. The Toolkit retains its own title, research and source material. No external Lab logos, brand images, JavaScript or copyrighted photos are copied.

## What changed

- `app.py` now loads the shared `PORTAL_CSS` styling from a new `portal_theme.py` module. The seven native Streamlit tabs remain intact, with a clean white horizontal navigation that scrolls on narrow screens.
- `institutional_toolkit/ui.py` has a fixed 70-pixel white masthead, a 320-pixel blue/teal editorial hero on desktop, and four side-by-side service cards (responsive on mobile). Its retrieval, comparison, checklist, AI calls, and country-change state handling are unchanged.
- The six embedded HTML documents have a consistent top bar, hero typography, background, cards, and focus indicators while remaining fully standalone. The overview page has been reorganized with four information areas and a cleaner evidence summary.
- The existing true four-column institutional comparison grid is retained and styled to match the new interface, with a full-width detail table below the selected card.
- Page background, notification panels and forms remain light and high-contrast, following the previous color fixes.

## Update your existing GitHub repo

**Safest option: complete ZIP.** Extract `Road_Safety_Toolkit_Lab_Inspired_Full_Repository.zip` locally and upload its contents into your GitHub repo, preserving the nested folders, replacing the same-named files as needed.

**Smaller option: patch ZIP.** Extract `Road_Safety_Toolkit_Lab_Inspired_GitHub_Patch.zip` and upload the following changed files:

```
app.py
portal_theme.py
institutional_toolkit/ui.py
Dashboard_Overview.html
road_safety_atlas.html
who_has_task_forces.html
Existing_road_safety_documents.html
Bodies_Their_Road_Safety_Strategies.html
Case_Studies.html
LAB_UI_UPDATE_GUIDE.md
```

GitHub's web uploader must preserve these relative paths. For nested files, keep the actual directory `institutional_toolkit/` or edit that file through GitHub in place. **Do not upload the ZIP itself as a single file.**

The `.streamlit/config.toml` light theme and every file in `data/` are unchanged. No API key is needed for the visual design changes.

## Validation completed

- **49 automated / Playwright tests passed** in `tests/`, covering country selection, RAG citation isolation, exports, comparison interactions, responsive grid and the new lab-inspired layouts.
- **12 additional Chromium standalone HTML smoke runs**: six pages at 1440px and 390px. All produced a visible title/header, and no JavaScript errors appeared in these runs.
- Verified the header is 70px and the hero is 320px on desktop; mobile uses flexible height for long country-directory headings rather than clipping text.
- Confirmed `data/*.csv` and `data/countries_195.json` are byte-identical to the previous release.
- The update has **not** been verified on a live Streamlit server; this execution environment does not have Streamlit installed. Check the seven tabs, country rerendering, and optional RAG flow after redeploying.

## Evidence boundaries and preservation

Source data, country records, verification classifications, intervention mapping, exports and RAG analysis remain unchanged. The UI does not claim that documentary coverage measures institutional performance. Online freshness checks still require an optional API key.
