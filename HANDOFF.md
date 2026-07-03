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
- [x] **(3) Headshots for current people** — 19 pulled from the Wix "Lab Member
      Photos" folder into `images/people/` and wired into the leadership + roster
      avatars (initials fall back where no photo). **Still on initials (no photo
      found):** Moira Sheehan, Sheng-Kai Hsu, Niranjani Gnanapragasam, Zong-Yan
      Liu, Szu-Ping Chen, Thuy La.

## Open — quick copy / asset fixes
- [x] **(4) Software icons** on `tools.html` — real logos on PlantCAD, GeneCAD,
      AnchorWave, and now **PHG, TASSEL, rTASSEL, GAPIT** (pulled from the
      maize-genetics / jiabowang GitHub repos into `images/tools/`). Only
      **BioKotlin** stays a "BK" text mark — no logo in its repo or on biokotlin.org.
- [ ] **(9) Test: move some section pictures adjacent to the title.** Ed wants to
      *try* it (current layout is good; may look crowded) — build a variant of the
      research threads / cards and compare.

## Open — bigger features
- [ ] **(3) Headshots for current people** — add photo support to the People
      "now" roster (leadership + role lists). *Needs:* headshot images per person.
- [ ] **(11) Rework "Join" into an "About Us / Join"** page — closer to the old
      site's About structure (lab overview + contact + open positions), not just a jobs CTA.
- [ ] **(8) TASSEL docs → modern structure** — update TASSEL documentation/links
      to the current layout (external to this repo; scope TBD).
- [ ] **(10) Test layout on phones** — QA all pages at mobile widths (nav,
      timelines, theme tiles, hero, roster grid); fix reflow issues.

## Open — data / content still owed
- [ ] **(2) Complete alumni / people years.** ~42 people (mostly staff,
      undergrads, short-term visitors) have no start year, so they're absent from
      the timeline. Fill years in `data/people-roster.xlsx` (yellow cells) →
      `python3 scripts/generate-people.py`.
- [ ] Relocate unoptimized source images (`images/LabPictures.png/`,
      `images/LabIn2023.png`, `images/1932GeneticsCongress.jpg`) to Cowork/Drive;
      they're gitignored but still on disk.
- [ ] Optional cleanup: redundant `data/people.csv` and stale
      `data/people-template.*` (TSV/roster xlsx are canonical now).

## How things regenerate (reference)
- Publications: Scholar CSV → `data/update_tools/dedupe_pubs.py` →
  `data/publications.csv` → `python3 scripts/generate-publications.py` → `js/publications-data.js`
- People: edit `data/people-roster.xlsx` → `python3 scripts/generate-people.py` → `js/people-data.js`
- See `data/UPDATE_GUIDE.md` for the monthly flow.
