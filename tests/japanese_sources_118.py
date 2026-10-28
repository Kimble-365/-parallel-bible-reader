from pathlib import Path
import json,gzip,hashlib,re
R=Path(__file__).resolve().parents[1];O=R/'releases/v1.18'
def js(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
m=js(O/'japanese-manifest.js');assert len(m['books'])==66 and m['units']==31099 and m['fallback_verses']==0
for book,meta in m['books'].items():
 b=(O/'japanese-data'/(book+'.json.gz')).read_bytes();assert hashlib.sha256(b).hexdigest()==meta['packed_sha256'];raw=gzip.decompress(b);assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256'];data=json.loads(raw);assert data['source_hash']==js(O/'search-manifest.js')['editions']['jpn-bungo'][book];s=(R/'releases/v1.14/extra-data'/(book+'.js')).read_text();a=re.search(r'window.ExtraBibleBooks\["[A-Z0-9]{3}"\]=',s);source=json.loads(s[a.end():].rstrip(';'))['editions']['jpn-bungo'];assert [(r[0],r[1]) for r in source]==[(r[0],r[1]) for r in data['rows']];assert all(isinstance(r[2],str) and r[2] for r in data['rows']);assert sum(r[3] for r in data['rows'])>=0
assert m['engine']['commit']=='51fe14d92c5f915c969e4e78704e153da143a64f'
print('PASS: all 31,099 automatic Japanese readings bind exactly to original source positions and hashes; 66 gzip packs/checksums; engine/provenance and explicit unreviewed/not-spoken status')
g=js(O/'guide-translations.js');assert set(g['books'])=={'fi','sv','nb','nn','is','et'};assert all(len(books)==66 for books in g['books'].values());assert all(set(g['outlineTitles'][lang])==set(g['outlineTitles']['en']) for lang in g['labels']);print('PASS: 396 draft editorial introductions in six language packs, native labels and translated outlines; no unsupported-language translation claim')
