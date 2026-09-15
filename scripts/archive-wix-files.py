#!/usr/bin/env python3
# Archive the files the old Wix site hosts itself (reprint PDFs, GAPIT docs)
# before the Wix plan is cancelled. Once Wix is gone these are unrecoverable —
# everything else the old site links to is external and survives the cutover.
#
# Usage (from repo root, while www.maizegenetics.net still serves the Wix site):
#   python3 scripts/archive-wix-files.py                 # publications + gapit
#   python3 scripts/archive-wix-files.py --out ~/Desktop/wix-archive
#   python3 scripts/archive-wix-files.py --pages /publications /gapit /tassel
#   python3 scripts/archive-wix-files.py --dry-run       # list, don't download
#
# Output (default _source/wix-archive/, which is gitignored — keep the PDFs in
# Cowork/Drive, not in this repo):
#   <page>/<Year>_<FirstAuthor>_<wixid8>.pdf   one file per Wix document
#   manifest.csv                               wix_id, file, original_name,
#                                              year, doi, citation, page, bytes
#
# Metadata comes from the page itself: Wix embeds the dataset JSON
# (original upload name via docInfo / wix:document URIs) and renders each
# citation in the same <tr> as its PDF icon. Re-running skips files already
# present, so it is safe to resume.
import argparse, csv, html, os, re, sys, time, unicodedata
from urllib.parse import unquote, urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SITE = 'https://www.maizegenetics.net'
UA = 'Mozilla/5.0 (lab_site archive; +https://github.com/maize-genetics/lab_site)'
DEFAULT_PAGES = ['/publications', '/gapit']

# Any Wix-hosted user document, whichever CDN alias the page used for it.
FILE_RE = re.compile(
    r'https?://(?:www\.maizegenetics\.net/_files|docs\.wixstatic\.com|'
    r'[a-z0-9-]+\.filesusr\.com|static\.wixstatic\.com)/ugd/'
    r'([a-f0-9]+_[a-f0-9]+\.(?:pdf|zip|tar|gz|tgz|txt|docx?|xlsx?|pptx?))', re.I)
NAME_RES = [
    re.compile(r'docId\\?":\\?"ugd\\?/([a-f0-9]+_[a-f0-9]+\.\w+)\\?",\\?"name\\?":\\?"([^"\\]+)'),
    re.compile(r'wix:document:\\?/\\?/v1\\?/ugd\\?/([a-f0-9]+_[a-f0-9]+\.\w+)\\?/([^"\\]+)'),
]
YEAR_RE = re.compile(r'\(((?:19|20)\d{2})\)')
BARE_YEAR_RE = re.compile(r'\b((?:19|20)\d{2})\b')
DOI_RE = re.compile(r'10\.\d{4,9}/[^\s"<>]+')
TAG_RE = re.compile(r'<[^>]+>')

def fetch(url, binary=False, retries=3):
    for attempt in range(retries):
        try:
            with urlopen(Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                data = r.read()
                return data if binary else data.decode('utf-8', 'ignore')
        except (HTTPError, URLError, TimeoutError) as e:
            if attempt == retries - 1: raise
            time.sleep(2 * (attempt + 1))

def text(fragment):
    return html.unescape(re.sub(r'\s+', ' ', TAG_RE.sub(' ', fragment))).strip()

def ascii_slug(s, keep='-_'):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^A-Za-z0-9' + re.escape(keep) + ']+', '', s)
    return s or 'x'

def first_author(citation):
    # "Wu Y, Li D, ... (2023)"  ->  "Wu"
    head = citation.split('(')[0]
    head = re.split(r'[,;]', head)[0].strip()
    surname = head.split()[0] if head.split() else ''
    return ascii_slug(surname)[:24] or 'Unknown'

def scan_page(path):
    """Return {wix_id: {url, original_name, citation, year, doi}} for one page."""
    url = urljoin(SITE, path)
    src = fetch(url)
    found = {}
    for m in FILE_RE.finditer(src):
        wid = m.group(1)
        found.setdefault(wid, {'url': m.group(0), 'original_name': '', 'citation': '', 'anchor': '',
                               'year': '', 'doi': '', 'from_row': False})
    if not found:
        return found
    # original upload names, embedded in the dataset JSON
    for rx in NAME_RES:
        for wid, name in rx.findall(src):
            if wid in found and not found[wid]['original_name']:
                found[wid]['original_name'] = unquote(name)
    # citation text: the table row that holds the PDF icon
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', src, flags=re.S):
        ids = {m.group(1) for m in FILE_RE.finditer(row)}
        if not ids: continue
        t = text(row)
        for wid in ids:
            if wid in found and not found[wid]['citation']:
                found[wid]['citation'] = t; found[wid]['from_row'] = True
    # fallback (prose pages like /gapit): the link's anchor text plus the
    # sentence leading up to it
    for wid, rec in found.items():
        m = re.search(r'<a[^>]+href="[^"]*' + re.escape(wid) + r'[^"]*"[^>]*>(.*?)</a>', src, flags=re.S)
        if m: rec['anchor'] = text(m.group(1))
        if rec['citation']: continue
        i = src.find(wid)
        lead = text(src[max(0, i - 1500):i])[-200:]
        rec['citation'] = (lead + ' ' + rec['anchor']).strip()
    for rec in found.values():
        y = YEAR_RE.search(rec['citation']) or BARE_YEAR_RE.search(rec['anchor'] or rec['citation'])
        rec['year'] = y.group(1) if y else ''
        d = DOI_RE.search(rec['citation']); rec['doi'] = d.group(0).rstrip('.') if d else ''
    return found

def target_name(wid, rec):
    ext = os.path.splitext(wid)[1].lower()
    year = rec['year'] or 'undated'
    if rec['from_row']:                       # "Wu Y, Li D, ... (2023) Title" -> Wu
        who = first_author(rec['citation'])
    elif rec['anchor']:                       # "Yu et al. Nature Genetics, 2006" -> Yu-et-al-Nature-Genetics-2006
        who = ascii_slug(re.sub(r'\s+', '-', rec['anchor']))[:40].strip('-')
    elif rec['original_name']:
        who = ascii_slug(os.path.splitext(rec['original_name'])[0])[:40]
    else:
        who = 'file'
    return f"{year}_{who or 'file'}_{wid.split('_')[1][:8]}{ext}"

def main():
    ap = argparse.ArgumentParser(description=__doc__ or '', formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pages', nargs='+', default=DEFAULT_PAGES, help='Wix page paths to scan')
    ap.add_argument('--out', default='_source/wix-archive', help='output folder (default is gitignored)')
    ap.add_argument('--dry-run', action='store_true', help='list files, do not download')
    ap.add_argument('--sleep', type=float, default=0.3, help='pause between downloads (s)')
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    manifest_path = os.path.join(args.out, 'manifest.csv')
    rows, n_ok, n_skip, n_fail = [], 0, 0, 0

    for path in args.pages:
        print(f'== {path}', flush=True)
        try:
            found = scan_page(path)
        except Exception as e:
            print(f'   !! could not fetch {path}: {e}', file=sys.stderr); continue
        print(f'   {len(found)} Wix-hosted file(s)')
        sub = os.path.join(args.out, path.strip('/').replace('/', '_') or 'home')
        if found and not args.dry_run: os.makedirs(sub, exist_ok=True)
        for wid, rec in sorted(found.items(), key=lambda kv: (kv[1]['year'], kv[1]['citation'])):
            fname = target_name(wid, rec)
            dest = os.path.join(sub, fname)
            status, size = 'listed', ''
            if not args.dry_run:
                if os.path.exists(dest) and os.path.getsize(dest) > 0:
                    status, size, n_skip = 'exists', os.path.getsize(dest), n_skip + 1
                else:
                    try:
                        data = fetch(rec['url'], binary=True)
                        if wid.lower().endswith('.pdf') and not data.startswith(b'%PDF'):
                            raise ValueError('response is not a PDF (login wall or HTML error page)')
                        with open(dest, 'wb') as f: f.write(data)
                        status, size, n_ok = 'downloaded', len(data), n_ok + 1
                        time.sleep(args.sleep)
                    except Exception as e:
                        status, n_fail = f'FAILED: {e}', n_fail + 1
            print(f'   {status:<11} {fname}  <- {rec["original_name"] or wid}')
            rows.append({'wix_id': wid, 'file': os.path.relpath(dest, args.out), 'original_name': rec['original_name'],
                         'year': rec['year'], 'doi': rec['doi'], 'citation': rec['citation'][:600],
                         'page': path, 'source_url': rec['url'], 'bytes': size, 'status': status})

    with open(manifest_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['wix_id'])
        w.writeheader(); w.writerows(rows)
    print(f'\n{len(rows)} files listed | {n_ok} downloaded | {n_skip} already present | {n_fail} failed')
    print(f'manifest: {manifest_path}')
    if n_fail: sys.exit(1)

if __name__ == '__main__':
    main()
