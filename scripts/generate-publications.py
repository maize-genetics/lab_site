#!/usr/bin/env python3
# Regenerate js/publications-data.js from a Google Scholar CSV export.
#
# Usage (from repo root):
#   python3 scripts/generate-publications.py
#
# Update SRC below to point at the newest Scholar export, then rerun. The
# script filters out posters / conference talks / errata / non-papers,
# deduplicates preprint+published pairs, tags each paper into LAB_THEMES,
# stamps curated DOIs + landmark flags (edit CURATED), and links the rest to a
# Google Scholar title search. LAB_THEMES is preserved from the existing
# js/publications-data.js, so edit theme names/blurbs there.
import csv, re, collections, json
from urllib.parse import quote

# Source is co-work's deduplicated publication list (data/publications.csv),
# produced by data/update_tools/dedupe_pubs.py from the raw Google Scholar
# exports. Same Scholar column schema as the raw dump.
SRC='data/publications.csv'
OUT='js/publications-data.js'

rows=[]
with open(SRC, encoding='utf-8-sig', newline='') as f:
    for row in csv.DictReader(f): rows.append(row)

# ---------- filters ----------
VENUE_BAD = re.compile(r'\b(conference|annual meeting|meeting|symposium|abstract|poster|CANVAS|ASA, CSSA|CSSA|Socio-Technical Innovation)\b', re.I)
def venue_bad(v):
    v=(v or '').strip()
    if not v: return False
    if 'national academy' in v.lower(): return False
    if re.search(r'proceedings of the .*(meeting|conference)', v, re.I): return True
    return bool(VENUE_BAD.search(v))
TITLE_BAD = re.compile(r'(user manual|a brief introduction to the .*library|technical appendix|getting from here to there|impact pathways|key external drivers|envisioning four design|state of agri-food|towards co-creation|final report|\(final|patent|thesis|dissertation|^correction:|^erratum|erratum to:|corrigend|^retraction)', re.I)
def norm(t): return re.sub(r'[^a-z0-9]+',' ', (t or '').lower()).strip()
def is_preprint(v):
    v=(v or '').strip().lower(); return v in ('biorxiv','arxiv','research square','preprints','ssrn','')

kept=[r for r in rows if not venue_bad(r['Publication']) and not TITLE_BAD.search(r['Title'] or '')]
groups=collections.OrderedDict()
for r in kept: groups.setdefault(norm(r['Title']),[]).append(r)
dedup=[]
for k,g in groups.items():
    if len(g)==1: dedup.append(g[0]); continue
    def score(r):
        y=int(r['Year']) if r['Year'].strip().isdigit() else 0
        return (0 if is_preprint(r['Publication']) else 1, y)
    dedup.append(sorted(g, key=score, reverse=True)[0])
final=[r for r in dedup if r['Year'].strip().isdigit()]

# ---------- author formatting ----------
def fmt_author(a):
    a=a.strip()
    if not a: return None
    if ',' in a: last, given = a.split(',',1)
    else: last, given = a, ''
    last=re.sub(r'\s+(IV|III|II|Jr|Sr)\.?$','',last.strip()).strip()
    if last.lower()=='buckler': return 'Buckler ES'
    inits=''.join(w[0] for w in re.findall(r"[A-Za-z]+", given))[:3].upper()
    return (last+' '+inits).strip()
def authors_str(raw):
    parts=[p for p in (raw or '').split(';')]
    names=[fmt_author(p) for p in parts if p.strip()]
    names=[n for n in names if n]
    if not names: return ''
    if len(names)<=8:
        disp=', '.join(names)
    else:
        head=names[:6]; disp=', '.join(head)+', …'
        if 'Buckler ES' in names and 'Buckler ES' not in head: disp+=', Buckler ES'
        elif names[-1] not in head: disp+=' '+names[-1]
    return disp

# ---------- venue ----------
def venue_str(r):
    v=(r['Publication'] or '').strip()
    if v.lower()=='biorxiv': v='bioRxiv'
    vol=(r['Volume'] or '').strip(); pg=(r['Pages'] or '').strip().split('-')[0].split('–')[0]
    if v and vol and pg and vol.replace('.','').isdigit():
        v=f'{v} {vol}:{pg}'
    return v

# ---------- theme rules ----------
RULES={
 'assoc': r'association mapping|genome-?wide association|\bGWAS\b|mixed[- ]model|mixed linear model|unified mixed|structured association|linkage disequilibrium|statistical power|multiple levels of relatedness|SUPER|study design|nested association|joint[- ]linkage',
 'genotyping': r'genotyping[- ]by[- ]sequencing|\bGBS\b|hap-?map|haplotype map|SNP discovery|SNP array|SNP genotyping|imputation|rAmpSeq|single[- ]feature polymorphism|sequenc(e|ing) technology|microsatellite|molecular markers',
 'nam': r'nested association|flowering time|leaf architecture|leaf angle|plant height|maize height|stalk strength|inflorescence|southern leaf blight|northern leaf blight|leaf blight|ear rot|tar spot|lodging|kernel (composition|color|size)|aphid|chlorotic mottle',
 'evolution': r'domesticat|teosinte|selective sweep|selection|recombination|Tripsacum|Andropogon|PanAnd|genome evolution|centromere|\bknob|molecular evolution|highland adaptation|local adaptation|introgress|phylogeo|ancient maize|transposon|pan-?genome|diversity of maize|genetic diversity|population structure|meiotic|inbred lines as inferred',
 'metabolism': r'metabolit|metabolome|carotenoid|provitamin|vitamin e|tocopherol|tocochromanol|benzoxazinoid|terpenoid|diterpen|specialized metabolite|flavonoid|maysin|chlorogenic|antifungal|diferuloyl|innate immunity|antibiotic|biosynthe|defen|insect|herbivore|homoterpene|carbon and nitrogen metabolism|isocitrate',
 'prediction': r'deleterious|mutation(al)? burden|mutation load|genomic prediction|genomic selection|evolutionary constraint|evolutionary conservation|heterosis|hybrid vigor|inbreeding depression|genetic load|\bHARE\b|incomplete dominance|BLUP|prediction accuracy|Muller.s Ratchet',
 'regulatory': r'chromatin|cis-?regulatory|regulatory (element|network|code)|non-?coding|open chromatin|RNA polymerase|transcript(ome|ion)|\bTWAS\b|k-?mer grammar|enhancer|terminator|\beQTL|gene expression|expression divergence|regulatory architecture|intergenic',
 'ml': r'deep learning|machine learning|neural network|language model|foundation model|PlantCAD|GeneCAD|convolutional|latent space|cross-?species modeling|DNA language|recurrent',
 'comparative': r'cassava|sorghum|grape|vitis|melon|cucumis|millet|switchgrass|wheat|\brice\b|barley|potato|\bhop\b|turfgrass|pearl millet|foxtail|reed canarygrass|watermelon|animal|FarmGTEx|perennial grain|biofuel',
 'tools': r'\bTASSEL\b|\bGAPIT\b|rTASSEL|practical haplotype graph|haplotype graph|BioKotlin|AnchorWave|\bPHG\b|Panzea|Gramene|R interface|software|pipeline|\bdatabase\b|genomes to fields|G2F|\bPICARA\b',
 'phenomics': r'phenotyp|phenomic|high-?throughput|aerial|multispectral|\bUAV\b|imaging|latent space phenotyping|spatio-?temporal|field-based|drone|robotic',
 'cerca': r'\bCERCA\b|nitrogen|N2\.0|nitrification|stover|fertilizer|cold[- ]toleran|circular economy|sustainable',
}
RULES={k:re.compile(v,re.I) for k,v in RULES.items()}
def themes_for(title, venue):
    s=(title or '')+' '+(venue or '')
    ts=[slug for slug,rx in RULES.items() if rx.search(s)]
    if not ts:
        if re.search(r'\bQTL\b|trait|mapping|genetic architecture|quantitative', s, re.I): ts=['assoc']
        elif re.search(r'maize|\bZea\b|genome', s, re.I): ts=['evolution']
        else: ts=['assoc']
    return ts

# ---------- curated DOIs + landmark flags (match by title substring) ----------
CURATED=[
 ('unified mixed-model method for association','10.1038/ng1702',True),
 ('TASSEL: software for association mapping','10.1093/bioinformatics/btm308',True),
 ('genetic architecture of maize flowering time','10.1126/science.1174276',True),
 ('Genetic properties of the maize nested association','10.1126/science.1174320',True),
 ('robust, simple genotyping-by-sequencing','10.1371/journal.pone.0019379',True),
 ('association study of leaf architecture','10.1038/ng.746',True),
 ('GAPIT: genome association and prediction','10.1093/bioinformatics/bts444',False),
 ('Comprehensive genotyping of the USA national maize','10.1186/gb-2013-14-6-r55',False),
 ('third-generation Zea mays haplotype map','10.1093/gigascience/gix134',False),
 ('Prediction of evolutionary constraint by genomic annotations','10.1186/s13059-022-02747-2',False),
 ('Practical Haplotype Graph, a platform','10.1093/bioinformatics/btac410',False),
 ('Cross-species modeling of plant genomes at single','10.1101/2024.06.04.596709',False),
 # landmarks from Ed's curated Landmarks.csv (DOIs verified via Crossref)
 ('Dwarf8 polymorphisms associate with','10.1038/90135',True),
 ('Structure of linkage disequilibrium and phenotypic','10.1073/pnas.201394398',True),
 ('Genetic design and statistical power of nested association','10.1534/genetics.107.074245',False),
 ('Mixed linear model approach adapted for genome','10.1038/ng.546',True),
 ('Diversity and heritability of the maize rhizosphere','10.1073/pnas.1302837110',True),
 ('Structure of linkage disequilibrium in plants','10.1146/annurev.arplant.54.031902.134907',True),
 ('lycopene epsilon cyclase','10.1126/science.1150255',True),
 ('first-generation haplotype map of maize','10.1126/science.1177837',True),
 ('Open chromatin reveals the functional maize genome','10.1073/pnas.1525244113',True),
 ('Dysregulation of expression correlates with rare-allele burden','10.1038/nature25966',True),
 # recent DOIs (not landmarks)
 ('PlantCAD2','10.1101/2025.08.27.672609',False),
 ('GeneCAD','10.1101/2025.10.31.685877',False),
 ('distinguishes maize within a stable tribe','10.1101/2025.01.22.633974',False),
 ('Widespread turnover of a conserved cis-regulatory','10.1093/molbev/msaf324',False),
 ('maize centromeres and knobs','10.1101/2025.01.31.635908',False),
 ('FarmGTEx','10.1038/s41588-025-02121-5',False),
 ('erosion of sexual reproduction genes in domesticated cassava','10.1093/g3journal/jkae282',False),
 ('nitrogen-efficient cold-tolerant maize','10.1093/plcell/koaf139',False),
 ('generalize across grass species but not alleles','10.1101/2024.04.11.589024',False),
 ('multispectral aerial images improves agronomic','10.1093/genetics/iyae037',False),
 # New Directions additions (Ed's NewDirections.csv; DOIs Crossref-verified)
 ('Evolutionarily informed deep learning','10.1073/pnas.1814551116',False),
 ('Reconstructing the maize leaf regulatory network','10.1038/s41467-020-18832-8',False),
 ('AnchorWave: Sensitive alignment of genomes with high sequence diversity','10.1073/pnas.2113075119',False),
 ('Scale up trials to validate modified','10.1038/d41586-023-02895-w',False),
 ('Translating functional molecular knowledge','10.1038/s41576-026-00968-w',False),
]

# DOIs that get the 'direction' flag -> the "New Directions" featured box (recent
# flagship papers; each DOI is already present in CURATED above). A paper is a
# landmark OR a direction OR neither.
DIRECTIONS={
 '10.1073/pnas.1814551116',        # Washburn 2019 deep learning transcript abundance
 '10.1038/s41467-020-18832-8',     # Tu 2020 maize leaf regulatory network
 '10.1093/bioinformatics/btac410', # Practical Haplotype Graph (Bradbury 2022)
 '10.1186/s13059-022-02747-2',     # evolutionary constraint (Ramstein 2022)
 '10.1073/pnas.2113075119',        # AnchorWave (Song 2022)
 '10.1038/d41586-023-02895-w',     # Khaipho-Burch 2023 scale-up trials
 '10.1093/plcell/koaf139',         # nitrogen-efficient cold-tolerant maize (Ojeda-Rivera 2025)
 '10.1101/2025.08.27.672609',      # PlantCAD2 (Zhai 2025)
 '10.1093/molbev/msaf324',         # Hale 2026 cis-regulatory turnover (published MBE)
 '10.1038/s41576-026-00968-w',     # Ramstein 2026 NRG review
}
def curated_for(title):
    tl=(title or '').lower()
    for sub,doi,lm in CURATED:
        if sub.lower() in tl: return doi,lm
    return None,False

# ---------- build ----------
pubs=[]
for r in final:
    t=r['Title'].strip()
    y=int(r['Year'])
    v=venue_str(r)
    a=authors_str(r['Authors'])
    themes=themes_for(t, v)
    doi,lm=curated_for(t)
    obj={'y':y,'a':a,'t':t,'v':v,'themes':themes}
    if doi: obj['doi']=doi
    else: obj['u']='https://scholar.google.com/scholar?q='+quote(t)
    if lm: obj['flags']=['landmark']
    elif doi and doi in DIRECTIONS: obj['flags']=['direction']
    pubs.append(obj)

# drop correction / erratum notices (not papers)
pubs=[p for p in pubs if not re.match(r'(author |publisher )?(correction|erratum)\b', p['t'].strip(), re.I)]
# de-duplicate variant rows that resolved to the same curated DOI (the dedup
# pipeline misses these because titles differ across preprint/published/versions);
# keep the earliest-year representative of each DOI
best={}
for p in pubs:
    d=p.get('doi')
    if d and (d not in best or p['y']<best[d]['y']): best[d]=p
seen=set(); dd=[]
for p in pubs:
    d=p.get('doi')
    if not d: dd.append(p)
    elif d not in seen: dd.append(best[d]); seen.add(d)
pubs=dd

# ensure themes tag cerca-adjacent: done. sort by year desc
pubs.sort(key=lambda p:(-p['y'], p['t']))

# stats
theme_counts=collections.Counter()
for p in pubs:
    for s in p['themes']: theme_counts[s]+=1
landmarks=[p for p in pubs if 'landmark' in p.get('flags',[])]
print("FINAL pubs:", len(pubs))
print("landmarks matched:", len(landmarks))
for p in landmarks: print("   ", p['y'], p['t'][:60])
directions=[p for p in pubs if 'direction' in p.get('flags',[])]
print("directions matched:", len(directions))
for p in directions: print("   ", p['y'], p['t'][:60])
print("with DOI:", sum(1 for p in pubs if 'doi' in p), " with scholar-url:", sum(1 for p in pubs if 'u' in p))
print("theme counts:", dict(theme_counts))
multi=sum(1 for p in pubs if len(p['themes'])>1)
print("multi-theme:", multi)

# ---------- emit JS ----------
THEMES_BLOCK = open(OUT, encoding='utf-8').read()
m=re.search(r'window\.LAB_THEMES\s*=\s*\[.*?\];', THEMES_BLOCK, re.S)
themes_js=m.group(0)

def esc(s): return s.replace('\\','\\\\').replace("'","\\'")
lines=[]
for p in pubs:
    parts=[f"y:{p['y']}", f"a:'{esc(p['a'])}'", f"t:'{esc(p['t'])}'", f"v:'{esc(p['v'])}'"]
    if 'doi' in p: parts.append(f"doi:'{esc(p['doi'])}'")
    if 'u' in p: parts.append(f"u:'{esc(p['u'])}'")
    parts.append('themes:['+','.join(f"'{s}'" for s in p['themes'])+']')
    if 'flags' in p: parts.append("flags:['"+p['flags'][0]+"']")
    lines.append('  { '+', '.join(parts)+' }')
body=',\n'.join(lines)

header='''/* ============================================================
   Publications data — single source of truth for the archive.
   Rendered by js/lab-archive.js on publications.html + theme.html.

   Generated from Ed's Google Scholar export
   (data/buckler_citations_260703.csv), filtered to drop posters,
   conference talks, and non-papers, then deduplicated (preprint +
   published merged) and tagged into themes. Curated landmarks and
   recent papers carry real DOIs; the rest link to a Google Scholar
   title search until DOIs are backfilled.

   Paper schema:
     y      publication year (number)
     a      author string (render bolds "Buckler ES")
     t      title
     v      venue (journal / preprint)
     doi    DOI (optional) -> https://doi.org/<doi>
     u      fallback URL (optional) when no DOI
     themes array of theme slugs (see LAB_THEMES)
     flags  optional; "landmark" pins to the landmarks strip
   ============================================================ */

'''
with open(OUT,'w',encoding='utf-8') as f:
    f.write(header+themes_js+'\n\nwindow.LAB_PUBS = [\n'+body+'\n];\n')
print("WROTE", OUT)
