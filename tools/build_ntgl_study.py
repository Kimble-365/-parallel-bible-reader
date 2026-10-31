"""Import public-domain lexicon, CC BY crosswalks, and attributed morphology sample."""
from pathlib import Path
import json,gzip,hashlib,re,xml.etree.ElementTree as ET
from lxml import etree
R=Path(__file__).resolve().parents[1];O=R/'releases/v1.22';N=Path('/workspace/TheWay/NTGL');S=Path('/tmp/ntgl-ready-sources')
def packed(path,obj):
 raw=json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode();z=gzip.compress(raw,mtime=0);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z)
 return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'packed_bytes':len(z),'packed_sha256':hashlib.sha256(z).hexdigest()}
tree=etree.parse(str(S/'abbott-smith/abbott-smith.tei.xml'));entries=[]
for e in tree.xpath('//*[local-name()="entry"]'):
 orth=e.xpath('./*[local-name()="form"]/*[local-name()="orth"]')
 entries.append({'key':e.get('n','').split('|')[0],'orth':' '.join(''.join(x.itertext()) for x in orth),'text':' '.join(''.join(e.itertext()).split())})
assert len(entries)==6153
packed(N/'sources/reader-corpora/abbott-smith.json.gz',{'source':'translatable-exegetical-tools/Abbott-Smith','revision':'8c00cb244761aa23659421a8cbbbf7a3b27b7d59','blob_sha':'e10dcfa534dbc71168ca6ac273e991348bab2bb2','license':'Public domain as declared by project README','xml':(S/'abbott-smith/abbott-smith.tei.xml').read_text()})
def mapping(name):
 text=(S/'integration'/name).read_text(encoding='utf-8-sig')
 return {json.loads('"'+m[1]+'"'):json.loads('"'+m[2]+'"') for m in re.finditer(r'"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"',text)}
lookups={'morphgnt_to_wordlist':mapping('gntLookups.js'),'wordlist_to_abbott':mapping('gwl2AsLookups.js'),'license':'CC BY 4.0','attribution':'Open Scriptures Septuagint Project','warning':'Upstream gntLookups header reports 87 mismatched entries. Suggestions require review, not automatic lemma identity.'}
packed(N/'sources/reader-corpora/greekresources.json.gz',{'source':'openscriptures/GreekResources','files':{p.name:p.read_text() for p in (S/'integration').glob('*Lookups.js')},'license':'CC BY 4.0'})
morph=[]
for line in (S/'integration/64-Jn-morphgnt.txt').read_text().splitlines():
 f=line.split()
 if f and f[0] in {f'04010{v}' for v in range(1,6)}:
  assert len(f)==7;morph.append({'reference':'JHN 1:'+str(int(f[0][-2:])),'part_of_speech':f[1],'analysis':f[2],'text':f[3],'word':f[4],'normalized':f[5],'lemma':f[6]})
assert len(morph)==61
packed(N/'sources/reader-corpora/morphgnt-pilot.json.gz',{'source':'morphgnt/sblgnt','scope':'JHN 1:1-5 only','version':'6.12 as cited by README','license_annotations':'CC BY-SA 3.0','text_license_current_official_source':'CC BY 4.0','records':morph})
projects=[json.loads(l) for l in (N/'data/github_projects.jsonl').read_text().splitlines()]
data={'lexicon':{'title':'Abbott-Smith, A Manual Greek Lexicon of the New Testament (1922)','license':'Public domain; digital TEI project declares public-domain markup','source':'https://github.com/translatable-exegetical-tools/Abbott-Smith','historical_not_modern_review':True,'entries':entries},'crosswalks':lookups,'morphgnt_pilot':morph,'projects':projects,'limits':['MorphGNT sample is independently identified, not assumed to match every version of SBLGNT.','CBGM libraries and CollateX are analysis tools, not Bible editions. No genealogical result is asserted.']}
meta=packed(O/'ntgl-data/study.json.gz',data);meta['lexicon_entries']=len(entries);meta['morphgnt_pilot_words']=len(morph)
(O/'ntgl-study-manifest.js').write_text('window.NTGLStudyPack='+json.dumps(meta)+';\n')
# Explicit evidence-only TEI: no invented adopted lemma, local stemma, or genealogy.
root=ET.Element('TEI',xmlns='http://www.tei-c.org/ns/1.0');header=ET.SubElement(root,'teiHeader');fd=ET.SubElement(header,'fileDesc');ET.SubElement(ET.SubElement(fd,'titleStmt'),'title').text='NTGL pilot evidence; no local stemmata supplied'
ET.SubElement(ET.SubElement(fd,'publicationStmt'),'p').text='CC BY-NC-SA 3.0 for Sinaiticus-derived evidence; source attribution in NTGL notices.'
ET.SubElement(ET.SubElement(fd,'sourceDesc'),'p').text='Codex Sinaiticus Project transcription v1.95; no manuscript images checked.'
body=ET.SubElement(ET.SubElement(root,'text'),'body');wits=ET.SubElement(body,'listWit');ET.SubElement(wits,'witness',{'{http://www.w3.org/XML/1998/namespace}id':'GA01'}).text='One physical manuscript: Codex Sinaiticus'
for unit in [json.loads(l) for l in (N/'data/apparatus.jsonl').read_text().splitlines()]:
 app=ET.SubElement(body,'app',{'{http://www.w3.org/XML/1998/namespace}id':unit['id'],'loc':unit['reference']})
 for reading in unit['readings']:
  attrs={'n':reading['id']}
  if reading['supports']:attrs.update(wit='#GA01',hand=reading['supports'][0]['hand'])
  else:attrs['type']='comparison-edition-only'
  ET.SubElement(app,'rdg',attrs).text=' '.join(w['form'] for w in reading['display_tokens'])
ET.indent(root);ET.ElementTree(root).write(O/'sources/ntgl-pilot-evidence.tei.xml',encoding='utf-8',xml_declaration=True)
tokens=[json.loads(l) for l in (N/'indices/manuscript_tokens.jsonl').read_text().splitlines()]
collation={'metadata':{'physical_witnesses':1,'warning':'Original/corrected projections are computational inputs, not independent manuscript witnesses. No critical decision inferred.'},'witnesses':[{'id':'01-'+view,'tokens':[{'t':t['normalized_display'] or t['transcribed_text'],'n':t['transcribed_text']} for t in tokens if t['view']==view]} for view in ['original','corrected_ca']]}
(O/'sources/ntgl-collatex-input.json').write_text(json.dumps(collation,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(meta,indent=2))
