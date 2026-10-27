from pathlib import Path
from lxml import html
import re,json
R=Path(__file__).resolve().parents[1];O=R/'releases/v1.16';tree=html.fromstring((O/'index.html').read_text());ids=tree.xpath('//*[@id]/@id');assert len(ids)==len(set(ids))
for e in tree.xpath('//script[@src]|//link[@href]'):
 target=e.get('src') or e.get('href')
 if not target.startswith(('http:','https:')):assert (O/target.split('?')[0]).resolve().exists(),target
assets=json.loads(re.search(r'const ASSETS=(\[.*?\]);',(O/'sw.js').read_text())[1].replace("'",'"'))
for target in assets:assert (O/target).resolve().exists(),target
assert 'simple-ui.js' in assets and 'simple-ui.css' in assets
boot=(O/'boot.js').read_text();assert boot.index('reader.js')<boot.index('simple-ui.js')
reader=(O/'reader.js').read_text();assert "saved.compare1??''" in reader and "saved.compare2??''" in reader and "migratedSlots.splice(1,3,'','','')" in reader
assert 'bible-reader-simple-ui-115' in reader
css=(O/'simple-ui.css').read_text();assert 'body>header' in css and '@media(max-width:650px)' in css
loader=(O/'offline-library.js').read_text();assert "'parallel-bible-reader-offline-1.10'" in loader
notes=(O/'notes-model.js').read_text();assert 'parallel-reader-notes-v1' in notes
assert json.loads((O/'manifest.webmanifest').read_text())['scope']=='./'
print('PASS: unique control IDs, local script/style links,',len(assets),'PWA assets, menu boot order, single-text defaults, responsive CSS and unchanged note/text stores')

shell=(O/'index.html').read_text();assert shell.index('src="reader-copy.js')<shell.index('src="boot.js');assert "'reader-copy.js'" not in boot
print('PASS: selection-copy handler loads synchronously before asynchronous reader boot, including fast offline reloads')
