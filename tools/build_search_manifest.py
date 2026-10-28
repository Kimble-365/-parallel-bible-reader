"""Fingerprint immutable public book rows; no private imports enter this manifest."""
from pathlib import Path
import json,hashlib,re,sys,gzip
ROOT=Path(__file__).resolve().parents[1];V=sys.argv[1] if len(sys.argv)>1 else '1.12';OUT=ROOT/'releases'/('v'+V)
cat=json.loads((OUT/'catalog.js').read_text().split('=',1)[1].rstrip(';\n'));wanted={e['id']:set(e['book_codes']) for e in cat['editions']};manifest={id:{} for id in wanted}
for folder in [ROOT/'data',ROOT/'releases/v1.8/extra-data',ROOT/'releases/v1.10/extra-data',ROOT/'releases/v1.11/extra-data',ROOT/'releases/v1.13/extra-data',ROOT/'releases/v1.14/extra-data',ROOT/'releases/v1.15/extra-data',OUT/'extra-data']:
 for file in folder.glob('*.js'):
  text=file.read_text();m=re.search(r'window\.(?:ExtraBibleBooks|BibleBooks)\["[A-Z0-9]{3}"\]\s*=',text);assert m,file;data=json.loads(text[m.end():].strip().rstrip(';'))
  for id,rows in data['editions'].items():
   if id in wanted and file.stem in wanted[id]:manifest[id][file.stem]=hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
for file in dict.fromkeys([*(ROOT/'releases/v1.18/packed-data').glob('*.json.gz'),*(OUT/'packed-data').glob('*.json.gz')]):
 data=json.loads(gzip.decompress(file.read_bytes()));book=data['book']
 for id,rows in data['editions'].items():
  if id in wanted and book in wanted[id]:manifest[id][book]=hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
for id,codes in wanted.items():assert set(manifest[id])==codes,(id,codes-set(manifest[id]))
result=dict(schema='public-source-rows-sha256-1',revision=cat['version'],editions=manifest);(OUT/'search-manifest.js').write_text('window.ReaderSearchManifest='+json.dumps(result,separators=(',',':'))+';\n');print('Verified manifest:',len(manifest),'public editions,',sum(map(len,manifest.values())),'book/edition pairs')
