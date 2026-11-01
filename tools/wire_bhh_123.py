from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];O=R/'releases/v1.23'
p=O/'offline-library.js';s=p.read_text();s=s.replace("(kind==='nordic'?'../v1.18/packed-data/':","(kind==='bhh'?'bhh-data/':kind==='nordic'?'../v1.18/packed-data/':");s=s.replace("kind==='nordic'?'.json.gz'","(kind==='nordic'||kind==='bhh')?'.json.gz'");s=s.replace("if(kind==='nordic'){","if(kind==='nordic'||kind==='bhh'){");s=s.replace('const expected=window.ReaderTextPacks?.[book]','const expected=(kind===\'bhh\'?window.BHHTextPacks:window.ReaderTextPacks)?.[book]');s=s.replace("const kindOf=id=>editions.get(id)?.data_group==='nordic-1.18'","const kindOf=id=>editions.get(id)?.data_group==='bhh-1.23'?'bhh':editions.get(id)?.data_group==='nordic-1.18'");p.write_text(s)
p=O/'index.html';s=p.read_text().replace('<script src="pack-manifest.js','<script src="bhh-manifest.js"></script><script src="pack-manifest.js');s=s.replace('<footer>','<footer><p><a href="bhh.html">BHH — manuscripts, source texts and textual research</a></p>',1);p.write_text(s)
p=O/'sw.js';s=p.read_text().replace("'./','index.html'","'bhh-manifest.js','bhh.html','bhh.js','bhh-library.js','./','index.html'",1);p.write_text(s)
p=O/'study-catalog.js';d=json.loads(p.read_text().split('=',1)[1].rstrip(';\n'));d.append(dict(id='bhh-research',title='Biblia Hebraica Hepta — manuscripts and sources',category='Original languages',source=None,kind='reference',url='bhh.html',access='Read licensed source packs and individual DSS source units; manuscript damage and editorial status remain explicit.'));p.write_text('window.ReaderStudyCatalog='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n')
p=O/'translations/metadata.js';s=p.read_text();print(s[:50]);d=json.loads(s.split('=',1)[1].rstrip(';\n'))
for id,language,iso,script,family,branch in [('hbo-sp','Samaritan Hebrew','smp','Hebrew','Afro-Asiatic','Semitic'),('hbo-mam','Biblical Hebrew','hbo','Hebrew','Afro-Asiatic','Semitic'),('lat-clementine-thb','Latin','lat','Latin','Indo-European','Italic')]:d.append(dict(id=id,language=language,iso6393=iso,aliases=[language,'BHH',id],family=family,branch=branch,subfamily=branch,countries=[],continents=[],states=[],script=script,variety=id,classification_source='ISO language identity; project browsing groups; no asserted UBS provider identifier',ubs_id=None))
p.write_text(s.split('=',1)[0]+'='+json.dumps(d,ensure_ascii=False,separators=(',',':'))+';\n')

(O/"README.md").write_text((R/"tools/bhh-123/README.md").read_text())
p=O/"LICENSES.md"
if "## BHH additions (1.23)" not in p.read_text():p.write_text(p.read_text()+"\n"+(R/"tools/bhh-123/NOTICE.md").read_text())
