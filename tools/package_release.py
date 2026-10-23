"""Build a self-contained reader ZIP; do not alter production assets."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import argparse,json,os
ROOT=Path(__file__).resolve().parents[1]
def build(version,outdir=None,reader_only=False):
 release=ROOT/'releases'/('v'+version)
 html=(release/'index.html').read_text().replace('data-data-path="../../data/"','data-data-path="data/"')
 html=html.replace('../../catalog.js','catalog.js').replace('../../reader-guides.js','reader-guides.js').replace('href="../../"','href="https://kimble-365.github.io/-parallel-bible-reader/"').replace('href="../"','href="https://kimble-365.github.io/-parallel-bible-reader/releases/"')
 target=Path(outdir) if outdir else Path('/workspace/reader-artifacts')/('v'+version);target.mkdir(parents=True,exist_ok=True);archive=target/('parallel-bible-reader-'+version+'.zip')
 files={p.name:p for p in [ROOT/'catalog.js',ROOT/'reader-guides.js',ROOT/'LICENSE',ROOT/'LICENSES.md']}
 files.update({str(p.relative_to(ROOT)):p for p in (ROOT/'data').glob('*.js')})
 for p in release.rglob('*'):
  if reader_only and 'sources' in p.relative_to(release).parts and (p.suffix=='.zip' or p.stat().st_size>100000):continue
  if p.is_file() and not (p.name.startswith('parallel-bible-reader-') and p.suffix=='.zip') and p!=release/'index.html':files[str(p.relative_to(release))]=p
 with ZipFile(archive,'w',ZIP_DEFLATED) as z:
  z.writestr('index.html',html)
  for name,p in sorted(files.items()):
   if p.suffix=='.html':
    text=p.read_text();prefix=os.path.relpath('.',Path(name).parent)
    for asset in ['catalog.js','reader-guides.js']:
     text=text.replace('../../../'+asset,prefix+'/'+asset).replace('../../'+asset,prefix+'/'+asset)
    z.writestr(name,text)
   else:z.write(p,name)
  z.writestr('.nojekyll','')
  if reader_only:z.writestr('sources/README.txt','Reader-only offline package. Raw source archives are available online at https://kimble-365.github.io/-parallel-bible-reader/releases/v1.8/source-library/ . Text display data, attribution and licenses remain included. Audio requires internet.\n')
 with ZipFile(archive) as z:
  assert z.testzip() is None
  assert not any('encyclopedia' in n.lower() or 'node_modules' in n for n in z.namelist())
  assert 'data/GEN.js' in z.namelist()
 print(json.dumps({'version':version,'zip':str(archive),'bytes':archive.stat().st_size}))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('version');parser.add_argument('--outdir');parser.add_argument('--reader-only',action='store_true');args=parser.parse_args();build(args.version,args.outdir,args.reader_only)
