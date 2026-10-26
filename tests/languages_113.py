"""Validate all new source units, archives, metadata and search fingerprints."""
from pathlib import Path
from zipfile import ZipFile
import hashlib, json, re, sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'releases/v1.13'
sys.path.insert(0,str(ROOT/'tools'))
from import_europe_asia_113 import usx_rows
from import_global_sample import extract
def readjs(p):return json.loads(p.read_text().split('=',1)[1].rstrip(';\n'))
cat=readjs(OUT/'catalog.js');directory={e['id']:e for e in readjs(OUT/'translations/metadata.js')};manifest=readjs(OUT/'search-manifest.js')['editions']
reports=json.loads((OUT/'sources/europe-asia-import.json').read_text());assert len(cat['editions'])==51 and len(reports)==5
# Book mapping is checked by the exact source labels/abbreviation sequence in the importer;
# this test independently verifies every rendered unit against the retained raw source.
bundles={}
for p in (OUT/'extra-data').glob('*.js'):
    m=re.search(r'window\.ExtraBibleBooks\["[A-Z0-9]{3}"\]\s*=',p.read_text());bundles[p.stem]=json.loads(p.read_text()[m.end():].rstrip(';'))['editions']
assert len(bundles)==66
for report in reports:
    id=report['id'];meta=next(e for e in cat['editions'] if e['id']==id)
    assert meta['data_group']=='europe-asia-1.13'
    assert len(meta['book_codes'])==66 and directory[id]['ubs_id'] is None
    total=0
    with ZipFile(OUT/'sources'/f'{id}-raw.zip') as z:
        assert z.testzip() is None
        for f in report['raw']:
            assert hashlib.sha256(z.read(f['file'])).hexdigest()==f['sha256']
        if id=='por-onbv':
            nested=next(n for n in z.namelist() if n.endswith('.zip'))
            from io import BytesIO
            with ZipFile(BytesIO(z.read(nested))) as raw:
                originals=dict(usx_rows(raw.read(n).decode('utf-8-sig')) for n in raw.namelist() if n.endswith('.usx'))
        elif id=='npi-oncv2024':
            originals=dict(extract(z.read(n).decode('utf-8-sig')) for n in z.namelist() if n.lower().endswith(('.sfm','.usfm')))
        else:
            filename=next(n for n in z.namelist() if n.endswith('.json') and n!='thiago-selected-index.json')
            raw=json.loads(z.read(filename));assert len(raw)==66
            # Canonical source order is explicit in the imported 66-book metadata.
            assert meta['book_codes'][0]=='GEN' and meta['book_codes'][-1]=='REV'
            originals={code:[[c,v,t] for c,chapter in enumerate(book['chapters'],1) for v,t in enumerate(chapter,1) if t.strip()] for code,book in zip(meta['book_codes'],raw)}
    with ZipFile(OUT/'sources'/f'{id}-display-usfm.zip') as usfm:
        assert usfm.testzip() is None
        assert len([n for n in usfm.namelist() if n.endswith('.usfm')])==66
        for book in meta['book_codes']:
            rows=bundles[book][id];total+=len(rows)
            assert [r[:3] for r in rows]==[r[:3] for r in originals[book]],(id,book)
            assert hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==manifest[id][book]
            text=usfm.read(book+'.usfm').decode('utf-8');assert '\\ide UTF-8' in text
            for row in rows:assert row[2] in text
            assert all(r[3] and r[3]!=r[2] for r in rows) if id=='kor-krv' else True
    assert total==report['units'],(id,total,report['units'])
    print('PASS:',id,total,'source units, 66 books, source fidelity, UTF-8 USFM, archive hashes and search fingerprints')
assert 'Europe' in directory['ces-bkr1613']['continents'] and 'Asia' in directory['tgl-angbiblia1905']['continents']
print('PASS: 51 public editions; all five new editions fully checked; project classifications do not claim UBS identifiers')
