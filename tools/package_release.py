"""Build a self-contained reader ZIP; do not alter production assets."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
def build(version):
 release=ROOT/'releases'/('v'+version)
 html=(release/'index.html').read_text().replace('data-data-path="../../data/"','data-data-path="data/"')
 html=html.replace('../../catalog.js','catalog.js').replace('../../reader-guides.js','reader-guides.js').replace('href="../../"','href="https://kimble-365.github.io/-parallel-bible-reader/"').replace('href="../"','href="https://kimble-365.github.io/-parallel-bible-reader/releases/"')
 archive=release/('parallel-bible-reader-'+version+'.zip')
 files={p.name:p for p in [ROOT/'catalog.js',ROOT/'reader-guides.js',ROOT/'LICENSE',ROOT/'LICENSES.md']}
 files.update({str(p.relative_to(ROOT)):p for p in (ROOT/'data').glob('*.js')})
 for p in release.rglob('*'):
  if p.is_file() and p.suffix not in ['.zip'] and p.name!='index.html':files[str(p.relative_to(release))]=p
 with ZipFile(archive,'w',ZIP_DEFLATED) as z:
  z.writestr('index.html',html)
  for name,p in sorted(files.items()):z.write(p,name)
  z.writestr('.nojekyll','')
 with ZipFile(archive) as z:
  assert z.testzip() is None
  assert not any('encyclopedia' in n.lower() or 'node_modules' in n for n in z.namelist())
  assert 'data/GEN.js' in z.namelist()
 print(json.dumps({'version':version,'zip':str(archive),'bytes':archive.stat().st_size}))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('version');build(parser.parse_args().version)
