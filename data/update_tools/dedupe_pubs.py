#!/usr/bin/env python3
"""Deduplicate the raw Google Scholar exports into canonical publication files.

Inputs (raw exports you drop in the data folder each update):
  - pubs.bib                        (BibTeX export)
  - buckler_citations_<YYMMDD>.csv  (CSV export; newest one is used)

Outputs (canonical, what the website reads):
  - publications.bib
  - publications.csv

Dedup key = normalized title (accents/punctuation/case stripped).
Run:  python3 dedupe_pubs.py
"""
import re, csv, glob, os, unicodedata

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def norm(t):
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()

def dedupe_bib():
    src = os.path.join(DATA, "pubs.bib")
    if not os.path.exists(src):
        print("skip bib: pubs.bib not found"); return
    txt = open(src, encoding="utf-8").read()
    parts = [p.strip() for p in re.split(r"(?=^@)", txt, flags=re.M) if p.strip().startswith("@")]
    seen, kept, removed = set(), [], 0
    for p in parts:
        tm = re.search(r"title=\{(.+?)\}", p, re.S)
        key = norm(tm.group(1)) if tm else p[:40]
        if key in seen:
            removed += 1; continue
        seen.add(key); kept.append(p)
    out = os.path.join(DATA, "publications.bib")
    open(out, "w", encoding="utf-8").write("\n\n".join(kept) + "\n")
    print(f"publications.bib: kept {len(kept)}, removed {removed} duplicates")

def dedupe_csv():
    cands = sorted(glob.glob(os.path.join(DATA, "buckler_citations_*.csv")))
    if not cands:
        print("skip csv: no buckler_citations_*.csv found"); return
    src = cands[-1]  # newest by name (YYMMDD sorts correctly)
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    seen, out, removed = set(), [], 0
    for r in rows:
        k = norm(r.get("Title", ""))
        if k in seen:
            removed += 1; continue
        seen.add(k); out.append(r)
    dst = os.path.join(DATA, "publications.csv")
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(out)
    print(f"publications.csv: kept {len(out)}, removed {removed} duplicates (from {os.path.basename(src)})")

if __name__ == "__main__":
    dedupe_bib()
    dedupe_csv()
