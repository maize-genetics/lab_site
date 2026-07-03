# Lab site + CV — monthly update guide

This folder holds the structured data that feeds the lab website (`lab_site`) and
mirrors the publications/people in the master CV. Doing an update = refreshing a
few source files, then running two scripts.

## Files

**What the site actually reads (generated JS — never hand-edit):**
- `../js/publications-data.js` — themed publication archive
- `../js/people-data.js` — the People timeline

**Publications data (generated; don't hand-edit):**
- `publications.bib` — deduplicated master bibliography
- `publications.csv` — deduplicated publication list (same set, tabular) — this
  is what the site's publication build reads.

**People roster — the fillable source of truth:**
- `people-roster.xlsx` — **Ed & Sara maintain this** (best kept/edited in Cowork).
  Columns: name, role, start_year, end_year, current_position, **website, linkedin**.
  Role has a dropdown; rows missing a start year are shaded yellow (needed for the
  timeline). `people.csv` / `people.tsv` are the older generated copies (CSV is
  redundant — TSV is the fallback the build reads if the xlsx is absent).

**Raw inputs (you drop these in; dated exports are kept for history):**
- `pubs.bib` — BibTeX export from Google Scholar
- `buckler_citations_<YYMMDD>.csv` — CSV export from Google Scholar

**Tools:**
- `update_tools/dedupe_pubs.py` — raw exports → `publications.bib` + `publications.csv`
- `update_tools/build_people.py` — roster + inferred lab years → `people.csv`/`people.tsv` (seed only)
- `../scripts/generate-publications.py` — `publications.csv` → `js/publications-data.js` (themes, landmarks)
- `../scripts/generate-people.py` — `people-roster.xlsx` (or `people.tsv`) → `js/people-data.js`

## Monthly steps

1. **Pull new publications.** Export a fresh BibTeX (`pubs.bib`) and CSV
   (`buckler_citations_<today YYMMDD>.csv`) from the Google Scholar profile
   (`scholar.google.com/citations?user=M7O1p6oAAAAJ`) into this folder.
   (Claude can also pull/verify recent additions from the web.)
2. `python3 update_tools/dedupe_pubs.py` → refreshes `publications.bib`/`.csv`.
3. `python3 ../scripts/generate-publications.py` → rebuilds `js/publications-data.js`.
4. **Update people.** Ed & Sara edit `people-roster.xlsx` (fill start years for the
   yellow rows, add current positions, add website/LinkedIn, add new members).
5. `python3 ../scripts/generate-people.py` → rebuilds `js/people-data.js` from the
   roster. It prints anyone still missing a start year (they can't be placed yet).
6. **Commit and deploy** the site.
7. **CV sync.** Publications in the master CV Google Doc
   (`MasterBucklerCurriculumVita`) are already maintained from the same Scholar
   set. Add any new people to the CV's Postdoc/Grad/Visiting name lists.

## Important caveats on inferred lab years

`start_year`/`end_year` in `people.csv` are **inferred from co-authorship** in the
bibliography: `start = first co-authored paper − 2`, `end = last co-authored paper`
(`present` if 2025 or later). Two known limitations to eyeball:

- **Long-term collaborators show inflated end years / "present".** People who kept
  publishing with the lab after leaving (e.g. Michael Gore, Jianbing Yan, Sherry
  Flint-Garcia) show `present` even though their *training* period ended earlier.
  Correct these by hand where you want true tenure dates.
- **No co-authorship match → blank years.** Short visitors and a few others have no
  matching paper, so years are blank. These need manual entry:
  Gnanapragasam, Ojeda, Konadu, J.A. Romero, Saft, Valdes Franco, Akaogu,
  Cordoba-Nooa, Coutino, Dai, Enciso-Rodriguez, Kolliker, X. Lu, Paliwal, Pipoli,
  Pook, Saidou, R.K. Sharma, Shirasawa, Sofi, Calderon Vazquez, Q. Xu, F. Yan.

`current_position` is filled for well-known alumni and blank otherwise — add more
as you learn them. The lab alumni page (maizegenetics.net/alumni) is a good source.
