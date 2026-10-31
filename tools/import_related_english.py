"""Build bounded, attributed comparison packs from pinned local source snapshots.
Run acquisition first; original source files are retained once as deterministic gzip.
"""
from pathlib import Path
import json,gzip,re,hashlib,sys
sys.path.insert(0,str(Path(__file__).parent))
from import_global_sample import extract
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'releases/v1.22';SRC=Path('/workspace/reader-related')
def read(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
def writejs(p,name,data):p.write_text(name+'='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
cat=read(OUT/'catalog.js');directory=read(OUT/'translations/metadata.js');known=dict(cat['books']);canonical=list(known)[:66];overlays={};reports=[]
pack=OUT/'related-data';originals=OUT/'sources/related';pack.mkdir(exist_ok=True);originals.mkdir(parents=True,exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def store_raw(id,name,b):
 p=originals/id/(name+'.gz');p.parent.mkdir(exist_ok=True);p.write_bytes(gzip.compress(b,mtime=0));return dict(path=str(p.relative_to(OUT)),sha256=sha(b),bytes=len(b))
def edition(id,label,license,repo,commit,books,files,scope):
 books={b:[r for r in rows if r[2].strip()] for b,rows in books.items() if b in canonical and rows}
 assert books
 for b,rows in books.items():
  assert len({(r[0],r[1]) for r in rows})==len(rows),(id,b)
  assert all(r[2].strip() and '\\' not in r[2] for r in rows),(id,b)
  overlays.setdefault(b,{})[id]=[[r[0],r[1],r[2],r[2]]+r[3:] for r in rows]
 meta=dict(id=id,label=label,title=label,language='en',latin_language='en',script='Latin',direction='ltr',available=True,scope=scope,source=f'https://github.com/{repo}/tree/{commit}',license=license,license_url='https://creativecommons.org/licenses/by-sa/4.0/' if license=='CC BY-SA 4.0' else 'https://creativecommons.org/licenses/by/4.0/' if license=='CC BY 4.0' else 'https://creativecommons.org/publicdomain/zero/1.0/',attribution=f'{label}. Original project: {repo}, commit {commit}. Display conversion by Parallel Bible Reader; no endorsement. See sources/related-import.json.',method='Source numbering retained. Verse text only; source notes and markup remain in compressed originals. No independent expert approval claimed.',has_transliteration=False,books=len(books),verses=sum(map(len,books.values())),book_codes=[b for b in canonical if b in books],positions=[[b,c] for b in canonical if b in books for c in sorted({r[0] for r in books[b]})],preserve_source_refs=True,versification_label='Source positions; matching labels do not establish textual alignment',data_group='related-english')
 cat['editions']=[e for e in cat['editions'] if e['id']!=id]+[meta];directory[:]=[e for e in directory if e['id']!=id]+[dict(id=id,language='English',iso6393='eng',aliases=[label,id],family='Indo-European',branch='Germanic',countries=[],continents=[],states=[],script='Latin',variety=label,classification_source='English source edition',ubs_id=None)]
 reports.append(dict(id=id,repo=repo,commit=commit,license=license,books=len(books),verses=sum(map(len,books.values())),scope=scope,files=files))
for variant in ['LiteralVersion','ReadersVersion']:
 id='eng-oet-'+('lv' if variant=='LiteralVersion' else 'rv');books={};files=[]
 for f in sorted((SRC/'OpenEnglishTranslation--OET/exportedFiles/cleanedUSFM'/variant).glob('*.USFM')):
  raw=f.read_text();code=re.search(r'\\id\s+(\w+)',raw)[1].upper()
  if code not in canonical:continue
  # Strip complete notes first, then inline marker tokens without eating following spaces.
  display=raw
  for marker in ['f','fe','x','va','ca','vp']:display=re.sub(r'\\'+marker+r'\s.*?\\'+marker+r'\*','',display,flags=re.S)
  display=re.sub(r'\\(?:add|it|bd|bk|ord|nd|wj|sc|qt)\*','',display)
  display=re.sub(r'\\(?:add|it|bd|bk|ord|nd|wj|sc|qt)\s','',display)
  _,rows=extract(display);books[code]=rows;files.append(store_raw(id,f.name,f.read_bytes()))
 edition(id,'English — OET '+('Literal' if variant=='LiteralVersion' else 'Readers')+' (draft)','CC BY-SA 4.0','Freely-Given-org/OpenEnglishTranslation--OET','9d135bfe6810976f102000030622ee5c4a8b6669',books,files,'Available canonical books; source draft, not expert-approved')
books={};files=[]
for f in sorted((SRC/'Open-English-Bible/artifacts/us-release/usfm').glob('*.usfm')):
 raw=f.read_text();m=re.search(r'\\id\s+(\w+)',raw)
 if not m or m[1].upper() not in canonical:continue
 display=raw
 for marker in ['f','fe','x','va','ca','vp']:display=re.sub(r'\\'+marker+r'\s.*?\\'+marker+r'\*','',display,flags=re.S)
 display=re.sub(r'\\(?:add|it|bd|bk|ord|nd|wj|sc|qt)\*','',display)
 display=re.sub(r'\\(?:add|it|bd|bk|ord|nd|wj|sc|qt)\s','',display)
 code,rows=extract(display);books[code.upper()]=rows;files.append(store_raw('eng-oeb',f.name,f.read_bytes()))
edition('eng-oeb','English — Open English Bible (US release)','CC0','openenglishbible/Open-English-Bible','1965127de5c3c103af3fdbc9288c1abec5f39994',books,files,'Published release books only; incomplete OT')
# Existing WEB already covers the Open Bibles reference candidate; do not duplicate it.
if (SRC/'pob-canonical.jsonl.gz').exists() and (SRC/'pob-complete').exists():
 books={};names={name.lower().replace(' ','_'):code for code,name in cat['books']};names.update({'song_of_solomon':'SNG','psalm':'PSA'})
 for line in gzip.open(SRC/'pob-canonical.jsonl.gz','rt'):
  row=json.loads(line);d=row['data'];parts=row['path'].split('/');code=names.get(parts[2]);assert code,parts[2]
  translation=d.get('translation');text=translation.get('text') if isinstance(translation,dict) else translation;assert isinstance(text,str),(row['path'],list(d))
  for footnote in translation.get('footnotes',[]) if isinstance(translation,dict) else []:
   marker=footnote.get('marker');text=text.replace('['+str(marker)+']','') if marker else text
  books.setdefault(code,[]).append([int(parts[3]),int(parts[4].split('.')[0]),text])
 for rows in books.values():rows.sort()
 edition('eng-pob','English — People’s Open Bible (AI-assisted draft)','CC BY 4.0','zackseyun/peoples-open-bible','5a6633695bfcc3264f508974c104ad556892c036',books,[store_raw('eng-pob','translation-records.jsonl',b''.join((json.dumps({'path':r['path'],'upstream_record_sha256':r['sha256'],'translation':r['data']['translation']},ensure_ascii=False)+'\n').encode() for r in (json.loads(l) for l in gzip.open(SRC/'pob-canonical.jsonl.gz','rt'))))],'Canonical OT/NT source draft; AI reviews are not independent expert approval')
manifest={}
for b,eds in overlays.items():
 raw=json.dumps(dict(book=b,editions=eds),ensure_ascii=False,separators=(',',':')).encode();z=gzip.compress(raw,mtime=0);(pack/(b+'.json.gz')).write_bytes(z);manifest[b]=dict(bytes=len(raw),sha256=sha(raw),packed_bytes=len(z),packed_sha256=sha(z))
writejs(OUT/'related-manifest.js','window.RelatedTextPacks',manifest);writejs(OUT/'catalog.js','window.BibleCatalog',cat);writejs(OUT/'translations/metadata.js','window.TranslationDirectory',directory)
(OUT/'sources/related-import.json').write_text(json.dumps(dict(date='2026-10-31',editions=reports,limits=['TWV derivative/full-text redistribution requires permission','AI Scribes lacks a verified content license','Swarm README/LICENSE conflict pending clarification; not imported','Greek Room is a checking tool, not a Bible text','Open Bibles WEB candidate already represented by engwebp; no duplicate import']),indent=2)+'\n')
print([(r['id'],r['books'],r['verses']) for r in reports])
