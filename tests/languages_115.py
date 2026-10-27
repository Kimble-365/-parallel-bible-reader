"""Verify new source archives, source spelling, all imported units and fingerprints."""
from pathlib import Path
from zipfile import ZipFile
import json,re,hashlib,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from import_global_sample import extract
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'releases/v1.15'
def read(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
cat=read(OUT/'catalog.js');manifest=read(OUT/'search-manifest.js')['editions'];assert len(cat['editions'])==57
bundles={}
for p in (OUT/'extra-data').glob('*.js'):
 s=p.read_text();m=re.search(r'window.ExtraBibleBooks\["[A-Z0-9]{3}"\]=',s);bundles[p.stem]=json.loads(s[m.end():].rstrip(';'))['editions']
reports=json.loads((OUT/'sources/languages-import.json').read_text());assert len(reports)==2
for r in reports:
 id=r['id'];books={}
 with ZipFile(OUT/'sources'/(id+'-raw.zip')) as z:
  assert z.testzip() is None
  assert any(b'DistributionLicense=Public Domain' in z.read(n) for n in z.namelist() if n.endswith('.conf'))
  for f in r['files']:
   b=z.read(f['file']);assert hashlib.sha256(b).hexdigest()==f['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['git_blob']
   if f['file'].endswith('.SFM'):
    code,rows=extract(b.decode());books[code]=[row[:3] for row in rows]
   else:
    for (code,_),book in zip(cat['books'][:66],json.loads(b)):
     books[code]=[[c,v,t] for c,ch in enumerate(book['chapters'],1) for v,t in enumerate(ch,1) if t.strip()]
 with ZipFile(OUT/'sources'/(id+'-display-usfm.zip')) as z:
  assert len(z.namelist())==r['books']
  for code,expected in books.items():
   rows=bundles[code][id];assert [x[:3] for x in rows]==expected
   assert all(x[2]==x[3] for x in rows)
   assert hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==manifest[id][code]
   text=z.read(code+'.usfm').decode();assert '\\ide UTF-8' in text
   assert all(x[2] in text for x in rows)
 assert len(books)==r['books'] and sum(map(len,books.values()))==r['units']
 print('PASS',id,r['books'],'books',r['units'],'units; exact sources/rights/UTF-8/fingerprints')
