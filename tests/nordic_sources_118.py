from pathlib import Path
from zipfile import ZipFile
import json,gzip,hashlib,re
R=Path(__file__).resolve().parents[1];O=R/'releases/v1.18'
def js(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
cat=js(O/'catalog.js');pack=js(O/'pack-manifest.js');manifest=js(O/'search-manifest.js')['editions'];reports=json.loads((O/'sources/nordic-import.json').read_text());assert len(cat['editions'])==62 and len(reports)==5
rows={}
for book,m in pack.items():
 b=(O/'packed-data'/(book+'.json.gz')).read_bytes();assert hashlib.sha256(b).hexdigest()==m['packed_sha256'];raw=gzip.decompress(b);assert len(raw)==m['bytes'] and hashlib.sha256(raw).hexdigest()==m['sha256'];rows[book]=json.loads(raw)['editions']
for report in reports:
 id=report['id'];meta=next(e for e in cat['editions'] if e['id']==id);actual={book:items[id] for book,items in rows.items() if id in items};assert len(actual)==report['books'];assert sum(map(len,actual.values()))==report['units'];assert set(actual)==set(meta['book_codes'])
 with ZipFile(O/'sources'/(id+'-source.zip')) as z:
  assert z.testzip() is None
  for f in report['files']:
   b=z.read(f['file']);assert hashlib.sha256(b).hexdigest()==f['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['git_blob']
  if id.startswith(('swe','nob','nno')):assert any(b'DistributionLicense=Public Domain' in z.read(n) for n in z.namelist() if n.endswith('.conf'))
 with ZipFile(O/'sources'/(id+'-usfm.zip')) as z:
  for book,data in actual.items():
   assert len({(r[0],r[1]) for r in data})==len(data);assert all(r[3] is None for r in data);assert hashlib.sha256(json.dumps(data,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==manifest[id][book]
   s=z.read(book+'.usfm').decode();assert '\\ide UTF-8' in s and all(r[2] in s for r in data)
 print('PASS',id,report['books'],'books',report['units'],'source units; archives, Unicode, USFM, source references and fingerprints')
assert next(e for e in cat['editions'] if e['id']=='isl-olo1995')['book_codes']==['PSA']+[x[0] for x in cat['books'][39:66]]
assert len(next(e for e in cat['editions'] if e['id']=='ekk-ocv2022')['book_codes'])==27
assert len(next(e for e in cat['editions'] if e['id']=='ekk-pkp-partial')['book_codes'])==5
print('PASS: Estonian editions are separate; a 27-book NT is not falsely described as a completed 66-book Bible')
