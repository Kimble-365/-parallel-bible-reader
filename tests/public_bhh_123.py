"""Byte-for-byte verification of the published root and every BHH release file."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,hashlib,time,json
from urllib.parse import quote
R=Path(__file__).resolve().parents[1];O=R/'releases/v1.23';base='https://kimble-365.github.io/-parallel-bible-reader/'
def fetch(p):
 req=urllib.request.Request(base+quote(p,safe='/')+'?bhhverify=1.23',headers={'Cache-Control':'no-cache','User-Agent':'BHH-source-integrity-check'})
 with urllib.request.urlopen(req,timeout=25) as r:return r.read()
expected=(R/'index.html').read_bytes();deadline=time.monotonic()+240
while True:
 try:
  if fetch('index.html')==expected:break
 except Exception:pass
 if time.monotonic()>deadline:raise RuntimeError('Pages root has not reached the prepared 1.23 release')
 time.sleep(5)
paths=['index.html','releases/index.html','legacy/index.html']+[str(p.relative_to(R)) for p in O.rglob('*') if p.is_file()]
def check(p):
 for attempt in range(3):
  try:
   b=fetch(p);assert hashlib.sha256(b).digest()==hashlib.sha256((R/p).read_bytes()).digest(),p;return len(b)
  except Exception:
   if attempt==2:raise
with ThreadPoolExecutor(max_workers=12) as pool:sizes=list(pool.map(check,paths))
result=dict(status='passed',reader='1.23',files=len(paths),bytes=sum(sizes),root=base,checked_epoch=int(time.time()),scope='Public root, history, legacy and every 1.23 release file byte-identical to local artifacts')
Path('/workspace/bhh-public-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
