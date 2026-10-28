"""Build optional, explicitly unreviewed Japanese dictionary readings.
The GPL-licensed engine is a build dependency, not browser runtime code.
"""
from pathlib import Path
import argparse,sys,importlib.util,importlib,json,re,gzip,hashlib,types,shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'releases/v1.18'
def js(path):return json.loads(path.read_text().split('=',1)[1].rstrip(';\n'))
def engine(vendor,jaconv):
 if not vendor:
  from pykakasi import Kakasi
  return Kakasi(),{'engine':'PyKakasi installed package','license':'GPL-3.0-or-later','source':'https://github.com/miurahr/pykakasi'}
 root=Path(vendor);manifest=json.loads((root.parent/'pykakasi-source-manifest.json').read_text())
 for f in manifest['files']:
  b=(root/f['path']).read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['sha'],f['path']
 if jaconv:sys.path.insert(0,jaconv)
 spec=importlib.util.spec_from_file_location('reader_kakasi_builder',root/'src/kakasidict.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.Genkanwadict().generate_dictionaries(str(root/'src/pykakasi/data'))
 spec=importlib.util.spec_from_file_location('reader_kakasi',root/'src/pykakasi/__init__.py',submodule_search_locations=[str(root/'src/pykakasi')]);package=importlib.util.module_from_spec(spec);sys.modules['reader_kakasi']=package
 # Compatibility path lookup only; the old pinned core uses setuptools resources.
 if importlib.util.find_spec('pkg_resources') is None:
  resources=types.ModuleType('pkg_resources');resources.resource_filename=lambda package,name:str(Path(sys.modules[package].__file__).parent/name);sys.modules['pkg_resources']=resources
 core=importlib.import_module('reader_kakasi.kakasi');return core.Kakasi(),{'engine':'PyKakasi','commit':manifest['commit'],'license':'GPL-3.0-or-later','source':'https://github.com/miurahr/pykakasi','compatibility':'Unmodified modern conversion core; unused legacy compatibility exports not loaded. Filesystem resource lookup supplied through a local compatibility bridge.'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--vendor-root');ap.add_argument('--jaconv-root');a=ap.parse_args();k,provenance=engine(a.vendor_root,a.jaconv_root);(OUT/'japanese-data').mkdir(exist_ok=True);manifest={};unknown_total=0;count=0;failures=0
 assert k.convert('日本語')[0]['hepburn']=='nihongo'
 source_manifest=js(OUT/'search-manifest.js')['editions']['jpn-bungo']
 for p in sorted((ROOT/'releases/v1.14/extra-data').glob('*.js')):
  s=p.read_text();m=re.search(r'window.ExtraBibleBooks\["[A-Z0-9]{3}"\]=',s);data=json.loads(s[m.end():].rstrip(';'));source=data['editions']['jpn-bungo'];rows=[]
  assert hashlib.sha256(json.dumps(source,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==source_manifest[p.stem]
  for c,v,text,*_ in source:
   try:
    parts=k.convert(text);assert ''.join(x['orig'] for x in parts)==text
    reading=[];unknown=0
    for item in parts:
     roman=item['hepburn'];remaining=re.findall(r'[\u3400-\u9fff\uf900-\ufaff]',roman)
     if not roman and item['orig']:roman='['+item['orig']+']';unknown+=1
     elif remaining:roman=re.sub(r'([\u3400-\u9fff\uf900-\ufaff]+)',r'[\1]',roman);unknown+=len(remaining)
     reading.append(roman)
    latin=re.sub(r'\s+([.,!?;:])',r'\1',' '.join(x for x in reading if x)).strip()
   except Exception:
    latin='['+text+']';unknown=len(re.findall(r'[\u3040-\u30ff\u3400-\u9fff]',text));failures+=1
   rows.append([c,v,latin,unknown]);unknown_total+=unknown;count+=1
  raw=json.dumps({'book':p.stem,'source_hash':source_manifest[p.stem],'rows':rows},ensure_ascii=False,separators=(',',':')).encode();packed=gzip.compress(raw,compresslevel=9,mtime=0);(OUT/'japanese-data'/(p.stem+'.json.gz')).write_bytes(packed);manifest[p.stem]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'packed_sha256':hashlib.sha256(packed).hexdigest(),'source_hash':source_manifest[p.stem],'rows':len(rows)}
 result={'revision':'japanese-dictionary-reading-1.18-1','kind':'automatic dictionary reading, not a spoken transcript','review_status':'experimental; linguistic review pending','method':'Hepburn output from PyKakasi with dictionary context. Historical spellings/proper names may have incorrect readings. Unresolved source characters remain bracketed; original text is never replaced. Orthographic particles are not normalized to recorded speech.','engine':provenance,'books':manifest,'units':count,'unknown_characters':unknown_total,'fallback_verses':failures}
 (OUT/'japanese-manifest.js').write_text('window.ReaderJapaneseManifest='+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';');(OUT/'sources/japanese-reading-provenance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 if a.vendor_root:shutil.copyfile(Path(a.vendor_root)/'COPYING',OUT/'sources/PYKAKASI-LICENSE.txt')
 print(json.dumps({'units':count,'books':len(manifest),'unknown_characters':unknown_total,'fallback_verses':failures,'bytes':sum(p.stat().st_size for p in (OUT/'japanese-data').glob('*.gz'))}))
if __name__=='__main__':main()
