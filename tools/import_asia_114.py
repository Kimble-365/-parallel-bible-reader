"""Four public-domain Asian snapshots with explicit source verse labels."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,re,tarfile,hashlib,sys
from import_original_languages import handle,latin,cl

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'releases/v1.14';SRC=Path('/workspace/reader-new-sources/v114')
def readjs(path):return json.loads(path.read_text().split('=',1)[1].rstrip(';\n'))
def source_books(data,known):
    mapping={name:code for code,name in known}
    for name,code in list(mapping.items()):
        for n,roman in [('1 ','I '),('2 ','II '),('3 ','III ')]:
            if name.startswith(n):mapping[roman+name[len(n):]]=code
    mapping.update({'Song of Solomon':'SNG','Song of Songs':'SNG','Revelation of John':'REV'})
    books={};empty=0
    for b in data['books']:
        code=mapping[b['name']];assert code not in books
        rows=[]
        for c in b['chapters']:
            for v in c['verses']:
                text=v['text'];assert isinstance(text,str)
                if not text.strip():empty+=1;continue
                rows.append([c['chapter'],v['verse'],text])
        assert rows and len({(r[0],r[1]) for r in rows})==len(rows),(code,len(rows))
        books[code]=rows
    assert len(books)==66
    return books,empty

def main():
    cat=readjs(OUT/'catalog.js');directory=readjs(OUT/'translations/metadata.js');(OUT/'sources').mkdir(exist_ok=True);(OUT/'extra-data').mkdir(exist_ok=True)
    acquisition=json.loads((SRC/'acquisition.json').read_text());byfile={r['file']:r for r in acquisition}
    specs=[
      dict(id='jpn-bungo',file='jpn-bungo.json',module='japbungo',label='Japanese — Bungo / Taisho historical Bible',language='ja',iso='jpn',script='Japanese (Han, Hiragana, Katakana)',family='Japonic',branch='Japanese',countries=['Japan'],aliases=['日本語','文語訳','Bungo','Taisho'],engine='Katakana-Latin; Hiragana-Latin',partial=True),
      dict(id='mya-judson',file='mya-judson-explicit.json',module='burjudson',label='Burmese — Judson 1835 (historical)',language='my',iso='mya',script='Myanmar',family='Sino-Tibetan',branch='Tibeto-Burman (project grouping)',countries=['Myanmar'],aliases=['မြန်မာ','Burmese','Myanmar','Judson'],engine='Myanmar-Latin'),
      dict(id='vie-1934',file='vie-1934.json',module='viet',label='Vietnamese — Kinh Thánh 1934 (historical)',language='vi',iso='vie',script='Latin',family='Austroasiatic',branch='Vietic',countries=['Vietnam'],aliases=['tiếng Việt','Tieng Viet','Kinh Thánh','Cadman'],engine=None),
      dict(id='ceb-pinadayag',file='ceb-pinadayag.json',module='cebpinadayag',label='Cebuano — Pinadayag',language='ceb',iso='ceb',script='Latin',family='Austronesian',branch='Malayo-Polynesian',countries=['Philippines'],aliases=['Cebuano','Bisaya','Binisaya','Pinadayag','Cebu'],engine=None),
    ]
    overlays={};reports=[];licenses=(OUT/'LICENSES.md').read_text().split('\n<!-- 1.14 additions -->')[0]+'\n<!-- 1.14 additions -->\n'
    with tarfile.open('/workspace/reader-new-sources/Brenton-catalog.tgz') as t:
      for s in specs:
        id=s['id'];raw=(SRC/s['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==byfile[s['file']]['sha256'];data=json.loads(raw.decode('utf-8-sig'));books,empty=source_books(data,cat['books'])
        conf=t.extractfile(next(n for n in t.getnames() if n.lower().endswith('/'+s['module']+'.conf'))).read().decode();assert 'DistributionLicense=Public Domain' in conf,s['module'];proof=OUT/'sources'/(id+'-rights.conf');proof.write_text(conf)
        h=handle(s['engine']) if s['engine'] else None
        try:
          for book,rows in books.items():overlays.setdefault(book,{})[id]=[[r[0],r[1],r[2],latin(h,r[2]) if h else r[2]] for r in rows]
        finally:
          if h:cl(h)
        partial=s.get('partial',False);method='Original Latin text, accents retained.' if not h else ('Only hiragana and katakana are romanized with ICU; kanji remain unchanged. Partial written conversion, not a complete reading or pronunciation guide.' if partial else 'ICU Myanmar-to-Latin orthographic conversion. Source spelling and combining signs retained in the original. Not reconstructed spoken language or a phonetic guide.')
        source=byfile[s['file']]['url'];attribution=s['label']+'. Corresponding CrossWire '+s['module']+' module explicitly declares Public Domain. Exact source JSON and module declaration retained. '+method+' Source reference labels retained; empty source placeholders are omitted from display. No cross-edition verse alignment is verified.'
        if id=='jpn-bungo':attribution+=' Source module identifies an 1887 OT tradition using a 1953 printed base and the Taisho NT using a 1950 printed base; it is not a current Japanese translation.'
        if id=='ceb-pinadayag':attribution+=' Pinadayag identifies the revised New Testament tradition; it is not labeled as identical to the 1917 Bugna NT.'
        meta=dict(id=id,label=s['label'],title=s['label'],language=s['language'],latin_language=s['language'] if not h or partial else s['language']+'-Latn',script=s['script'],direction='ltr',available=True,scope='Full Bible (66 source books)',source=source,license='Public Domain',license_url='https://creativecommons.org/publicdomain/mark/1.0/',attribution=attribution,method=method,has_transliteration=bool(h),book_codes=[b for b,_ in cat['books'] if b in books],positions=[[b,c] for b,_ in cat['books'] if b in books for c in dict.fromkeys(r[0] for r in books[b])],preserve_source_refs=True,versification_label='Source labels retained; equal labels do not prove equivalent passages',data_group='asia-1.14',provider_links=[dict(label='Other editions on YouVersion — external reading',url='https://www.bible.com/languages/'+s['iso'])])
        if partial:meta.update(transliteration_status='partial',latin_label='Kana romanization — kanji retained',transliteration_note='Japanese: only kana are romanized. Kanji stay in their original form; this is not a complete Latin reading or pronunciation guide.')
        if id=='vie-1934':meta['search_policy']='vietnamese'
        cat['editions']=[e for e in cat['editions'] if e['id']!=id]+[meta];directory=[e for e in directory if e['id']!=id]+[dict(id=id,language={'jpn':'Japanese','mya':'Burmese','vie':'Vietnamese','ceb':'Cebuano'}[s['iso']],iso6393=s['iso'],aliases=s['aliases'],family=s['family'],branch=s['branch'],countries=s['countries'],continents=['Asia'],states=[],script=s['script'],variety=s['label'],classification_source='ISO language identity and project browsing groups; no asserted UBS identifier',ubs_id=None)]
        with ZipFile(OUT/'sources'/(id+'-raw.zip'),'w',ZIP_DEFLATED,strict_timestamps=False) as z:
          z.writestr(s['file'],raw);z.writestr(proof.name,conf);z.writestr('PROVENANCE.json',json.dumps(byfile[s['file']],indent=2))
        with ZipFile(OUT/'sources'/(id+'-display-usfm.zip'),'w',ZIP_DEFLATED) as z:
          z.writestr('PROVENANCE.txt',attribution+'\n'+source+'\nPublic Domain\n')
          for book,rows in books.items():
            lines=['\\id '+book,'\\usfm 3.0','\\ide UTF-8'];last=None
            for c,v,text in rows:
              if c!=last:lines.append('\\c '+str(c));last=c
              lines.append('\\v '+str(v)+' '+text)
            z.writestr(book+'.usfm','\n'.join(lines)+'\n')
        licenses+='\n## '+s['label']+'\n\n'+attribution+'\n\nPublic Domain. Original source and rights: sources/'+id+'-raw.zip. Derived UTF-8 USFM: sources/'+id+'-display-usfm.zip.\n'
        reports.append(dict(id=id,books=len(books),units=sum(map(len,books.values())),empty_placeholders_omitted=empty,license='Public Domain',source=source,sha256=hashlib.sha256(raw).hexdigest(),git_blob=byfile[s['file']]['git_blob'],transliteration=method))
    for book,editions in overlays.items():(OUT/'extra-data'/(book+'.js')).write_text('window.ExtraBibleBooks=window.ExtraBibleBooks||{};window.ExtraBibleBooks['+json.dumps(book)+']='+json.dumps(dict(book=book,editions=editions),ensure_ascii=False,separators=(',',':'))+';')
    (OUT/'catalog.js').write_text('window.BibleCatalog='+json.dumps(cat,ensure_ascii=False,separators=(',',':'))+';');(OUT/'translations/metadata.js').write_text('window.TranslationDirectory='+json.dumps(directory,ensure_ascii=False,separators=(',',':'))+';');(OUT/'LICENSES.md').write_text(licenses);(OUT/'sources/asia-import.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n');print(json.dumps(reports,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
