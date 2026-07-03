#!/usr/bin/env python3
"""Build people.csv for the Buckler lab site.

Roster comes from the CV's three personnel groups (Postdoctoral Researchers,
Graduate Students, Visiting Scientists). Lab years are INFERRED from
co-authorship years in pubs.bib using Ed's heuristic: a person was in the lab
starting ~2 years before their first co-authored paper, through their last.
current_position is filled from the lab alumni page / known facts where
reliable, else left blank for later review.
"""
import re, csv, unicodedata

import os
DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIB = os.path.join(DATA, "publications.bib") if os.path.exists(os.path.join(DATA,"publications.bib")) else os.path.join(DATA, "pubs.bib")
OUT = os.path.join(DATA, "people.csv")
CURRENT_YEAR = 2026
PRESENT_CUTOFF = 2025  # last co-auth year >= this -> "present"

postdocs = [
    ("Nonoy Bandillo","Bandillo","N","Associate Professor, North Dakota State University"),
    ("Lara Brindisi","Brindisi","L",""),
    ("Patrick Brown","Brown","P","Associate Professor, UC Davis"),
    ("Charles Chen","Chen","C","Associate Professor, Oklahoma State University"),
    ("Shu-Yun Chen","Chen","S",""),
    ("Emre Cimen","Cimen","E",""),
    ("Germano Costa-Neto","Costa-Neto","G",""),
    ("Elhan Ersoz","Ersoz","E",""),
    ("Joseph Gage","Gage","J","Assistant Professor, North Carolina State University"),
    ("Sherry Flint-Garcia","Flint-Garcia","S","Research Geneticist, USDA-ARS; Adjunct Professor, University of Missouri"),
    ("Christy Gault","Gault","C",""),
    ("Anju Giri","Giri","A",""),
    ("Niranjani Gnanapragasam","Gnanapragasam","N",""),
    ("Amit Gur","Gur","A",""),
    ("Carlos Harjes","Harjes","C",""),
    ("Sheng-Kai Hsu","Hsu","S",""),
    ("Matias Kirst","Kirst","M","Professor, University of Florida"),
    ("Omry Koren","Koren","O","Professor, Bar-Ilan University"),
    ("Wei-Yun Lai","Lai","W",""),
    ("Bo Li","Li","B",""),
    ("Huihui Li","Li","H",""),
    ("Alex Lipka","Lipka","A","Professor, University of Illinois Urbana-Champaign"),
    ("Yun Luo","Luo","Y",""),
    ("Fei Lu","Lu","F","Professor, Chinese Academy of Sciences"),
    ("Maria Katherine Mejia-Guerra","Mejia-Guerra","M",""),
    ("Brandon Monier","Monier","B",""),
    ("Sean Myles","Myles","S","Professor, Dalhousie University"),
    ("Jonathan Ojeda","Ojeda","J",""),
    ("Elad Oren","Oren","E",""),
    ("Gael Pressoir","Pressoir","G",""),
    ("Ramu Punna","Punna","R",""),
    ("Guillaume Ramstein","Ramstein","G","Assistant Professor, Aarhus University"),
    ("David Remington","Remington","D","Associate Professor, UNC Greensboro"),
    ("Eli Rodgers-Melnick","Rodgers-Melnick","E",""),
    ("M. Cinta Romay","Romay","M","Research Associate, Cornell University (IGD)"),
    ("Moira Sheehan","Sheehan","M",""),
    ("Nisha Singh","Singh","N",""),
    ("Baoxing Song","Song","B","Principal Investigator, Peking University"),
    ("Michelle Stitzer","Stitzer","M",""),
    ("Jeff Thornsberry","Thornsberry","J",""),
    ("Feng Tian","Tian","F","Professor, China Agricultural University"),
    ("Ravi Valluru","Valluru","R","Lecturer, University of Lincoln"),
    ("Irie Vroh Bi","Bi","I",""),
    ("Jason Wallace","Wallace","J","Associate Professor, University of Georgia"),
    ("Hai Wang","Wang","H","Associate Professor, China Agricultural University"),
    ("Jacob Washburn","Washburn","J","Research Geneticist, USDA-ARS"),
    ("Yaoyao Wu","Wu","Y",""),
    ("Jianbing Yan","Yan","J","Professor, Huazhong Agricultural University"),
    ("Jianming Yu","Yu","J","Professor, Iowa State University"),
    ("Jingjing Zhai","Zhai","J",""),
    ("Dong Zhang","Zhang","D",""),
    ("Nengyi Zhang","Zhang","N",""),
    ("Zhiwu Zhang","Zhang","Z","Professor, Washington State University"),
    ("Tao Zuo","Zuo","T",""),
]
grads = [
    ("Szu-Ping Chen","Chen","S",""),
    ("Henry Dawson","Dawson","H",""),
    ("Mohamed El-Walid","El-Walid","M",""),
    ("Taylor Ferebee","Ferebee","T",""),
    ("Michael Gore","Gore","M","Professor, Cornell University"),
    ("Charles Hale","Hale","C",""),
    ("Tiffany A Ho","Ho","T",""),
    ("Sarah Jensen","Jensen","S",""),
    ("Merritt Khaipho-Burch","Khaipho-Burch","M",""),
    ("Beatrice Konadu","Konadu","B",""),
    ("Karl Kremling","Kremling","K",""),
    ("Sara Larsson","Larsson","S",""),
    ("Zong-Yan Liu","Liu","Z",""),
    ("Evan Long","Long","E",""),
    ("Jason Peiffer","Peiffer","J",""),
    ("Evan Rees","Rees","E",""),
    ("Jorge Alberto Romero","Romero","J",""),
    ("Travis Rooney","Rooney","T",""),
    ("Beth Kraft Saft","Saft","B",""),
    ("Aimee Schulz","Schulz","A",""),
    ("Kelly Swarts","Swarts","K","Assistant Professor, Wageningen University"),
    ("Arcadio Valdes Franco","Valdes","A",""),
    ("Larissa Wilson","Wilson","L",""),
    ("Travis Wrightsman","Wrightsman","T",""),
]
visiting = [
    ("Ijeoma Akaogu","Akaogu","I",""),
    ("Dong An","An","D",""),
    ("Henry Cordoba-Nooa","Cordoba","H",""),
    ("Victor Chavez Bulmaro Coutino","Coutino","V",""),
    ("Mingqiu Dai","Dai","M","Professor, Huazhong Agricultural University"),
    ("Felix Enciso-Rodriguez","Enciso","F",""),
    ("Elisabeth Esch","Esch","E",""),
    ("Williams Esuma","Esuma","W",""),
    ("Meng Huang","Huang","M",""),
    ("Roland Kolliker","Kolliker","R","Professor, ETH Zurich"),
    ("Meng Li","Li","M",""),
    ("Xiaolei Lu","Lu","X",""),
    ("Rajneesh Paliwal","Paliwal","R",""),
    ("Vittorio Pipoli","Pipoli","V",""),
    ("Torsten Pook","Pook","T","Assistant Professor, University of Goettingen"),
    ("Carlos Alexandre Gomes Ribeiro","Ribeiro","C",""),
    ("Abdoul-Aziz Saidou","Saidou","A",""),
    ("Trushar Shah","Shah","T",""),
    ("Ram Kumar Sharma","Sharma","R",""),
    ("Kenta Shirasawa","Shirasawa","K","Senior Researcher, Kazusa DNA Research Institute"),
    ("Mehraj Sofi","Sofi","M",""),
    ("Benjamin Stich","Stich","B","Professor, Heinrich Heine University Duesseldorf"),
    ("Mei-Hsiu Su","Su","M",""),
    ("Carlos Ligne Calderon Vazquez","Calderon","C",""),
    ("Qishan Wang","Wang","Q",""),
    ("Marilyn Warburton","Warburton","M","Research Geneticist, USDA-ARS"),
    ("Penghao Wu","Wu","P",""),
    ("Qiang Xu","Xu","Q",""),
    ("Feiyan Yan","Yan","F",""),
    ("Hongliang Zhang","Zhang","H",""),
    ("Xiao Zhang","Zhang","X",""),
]
# Professional staff (programmers, technicians, admins, staff scientists).
# Publishing staff get years from co-authorship inference; the rest rely on the
# MANUAL overrides below or are left blank for review.
staff = [
    ("Ana Berthel","Berthel","A","Programmer, USDA-ARS"),
    ("Sarah McMorrow","McMorrow","S","Bioinformatics, USDA-ARS"),
    ("Thuy La","La","T","Technician, USDA-ARS"),
    ("Sara Miller","Miller","S","Business Director"),
    ("Zack Miller","Miller","Z","Programmer, USDA-ARS"),
    ("Nick Lepak","Lepak","N","Field Manager, USDA-ARS"),
    ("Bethany Econopouly","Econopouly","B","International Applied Genomics Lead, Breeding Insight"),
    ("Terry Casstevens","Casstevens","T","Retired (formerly Bioinformatics Lead)"),
    ("Peter Bradbury","Bradbury","P","Computational Biologist, USDA-ARS"),
    ("Jeff Glaubitz","Glaubitz","J",""),
    ("Rob Elshire","Elshire","R","Founder, Elshire Group Ltd."),
    ("Dallas E. Kroon","Kroon","D",""),
    ("Yogesh Ramdoss","Ramdoss","Y",""),
    ("Denise Costich","Costich","D","Retired (formerly CIMMYT Maize Germplasm Bank)"),
    ("Lynn Johnson","Johnson","L","Statistical Consultant, Cornell University"),
    ("Nick Kaczmar","Kaczmar","N",""),
    ("Brad Rauh","Rauh","B",""),
    ("Janu Verma","Verma","J",""),
    ("Arturo Garcia","Garcia","A",""),
    ("James Harriman","Harriman","J",""),
    ("Matthew Wiese","Wiese","M",""),
    ("George Day","Day","G",""),
    ("Josh Budka","Budka","J",""),
    ("Heather Mose-Yates","Mose-Yates","H",""),
    ("Susan Romero","Romero","S",""),
    ("Natalie Stevens","Stevens","N",""),
    ("Sherry Whitt","Whitt","S",""),
    ("Shawna Robertson","Robertson","S",""),
    ("Andrew Robertson","Robertson","A",""),
    ("Linda Rigamer Lirette","Lirette","L",""),
    ("Patrick O'Briant","O'Briant","P",""),
    ("Elliot Richards","Richards","E",""),
    ("Allison Krill Brown","Krill Brown","A",""),
]
undergrad = [
    ("Alina Miller","Miller","A",""),
    ("Allen Gelfond","Gelfond","A",""),
    ("Emily Li","Li","E",""),
    ("Grace Campidilli","Campidilli","G",""),
    ("Gregory Young","Young","G",""),
    ("Jack Greenberg","Greenberg","J",""),
    ("Jennifer Zhao","Zhao","J",""),
    ("Jeffrey Morse","Morse","J",""),
    ("Libby Gilmore","Gilmore","L",""),
    ("Lu Cao","Cao","L",""),
    ("Maxwell Swann","Swann","M",""),
    ("Michael Oak","Oak","M",""),
    ("Sophie McComb","McComb","S",""),
    ("Truman Tse","Tse","T",""),
]

# Manual start/end for people whose lab years can't be inferred from papers
# (current non-publishing staff, retirees). Approximate — correct in the roster.
MANUAL = {
    "Ana Berthel": ("2019","present"),
    "Sarah McMorrow": ("2021","present"),
    "Thuy La": ("2016","present"),
    "Sara Miller": ("2014","present"),
    "Zack Miller": ("2019","present"),
    "Nick Lepak": ("2005","present"),
    "Bethany Econopouly": ("2020","present"),
    "Terry Casstevens": ("2003","2024"),
}

groups = [("postdoc",postdocs),("grad",grads),("visiting",visiting),("staff",staff),("undergrad",undergrad)]

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD",s) if unicodedata.category(c)!="Mn")

txt = open(BIB,encoding="utf-8").read()
entries = re.split(r'\n@', txt)
records = []
for e in entries:
    ym = re.search(r'year\s*=\s*\{?(\d{4})', e)
    am = re.search(r'author\s*=\s*\{(.+?)\}\s*,?\s*\n', e, re.S)
    if not am:
        am = re.search(r'author\s*=\s*\{(.+?)\}', e, re.S)
    if not ym or not am:
        continue
    year = int(ym.group(1))
    authors = am.group(1)
    parsed = []
    for a in authors.split(" and "):
        a = a.strip()
        if a.lower() == "others" or not a:
            continue
        if "," in a:
            last, first = a.split(",",1)
            last = strip_accents(last.strip()); first = first.strip()
            init = strip_accents(first[:1]).upper() if first else ""
        else:
            parts = a.split()
            last = strip_accents(parts[-1]); init = strip_accents(parts[0][:1]).upper() if parts else ""
        parsed.append((last.lower(), init))
    records.append((year, parsed))

def years_for(last, init):
    last_l = strip_accents(last).lower()
    yrs = []
    for year, authors in records:
        for (l,i) in authors:
            if l == last_l and (init=="" or i==init):
                yrs.append(year); break
    return sorted(set(yrs))

rows = []
seen = set()
rows.append(["Edward S. Buckler","pi","1998","present","Research Geneticist, USDA-ARS; Adjunct Professor, Cornell University"])
for role, lst in groups:
    for disp, last, init, pos in lst:
        key = disp.lower()
        if key in seen:
            continue
        seen.add(key)
        yrs = years_for(last, init)
        if yrs:
            start = str(min(yrs)-2)
            end = "present" if max(yrs) >= PRESENT_CUTOFF else str(max(yrs))
        else:
            start = ""; end = ""
        if disp in MANUAL:               # override inference for known staff/retirees
            start, end = MANUAL[disp]
        rows.append([disp, role, start, end, pos])

with open(OUT,"w",newline="",encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["name","role","start_year","end_year","current_position"])
    w.writerows(rows)

# also emit TSV (site template supports both)
with open(OUT.replace(".csv",".tsv"),"w",encoding="utf-8") as f:
    f.write("\t".join(["name","role","start_year","end_year","current_position"])+"\n")
    for r in rows:
        f.write("\t".join(r)+"\n")

nomatch = [r[0] for r in rows if r[2]=="" and r[1]!="pi"]
print(f"Wrote {len(rows)} people to people.csv")
print(f"Inferred years for {len(rows)-1-len(nomatch)} of {len(rows)-1} non-PI people")
print(f"No co-authorship match (blank years) [{len(nomatch)}]: {', '.join(nomatch)}")
print()
for r in rows[:8]:
    print("  ", r)
