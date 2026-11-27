"""Verify supplied 1.29 bytes, all runtime packs, baseline and distribution assets."""
from pathlib import Path
import gzip,hashlib,json,subprocess,zipfile,sys
R=Path(__file__).resolve().parents[1];A=R/'original-documents/reference-editions/parallel-reader-1.29';B=R/'releases/v2.0'
def js(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
def sha(b):return hashlib.sha256(b).hexdigest()
cat=js(B/'catalog.js');base=js(R/'releases/v1.28/catalog.js');by={e['id']:e for e in cat['editions']}
assert len(by)==len(cat['editions'])==200
assert all(by[e['id']]==e for e in base['editions']) and len(base['editions'])==84
new=[e for e in cat['editions'] if e.get('data_group')=='europe-english-1.29'];assert len(new)==116
manifest=js(B/'europe-manifest.js');assert len(manifest)==85
seen={};rows=0
for book,m in manifest.items():
 p=R/'releases/v1.29/europe-data'/f'{book}.json.gz';packed=p.read_bytes();assert packed==(A/'europe-data'/p.name).read_bytes()
 raw=gzip.decompress(packed);assert sha(packed)==m['packed_sha256'] and len(packed)==m['packed_bytes'];assert sha(raw)==m['sha256'] and len(raw)==m['bytes']
 d=json.loads(raw);assert d['book']==book
 for id,rs in d['editions'].items():
  assert id in by and by[id]['data_group']=='europe-english-1.29';assert all(len(r)>=3 and isinstance(r[2],str) for r in rs)
  seen.setdefault(id,set()).add(book);rows+=len(rs)
assert all(set(e['book_codes'])==seen[e['id']] for e in new)
assert rows==2431331
for e in new:
 for suffix in ['source','display-usfm']:
  p=R/'releases/v1.29/sources'/f"{e['id']}-{suffix}.zip";assert p.read_bytes()==(A/'sources'/p.name).read_bytes()
  with zipfile.ZipFile(p) as z:assert z.testzip() is None
 for name in ['RIGHTS.txt','DETAILS.html','PROVENANCE.json']:
  with zipfile.ZipFile(A/'sources'/f"{e['id']}-source.zip") as z:assert z.read(name)
# Full archive bytes preserved; no prior source/app/store replacements.
m=json.loads((R/'incoming/v1.29/package/PACKAGE-MANIFEST.json').read_text())
for e in m['control_files']:
 p=R/'incoming/v1.29/package'/e['path'] if e['path']=='README.md' else R/e['path']
 assert len(p.read_bytes())==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
sys.path.insert(0,str(R/'tools'));from package_reader_20 import inventory
files=inventory(R);assert all(f'releases/v1.29/europe-data/{book}.json.gz' in files for book in manifest)
print(f'PASS: 84 byte-equivalent catalog records retained; 116 incoming editions; 85 exact gzip/source hashes; {rows:,} rows; 232 intact source/display archives; all notices and distribution paths')
