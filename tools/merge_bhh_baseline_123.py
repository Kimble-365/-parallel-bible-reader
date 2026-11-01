"""Preserve the latest 1.22 English comparison increment in BHH 1.23."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1];B=R/'releases/v1.22';O=R/'releases/v1.23'
def read(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
def write(p,name,d):p.write_text('window.'+name+'='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n')
c=read(B/'catalog.js');mine=read(O/'catalog.js');c['editions']+=[x for x in mine['editions'] if x.get('data_group')=='bhh-1.23'];write(O/'catalog.js','BibleCatalog',c)
d=read(B/'translations/metadata.js');mine=read(O/'translations/metadata.js');ids={x['id'] for x in d};d += [x for x in mine if x['id'] not in ids];write(O/'translations/metadata.js','TranslationDirectory',d)
s=(B/'offline-library.js').read_text();s=s.replace("kind==='related'?'related-data/':","kind==='bhh'?'bhh-data/':kind==='related'?'../v1.22/related-data/':");s=s.replace("['related','nordic']","['bhh','related','nordic']");s=s.replace("(kind==='related'?window.RelatedTextPacks:window.ReaderTextPacks)","(kind==='bhh'?window.BHHTextPacks:kind==='related'?window.RelatedTextPacks:window.ReaderTextPacks)");s=s.replace("const kindOf=id=>","const kindOf=id=>editions.get(id)?.data_group==='bhh-1.23'?'bhh':");(O/'offline-library.js').write_text(s)
shutil.copyfile(B/'related-manifest.js',O/'related-manifest.js')
p=O/'index.html';s=p.read_text();s=s.replace('<script src="bhh-manifest.js">','<script src="related-manifest.js"></script><script src="bhh-manifest.js">') if 'src="related-manifest.js"' not in s else s;p.write_text(s)
p=O/'sw.js';s=p.read_text().replace("const ASSETS=[","const ASSETS=['related-manifest.js',") if "ASSETS=['related-manifest.js'" not in p.read_text() else p.read_text();p.write_text(s)
p=O/'LICENSES.md';s=p.read_text();additional=(B/'LICENSES.md').read_text().split('## Related English',1)
if len(additional)>1 and '## Related English' not in s:s+='\n## Related English'+additional[1]
else:
 tail=(B/'LICENSES.md').read_text()[-5000:];marker='## Related';start=tail.find(marker)
 if start>=0 and tail[start:start+60] not in s:s+='\n'+tail[start:]
s=s.replace('raw paths: sources/related-import.json','raw paths: ../v1.22/sources/related-import.json').replace('see related-projects.md for rights limits','see ../v1.22/related-projects.md for rights limits');p.write_text(s)
print('Retained',len(c['editions'])-3,'baseline editions; total',len(c['editions']))
