"""Optional token-level kana annotations; not reviewed pronunciation or source text."""
from pathlib import Path
import json,gzip,hashlib,re,sys
sys.path.insert(0,str(Path(__file__).parent))
from build_japanese_reading_118 import engine,js,ROOT
OUT=ROOT/'releases/v1.19';(OUT/'ruby-data').mkdir(exist_ok=True)
k,provenance=engine('/workspace/reader-tools/pykakasi','/workspace/reader-tools/jaconv')
manifest={};count=0
for p in sorted((ROOT/'releases/v1.14/extra-data').glob('*.js')):
 s=p.read_text();m=re.search(r'window.ExtraBibleBooks\["[A-Z0-9]{3}"\]=',s);source=json.loads(s[m.end():].rstrip(';'))['editions']['jpn-bungo'];rows=[]
 for c,v,text,*_ in source:
  tokens=k.convert(text);assert ''.join(x['orig'] for x in tokens)==text
  rows.append([c,v,[[x['orig'],x['hira']] for x in tokens]])
 raw=json.dumps({'book':p.stem,'source_hash':js(OUT/'search-manifest.js')['editions']['jpn-bungo'][p.stem],'rows':rows},ensure_ascii=False,separators=(',',':')).encode();packed=gzip.compress(raw,compresslevel=9,mtime=0);(OUT/'ruby-data'/(p.stem+'.json.gz')).write_bytes(packed)
 manifest[p.stem]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'packed_sha256':hashlib.sha256(packed).hexdigest(),'rows':len(rows),'source_hash':hashlib.sha256(json.dumps(source,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()};count+=len(rows)
result={'revision':'experimental-japanese-ruby-1.19-1','units':count,'engine':provenance,'status':'Automatic dictionary kana; historical/contextual/name readings may be wrong. Not publisher-supplied furigana or a recording transcript.','books':manifest}
(OUT/'ruby-manifest.js').write_text('window.ReaderRubyManifest='+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';')
print(json.dumps({'books':len(manifest),'units':count,'packed_bytes':sum(p.stat().st_size for p in (OUT/'ruby-data').glob('*.gz'))}))
