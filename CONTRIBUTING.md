# Contributing & branching workflow

This site uses **GitHub Flow**: one long-lived branch (`main` = production) and
short-lived branches for every change. There is no build step — the repo is
served as-is — so "deploy" just means merging to `main`.

## The golden rule

**`main` is always deployable.** Every commit on `main` is what production
serves. You never commit directly to `main`; all changes arrive through a pull
request.

## Hosting & previewing

- **Production → GitHub Pages.** The workflow in `.github/workflows/` publishes
  `main` on every merge; the custom domain (once cut over) points here.
- **Preview → locally.** There's no build step, so `python3 -m http.server 8000`
  (from the repo root) serves the site exactly as it will look in production —
  open <http://localhost:8000/>. That local preview is the dev site; review your
  branch there before opening the PR.

## Branch naming

Branch off the latest `main`, one change per branch:

| Prefix       | Use for                                             |
|--------------|-----------------------------------------------------|
| `feature/`   | new sections or functionality                       |
| `fix/`       | bug or layout fixes                                 |
| `content/`   | copy, roster, or publication-data updates           |
| `hotfix/`    | urgent production fix (same flow, fast-tracked)     |

e.g. `feature/alumni-map`, `fix/mobile-nav-overlap`, `content/2026-roster-update`.

## The flow

```bash
git checkout main && git pull            # start from current production
git checkout -b fix/short-slug           # one change per branch
# …edit, then:
git add -A && git commit                 # see commit-message style below
git push -u origin fix/short-slug
```

Then open a PR against `main`, **review the change locally** (desktop, mobile, and
dark mode), get it approved, and **Squash & merge**. The branch auto-deletes;
`main` deploys to production automatically.

## Commit messages

Short imperative subject (≤ ~70 chars), then a body explaining *why* if it isn't
obvious. Example:

```
Fix nav overlap on narrow phones

The pinned bar height wasn't feeding scroll-padding-top on <360px, so
anchor jumps hid section headers under the nav.
```

## If you change generated data, regenerate it

Some JS data files are **generated — don't hand-edit them**. Edit the source,
then run the generator and commit both:

- **People / profiles** — edit `data/people-roster.xlsx`, then
  `python3 scripts/generate-people.py` → `js/people-data.js` + `js/profiles-data.js`.
- **Publications** — update `data/publications.csv`, then
  `python3 scripts/generate-publications.py` → `js/publications-data.js`.

See `data/UPDATE_GUIDE.md` for the monthly update flow.

## Before you open a PR

- Preview locally: `python3 -m http.server 8000` → <http://localhost:8000/>.
- Check the page you touched on desktop, mobile width, and dark mode.
- If you edited roster/publication data, confirm you regenerated the JS.
- No stray files (source dumps, `~$` temp files, `.DS_Store`).
