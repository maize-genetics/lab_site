#!/usr/bin/env python3
# Build the "lab through the years" gallery from the archived Wix photo sites.
#
#   _source/year-photos/<year>/*  ->  images/years/<year>/<name>.jpg       (lightbox)
#                                     images/years/<year>/<name>-thumb.jpg (grid)
#                                     js/year-photos-data.js  (window.LAB_YEAR_PHOTOS)
#
# The originals (~305 MB, 2–6 MB each) come from scripts/archive-year-photos.py
# and live in the gitignored _source/ tree, so the site can't serve them
# directly; this writes web-sized copies that are small enough to commit.
#
# Usage (from repo root):
#   python3 scripts/build-year-photos.py              # only what's missing/stale
#   python3 scripts/build-year-photos.py --force      # re-encode everything
#   python3 scripts/build-year-photos.py --years 2019 2021
#
# Needs ImageMagick (`magick`) or, as a fallback, macOS `sips`. Stdlib only.
import argparse, csv, os, re, shutil, subprocess, sys

SRC = '_source/year-photos'
MANIFEST = os.path.join(SRC, 'manifest.csv')
OUT_IMG = 'images/years'
OUT_DATA = 'js/year-photos-data.js'
FULL_MAX, FULL_Q = 1600, 78
THUMB_MAX, THUMB_Q = 600, 76

# Words kept as-is when humanising a file name into a caption.
ACRONYMS = {'gbs', 'usda', 'cbsu', 'ncsu', 'phg', 'nsf', 'ars'}
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']

# File names the humaniser can't do justice to. Keyed by the source stem.
CAPTIONS = {
    '2008_LabWithHuihui': 'The lab with Huihui',
    '2008_SeedPacking.AntHill': 'Seed packing at Ant Hill',
    '2011_lab_group_at_MaizeExhibitDebut': 'Lab group at the maize exhibit debut',
    '2013_Spring_GBS_Workshop_CBSU': 'Spring GBS workshop — CBSU',
    '2013_Spring_GBS_Workshop_Ed': 'Spring GBS workshop — Ed',
    '2013_Spring_GBS_Workshop_Jeff': 'Spring GBS workshop — Jeff',
    '2013_Spring_GBS_Workshop_Terry': 'Spring GBS workshop — Terry',
    '2013_Planting_Nick_Rob': 'Planting — Nick and Rob',
    'BucklergroupphotoatMusgrave2016': 'Buckler group photo at Musgrave',
}

# Stems that carry no meaning: Wix hashes, camera/phone export names, UUIDs.
NO_CAPTION = re.compile(r"""^(
    [0-9a-f]{8} |
    [0-9A-F]{8}(-[0-9A-F]{4}){3}-[0-9A-F]{12}(_\d+)? |
    img[-_ ]?\d+ |
    image[ _]from[ _]ios([ _]\d+)? |
    dsc[-_ ]?\d+
)$""", re.VERBOSE | re.IGNORECASE)


def slugify(s):
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', s.lower()))


def humanize(stem, year):
    """Turn a source file stem into a caption, or '' if it carries no meaning."""
    if stem in CAPTIONS:
        return CAPTIONS[stem]
    rest = re.sub(r'^%s[._\s-]*' % year, '', stem)
    if not rest or NO_CAPTION.match(rest):
        return ''
    # 2010_0520, 2011_1014 — the shoot date as MMDD.
    if re.fullmatch(r'\d{4}', rest):
        month, day = int(rest[:2]), int(rest[2:])
        if 1 <= month <= 12 and 1 <= day <= 31:
            return '%s %d' % (MONTHS[month - 1], day)
    rest = rest.replace('_s_', "'s ")                      # Judy_s_Day
    rest = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', rest)       # PlantingDayCrew
    rest = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', rest)       # Hackathon2
    words = [w for w in re.split(r'[\s._-]+', rest) if w]
    while words and re.fullmatch(r'\d{1,4}', words[-1]):   # trailing counters/years
        words.pop()
    if not words:
        return ''
    # Source capitalisation is meaningful (names vs. verbs), so only the first
    # word and known acronyms are recased.
    out = [w.upper() if w.lower() in ACRONYMS else w for w in words]
    out[0] = out[0][0].upper() + out[0][1:]
    return re.sub(r'\s+', ' ', ' '.join(out)).strip()


class Converter:
    """Resize + re-encode to JPEG, honouring EXIF orientation."""

    def __init__(self):
        self.magick = shutil.which('magick') or shutil.which('convert')
        self.sips = shutil.which('sips')
        if not (self.magick or self.sips):
            sys.exit('need ImageMagick (magick) or macOS sips on PATH')

    def convert(self, src, dst, long_edge, quality):
        if self.magick:
            subprocess.run([self.magick, src, '-auto-orient',
                            '-resize', '%dx%d>' % (long_edge, long_edge),
                            '-strip', '-interlace', 'Plane', '-quality', str(quality), dst],
                           check=True, capture_output=True)
        else:
            subprocess.run([self.sips, '-s', 'format', 'jpeg',
                            '-s', 'formatOptions', str(quality),
                            '--rotate', '0', '--resampleHeightWidthMax', str(long_edge),
                            src, '--out', dst], check=True, capture_output=True)

    def size(self, path):
        if self.magick:
            out = subprocess.run([self.magick, 'identify', '-format', '%w %h', path],
                                 check=True, capture_output=True, text=True).stdout
            w, h = out.split()
        else:
            out = subprocess.run([self.sips, '-g', 'pixelWidth', '-g', 'pixelHeight', path],
                                 check=True, capture_output=True, text=True).stdout
            w = re.search(r'pixelWidth: (\d+)', out).group(1)
            h = re.search(r'pixelHeight: (\d+)', out).group(1)
        return int(w), int(h)


def exif_dates():
    """file path (relative to _source/year-photos) -> EXIF date, from the archive manifest."""
    if not os.path.exists(MANIFEST):
        return {}
    with open(MANIFEST, encoding='utf-8') as fh:
        return {r['file']: (r.get('exif_date') or '')
                for r in csv.DictReader(fh) if r.get('file')}


def esc(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--years', nargs='*', help='only these years (default: all)')
    ap.add_argument('--force', action='store_true', help='re-encode even if up to date')
    args = ap.parse_args()

    if not os.path.isdir(SRC):
        sys.exit('%s not found — run scripts/archive-year-photos.py first' % SRC)
    conv = Converter()
    dates = exif_dates()
    years = sorted(d for d in os.listdir(SRC)
                   if re.fullmatch(r'\d{4}', d) and (not args.years or d in args.years))

    built = skipped = 0
    out_years = []
    for year in years:
        src_dir = os.path.join(SRC, year)
        out_dir = os.path.join(OUT_IMG, year)
        os.makedirs(out_dir, exist_ok=True)
        photos = []
        for name in sorted(os.listdir(src_dir)):
            if not name.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            src = os.path.join(src_dir, name)
            stem = os.path.splitext(name)[0]
            base = slugify(stem)
            full = os.path.join(out_dir, base + '.jpg')
            thumb = os.path.join(out_dir, base + '-thumb.jpg')
            stale = args.force or not os.path.exists(full) or not os.path.exists(thumb) \
                or os.path.getmtime(src) > os.path.getmtime(full)
            if stale:
                conv.convert(src, full, FULL_MAX, FULL_Q)
                conv.convert(src, thumb, THUMB_MAX, THUMB_Q)
                built += 1
                print('  %s/%s' % (year, base))
            else:
                skipped += 1
            w, h = conv.size(full)
            photos.append({
                'src': full, 'thumb': thumb, 'w': w, 'h': h,
                'caption': humanize(stem, year),
                'sort': (dates.get('%s/%s' % (year, name)) or '~') + name,
            })
        if photos:
            photos.sort(key=lambda p: p['sort'])
            out_years.append({'year': year, 'photos': photos})

    total = sum(len(y['photos']) for y in out_years)
    lines = ["/* ============================================================",
             '   Lab photos by year — drives photos.html.',
             '   GENERATED by scripts/build-year-photos.py from _source/year-photos/',
             '   (the gitignored originals archived off the old Wix per-year sites).',
             '   Schema: { year, photos:[{ src, thumb, w, h, caption }] }',
             '   ============================================================ */',
             '',
             'window.LAB_YEAR_PHOTOS = [']
    for y in out_years:
        lines.append("  { year:%s, photos:[" % y['year'])
        for p in y['photos']:
            lines.append("    { src:'%s', thumb:'%s', w:%d, h:%d, caption:'%s' },"
                         % (esc(p['src']), esc(p['thumb']), p['w'], p['h'], esc(p['caption'])))
        lines.append('  ] },')
    lines += ['];', '']
    with open(OUT_DATA, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))

    print('%d photos across %d years (%d encoded, %d already current)'
          % (total, len(out_years), built, skipped))
    print('wrote %s' % OUT_DATA)


if __name__ == '__main__':
    main()
