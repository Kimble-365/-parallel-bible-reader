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
# Preserve additional concurrent Greek/LXXL groups without copying their payloads.
s=(B/'offline-library.js').read_text()
s=s.replace("new URL((", "new URL((kind==='bhh'?'bhh-data/':",1)
for folder in ['related-data','ntgl-data','lxxl-data']:s=s.replace("?'"+folder+"/'", "?'../v1.22/"+folder+"/'")
s=s.replace("['lxxl','ntgl','related','nordic']","['bhh','lxxl','ntgl','related','nordic']")
s=s.replace("const expected=(", "const expected=(kind==='bhh'?window.BHHTextPacks:",1)
s=s.replace("const kindOf=id=>","const kindOf=id=>editions.get(id)?.data_group==='bhh-1.23'?'bhh':",1)
(O/'offline-library.js').write_text(s)
for name in ['ntgl-manifest.js','lxxl-manifest.js']:shutil.copyfile(B/name,O/name)
s=(B/'index.html').read_text().replace('1.22','1.23')
s=s.replace('<script src="pack-manifest.js','<script src="bhh-manifest.js"></script><script src="pack-manifest.js',1)
s=s.replace('href="lxxl/index.html"','href="../v1.22/lxxl/index.html"').replace('href="ntgl-resources.html"','href="../v1.22/ntgl-resources.html"')
s=s.replace('<footer>','<footer><p><a href="bhh.html">BHH — manuscripts, source texts and textual research</a> · <a href="../v1.22/ntgl-resources.html">Greek lexicon and study resources</a></p>',1)
(O/'index.html').write_text(s)
p=O/'sw.js';s=p.read_text()
for name in ['ntgl-manifest.js','lxxl-manifest.js']:
 if "'"+name+"'" not in s:s=s.replace('const ASSETS=[','const ASSETS=['+repr(name)+',',1)
p.write_text(s)
d=read(B/'study-catalog.js');mine=read(O/'study-catalog.js');d+=[x for x in mine if x['id']=='bhh-research']
for x in d:
 if x.get('url')=='ntgl-resources.html':x['url']='../v1.22/ntgl-resources.html'
write(O/'study-catalog.js','ReaderStudyCatalog',d)
s=(B/'LICENSES.md').read_text()+'\n'+(R/'tools/bhh-123/NOTICE.md').read_text()
s=s.replace('raw paths: sources/related-import.json','raw paths: ../v1.22/sources/related-import.json').replace('see related-projects.md for rights limits','see ../v1.22/related-projects.md for rights limits')
s=s.replace('sources/ntgl-','../v1.22/sources/ntgl-')
(O/'LICENSES.md').write_text(s.rstrip()+'\n')
