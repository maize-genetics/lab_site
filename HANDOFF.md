# Lab site — open tasks / handoff

Running list of what's left. Grouped by "quick copy/asset fixes", "bigger
features", and "data/content still owed". Check items off as they land.

## ✅ Done in the latest pass
- [x] People page uses the full-lab 2023 field photo (`images/lab-2023.jpg`) as the main image.
- [x] Landing headline: "Reading the **Genome** to design the crops we need." (#1)
- [x] Removed the ">1,000 citations" line from the Landmarks card/header (#6)
- [x] Removed "Ed's and Cinta's complete… on Google Scholar" from the Publications intro (#7)
- [x] Compact green page-hero (~half height)
- [x] **(5) Two Google Scholar links** — Buckler + Romay on Publications (hero + footer links).
- [x] **(3) Headshots — now for EVERYONE (137 people).** Migrated every member
      photo + bio + links forward from the old Wix person pages into the roster
      (`data/people-roster.xlsx`). `images/people/<slug>.jpg` for all 135 with a
      photo; the leadership + team roster and the timeline are now data-driven and
      link to per-person profile pages.
- [x] **Per-person profile pages** — new `person.html` renders a full profile
      (photo, bio, years, current position, Email/Scholar/ORCID/Website/LinkedIn/
      Twitter) from `js/profiles-data.js`. Legacy `/edwardbuckler`, `/jingjingzhai`,
      `/gaelpressoir`, … redirect to `person.html#<slug>` via the 404 router.

## Open — quick copy / asset fixes
- [x] **(4) Software icons** on `tools.html` — real logos on PlantCAD, GeneCAD,
      AnchorWave, and now **PHG, TASSEL, rTASSEL, GAPIT** (pulled from the
      maize-genetics / jiabowang GitHub repos into `images/tools/`). Only
      **BioKotlin** stays a "BK" text mark — no logo in its repo or on biokotlin.org.
- [ ] **(9) Test: move some section pictures adjacent to the title.** Ed wants to
      *try* it (current layout is good; may look crowded) — build a variant of the
      research threads / cards and compare.

## Open — bigger features
- [x] **(11) Rework "Join" into an "About Us / Join"** page — `join.html` now leads
      with a lab overview + contact, then open positions (`#positions`); nav relabeled
      "About & Join". Routes `/about-us` & `/contact-us`.
- [x] **(8) TASSEL docs → modern structure** — new `tassel.html` hub points to
      GitHub downloads/docs + rTASSEL + citation. (Team still to place the actual
      files on GitHub — see "Files still owed a canonical GitHub home" below.)
- [ ] **(10) Test layout on phones** — QA all pages at mobile widths (nav,
      timelines, theme tiles, hero, roster grid); fix reflow issues.

## Open — data / content still owed
- [ ] **(2) Complete people years.** ~50 people (mostly undergrads / short-term
      visitors) have no start year, so they're absent from the *timeline* (they DO
      have full profile pages now). Fill years in `data/people-roster.xlsx` →
      `python3 scripts/generate-people.py`.
- [ ] **Profile QA.** Bios/titles were scraped from the old Wix pages by a small
      model; a few Scholar/ORCID links were dropped where the extractor cross-
      contaminated them (nulled to avoid wrong links). Skim `js/profiles-data.js`
      /the roster and fill gaps. Two people have no photo (blank Wix placeholder):
      Kristina Volkert, Jennifer Heer.
- [ ] Relocate unoptimized source images (`images/LabPictures.png/`,
      `images/LabIn2023.png`, `images/1932GeneticsCongress.jpg`) to Cowork/Drive;
      they're gitignored but still on disk.
- [ ] Optional cleanup: redundant `data/people.csv` and stale
      `data/people-template.*` (TSV/roster xlsx are canonical now).

## URL migration / GitHub consolidation (cutover from Wix)

Backed by a year of Wix analytics (`Traffic report_*.csv`). When maizegenetics.net
cuts over from Wix to this site, inbound links must still resolve.

- **Router:** `404.html` is a JS redirect map — GitHub Pages serves it for any
  unmatched path and it forwards legacy URLs to the new pages. Edit the
  `REDIRECTS` / `PERSON_OVERRIDES` tables there to adjust. Test in the console:
  `resolveRedirect('/tassel')` etc.
- **People:** legacy person pages (`/edwardbuckler`, `/gaelpressoir`, …) resolve
  to profile pages `person.html#<slug>` via `PERSON_MAP` in `404.html` (with an
  alphanumeric fallback so `/baoxingsong` finds `baoxing-song`). Unmapped bare
  name slugs soft-land on `people.html`.
- **TASSEL (#1 page, 10,916 sessions):** `/tassel` → new `tassel.html` hub; all
  `/tassel/*` deep links also land there.
- **About:** `join.html` reworked into "About & Join"; `/about-us`, `/contact-us`
  route there, `/our-team` → `people.html`.

### ⚠️ Files still owed a canonical GitHub home (team action)
The `/tassel/*` and `/publications/*.pdf` deep links currently 404 with no
confirmed destination — right now they all funnel to `tassel.html` /
`publications.html`. Put the real artifacts on GitHub and point the router at them:
- **TASSEL downloads:** `tassel5-standalone.zip`, `tassel5-windows-x64.zip`,
  `tassel4.0/3.0_standalone.zip`, `jws/tassel{3,4}.jnlp`.
- **TASSEL docs (PDFs):** tasselpipelinegbs, tasselpipelinecli, executingtassel,
  ldpipeline, mlmglmpipeline, uneak, `tassel_user_guide_3.0.pdf`,
  `tassel5userguide.html`, `javadoc/*`; data: `TASSELTutorialData3.zip`,
  `gbstestdata.tar`.
- **GAPIT:** confirm zzlab.net is canonical (currently `/gapit` → `tools.html#gapit`).
- **Legacy reprints:** `/publications/*.pdf` (Matsuoka2002PNAS, Vollbrecht2005Nature,
  Remington2001PNAS, Buckler2002COPB) — map each to a DOI or repo.

### At cutover
- Add a `CNAME` file containing `maizegenetics.net`, set DNS, and make the repo /
  Pages public — redirects only serve once Pages is live.

## How things regenerate (reference)
- Publications: Scholar CSV → `data/update_tools/dedupe_pubs.py` →
  `data/publications.csv` → `python3 scripts/generate-publications.py` → `js/publications-data.js`
- People: edit `data/people-roster.xlsx` → `python3 scripts/generate-people.py`
  → `js/people-data.js` (timeline) + `js/profiles-data.js` (profile pages).
- Profiles were migrated from the old Wix pages via `data/update_tools/`:
  `parse_scrape.py` (accumulates scraped blocks → `scraped_people.json`) →
  `merge_scraped.py --write` (merges into the roster, emits `photo_manifest.tsv`
  + `router_person_map.json` for the `404.html` `PERSON_MAP`). Photos live in
  `images/people/<slug>.jpg`.
- See `data/UPDATE_GUIDE.md` for the monthly flow.
