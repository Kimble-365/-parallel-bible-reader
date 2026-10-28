from pathlib import Path
import json,re,gzip,hashlib
R=Path(__file__).resolve().parents[1];O=R/'releases/v1.19'
manifest=json.loads((O/'ruby-manifest.js').read_text().split('=',1)[1].rstrip(';'))
count=0
for book,expected in manifest['books'].items():
 packed=(O/'ruby-data'/(book+'.json.gz')).read_bytes();raw=gzip.decompress(packed);assert len(raw)==expected['bytes'];assert hashlib.sha256(raw).hexdigest()==expected['sha256'];assert hashlib.sha256(packed).hexdigest()==expected['packed_sha256'];data=json.loads(raw)
 s=(R/'releases/v1.14/extra-data'/(book+'.js')).read_text();m=re.search(r'window.ExtraBibleBooks\["[A-Z0-9]{3}"\]=',s);source=json.loads(s[m.end():].rstrip(';'))['editions']['jpn-bungo'];assert len(source)==len(data['rows'])==expected['rows'];assert hashlib.sha256(json.dumps(source,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==expected['source_hash']==data['source_hash']
 for row,tokens in zip(source,data['rows']):assert row[:2]==tokens[:2] and row[2]==''.join(t[0] for t in tokens[2]);count+=1
assert count==31099 and len(manifest['books'])==66
print('PASS: all 31,099 Japanese token readings reconstruct unchanged source exactly; 66 packed checksums/lengths/source bindings; kana is explicitly experimental')
