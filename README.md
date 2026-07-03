# Lab for Plant Genomic Diversity &amp; Design — website

Static multi-page site for the lab (formerly the Buckler Lab). Built with plain
HTML, CSS, and vanilla JavaScript — **no build step** — and deployed via GitHub
Pages.

## Structure

```
index.html             Home (hero, research preview, news)
research.html          "Now" threads + research-lines timeline (1998→today)
people.html            Leadership, roster, gallery, "lab over time" timeline
publications.html      Landmarks + recent + theme tiles (data-driven)
theme.html             One template; shows a theme's papers via #slug
tools.html             Open-source software cards
join.html              Open positions + contact

css/lab-base.css       Tokens, theming (light/dark), nav, footer, buttons, shared bits
css/lab-home.css       Home-only section styles
css/lab-pages.css      Interior-page styles (threads, timelines, theme tiles, …)
js/lab-global.js       Shared chrome injector (nav + footer) + theme toggle,
                       mobile nav, scroll-spy, reveal, genome-track drift
js/publications-data.js  All papers (LAB_PUBS) + themes (LAB_THEMES) — one data file
js/people-data.js        All lab members with years (LAB_PEOPLE) for the timeline
js/lab-archive.js        Renders landmarks/recent/theme tiles/theme page + timelines
data/people-template.csv Blank template for the members-with-years export
images/                Photos, figures, and logos (migrated from Wix; see CREDITS.md)
.nojekyll              Serve files as-is (skip Jekyll)
.github/workflows/     GitHub Pages deploy (publishes the whole folder on push to main)
```

### Shared nav & footer

The primary nav and footer are injected by `renderChrome()` in `js/lab-global.js`
into the `<div id="site-nav">` and `<footer id="site-footer">` placeholders on
every page — so there is one source of truth and still no build step. The active
nav item comes from each page's `<body data-page="…">`. Add a page by copying an
interior page, setting its `data-page`, and (optionally) adding it to the `PAGES`
array in `js/lab-global.js`.

### Publication archive & timelines (data-driven)

The publication archive and the two timelines are rendered from plain-JS data
files by `js/lab-archive.js` — no build step:

- **`js/publications-data.js`** — `LAB_PUBS` (one object per paper:
  `{y, a, t, v, doi, themes:[slug], flags:["landmark"]}`) and `LAB_THEMES`
  (the ~12 themes). `publications.html` auto-builds the landmark strip
  (`flags` includes `landmark`, capped 10), the most-recent list (top 10 by
  year), and the theme tiles with live counts. `theme.html#<slug>` filters that
  theme's papers. **To load the full ~350 papers: replace the `LAB_PUBS` array**
  with the full export (same schema) — everything else updates automatically.
- **`js/people-data.js`** — `LAB_PEOPLE`
  (`{name, role, start, end, now}`); drives the People-page timeline and its role
  filters. Fill it from `data/people-template.csv`.
- **`research.html`** defines its research-lines timeline inline as `LAB_LINES`
  (`{name, start, milestones:[{y,label}]}`).

> The paper set and people list are currently **interim samples** (≈75 papers,
> ≈22 people) so the pages render; swap in the full exports when ready.

### Images

All images live in `images/` and were migrated from the lab's own Wix media
library, then downscaled/compressed for the web. See `images/CREDITS.md` for the
source-to-file mapping. Swap any file in place to update the site.

## Local preview

No build required. Serve the folder with any static file server:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/>.

## Deploy on GitHub Pages

1. Create a repo (e.g. `maize-genetics/lab_landing_page`) and push these files to `main`.
2. In the repo: **Settings → Pages → Source → GitHub Actions**.
3. The included workflow publishes on every push to `main`.

## Custom domain (maizegenetics.net)

Only do this once you're ready to move the domain off Wix.

1. Repo **Settings → Pages → Custom domain** → enter your domain (writes a `CNAME` file).
2. At your DNS host, point the domain to GitHub Pages using the **exact A/AAAA
   records for the apex and the CNAME for `www`** listed in GitHub's docs
   ("Managing a custom domain for your GitHub Pages site"). Confirm current
   values there — do not hard-code IPs from memory.
3. Enable **Enforce HTTPS** once the certificate provisions.
4. Note: pointing the apex domain here disconnects the current Wix site from it.

## Content

People, publications, contact details, social links, and profile URLs were
pulled from the live site at <https://www.maizegenetics.net> (team roster from
`/our-team`, publications from `/publications`). Verified Google Scholar / ORCID,
YouTube / X / Facebook, and the corrected rTASSEL docs URL are wired in.

### Still to confirm

- **Team photos** (`people.html`): the gallery reuses field/lab photos — swap in
  current team candids when available.
- **Publications** (`publications.html`): a curated recent + landmark selection —
  the full ~230-item archive can be ported if a complete on-site list is wanted.
- **Tools** (`tools.html`): a couple of repo/doc links are best-guess canonical
  URLs — confirm each (rTASSEL, GAPIT, BioKotlin are verified).
- **Jobs** (`join.html`): link real postings / application system when available.
- **Group name**: currently "Lab for Plant Genomic Diversity &amp; Design" — swap freely.
