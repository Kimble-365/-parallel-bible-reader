"""Prepare exact, reader-only static assets for the Rust app; no user data or network."""
from pathlib import Path
import sys,shutil,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from package_reader_20 import inventory,digest
def main():
 out=ROOT/'apps/native-20/dist';out.mkdir(parents=True,exist_ok=True);files=inventory(ROOT)
 for name,source in files.items():
  target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 (out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Parallel Bible Reader 2.0</title><a href="releases/v2.0/">Open Reader 2.0</a><script>location.replace("releases/v2.0/"+location.search+location.hash)</script></html>')
 report={'version':'2.0.0','files':[{'path':n,'bytes':p.stat().st_size,'sha256':digest(p)} for n,p in files.items()],'private_data_included':False,'dataset_version_preserved':True}
 (out/'NATIVE-ASSET-MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Prepared native 2.0:',len(files),'verbatim runtime/source files;',sum(p.stat().st_size for p in files.values()),'bytes')
if __name__=='__main__':main()
