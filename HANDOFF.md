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

### Files hosted *on Wix* (gone the day the plan is cancelled)
Audit of every page in the Wix sitemap (182 URLs): all outbound links are external
(Bitbucket, GitHub, zzlab, DOIs) **except** 191 reprint PDFs behind the "PDF" icons
on `/publications` and 3 PDFs on `/gapit`, all served from Wix's `_files/ugd/` CDN.
The new site links Scholar/DOI instead, so nothing breaks — but the reprints are
unrecoverable once Wix is gone.

- `python3 scripts/archive-wix-files.py` pulls all 194 into `_source/wix-archive/`
  (gitignored) as `<page>/<Year>_<FirstAuthor>_<wixid>.pdf` plus a `manifest.csv`
  (wix id, original upload name, year, DOI, full citation). Stdlib only, resumable.
  **Run it before cancelling Wix and park the folder in Cowork/Drive.**

## DNS cutover - two phases (Wix DNS now, Directnic later)

Facts (checked 2026‑09‑15):
- Registrar **Directnic** (DNC Holdings), registration paid through **2027‑07‑01**.
- Nameservers are **`ns1/ns2.wix.com`** → the DNS zone lives in the Wix account,
  not at Directnic. No MX/TXT records exist (no email on the domain).
- Five lab GitHub‑Pages sites already hang off this zone and must never be dropped:
  `hub.`, `phg.`, `rphg.`, `rphg2.`, `rtassel.maizegenetics.net` → CNAME
  `maize-genetics.github.io` (repos breeder-genomics-hub, phg_v2/phg-docs, rPHG,
  rPHG2, rTASSEL).
- Old site canonicalises to **www** (apex 301s to www), so the custom domain is
  `www.maizegenetics.net` - inbound URLs keep their exact host and GitHub redirects
  apex → www. The `CNAME` file in the repo root says so; for a workflow deploy the
  value that actually matters is the one in Settings → Pages → Custom domain.

### Phase 1 - repoint at GitHub while Wix still hosts DNS (reversible in minutes)
1. Archive the Wix PDFs (above).
2. **Org‑level domain verification** (protects the five subdomains from takeover):
   github.com/organizations/maize-genetics/settings/pages → Add domain
   `maizegenetics.net` → copy the `_github-pages-challenge-maize-genetics` TXT →
   add it in Wix (Domains → Domain Actions → Manage DNS records) → Verify.
3. **Pages custom domain** (do this together with step 4 - as soon as it is set,
   `maize-genetics.github.io/lab_site` starts redirecting to the custom domain):
   Settings → Pages → Custom domain `www.maizegenetics.net`, or
   `gh api -X PUT repos/maize-genetics/lab_site/pages -f cname=www.maizegenetics.net`
4. **Edit the Wix zone** (same panel as step 2):

   | Host | Type | Old value (Wix) | New value (GitHub Pages) |
   |---|---|---|---|
   | `@` | A | 185.230.63.107 / .186 | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 |
   | `www` | CNAME | cdn3.wixdns.net | `maize-genetics.github.io` |
   | `hub` `phg` `rphg` `rphg2` `rtassel` | CNAME | - | **leave untouched** |

   Wix reserves the `www` host for a connected Wix site; if the edit is refused,
   first disconnect the domain from the Wix site ("leave it unassigned" - the zone
   stays in the account), then edit. Rollback = Wix's "reset A/CNAME to defaults".
5. TTLs are ~1 h. Once `dig www.maizegenetics.net` shows GitHub, tick **Enforce
   HTTPS** in Pages settings (cert takes up to ~1 h), then smoke‑test the router:
   `/tassel`, `/edwardbuckler`, `/about-us`, `/gapit`, `/our-team`, `/publications`.
6. Leave the Wix site published on its free `wixsite.com` URL as a reference copy.
   Do **not** cancel the Wix plan yet - it is still hosting the DNS zone.

### Phase 2 - move DNS to Directnic, then cancel Wix
Trigger: the Wix Premium renewal date (Wix → Billing → Premium Subscriptions),
or whenever someone with the Directnic login has a quiet week.
1. Copy the full Wix zone (after Phase 1: 4 A, 6 CNAME, 1 TXT - see table above).
2. Directnic -> My Services -> Domains -> maizegenetics.net -> Services -> DNS
   **Manage** -> recreate every record verbatim *before* touching nameservers.
3. Details → Name Servers -> Edit -> **"Directnic Defaults"** (`ns0`–`ns3.directnic.com`).
   Both zones are identical, so there is no downtime; allow 24–48 h.
4. Confirm with `dig +short maizegenetics.net NS` and
   `for h in www hub phg rphg rphg2 rtassel; do dig +short $h.maizegenetics.net; done`.
5. Cancel the Wix plan. Registration at Directnic is unaffected.

Anti‑patterns rejected: iframing the GitHub site inside Wix (kills the 404 router,
wrong host indexed) and using Wix as a redirect shim to `github.io` (Wix cannot 301
to external URLs; every legacy URL would bounce through JS and be migrated twice).

## How things regenerate (reference)
- Publications: Scholar CSV -> `data/update_tools/dedupe_pubs.py` ->
  `data/publications.csv` -> `python3 scripts/generate-publications.py` -> `js/publications-data.js`
- People: edit `data/people-roster.xlsx` -> `python3 scripts/generate-people.py`
  -> `js/people-data.js` (timeline) + `js/profiles-data.js` (profile pages).
- Profiles were migrated from the old Wix pages via `data/update_tools/`:
  `parse_scrape.py` (accumulates scraped blocks -> `scraped_people.json`) ->
  `merge_scraped.py --write` (merges into the roster, emits `photo_manifest.tsv`
  + `router_person_map.json` for the `404.html` `PERSON_MAP`). Photos live in
  `images/people/<slug>.jpg`.
- See `data/UPDATE_GUIDE.md` for the monthly flow.
