"""Build source-pinned Greek comparison packs; no network or editorial emendation."""
from pathlib import Path
from collections import defaultdict
import json, gzip, hashlib, re, html, unicodedata, sys
from lxml import html as LH, etree

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'releases/v1.22'
(OUT/'sources').mkdir(parents=True,exist_ok=True)
NTGL=Path('/workspace/TheWay/NTGL')
SRC=Path('/tmp/ntgl-ready-sources')
NT='MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV'.split()
SHORT=dict(zip('MT MR LU JOH AC RO 1CO 2CO GA EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JO 2JO 3JO JUDE RE'.split(),NT))
SBL=dict(zip('Matt Mark Luke John Acts Rom 1Cor 2Cor Gal Eph Phil Col 1Thess 2Thess 1Tim 2Tim Titus Phlm Heb Jas 1Pet 2Pet 1John 2John 3John Jude Rev'.split(),NT))
def sha(b):return hashlib.sha256(b).hexdigest()
def jsread(p):return json.loads(p.read_text().split('=',1)[1].strip().rstrip(';'))
def jswrite(p,name,data):p.write_text(name+'='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
def records(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def pack(p,data):
 raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode();z=gzip.compress(raw,mtime=0);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z)
 return {'bytes':len(raw),'sha256':sha(raw),'packed_bytes':len(z),'packed_sha256':sha(z)}
cat=jsread(OUT/'catalog.js');directory=jsread(OUT/'translations/metadata.js')
names={name.replace(' ','-'):code for code,name in cat['books'][:66]}
ledger=json.loads((SRC/'manifest.json').read_text());assert not ledger['errors']
overlays={};imports=[];paratext=[]

def save_originals(id,files):
 payload={'id':id,'upstream':[x for x in ledger['sources'] if x['id']==id],
          'line_endings':'CRLF normalized to LF; no intended text changes',
          'files':{p.name:p.read_text() for p in files}}
 return pack(NTGL/'sources/reader-corpora'/(id+'.json.gz'),payload)

def add(id,label,books,license,repo,revision,method,attribution,raw_id=None):
 assert books and set(books)<=set(NT)
 for code,rows in books.items():
  assert len({(r[0],r[1]) for r in rows})==len(rows),(id,code,'duplicate')
  assert all(isinstance(r[0],int) and isinstance(r[1],int) and r[2].strip() for r in rows),(id,code)
  overlays.setdefault(code,{})[id]=rows
 meta=dict(id=id,label=label,title=label,language='grc',latin_language='grc-Latn',script='Greek',direction='ltr',available=True,
           scope='27-book New Testament' if len(books)==27 else 'John 1:1–5 transcription sample only',
           source=f'https://github.com/{repo}/tree/{revision}',license=license,
           license_url={'Public domain':'https://creativecommons.org/publicdomain/mark/1.0/','CC BY 4.0':'https://creativecommons.org/licenses/by/4.0/','CC BY-SA 4.0':'https://creativecommons.org/licenses/by-sa/4.0/','CC BY-NC-SA 3.0':'https://creativecommons.org/licenses/by-nc-sa/3.0/'}[license],
           attribution=attribution+' No endorsement. See sources/ntgl-import.json.',method=method,
           has_transliteration=False,books=len(books),verses=sum(map(len,books.values())),
           book_codes=[b for b in NT if b in books],positions=[[b,c] for b in NT if b in books for c in sorted({r[0] for r in books[b]})],
           preserve_source_refs=True,versification_label='Source reference labels; cross-edition equivalence is not asserted',data_group='ntgl-greek')
 cat['editions']=[e for e in cat['editions'] if e['id']!=id]+[meta]
 directory[:]=[e for e in directory if e['id']!=id]+[dict(id=id,language='Ancient Greek',iso6393='grc',aliases=[label,id,'Greek','Koine','NTGL'],family='Indo-European',branch='Hellenic',countries=['Greece'],continents=['Europe'],states=[],script='Greek',variety=label,classification_source='Historical Greek text; country is a modern browsing association, not manuscript provenance',ubs_id=None)]
 imports.append({k:meta[k] for k in ['id','label','books','verses','source','license','method']})

# Tischendorf: column 3 is printed-form kethiv, NOT the editor's column 4 qere.
books={}
files=sorted((SRC/'tischendorf').glob('*.txt'))
for p in files:
 rows=defaultdict(list)
 for line in p.read_text().splitlines():
  if not line.strip():continue
  fields=line.split(maxsplit=7);assert len(fields)==8,(p,line)
  m=re.fullmatch(r'(\d+):(\d+)\.(\d+)',fields[1]);assert m,(p,line)
  rows[(int(m[1]),int(m[2]))].append(fields[3])
 books[SHORT[p.stem]]=[[c,v,' '.join(words),''] for (c,v),words in rows.items()]
assert len(books)==27
save_originals('tischendorf',files)
add('grc-tischendorf8','Greek — Tischendorf 8 (printed-form digital text)',books,'Public domain','morphgnt/tischendorf-data',ledger['sources'][0]['revision'],
    'Version 2.8 Unicode kethiv column; source punctuation and reference labels retained. Qere and morphology remain in compressed originals. Printed apparatus is not in this dataset.',
    'Tischendorf 8 digital text based on G. Clint Yale; morphology/edition by Ulrik Sandborg-Petersen with Maurice A. Robinson. Version 2.8 README declares text and analysis public domain.')

def nestle_rows(p):
 body=LH.fromstring(p.read_bytes(),parser=LH.HTMLParser(encoding='utf-8')).find('body');assert body is not None
 rows=[];c=None;v=None;parts=[]
 def flush():
  nonlocal parts
  if v is not None:
   text=' '.join(''.join(parts).split());assert text,(p,c,v);rows.append([c,v,text,''])
  parts=[]
 def append(text):
  nonlocal v
  if v is None:return
  start=0
  for marker in re.finditer(r'(?<!\w)([0-9]{1,3})(?!\w)',text):
   parts.append(text[start:marker.start()]);flush();v=int(marker[1]);start=marker.end()
  parts.append(text[start:])
 def visit(node):
  nonlocal c,v
  if node.tag=='h2':
   flush();heading=''.join(node.itertext()).strip();v=None
   if not heading.isdigit():
    content=[]
    for sibling in node.itersiblings():
     if sibling.tag=='h2':break
     content.append(''.join(sibling.itertext()))
    paratext.append({'edition':'grc-nestle1904','source_file':p.name,'heading':heading,'text':' '.join(' '.join(content).split()),'status':'unnumbered_source_appendix_not_assigned_a_verse'})
    c=None;return
   c=int(heading);return
  if node.tag in ('h1','script','style'):return
  if node.tag=='span' and ''.join(node.itertext()).strip().isdigit():
   assert c is not None;flush();v=int(''.join(node.itertext()).strip());return
  append(node.text or '')
  for child in node:
   visit(child)
   append(child.tail or '')
 visit(body);flush();return rows
files=sorted((SRC/'nestle1904').glob('*.xhtml'));books={names[p.name.removesuffix('-ap.xhtml')]:nestle_rows(p) for p in files};assert len(books)==27
save_originals('nestle1904',files)
add('grc-nestle1904','Greek — Nestle 1904 digital base text',books,'Public domain','biblicalhumanities/Nestle1904','713f28a3b7d4d66132f5aa809fa223fe79762e5d',
    'Verse text extracted from the dos Santos XHTML component; punctuation retained, markup removed. Historical printing identity is not newly verified by this import.',
    'Eberhard Nestle edition; digital base text prepared by Diego Renato dos Santos, XHTML distributed by Biblical Humanities. Component README reports public-domain status.')

files=sorted((SRC/'sblgnt').glob('*.txt'));books={}
for p in files:
 rows=[]
 for line in p.read_text().splitlines():
  m=re.match(r'^\S+\s+(\d+):(\d+)\t(.*)$',line)
  if m:rows.append([int(m[1]),int(m[2]),m[3].strip(),''])
 books[SBL[p.stem]]=rows
assert len(books)==27
save_originals('sblgnt',files)
add('grc-sblgnt','Greek — SBLGNT (official text, v1.2)',books,'CC BY 4.0','Faithlife/SBLGNT','d7f35adca9ec410e1d1499c63b4dd989d76c8d4d',
    'Official verse text, including its textual marks, preserved. This is an edited comparison text, not an independent manuscript witness.',
    'SBL Greek New Testament, edited by Michael W. Holmes. Copyright 2010 Society of Biblical Literature and Logos Bible Software. CC BY 4.0; README v1.2 dated 2023-07-10.')

alphabet=dict(zip('abgdezhyiklmnxoprstufcqwvs','αβγδεζηθικλμνξοπρστυφχψωςσ'))
files=sorted((SRC/'westcott-hort').glob('*.WH'));books={}
for p in files:
 raw=p.read_text();matches=list(re.finditer(r'(?m)^\s*(\d+):(\d+)\s+',raw));rows=[]
 for i,m in enumerate(matches):
  text=' '.join(raw[m.end():matches[i+1].start() if i+1<len(matches) else len(raw)].split())
  greek=''.join(alphabet.get(ch.lower(),ch).upper() if ch.isupper() else alphabet.get(ch,ch) for ch in text)
  rows.append([int(m[1]),int(m[2]),greek,''])
 books[SHORT[p.stem]]=rows
assert len(books)==27
save_originals('westcott-hort',files)
add('grc-westcott-hort','Greek — Westcott–Hort (unaccented digital text)',books,'Public domain','byztxt/greektext-westcott-hort','91473892d7f36f1227e5c24f8d994d1da40311ad',
    'Mechanical ASCII-to-Greek alphabet conversion from the unaccented source; no accents, breathings or lost punctuation reconstructed. Source ASCII retained in compressed originals.',
    'Westcott–Hort digital text by Maurice A. Robinson, maintained by Ulrik Sandborg-Petersen. Upstream declares public domain.')

books=defaultdict(list);p=SRC/'opengnt/OGNT_KoineGreek.csv'
for line in p.read_text(encoding='utf-8-sig').splitlines():
 if not line.strip():continue
 fields=line.split('\t',3);assert len(fields)==4
 b,c,v=map(int,fields[:3]);text=html.unescape(re.sub('<[^>]+>','',fields[3])).strip();books[NT[b-40]].append([c,v,text,''])
assert len(books)==27
pack(NTGL/'sources/reader-corpora/opengnt.json.gz',{'source':'eliranwong/OpenGNT','revision':'0029589cccd50bd48b1941aa041a956de6c29ac4','path':'Modules_for_Bible_Applications/e-Sword/OGNT_KoineGreek.csv','blob_sha':'d346e182e975d1e2ff23faf5c424794924c05f01','text':p.read_text()})
add('grc-opengnt-koine','Greek — OpenGNT (unaccented Koine module)',books,'CC BY-SA 4.0','eliranwong/OpenGNT','0029589cccd50bd48b1941aa041a956de6c29ac4',
    'OGNT_KoineGreek module: original lunate sigma and unaccented text retained, font markup removed. Upstream NA-equivalence claim is not independent verification and does not include the NA apparatus.',
    'Open Greek New Testament Project by Eliran Wong, main text CC BY-SA 4.0. This import contains the Greek verse text only, not bundled third-party translations or lexicons.')

manu=records(NTGL/'indices/manuscript_tokens.jsonl')
for view,suffix in [('original','original'),('corrected_ca','ca')]:
 rows=[]
 for v in range(1,6):
  words=[x for x in manu if x['view']==view and x['reference']==f'JHN 1:{v}']
  rows.append([1,v,' '.join(x['normalized_display'] or x['transcribed_text'] for x in words),''])
 add('grc-sinaiticus-'+suffix+'-pilot','Greek — Sinaiticus '+('original hand' if view=='original' else 'ca-corrected view')+' (John 1:1–5 sample)',{'JHN':rows},'CC BY-NC-SA 3.0','itsee-birmingham/codex-sinaiticus','af1633b5102cbe6200e79053cc618ac447e1bb16',
     'Normalized display derived from identified TEI words; source abbreviations/expansions and corrections are retained in NTGL originals. No image verification. Two views are one physical witness.',
     'Codex Sinaiticus Project / ITSEE Birmingham, transcription v1.95. CC BY-NC-SA 3.0. Only John 1:1–5 is included; other verses are unavailable, not reconstructed.')

manifest={b:pack(OUT/'ntgl-data'/(b+'.json.gz'),{'book':b,'editions':eds}) for b,eds in overlays.items()}
jswrite(OUT/'ntgl-manifest.js','window.NTGLTextPacks',manifest)
(OUT/'sources/ntgl-paratext.json').write_text(json.dumps(paratext,ensure_ascii=False,indent=2)+'\n')
jswrite(OUT/'catalog.js','window.BibleCatalog',cat);jswrite(OUT/'translations/metadata.js','window.TranslationDirectory',directory)
(OUT/'sources/ntgl-import.json').write_text(json.dumps({'project_name':'Novum Testamentum Graece Aboensis','date':'2026-10-31','editions':imports,'source_file_count':len(ledger['sources']),'packed_bytes':sum(x['packed_bytes'] for x in manifest.values()),'limits':['Imported editions are comparison sources, not NTGL adopted readings','Tischendorf printed apparatus is NOT supplied by the 2.8 dataset','Sinaiticus is a five-verse sample only','Matching reference labels do not prove cross-edition verse equivalence']},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'editions':[(x['id'],x['books'],x['verses']) for x in imports],'pack_bytes':sum(x['packed_bytes'] for x in manifest.values())},indent=2))
