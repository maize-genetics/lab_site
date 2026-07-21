#!/usr/bin/env python3
"""Merge scraped person-profile blocks into scraped_people.json.

Reads stdin blocks of the form:
    @@@ <slug>
    NAME: ...
    TITLE: ...
    BIO: ...
    EMAIL: ...
    WEBSITE: ...
    SCHOLAR: ...
    ORCID: ...
    LINKEDIN: ...
    TWITTER: ...
    PHOTO: ...
Each field 'NONE' becomes null. Photo URL is normalized to its full-res base.
Re-running updates existing slugs. Usage: python3 parse_scrape.py < batch.txt
"""
import json, re, sys, os

HERE = os.path.dirname(__file__)
STORE = os.path.join(HERE, "scraped_people.json")
FIELDS = ["name","title","bio","email","website","scholar","orcid","linkedin","twitter","photo"]

def photo_base(url):
    if not url: return None
    # https://static.wixstatic.com/media/<id>/v1/fill/... -> strip transform
    m = re.match(r"(https://static\.wixstatic\.com/media/[^/]+)", url)
    return m.group(1) if m else url

def clean(v):
    v = v.strip()
    return None if v.upper() == "NONE" or v == "" else v

def main():
    data = json.load(open(STORE)) if os.path.exists(STORE) else {}
    text = sys.stdin.read()
    blocks = re.split(r"(?m)^@@@\s+", text)
    added = 0
    for b in blocks:
        b = b.strip()
        if not b: continue
        lines = b.splitlines()
        slug = lines[0].strip()
        rec = {}
        for ln in lines[1:]:
            m = re.match(r"([A-Za-z]+):\s?(.*)", ln)
            if not m: continue
            k = m.group(1).lower()
            if k in FIELDS:
                rec[k] = clean(m.group(2))
        if "photo" in rec:
            rec["photo"] = photo_base(rec.get("photo"))
        if rec.get("name"):
            data[slug] = rec
            added += 1
    json.dump(data, open(STORE, "w"), indent=1, ensure_ascii=False)
    print(f"merged {added} record(s); total {len(data)}")

if __name__ == "__main__":
    main()
