"""Build an empty, network-free PPTX skeleton from python-pptx's MIT template."""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import json,re,xml.etree.ElementTree as E,importlib.metadata
from pptx import Presentation

out=Path(__file__).resolve().parents[1]/'releases/v1.14'
buf=BytesIO();Presentation().save(buf)
with ZipFile(buf) as z:
    parts={n:z.read(n).decode('utf-8') for n in z.namelist() if n.endswith(('.xml','.rels'))}
for key in ['_rels/.rels','ppt/_rels/presentation.xml.rels']:
    parts[key]=re.sub(r'<Relationship\b[^>]*Target="[^"]*(?:thumbnail\.jpeg|printerSettings1\.bin)"[^>]*/>','',parts[key])
E.register_namespace('','http://schemas.openxmlformats.org/package/2006/content-types')
root=E.fromstring(parts['[Content_Types].xml'])
for n in list(root):
    if n.get('Extension') in ['jpeg','bin']:root.remove(n)
parts['[Content_Types].xml']=E.tostring(root,encoding='utf-8',xml_declaration=True).decode()
version=importlib.metadata.version('python-pptx')
(out/'office-template.js').write_text('/* Empty presentation package generated with python-pptx '+version+' (MIT). No note text is stored here. */\nwindow.ReaderOfficeTemplate='+json.dumps(parts,separators=(',',':'))+';\n')
licenses=[]
dist=importlib.metadata.distribution('python-pptx')
for file in dist.files:
    if str(file).endswith('/LICENSE'):
        licenses.append(dist.locate_file(file).read_text())
assert licenses,'Retain python-pptx license with the generated template'
(out/'OFFICE-TEMPLATE-LICENSE.txt').write_text('Template generated from python-pptx '+version+'.\n\n'+licenses[0])
print('Generated',len(parts),'XML parts; removed printer settings and thumbnail; retained MIT license')
