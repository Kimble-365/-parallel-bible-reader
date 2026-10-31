"""Release integrity and independent source-position regression checks."""
from pathlib import Path
import gzip,hashlib,json,sys,collections,csv
R=Path(__file__).resolve().parents[1];O=R/'releases/v1.23';sys.path.insert(0,str(R/'tools'));from import_bhh_123 import mam

def js(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
def unpack(p,m):
 b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==m['packed_sha256'];assert len(b)==m['packed_bytes'];raw=gzip.decompress(b);assert len(raw)==m['bytes'];assert hashlib.sha256(raw).hexdigest()==m['sha256'];return raw
C=js(O/'catalog.js');old=js(R/'releases/v1.22/catalog.js');assert len(C['editions'])==65;assert C['editions'][:62]==old['editions'];assert C['version']==old['version'] # keep old permitted private data/offline keys
P=js(O/'bhh-manifest.js');library=js(O/'bhh-library.js');search=js(O/'search-manifest.js')['editions'];data=collections.defaultdict(dict)
for b,m in P.items():
 d=json.loads(unpack(O/'bhh-data'/(b+'.json.gz'),m));assert d['book']==b
 for id,rows in d['editions'].items():
  assert len({(r[0],r[1]) for r in rows})==len(rows);assert all(isinstance(r[2],str) and r[3] is None for r in rows);assert hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==search[id][b];data[id][b]=rows
for id,books,count in [('hbo-sp',5,5841),('hbo-mam',39,23202),('lat-clementine-thb',39,23480)]:
 assert len(data[id])==books;assert sum(map(len,data[id].values()))==count;meta=next(e for e in C['editions'] if e['id']==id);assert set(meta['book_codes'])==set(data[id]);assert {(b,c) for b,rows in data[id].items() for c in {r[0] for r in rows}}==set(map(tuple,meta['positions']));assert meta['has_transliteration'] is False and meta['preserve_source_refs']
assert 'הששי' in next(r[2] for r in data['hbo-sp']['GEN'] if r[:2]==[2,2]).replace('שׁ','ש')
assert mam({'type':'implicit-maqaf'})=='־';assert mam({'type':'spi-invnun','class':'including-trailing-space'})=='׆ ';assert mam({'type':'shirah-space'})==' '
assert mam({'type':'slh-word','slhw-desc-0':'DO NOT REPEAT','contents':[{'type':'letter-small','text':'א'}]})=='א'
assert mam({'type':'scrdfftar','contents':[{'type':'sdt-target','text':'TEXT'},{'type':'sdt-note','text':'NOT SCRIPTURE'}]})=='TEXT'
assert mam({'type':'cant-all-three','contents':[{'type':'cant-combined','text':'ONCE'},{'type':'cant-alef','text':'NO'}]})=='ONCE'
try:mam({'type':'unknown-future-role','text':'unsafe'})
except ValueError:pass
else:raise AssertionError('Unknown MAM role silently accepted')
seen=set();units=0;critical={}
for m in library['scrolls']:
 d=json.loads(unpack(O/m['url'],m));assert len(d)==m['units'];units+=len(d)
 for x in d:
  assert x['id'] not in seen;seen.add(x['id']);assert x['witness']==m['name'];assert 'tf_node' in x['locator'] and isinstance(x['flags'],dict)
  if x['id'] in {'dss:1941896','dss:1941905','dss:1988971','dss:1988972'}:critical[x['id']]=x
assert units==500995 and len(library['scrolls'])==997
for k in ['dss:1941896','dss:1941905']:assert critical[k]['flags']['rec'] # restored seventh is not visible-ink evidence
for k in ['dss:1988971','dss:1988972']:assert not critical[k]['flags'].get('rec')
for m in library['assets']:unpack(O/m['url'],m)
assert len([m for m in library['assets'] if m['id'].startswith('step-TAHOT')])==4
assert len(library['projects'])==9
# Every service-worker precache URL exists locally (ignoring inherited query strings).
import re
sw=(O/'sw.js').read_text();assert "const readerRoutes=new Set(['./','index.html'" in sw;assets=re.search(r'const ASSETS=(\[.*?\]);',sw)[1]
for a in json.loads(assets.replace("'",'"')):
 p=(O/a).resolve();assert p.exists(),p
print('PASS: 65 editions; all new text/source/DSS packed and expanded checksums; 52,523 verse records; 500,995 unique source units; 997 labels; full metadata/search coverage; four decisive damage fixtures; closed MAM roles; nine project entries; all shell assets exist')
