"""Reproducible 1.28 reader-only distribution; retain source/runtime bytes and paths."""
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import argparse,hashlib,json,re,shutil

ROOT=Path(__file__).resolve().parents[1]
PREFIXES=[
 'data/', 'releases/v1.28/',
 'releases/v1.8/extra-data/','releases/v1.8/pronunciation/',
 'releases/v1.10/extra-data/','releases/v1.11/extra-data/',
 'releases/v1.13/extra-data/','releases/v1.14/extra-data/','releases/v1.15/extra-data/',
 'releases/v1.18/packed-data/','releases/v1.18/japanese-data/','releases/v1.19/ruby-data/',
 'releases/v1.22/lxxl-data/','releases/v1.22/ntgl-data/','releases/v1.22/related-data/',
 'releases/v1.23/bhh-data/','releases/v1.23/bhh-dss/',
 'releases/v1.24/interlinear-index/',
 'releases/v1.25/syriac-data/','releases/v1.25/syriac-index/','releases/v1.25/syriac-lexicon/'
]
VERSIONS=['1.8','1.10','1.11','1.13','1.14','1.15','1.18','1.19','1.22','1.23','1.24','1.25','1.28']
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def inventory(root):
 found={}
 for prefix in PREFIXES:
  d=root/prefix
  if not d.is_dir():raise ValueError('Missing required directory: '+prefix)
  for p in d.rglob('*'):
   if p.is_file() and p.suffix!='.zip':found[p.relative_to(root).as_posix()]=p
 for name in ['LICENSE','LICENSES.md','reader-guides.js']:
  p=root/name
  if not p.is_file():raise ValueError('Missing required asset: '+name)
  found[name]=p
 # Preserve license/provenance material. Raw source ZIPs and old application shells are not bundled.
 for version in VERSIONS:
  base=root/'releases'/('v'+version)
  for name in ['LICENSES.md','LICENSE','PRAYER-SOURCES.md']:
   p=base/name
   if p.is_file():found[p.relative_to(root).as_posix()]=p
  for dirname in ['sources','bhh-sources']:
   d=base/dirname
   if d.is_dir():
    for p in d.rglob('*'):
     if p.is_file() and p.suffix.lower() in {'.json','.txt','.md'}:found[p.relative_to(root).as_posix()]=p
 for name in ['releases/v1.8/source-library/index.html','releases/v1.22/ntgl-resources.html']:
  p=root/name
  if p.is_file():found[name]=p
 for name in found:
  if any(x in name.lower() for x in ['encyclopedia','node_modules','incoming/','canonical.epub']):raise ValueError('Unexpected distribution content: '+name)
 return dict(sorted(found.items()))

LAUNCHER='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Parallel Bible Reader 1.28</title><body><h1>Parallel Bible Reader 1.28</h1><p>For the full reader, run <code>python3 START-READER.py</code> in the extracted folder (Windows: <code>py START-READER.py</code>). Python 3 is required; no extra packages or account are needed.</p><p>Direct opening from Files uses a file:// address. Browsers restrict fetch, workers and persistent storage there, so this is not a complete extract-and-open edition. On iPhone/iPad use an HTTPS-hosted reader and save texts for offline reading.</p><p><a href="releases/v1.28/index.html">Open reader directly (browser restrictions may apply)</a></p><p>Read README-1.28.txt for coverage, licenses, saved-data transfer and limitations.</p><script>if(location.protocol==='http:'||location.protocol==='https:')location.replace('releases/v1.28/'+location.search+location.hash);</script></body></html>'''
STARTER='''"""Serve only this extracted folder on loopback with a stable origin for saved notes."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import argparse,functools,webbrowser
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);p.add_argument('--no-browser',action='store_true');a=p.parse_args()
if not 1024<=a.port<=65535:p.error('Choose a port from 1024 to 65535.')
root=Path(__file__).resolve().parent
handler=functools.partial(SimpleHTTPRequestHandler,directory=str(root))
try:s=ThreadingHTTPServer(('127.0.0.1',a.port),handler)
except OSError as e:raise SystemExit('Could not open the local port. Close an older reader server or choose --port. Changing the port changes the browser storage origin. '+str(e))
url='http://127.0.0.1:'+str(a.port)+'/releases/v1.28/'
print('Parallel Bible Reader 1.28: '+url+' — press Ctrl+C to stop.')
if not a.no_browser:webbrowser.open(url)
try:s.serve_forever()
except KeyboardInterrupt:pass
finally:s.server_close()
'''
README='''Parallel Bible Reader 1.28 — reader-only review package

Open with Python 3: python3 START-READER.py (Windows: py START-READER.py).
The launcher opens the full reader at http://127.0.0.1:8765/releases/v1.28/ .
Keep the server running while reading. No installation of Python packages, account,
API key or Internet connection is needed for the included Bible reading assets.
Run only trusted launchers; this one uses Python's standard loopback HTTP server.

Retain this exact extracted folder structure. Do not move index.html or individual
release folders: shared text datasets deliberately retain their original paths.
All application shell assets, all 84 catalog editions and all their
local text delivery families are retained. Font choices, verse actions, Notes,
highlights, PNG export, Compare and the 14 editorial faith/prayer resources remain.
The application and source dataset versions are separate; dataset IDs are unchanged.

Direct file:// opening is limited by browser security and is not promised to run
the full reader. Desktop Safari/Chrome/Edge can use the local server. iPhone/iPad
Files is not a web server; use a separately approved HTTPS publication/PWA there.
The existing production website is not changed by building this package.

Use the same browser, host (127.0.0.1) and port (8765) across local sessions to keep
the same saved-data origin. GitHub Pages and a local server have separate stores.
Export a Notes/vocabulary backup before transfer. Browser site data includes other
preferences, bookmarks and highlights; do not clear it. This package neither reads
nor rewrites existing browser stores during build or extraction.

Included text is not all MIT/public domain. Each edition retains its catalog
attribution and LICENSES.md terms (including noncommercial/share-alike conditions).
Project LICENSE does not relicense Bible texts. Provenance/license metadata is
included verbatim. Original source ZIP archives, encyclopedias, repository history,
the unavailable 1.29 package and private user data are excluded.

Bible.is/audio/video, publisher links, raw source-archive links, and source-hosted
study/apparatus resources may require Internet. Some historical source links are
not mirrored in this reader-only ZIP. Save supported study sources while online
before expecting them offline. The 84-edition count is not a claim of 84 complete
66-book Bibles; original coverage/canons/source numbering remain per edition.

PACKAGE-MANIFEST.json records SHA-256/size for every other file, distinguishing
verbatim repository files from generated launch/docs files. The separate .sha256
checks the whole ZIP. Rebuild determinism is verified with the same pinned inputs
and Python/zlib environment. A package is a review artifact, not a deployment or
an authorization to merge, publish a GitHub Release or change permissions.
'''
def build(root,out,commit):
 root=Path(root).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
 files=inventory(root)
 raw=(root/'releases/v1.28/catalog.js').read_text();catalog=json.loads(raw.split('=',1)[1].strip().removesuffix(';'))
 editions=catalog['editions']
 if len(editions)!=84:raise ValueError('Expected the preserved 84-edition baseline')
 generated={'index.html':LAUNCHER.encode(),'START-READER.py':STARTER.encode(),'README-1.28.txt':README.encode(),'releases/index.html':b'<!doctype html><html lang="en"><meta charset="utf-8"><title>Packaged reader</title><h1>Parallel Bible Reader 1.28</h1><p><a href="v1.28/">Open packaged reader</a></p><p>Other historical app shells are not included. Keep the shared data folders.</p></html>','.nojekyll':b''}
 items=[{'path':n,'bytes':p.stat().st_size,'sha256':digest(p),'kind':'verbatim-repository'} for n,p in files.items()]
 items +=[{'path':n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'kind':'generated-package'} for n,b in generated.items()]
 manifest={'application_version':'1.28','source_commit':commit,'package_kind':'reader-only-review','edition_count':len(editions),'editions':[{'id':e['id'],'books':len(e['book_codes']),'license':e.get('license'),'license_url':e.get('license_url'),'required_attribution':e.get('required_attribution'),'source':e.get('source_url') or e.get('source')} for e in editions],'files':sorted(items,key=lambda x:x['path']),'manifest_self_excluded':True,'local_file_full_reader_supported':False,'requires_server_for_full_reader':True}
 generated['PACKAGE-MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
 archive=out/'parallel-bible-reader-1.28.zip'
 with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
  for name in sorted(set(files)|set(generated)):
   info=ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16;info.create_system=3
   with z.open(info,'w') as target:
    if name in generated:target.write(generated[name])
    else:
     with files[name].open('rb') as source:shutil.copyfileobj(source,target,1024*1024)
 result={'version':'1.28','source_commit':commit,'archive':archive.name,'archive_bytes':archive.stat().st_size,'sha256':digest(archive),'file_count':len(files)+len(generated),'uncompressed_bytes':sum(p.stat().st_size for p in files.values())+sum(map(len,generated.values())),'edition_count':len(editions)}
 (out/(archive.name+'.sha256')).write_text(result['sha256']+'  '+archive.name+'\n')
 (out/'PACKAGE-REPORT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--out',required=True);p.add_argument('--commit',required=True);a=p.parse_args()
 if not re.fullmatch('[0-9a-f]{40}',a.commit):p.error('Use the exact 40-character source commit.')
 build(a.root,a.out,a.commit)
