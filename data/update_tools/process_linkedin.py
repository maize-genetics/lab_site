#!/usr/bin/env python3
"""Collapse the per-affiliation Cornell/NCSU LinkedIn CSV to one record per
person and merge the RELIABLE fields into people-roster.xlsx.

The CSV only contains Cornell/NCSU affiliations (lab tenure), so:
  - LinkedIn URL      -> filled where the roster cell is empty
  - Start / End year  -> filled where empty (min start / latest end across the
                          person's valid Cornell/NCSU rows); never overwritten
  - Current position  -> NOT touched (this file has no post-lab jobs)

CSV columns: Name, LinkedIn URL, Institution, Role, Start, End, Notes
Dry run by default; pass --write to apply. --add-new also appends roster rows
for people not already present (LinkedIn + years only).
"""
import csv, re, sys, os
import openpyxl

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CSV = os.path.join(ROOT, "data", "Cornell_NCSU_LinkedIn_260718.csv")
ROSTER = os.path.join(ROOT, "data", "people-roster.xlsx")

# CSV spelling/accent variants -> exact roster name
NAME_OVERRIDES = {
    "Niranjani Gnanaprasagam": "Niranjani Gnanapragasam",
    "Yógesh Ramdoss": "Yogesh Ramdoss",
    "Jorge Alberto Romero (Navarro)": "Jorge Alberto Romero",
    "Beth Kraft Sant": "Beth Kraft Sant",
}
BAD = ("NOT FOUND", "NOT CONFIDENTLY FOUND", "N/A", "")

def norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())
def loose(s):
    t = [w for w in re.sub(r"[^a-z ]", " ", (s or "").lower()).split() if len(w) > 1]
    return (t[-1] + t[0][0]) if t else ""
def norm_url(u):
    u = (u or "").strip()
    return None if not u else (u if u.startswith("http") else "https://" + u)
def yr(v):
    m = re.search(r"\d{4}", v or ""); return int(m.group()) if m else None

def collapse():
    people = {}
    with open(CSV, newline='', encoding='utf-8', errors='replace') as fh:
        for row in csv.DictReader(fh):
            nm = (row.get("Name") or "").strip()
            if not nm: continue
            p = people.setdefault(nm, {"linkedin": None, "starts": [], "ends": [], "present": False})
            if not p["linkedin"]:
                p["linkedin"] = norm_url(row.get("LinkedIn URL"))
            inst = (row.get("Institution") or "").strip().upper()
            if inst in BAD: continue           # skip unfound affiliations for years
            s = yr(row.get("Start"))
            if s: p["starts"].append(s)
            e = (row.get("End") or "").strip().lower()
            if e in ("present", "current", "now"): p["present"] = True
            elif yr(e): p["ends"].append(yr(e))
    for p in people.values():
        p["start"] = min(p["starts"]) if p["starts"] else None
        p["end"] = "present" if p["present"] else (max(p["ends"]) if p["ends"] else None)
    return people

def main():
    write = "--write" in sys.argv
    add_new = "--add-new" in sys.argv
    people = collapse()
    wb = openpyxl.load_workbook(ROSTER); ws = wb.active
    H = [c.value for c in ws[1]]; col = {h: i for i, h in enumerate(H)}
    bn, bl = {}, {}
    for r in ws.iter_rows(min_row=2):
        v = r[col["Name"]].value
        if v: bn.setdefault(norm(v), r); bl.setdefault(loose(str(v)), r)

    def find(nm):
        tgt = NAME_OVERRIDES.get(nm, nm)
        return bn.get(norm(tgt)) or bl.get(loose(tgt))

    li = st = en = 0; newp = []
    for nm, p in people.items():
        r = find(nm)
        if r is None: newp.append(nm); continue
        if p["linkedin"] and not str(r[col["LinkedIn"]].value or "").strip():
            li += 1
            if write: r[col["LinkedIn"]].value = p["linkedin"]
        if p["start"] and not str(r[col["Start year"]].value or "").strip():
            st += 1
            if write: r[col["Start year"]].value = p["start"]
        if p["end"] and not str(r[col["End year"]].value or "").strip():
            en += 1
            if write: r[col["End year"]].value = p["end"]

    print(f"unique people in CSV: {len(people)}")
    print(f"LinkedIn URLs filled (empty cells): {li}")
    print(f"Start years filled (were blank): {st}")
    print(f"End years filled (were blank): {en}")
    print(f"not in roster: {len(newp)} -> {sorted(newp)}")

    if add_new and write:
        for nm in newp:
            p = people[nm]
            row = [None] * len(H)
            row[col["Name"]] = nm
            row[col["Role"]] = "visiting"
            if p["start"]: row[col["Start year"]] = p["start"]
            if p["end"]: row[col["End year"]] = p["end"]
            if p["linkedin"]: row[col["LinkedIn"]] = p["linkedin"]
            ws.append(row)
        print(f"appended {len(newp)} new rows")

    if write:
        wb.save(ROSTER); print("roster saved.")
    else:
        print("\n(dry run — pass --write to apply; add --add-new to append new people)")

if __name__ == "__main__":
    main()
