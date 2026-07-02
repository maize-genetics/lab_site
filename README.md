# Lab for Plant Genomic Diversity &amp; Design — landing page

Static landing site for the lab (formerly the Buckler Lab). Built with plain
HTML, CSS, and vanilla JavaScript — **no build step** — and deployed via GitHub
Pages. Structured as a sibling to the `cerca_landing_page` repo.

## Structure

```
index.html            Landing page
css/lab-base.css       Tokens, theming (light/dark), nav, shared elements
css/lab-home.css       Section styles (hero, research, institutions, papers, …)
js/lab-global.js       Theme toggle, mobile nav, scroll-spy, reveal, track drift
images/                Photos and assets (see image slots below)
.nojekyll              Serve files as-is (skip Jekyll)
.github/workflows/     GitHub Pages deploy
```

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

## Content still to fill in (placeholders in `index.html`)

- **Images**: hero/research/news slots and the lab group photo (`images/lab-team.jpg`).
- **Links** marked `href="#"`: tool pages, full publication list, Scholar/ORCID, jobs, socials.
- **Leadership**: confirm names/roles (e.g. Z. Miller full name; whether Sheehan reads as co-PI).
- **Publications**: the three featured papers can be expanded; the full archive can be
  ported from the existing Wix CMS collections.
- **Group name**: currently "Lab for Plant Genomic Diversity &amp; Design" — swap freely.
