#!/usr/bin/env python3
# Archive the lab photos hosted on the per-year Wix sites
# (2008.maizegenetics.net … 2022.maizegenetics.net) and the pre-2008
# buckler-lab-photos.maizegenetics.net before the Wix plan is cancelled. Each
# site is a small Wix photo gallery/album.
#
# Usage (from repo root):
#   python3 scripts/archive-year-photos.py                     # every site below
#   python3 scripts/archive-year-photos.py --sites 2019 2021   # only some years
#   python3 scripts/archive-year-photos.py --sites buckler-lab-photos=2007
#   python3 scripts/archive-year-photos.py --out ~/Desktop/lab-photos
#   python3 scripts/archive-year-photos.py --dry-run           # list, don't download
#
# --sites takes years / ranges (the site <year>.maizegenetics.net, saved under
# <year>/) or <subdomain>=<folder>. The default is 2008-2022 plus
# buckler-lab-photos=2007: that site (titled "2006 - 2007") holds one album
# named "2007" of scanned prints with no per-photo dates.
#
# Output (default _source/year-photos/, which is gitignored — keep the photos in
# Cowork/Drive, not in this repo):
#   <year>/<original file name>      when Wix kept the upload name (2008–2019)
#   <year>/<year>_<wixid8>.<ext>     otherwise (2020–2022, buckler-lab-photos)
#   manifest.csv                     year, site, file, wix_id, source, exif_date, …
#
# How the photos are found: every page in the site's sitemap plus any
# /set/<uuid> album page linked from them is scanned for media owned by the
# lab's Wix account (--owner). 2008–2019 serve the original upload. The
# 2020–2022 "Photo Albums" sites refuse the original (403) and only serve
# token-signed renditions; the largest one is requested at full resolution and
# high quality (its watermark is a 1x1 transparent pixel), so those files are
# full-size re-encodes and carry little or no EXIF. Byte-identical duplicates
# (Wix stores the share-preview copy separately) are skipped. Re-running skips
# files already present, so it is safe to resume.
import argparse, csv, hashlib, html, os, re, struct, sys, time, unicodedata
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

DOMAIN = 'maizegenetics.net'
MEDIA = 'https://static.wixstatic.com/media/'
UA = 'Mozilla/5.0 (lab_site archive; +https://github.com/maize-genetics/lab_site)'
IMG_EXT = r'(?:jpe?g|png|gif|tiff?|bmp|heic)'

LOC_RE = re.compile(r'<loc>\s*([^<\s]+)\s*</loc>')
SET_RE = re.compile(r'/set/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
# Gallery JSON on the 2008–2019 sites: ..."fileName":"2008_Party.JPG","name":"a763bb_…~mv2….jpg"
NAMED_RE = re.compile(r'\\?"fileName\\?":\\?"([^"\\]+)\\?",\\?"name\\?":\\?"([a-z0-9]{6}_[0-9a-f]{32}~mv2[\w]*\.\w+)')

def fetch(url, binary=False, retries=3):
    """Return (final_url, body). 4xx is raised immediately; other errors retry."""
    for attempt in range(retries):
        try:
            with urlopen(Request(url, headers={'User-Agent': UA}), timeout=90) as r:
                data = r.read()
                return r.geturl(), (data if binary else data.decode('utf-8', 'ignore'))
        except HTTPError as e:
            if 400 <= e.code < 500 or attempt == retries - 1: raise
        except (URLError, TimeoutError):
            if attempt == retries - 1: raise
        time.sleep(2 * (attempt + 1))

def image_ext(data):
    if data[:3] == b'\xff\xd8\xff': return '.jpg'
    if data[:8] == b'\x89PNG\r\n\x1a\n': return '.png'
    if data[:4] in (b'GIF8',): return '.gif'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP': return '.webp'
    if data[:4] in (b'II*\x00', b'MM\x00*'): return '.tif'
    return None

def exif_date(data):
    """DateTimeOriginal (or DateTime) from a JPEG's EXIF block, as 'YYYY-MM-DD HH:MM:SS'."""
    if data[:2] != b'\xff\xd8': return ''
    i = 2
    while i + 4 <= len(data) and data[i] == 0xFF:
        marker, size = data[i + 1], struct.unpack('>H', data[i + 2:i + 4])[0]
        if marker == 0xE1 and data[i + 4:i + 10] == b'Exif\x00\x00':
            tiff = data[i + 10:i + 2 + size]
            try: return _tiff_date(tiff)
            except (struct.error, IndexError, ValueError): return ''
        if marker == 0xDA: break
        i += 2 + size
    return ''

def _tiff_date(t):
    e = '<' if t[:2] == b'II' else '>'
    def ifd(off):
        n = struct.unpack(e + 'H', t[off:off + 2])[0]
        for k in range(n):
            tag, typ, cnt, val = struct.unpack(e + 'HHII', t[off + 2 + 12 * k:off + 14 + 12 * k])
            yield tag, typ, cnt, val
    def ascii_at(cnt, val): return t[val:val + cnt].rstrip(b'\x00').decode('ascii', 'ignore')
    ifd0 = struct.unpack(e + 'I', t[4:8])[0]
    found = {}
    for tag, typ, cnt, val in ifd(ifd0):
        if tag == 0x0132 and typ == 2: found['dt'] = ascii_at(cnt, val)
        if tag == 0x8769:
            for tag2, typ2, cnt2, val2 in ifd(val):
                if tag2 in (0x9003, 0x9004) and typ2 == 2: found.setdefault(tag2, ascii_at(cnt2, val2))
    raw = found.get(0x9003) or found.get(0x9004) or found.get('dt') or ''
    m = re.match(r'(\d{4}):(\d{2}):(\d{2}) (\d{2}:\d{2}:\d{2})', raw)
    return f'{m[1]}-{m[2]}-{m[3]} {m[4]}' if m and m[1] != '0000' else ''

def safe_name(name):
    stem, ext = os.path.splitext(name)
    stem = unicodedata.normalize('NFKD', stem).encode('ascii', 'ignore').decode()
    stem = re.sub(r'[^A-Za-z0-9._-]+', '_', stem).strip('._') or 'photo'
    return stem[:80], ext.lower()

def site_pages(subdomain):
    """Home page + every sitemap page, plus /set/ album pages linked from them."""
    home, src = fetch(f'https://{subdomain}.{DOMAIN}/')
    base = f'{urlparse(home).scheme}://{urlparse(home).netloc}'
    pages = {home.rstrip('/') or base: src}
    try:
        _, idx = fetch(base + '/sitemap.xml')
        locs = []
        for sm in LOC_RE.findall(idx):
            sm = html.unescape(sm)
            if sm.endswith('.xml'): locs += LOC_RE.findall(fetch(sm)[1])
            else: locs.append(sm)
    except (HTTPError, URLError) as e:
        print(f'   (no sitemap: {e})'); locs = []
    queue = [html.unescape(l).rstrip('/') for l in locs]
    while queue:
        url = queue.pop(0)
        if url in pages or urlparse(url).netloc != urlparse(base).netloc: continue
        try: pages[url] = fetch(url)[1]
        except (HTTPError, URLError) as e:
            print(f'   !! {url}: {e}', file=sys.stderr); continue
    for url, s in list(pages.items()):
        for path in set(SET_RE.findall(s)):
            u = base + path
            if u not in pages:
                try: pages[u] = fetch(u)[1]
                except (HTTPError, URLError) as e: print(f'   !! {u}: {e}', file=sys.stderr)
    return pages

def scan(pages, owner):
    """{key: {name, file_name, signed, unsigned, pages}} for every photo owned by `owner`."""
    id_re = re.compile(owner + r'_([0-9a-f]{32})~mv2[\w]*\.' + IMG_EXT + r'\b', re.I)
    rend_re = re.compile(r'https://static\.wixstatic\.com/media/(' + owner + r'_([0-9a-f]{32})~mv2[\w]*\.\w+)'
                         r'/v1/(?:fill|fit)/w_(\d+),h_(\d+)[^/"\s]*/[^?"\s,]+(?:\?token=([\w.-]+))?')
    found = {}
    def rec(key): return found.setdefault(key, {'name': '', 'file_name': '', 'signed': None, 'unsigned': None, 'pages': set()})
    for url, s in pages.items():
        path = urlparse(url).path or '/'
        for m in id_re.finditer(s):
            r = rec(m.group(1)); r['pages'].add(path)
            if not r['name']: r['name'] = m.group(0)
        for fname, name in NAMED_RE.findall(s):
            m = id_re.match(name)
            if m: r = rec(m.group(1)); r['file_name'] = r['file_name'] or html.unescape(fname); r['name'] = name
        for m in rend_re.finditer(s):
            name, key, w, h, tok = m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), m.group(5)
            if name.lower().endswith('.webp'): continue
            r = rec(key); slot = 'signed' if tok else 'unsigned'
            if r[slot] is None or w * h > r[slot][1] * r[slot][2]:
                r[slot] = (name, w, h, tok)
            if not r['name']: r['name'] = name
    return found

def download(rec, quality):
    """Return (bytes, source) — the original if public, else the largest signed rendition."""
    tried = []
    try:
        return fetch(MEDIA + rec['name'], binary=True)[1], 'original'
    except HTTPError as e: tried.append(f'original {e.code}')
    if rec['signed']:
        name, w, h, tok = rec['signed']
        url = f'{MEDIA}{name}/v1/fill/w_{w},h_{h},q_{quality}/{name}?token={tok}'
        try: return fetch(url, binary=True)[1], f'signed rendition {w}x{h}'
        except HTTPError as e: tried.append(f'signed {e.code}')
    if rec['unsigned']:
        name, w, h, _ = rec['unsigned']
        url = f'{MEDIA}{name}/v1/fit/w_{w},h_{h},q_{quality}/{name}'
        try: return fetch(url, binary=True)[1], f'rendition {w}x{h} (not full size)'
        except HTTPError as e: tried.append(f'rendition {e.code}')
    raise ValueError('; '.join(tried) or 'no downloadable URL')

def site_list(vals):
    """[(subdomain, folder)] from '2008-2012', '2019' or 'buckler-lab-photos=2007'."""
    sites = []
    for v in vals:
        if '=' in v:
            sub, _, folder = v.partition('=')
            sites.append((sub, folder))
        elif re.fullmatch(r'\d{4}(-\d{4})?', v):
            a, _, b = v.partition('-')
            sites += [(str(y), str(y)) for y in range(int(a), int(b or a) + 1)]
        else:
            sys.exit(f'bad --sites value {v!r}: use a year, a range, or subdomain=folder')
    return sorted(set(sites), key=lambda s: (s[1], s[0]))

def main():
    ap = argparse.ArgumentParser(description='Archive photos from the 20xx.maizegenetics.net Wix sites.')
    ap.add_argument('--sites', '--years', nargs='+', default=['2008-2022', 'buckler-lab-photos=2007'],
                    help='years, ranges, or subdomain=folder, e.g. 2008-2012 2019 buckler-lab-photos=2007')
    ap.add_argument('--out', default='_source/year-photos', help='output folder (default is gitignored)')
    ap.add_argument('--owner', default='a763bb', help="lab's Wix media-owner prefix (filters out template stock images)")
    ap.add_argument('--quality', type=int, default=95, help='JPEG quality for signed renditions (2020–2022)')
    ap.add_argument('--dry-run', action='store_true', help='list photos, do not download')
    ap.add_argument('--sleep', type=float, default=0.3, help='pause between downloads (s)')
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rows, n_ok, n_skip, n_dup, n_fail = [], 0, 0, 0, 0
    for subdomain, year in site_list(args.sites):
        print(f'== {subdomain}.{DOMAIN}  ->  {year}/', flush=True)
        try:
            pages = site_pages(subdomain)
        except Exception as e:
            print(f'   !! could not fetch site: {e}', file=sys.stderr); n_fail += 1; continue
        found = scan(pages, args.owner)
        print(f'   {len(pages)} page(s), {len(found)} candidate image(s)')
        sub = os.path.join(args.out, year)
        if found and not args.dry_run: os.makedirs(sub, exist_ok=True)
        seen = {}                                       # sha256 -> file already kept this year
        used = set(os.listdir(sub)) if os.path.isdir(sub) else set()
        # named gallery items first, so a byte-identical share copy dedupes onto the named file
        for key, rec in sorted(found.items(), key=lambda kv: (not kv[1]['file_name'], kv[1]['name'])):
            if rec['file_name']: stem, ext = safe_name(rec['file_name'])
            else: stem, ext = f'{year}_{key[:8]}', os.path.splitext(rec['name'])[1].lower()
            prior = next((f for f in used if f.startswith(stem + '.') or f.startswith(f'{stem}_{key[:8]}.')), None)
            row = {'year': year, 'site': f'{subdomain}.{DOMAIN}', 'file': '', 'wix_id': rec['name'], 'original_name': rec['file_name'],
                   'source': '', 'exif_date': '', 'bytes': '', 'pages': ' '.join(sorted(rec['pages'])), 'status': 'listed'}
            if args.dry_run:
                row['source'] = 'original' if not rec['signed'] else 'original or signed rendition'
            elif prior:
                data = open(os.path.join(sub, prior), 'rb').read()
                h = hashlib.sha256(data).hexdigest()
                if h in seen: row.update(status=f'duplicate of {seen[h]}'); n_dup += 1
                else:
                    seen[h] = prior; n_skip += 1
                    row.update(file=f'{year}/{prior}', status='exists', bytes=len(data), exif_date=exif_date(data))
            else:
                try:
                    data, source = download(rec, args.quality)
                    real_ext = image_ext(data)
                    if not real_ext: raise ValueError('response is not an image')
                    h = hashlib.sha256(data).hexdigest()
                    row['source'] = source
                    if h in seen:
                        row.update(status=f'duplicate of {seen[h]}'); n_dup += 1
                    else:
                        if real_ext != '.jpg' or ext not in ('.jpg', '.jpeg'): ext = real_ext
                        fname = stem + ext
                        if fname in used: fname = f'{stem}_{key[:8]}{ext}'
                        with open(os.path.join(sub, fname), 'wb') as f: f.write(data)
                        used.add(fname); seen[h] = fname; n_ok += 1
                        row.update(file=f'{year}/{fname}', status='downloaded', bytes=len(data), exif_date=exif_date(data))
                    time.sleep(args.sleep)
                except Exception as e:
                    row['status'] = f'FAILED: {e}'; n_fail += 1
            note = ''
            if row['exif_date'] and not row['exif_date'].startswith(str(year)):
                note = f'  (EXIF says {row["exif_date"][:10]})'
            print(f'   {row["status"]:<11} {row["file"] or rec["file_name"] or rec["name"]}{note}')
            rows.append(row)

    manifest = os.path.join(args.out, 'manifest.csv')
    with open(manifest, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ['year'])
        w.writeheader(); w.writerows(rows)
    print(f'\n{len(rows)} images | {n_ok} downloaded | {n_skip} already present | '
          f'{n_dup} duplicates skipped | {n_fail} failed')
    print(f'manifest: {manifest}')
    if n_fail: sys.exit(1)

if __name__ == '__main__':
    main()
