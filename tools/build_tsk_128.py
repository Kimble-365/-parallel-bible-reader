"""Build source-preserving TSK and Finnish companion editions for reader 1.28.
Requires pysword 0.2.8. zCom and zText share the SWORD compressed verse layout.
"""
from pathlib import Path
from html.parser import HTMLParser
import argparse, collections, hashlib, json, re, shutil, gzip, zipfile
from pysword.bible import SwordBible

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('module',type=Path);p.add_argument('archive',type=Path);a=p.parse_args()
assert hashlib.sha256(a.archive.read_bytes()).hexdigest()=='6784c7099465995a8e66f02ead82b0bca66603c1bdeaf8332949774b7bfd4293','Unexpected source edition; review a new source before rebuilding'
with zipfile.ZipFile(a.archive) as z:
    for name in z.namelist():
        if name.endswith('/'):continue
        assert (a.module.parents[3]/name).read_bytes()==z.read(name),name
R=ROOT/'releases/v1.28';R.mkdir(exist_ok=True)
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
for f in (ROOT/'releases/v1.27').iterdir():
    if f.is_dir():shutil.copytree(f,R/f.name,dirs_exist_ok=True)
    elif f.suffix not in ['.zip'] and f.name!='README.md':shutil.copy2(f,R/f.name)
for f in [R/'index.html',R/'boot.js',R/'reader.js',R/'sw.js',R/'manifest.webmanifest',R/'VERSION']:
    f.write_text(f.read_text(encoding='utf-8').replace('1.27','1.28'),encoding='utf-8',newline='\n')
catalog=json.loads((R/'catalog.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
catalog['release_version']='1.28'; codes=[x['code'] for x in json.loads((ROOT/'texts/finnish-study-v005/metadata.json').read_text(encoding='utf-8'))['books']]
module=SwordBible(a.module,source_type='ThML')
books=[b for testament in ['ot','nt'] for b in module.get_structure()._books[testament]]
assert len(books)==len(codes)==66
limits={code:b.chapter_lengths for code,b in zip(codes,books)}
aliases={}
for code,b in zip(codes,books):
    for name in [code,b.name,b.osis_name,b.preferred_abbreviation]:aliases[name.lower().replace(' ','')]=code
for code,names in {'GEN':['Ge'], 'EXO':['Ex'], 'LEV':['Le'], 'NUM':['Nu'], 'DEU':['De'], 'JOS':['Jos'], 'JDG':['Jud'], 'RUT':['Ru'], '1SA':['1Sa'], '2SA':['2Sa'], '1KI':['1Ki'], '2KI':['2Ki'], '1CH':['1Ch'], '2CH':['2Ch'], 'EZR':['Ezr'], 'NEH':['Ne'], 'EST':['Es'], 'PSA':['Ps'], 'PRO':['Pr'], 'ECC':['Ec'], 'SNG':['So','Cant'], 'EZK':['Eze'], 'HOS':['Ho'], 'JOL':['Joe'], 'OBA':['Ob'], 'JON':['Jon'], 'NAM':['Na'], 'HAB':['Hab'], 'ZEP':['Zep'], 'HAG':['Hag'], 'ZEC':['Zec'], 'MAL':['Mal'], 'MAT':['Mt'], 'MRK':['Mr'], 'LUK':['Lu'], 'JHN':['Joh'], 'ACT':['Ac'], 'ROM':['Ro'], '1CO':['1Co'], '2CO':['2Co'], 'EPH':['Eph'], 'PHP':['Php'], 'COL':['Col'], '1TH':['1Th'], '2TH':['2Th'], '1TI':['1Ti'], '2TI':['2Ti'], 'TIT':['Tit'], 'PHM':['Phm'], 'JAS':['Jas'], '1PE':['1Pe'], '2PE':['2Pe'], '1JN':['1Jo'], '2JN':['2Jo'], '3JN':['3Jo'], 'JUD':['Jude'], 'REV':['Re']}.items():
    for name in names:aliases[name.lower()]=code
aliases.update({'da':'DAN','ga':'GAL','am':'AMO','la':'LAM'})
issues=[];link_count=0;source_tags=0
def parse_refs(s,origin):
    global link_count
    result=[];book,cv=origin.split();chapter=int(cv.split(':')[0])
    # Asterisk tails are TSK margin/language/title annotations, not references.
    for token in re.split(r'[;,]',s.split('*',1)[0]):
        token=token.strip().rstrip('.');original=token
        if not token:continue
        if token.lower()=='marg:':continue
        token=re.sub(r'\s*:\s*',':',token)
        m=re.match(r'^([1-3]?\s*[A-Za-z]+)\.?\s+(.*)$',token)
        if m:
            name=m[1].lower().replace(' ','');book=aliases.get(name);chapter=None;token=m[2]
        cross=re.fullmatch(r'(\d+):(\d+)-\s*([1-3]?\s*[A-Za-z]+)\s+(\d+):(\d+)',token)
        if cross and book:
            c1,v1,name,c2,v2=cross.groups();c1,v1,c2,v2=map(int,[c1,v1,c2,v2]);b2=aliases.get(name.lower().replace(' ',''))
            if b2 and codes.index(b2)>=codes.index(book) and 1<=c1<=len(limits[book]) and 1<=v1<=limits[book][c1-1] and 1<=c2<=len(limits[b2]) and 1<=v2<=limits[b2][c2-1]:
                result.append({'book':book,'chapter':c1,'verse':v1,'end_book':b2,'end_chapter':c2,'end_verse':v2,'label':original});link_count+=1;chapter=c1;continue
        m=re.fullmatch(r'(?:(\d+):)?(\d+)(?:-(?:(\d+):)?(\d+))?',token)
        if not book or not m:
            issues.append({'origin':origin,'source':s,'token':original,'reason':'unparsed'})
            partial=re.fullmatch(r'(\d+):',token)
            if partial:chapter=int(partial[1])
            else:book=None;chapter=None
            continue
        if m[1]:chapter=int(m[1])
        elif chapter is None:
            # An explicit book followed by a chapter without a colon denotes a chapter.
            chapter=int(m[2]);start=1;endchapter=int(m[4] or chapter);end=limits[book][endchapter-1] if 1<=endchapter<=len(limits[book]) else 0
            if 1<=chapter<=endchapter<=len(limits[book]):result.append({'book':book,'chapter':chapter,'verse':start,'end_chapter':endchapter,'end_verse':end,'label':original});link_count+=1;continue
        start=int(m[2]);endchapter=int(m[3] or chapter);end=int(m[4] or start)
        valid=1<=chapter<=len(limits[book]) and 1<=endchapter<=len(limits[book]) and 1<=start<=limits[book][chapter-1] and 1<=end<=limits[book][endchapter-1] and (endchapter,end)>=(chapter,start)
        if not valid:issues.append({'origin':origin,'source':s,'token':original,'reason':'outside KJV verse boundaries'});continue
        result.append({'book':book,'chapter':chapter,'verse':start,'end_chapter':endchapter,'end_verse':end,'label':original});link_count+=1
    return result
class Entry(HTMLParser):
    def __init__(self,origin):super().__init__(convert_charrefs=True);self.blocks=[];self.bits=[];self.inref=False;self.reftext=[];self.passage=None;self.origin=origin
    def flush(self):
        t=''.join(self.bits).strip()
        if t:self.blocks.append({'text':t})
        self.bits=[]
    def handle_starttag(self,t,attrs):
        if t=='br':self.flush()
        if t.lower()=='scripref':
            self.flush();self.inref=True;self.reftext=[];self.passage=dict(attrs).get('passage')
    def handle_data(self,s):
        (self.reftext if self.inref else self.bits).append(s)
    def handle_endtag(self,t):
        global source_tags
        if t.lower()=='scripref':
            source_tags+=1;s=''.join(self.reftext);refs=self.passage or s
            before=len(issues);targets=parse_refs(refs,self.origin)
            self.blocks.append({'text':s,'source_reference':refs,'targets':targets,'unlinked_notation':len(issues)>before});self.inref=False
raw=[];bybook={};nonempty=0
for code,b in zip(codes,books):
    rows=[]
    for ch,length in enumerate(b.chapter_lengths,1):
        for v in range(1,length+1):
            ref=f'{code} {ch}:{v}';text=module.get(books=[b.name],chapters=[ch],verses=[v],clean=False)
            if text:
                nonempty+=1;raw.append({'reference':ref,'thml':text});e=Entry(ref);e.feed(text);e.flush();blocks=e.blocks
            else:blocks=[{'text':'No TSK entry for this verse in the source module.'}]
            plain='\n'.join(x.get('source_reference',x['text']) for x in blocks)
            rows.append([ch,v,plain,None,None,None,None,{'blocks':blocks,'versification':'KJV'}])
    bybook[code]=rows
    print(code,flush=True)
S=R/'sources/tsk';S.mkdir(parents=True,exist_ok=True)
shutil.copy2(a.archive,S/'TSK-1.4.zip');shutil.copy2(a.module.parents[3]/'mods.d/tsk.conf',S/'tsk.conf')
rawbytes=('\n'.join(json.dumps(x,ensure_ascii=False,separators=(',',':')) for x in raw)+'\n').encode()
(S/'source-entries.jsonl.gz').write_bytes(gzip.compress(rawbytes,mtime=0))
dump(S/'reference-issues.json',issues)
report={'status':'PASS_WITH_SOURCE_ISSUES' if issues else 'PASS','source':'CrossWire TSK 1.4','url':'https://crosswire.org/ftpmirror/pub/sword/packages/rawzip/TSK.zip','license':'Public Domain','source_archive_sha256':hashlib.sha256(a.archive.read_bytes()).hexdigest(),'source_entries_sha256':hashlib.sha256(rawbytes).hexdigest(),'source_entries':nonempty,'source_scripref_tags':source_tags,'validated_target_links':link_count,'source_issues':len(issues),'scope':'Every parsed link endpoint checked against SWORD KJV chapter/verse boundaries. Source text retained; unparsed/out-of-bound references remain readable without invented links. Not a scholarly evaluation of every thematic connection. No KJV-to-Finnish versification mapping asserted.'}
dump(S/'validation.json',report)
fin=json.loads((ROOT/'texts/finnish-study-v005/bible.json').read_text(encoding='utf-8'))['verses']
notes=json.loads((ROOT/'texts/finnish-study-v005/footnotes.json').read_text(encoding='utf-8'))['notes'];refs=json.loads((ROOT/'texts/finnish-study-v005/crossreferences.json').read_text(encoding='utf-8'))['links']
ns=collections.defaultdict(list);xs=collections.defaultdict(list)
for n in notes:ns[n['reference']].append({'text':n['text'],'note_id':n['id']})
for x in refs:
    code,cv=x['target'].split();ch,v=map(int,cv.split(':'));xs[x['reference']].append({'book':code,'chapter':ch,'verse':v,'label':x['target']})
fr=collections.defaultdict(list);nr=collections.defaultdict(list)
for v in fin:
    code=v['book'];ch=v['chapter'];n=v['verse'];key=f'{code} {ch}:{n}';fr[code].append([ch,n,v['text'],None,None])
    blocks=list(ns[key]);
    if xs[key]:blocks.append({'text':'Ristiviitteet','targets':xs[key]})
    if not blocks:blocks=[{'text':'Ei lukijahuomautusta tähän jakeeseen.'}]
    nr[code].append([ch,n,'\n'.join(x['text']+(' '+', '.join(t['label'] for t in x['targets']) if x.get('targets') else '') for x in blocks),None,None,None,None,{'blocks':blocks,'versification':'Finnish project edition'}])
packs={}
for code in codes:
    data={'book':code,'editions':{'tsk-crosswire':bybook[code],'fin-study-v005':fr[code],'fin-study-notes-v005':nr[code]}}
    dump(R/f'study-data/{code}.json',data);f=R/f'study-data/{code}.json';packs[code]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
(R/'reference-manifest.js').write_text('window.ReaderReferencePacks='+json.dumps(packs,separators=(',',':'))+';\n',encoding='utf-8',newline='\n')
for id,label,lang,rows,kind,version in [('fin-study-v005','Suomenkielinen tutkimusraamattu v005','fi',fr,'bible','Finnish project source numbering'),('fin-study-notes-v005','Suomenkieliset alaviitteet ja ristiviitteet','fi',nr,'commentary','Finnish project source numbering'),('tsk-crosswire','TSK — Treasury of Scripture Knowledge (KJV numbering)','en',bybook,'commentary','KJV source numbering')]:
    base=dict(catalog['editions'][0]);base.update(id=id,label=label,title=label,language=lang,latin_language=lang,script='Latin',direction='ltr',scope='66 books · '+('reference companion' if kind=='commentary' else '31,170 verses'),book_codes=codes,positions=[[code,ch] for code in codes for ch in sorted({r[0] for r in rows[code]})],data_group='references-1.28',source='https://crosswire.org/sword/modules/ModInfo.jsp?modName=TSK' if id=='tsk-crosswire' else '../../texts/finnish-study-v005/',license='Public Domain' if id=='tsk-crosswire' else 'User-authorized project edition; unreviewed',attribution='CrossWire TSK 1.4 (2001-12-15), Public Domain.' if id=='tsk-crosswire' else 'Finnish project edition v005, 2026-11-18; AI-assisted, unreviewed.',required_attribution='',method=report['scope'] if id=='tsk-crosswire' else 'Frozen v005 text and reader notes, separate editions.',preserve_source_refs=True,versification_label=version,resource_kind=kind,available=True)
    for k in ['forms','directory','source_files','private_local','has_transliteration','audio','audio_id','book_labels']:base.pop(k,None)
    base['books']=66;base['verses']=sum(len(v) for v in rows.values());base['license_url']='https://crosswire.org/sword/copyright/ModInfoCopyright.jsp?modName=TSK' if id=='tsk-crosswire' else '../../texts/finnish-study-v005/README.md'
    catalog['editions'].append(base)
(R/'catalog.js').write_text('window.BibleCatalog='+json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8',newline='\n')
print(json.dumps(report),flush=True)
