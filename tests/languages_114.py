"""Every new source unit, empty placeholder, USFM and search fingerprint."""
from pathlib import Path
from zipfile import ZipFile
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'releases/v1.14'
def readjs(path):return json.loads(path.read_text().split('=',1)[1].rstrip(';\n'))
cat=readjs(OUT/'catalog.js');old=readjs(ROOT/'releases/v1.13/catalog.js');manifest=readjs(OUT/'search-manifest.js')['editions'];reports=json.loads((OUT/'sources/asia-import.json').read_text());assert len(cat['editions'])==55 and len(reports)==4
assert len({e['language'] for e in cat['editions']}-{e['language'] for e in old['editions']})==4
bundles={}
for path in (OUT/'extra-data').glob('*.js'):
    raw=path.read_text();m=re.search(r'window\.ExtraBibleBooks\["[A-Z0-9]{3}"\]\s*=',raw);bundles[path.stem]=json.loads(raw[m.end():].rstrip(';'))['editions']
assert len(bundles)==66
names={name:code for code,name in cat['books']}
def code(name):
    for roman,number in [('III ','3 '),('II ','2 '),('I ','1 ')]:
        if name.startswith(roman):name=number+name[len(roman):];break
    return {'Song of Solomon':'SNG','Revelation of John':'REV'}.get(name) or names[name]
for report in reports:
    id=report['id'];meta=next(e for e in cat['editions'] if e['id']==id);count=0;empty=0
    assert len(meta['book_codes'])==66 and meta['data_group']=='asia-1.14'
    with ZipFile(OUT/'sources'/f'{id}-raw.zip') as z:
        assert z.testzip() is None
        file=next(n for n in z.namelist() if n.endswith('.json') and n!='PROVENANCE.json');raw=z.read(file)
        assert hashlib.sha256(raw).hexdigest()==report['sha256']
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==report['git_blob']
        source=json.loads(raw);assert len(source['books'])==66
        assert b'DistributionLicense=Public Domain' in z.read(id+'-rights.conf')
    with ZipFile(OUT/'sources'/f'{id}-display-usfm.zip') as z:
        assert z.testzip() is None and len([n for n in z.namelist() if n.endswith('.usfm')])==66
        for book in source['books']:
            b=code(book['name']);expected=[]
            for c in book['chapters']:
                for v in c['verses']:
                    if not v['text'].strip():empty+=1;continue
                    expected.append([c['chapter'],v['verse'],v['text']])
            rows=bundles[b][id];count+=len(rows)
            assert [r[:3] for r in rows]==expected,(id,b)
            assert len({(r[0],r[1]) for r in rows})==len(rows)
            assert hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==manifest[id][b]
            usfm=z.read(b+'.usfm').decode('utf-8');assert '\\ide UTF-8' in usfm
            for row in rows:
                assert row[2] in usfm
                if id=='jpn-bungo':assert re.findall(r'[\u3400-\u9fff]',row[2])==re.findall(r'[\u3400-\u9fff]',row[3]),'Never guess kanji readings'
    assert count==report['units'] and empty==report['empty_placeholders_omitted']
    print('PASS:',id,count,'source units,',empty,'empty placeholders retained only in raw archive; 66 source books, exact source text, original labels, UTF-8 USFM and fingerprints')
assert next(e for e in cat['editions'] if e['id']=='jpn-bungo')['transliteration_status']=='partial'
audios={e['id']:e for e in cat['audio_editions']};assert len(audios)==34
assert audios['MYAOJV']['audio_scope']=='Old Testament' and 'MAT' not in audios['MYAOJV']['book_codes']
assert not any(e['id']=='CEBCBV' for e in cat['audio_editions']),'Text-only provider must not be labeled audio'
for id in ['JPNJCB','JPNNIT','MYAOJV','CEBRPV']:assert audios[id]['same_text_edition'] is False
print('PASS: four genuinely new language tags; 55 editions; 34 audio choices with explicit OT/NT coverage; external providers are not falsely labeled imported text/audio')
