"""Optional pinned acquisition helper; PyYAML needed for POB records.
Downloads source texts into /workspace/reader-related; never invokes an AI model.
USFM acquisition uses sources/related-import.json, not mutable upstream main.
"""
import json,urllib.request,tarfile,gzip,concurrent.futures,hashlib
from pathlib import Path
base=Path('/workspace/reader-related');records=[]
def fetch(repo,sha,path):
 u=f'https://raw.githubusercontent.com/{repo}/{sha}/{urllib.parse.quote(path)}';b=urllib.request.urlopen(u,timeout=90).read();q=base/repo.split('/')[1]/path;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);return dict(repo=repo,sha=sha,path=path,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
jobs=[]
manifest=json.loads((Path(__file__).resolve().parents[1]/'releases/v1.22/sources/related-import.json').read_text())
for ed in manifest['editions']:
 if ed['id']=='eng-pob':continue
 prefix='exportedFiles/cleanedUSFM/'+('LiteralVersion' if ed['id']=='eng-oet-lv' else 'ReadersVersion')+'/' if ed['id'].startswith('eng-oet') else 'artifacts/us-release/usfm/'
 for f in ed['files']:jobs.append((ed['repo'],ed['commit'],prefix+Path(f['path']).name.removesuffix('.gz')))
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for r in pool.map(lambda a:fetch(*a),jobs):records.append(r)
(base/'acquisition.json').write_text(json.dumps(records,indent=2));print('USFM files',len(records),flush=True)
repo='zackseyun/peoples-open-bible';sha='5a6633695bfcc3264f508974c104ad556892c036';url=f'https://codeload.github.com/{repo}/tar.gz/{sha}'
with urllib.request.urlopen(url,timeout=180) as response,tarfile.open(fileobj=response,mode='r|gz') as tar:
 with gzip.open(base/'pob-canonical.jsonl.gz','wt') as out:
  import yaml
  count=0
  for m in tar:
   path=m.name.split('/',1)[-1]
   if m.isfile() and path.startswith(('translation/ot/','translation/nt/')) and path.endswith('.yaml'):
    b=tar.extractfile(m).read();d=yaml.safe_load(b);out.write(json.dumps(dict(path=path,sha256=hashlib.sha256(b).hexdigest(),data=d),ensure_ascii=False)+'\n');count+=1
  assert count==31221, 'Unexpected canonical source count'
  (base/'pob-complete').write_text(json.dumps(dict(verses=count,archive_finished=True)))
  print('POB verses',count,flush=True)
