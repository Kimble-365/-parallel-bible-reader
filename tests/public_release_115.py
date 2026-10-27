"""Verify deployed Pages bytes after the main URL switches to the new release."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import urllib.request,hashlib,os,re,time
ROOT=Path(__file__).resolve().parents[1];APP=ROOT/'releases/v1.15';BASE='https://kimble-365.github.io/-parallel-bible-reader/';SHA=os.environ.get('GITHUB_SHA','verify-115')
def fetch(path):
 req=urllib.request.Request(urljoin(BASE,path)+'?verify='+SHA,headers={'Cache-Control':'no-cache','User-Agent':'ParallelBibleReader-release-verification'})
 with urllib.request.urlopen(req,timeout=45) as r:
  assert r.status==200;return r.read()
expected=(ROOT/'index.html').read_bytes();deadline=time.monotonic()+300
while True:
 try:
  if fetch('index.html')==expected:break
 except Exception as e:print('Deployment pending:',str(e),flush=True)
 if time.monotonic()>=deadline:raise RuntimeError('The current Pages root did not reach the expected commit within five minutes')
 time.sleep(10)
paths={'index.html','legacy/index.html','releases/index.html'}
for value in re.findall(r"'([^']+)'",(APP/'sw.js').read_text().split('const ASSETS=[',1)[1].split('];',1)[0]):
 p=(APP/value).resolve()
 if p.is_dir():p=p/'index.html'
 paths.add(str(p.relative_to(ROOT)))
for v in ['1.14','1.15']:
 for folder in ['extra-data','sources']:
  for p in (ROOT/'releases'/('v'+v)/folder).iterdir():
   if p.is_file():paths.add(str(p.relative_to(ROOT)))
paths.add('releases/v1.13/extra-data/JHN.js')
def check(path):
 data=fetch(path);assert hashlib.sha256(data).digest()==hashlib.sha256((ROOT/path).read_bytes()).digest(),path
 return path
with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,sorted(paths)))
assert b"'releases/v1.15/'" in fetch('index.html')
print('PASS: live Pages root is 1.15;',len(results),'public files HTTP 200 and byte-identical, including app shell, reused texts, all new book bundles and source archives; verification commit',SHA,flush=True)
