"""Import licensed local SAB snapshots without requiring the author's text database."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json, re, hashlib, tarfile, xml.etree.ElementTree as E
from import_global_sample import extract
from import_original_languages import handle, latin, cl

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'releases/v1.13'
BASE = Path('/workspace/sab-hindi-pilot/tools/sab/data/bibles')

def readjs(path):
    return json.loads(path.read_text().split('=', 1)[1].rstrip(';\n'))

def usx_rows(raw):
    root = E.fromstring(raw)
    book = root.find('book').get('code')
    chapter = None
    verse = None
    parts = []
    rows = []
    def flush():
        nonlocal verse, parts
        if verse is not None:
            text = re.sub(r'\s+', ' ', ''.join(parts)).strip()
            if text:
                m = re.fullmatch(r'(\d+[a-z]?)(?:-(\d+))?', verse)
                assert m, (book, verse)
                v = int(m[1]) if m[1].isdigit() else m[1]
                rows.append([chapter, v, text, text] + ([int(m[2])] if m[2] else []))
        verse, parts = None, []
    def walk(node):
        nonlocal chapter, verse
        tag = node.tag
        skip = tag == 'note' or tag == 'para' and re.match(r'^(h|toc|mt|s\d?|ms\d?|r|d)$', node.get('style', ''))
        if tag == 'chapter' and node.get('number'):
            flush()
            chapter = int(node.get('number'))
        if tag == 'verse':
            flush()
            if node.get('number'):
                verse = node.get('number')
        if not skip:
            if verse is not None and node.text:
                parts.append(node.text)
            for child in node:
                walk(child)
        if verse is not None and node.tail:
            parts.append(node.tail)
    walk(root)
    flush()
    assert rows and len({(r[0], r[1]) for r in rows}) == len(rows)
    return book, rows

def main():
    cat = readjs(OUT / 'catalog.js')
    directory = readjs(OUT / 'translations/metadata.js')
    (OUT / 'sources').mkdir(exist_ok=True)
    (OUT / 'extra-data').mkdir(exist_ok=True)
    specs = []
    folder = BASE / 'por - Biblica Open Nova Biblia Viva'
    archive = next(folder.glob('*.zip'))
    with ZipFile(archive) as z:
        proof = z.read('metadata.xml').decode('utf-8-sig')
        assert 'creativecommons.org/licenses/by-sa/4.0' in proof and 'Copyright © 2007, 2010 by Biblica' in proof
        books = dict(usx_rows(z.read(n).decode('utf-8-sig')) for n in z.namelist() if n.endswith('.usx'))
        labels = {n.get('id').replace('book-', '').upper(): n.findtext('long') for n in E.fromstring(proof).findall('./names/name')}
    specs.append(dict(id='por-onbv', label='Portuguese — Open Nova Bíblia Viva 2007', language='pt-BR', iso='por', script='Latin', family='Indo-European', branch='Romance', countries=['Portugal', 'Brazil', 'Angola', 'Mozambique'], continents=['Europe', 'South America', 'Africa'], aliases=['português', 'portugues', 'Nova Bíblia Viva', 'ONBV'], books=books, labels=labels, raw_files=[archive], attribution='Biblica® Open Nova Bíblia Viva™. Copyright © 2007, 2010 by Biblica, Inc. The original Work by its copyright holders is available for free at www.biblica.com and open.bible. Source: Scripture App Builder distribution. Plain-verse display extraction by this project omits headings and footnotes; source spelling retained. This extraction is CC BY-SA 4.0; no endorsement implied. The original release archive includes the full license statement.'))
    folder = BASE / 'nep - Biblica Open Nepali Contemporary Version'
    proof = (folder / '!books.xml').read_text()
    assert '© 2024 Biblica' in proof and 'CC BY-SA 4.0' in proof
    files = [p for p in folder.iterdir() if p.suffix.lower() in ['.sfm', '.usfm']]
    books = {}
    h = handle('Devanagari-Latin')
    try:
        for file in files:
            book, rows = extract(file.read_text(encoding='utf-8-sig'))
            books[book] = [[r[0], r[1], r[2], latin(h, r[2])] + r[3:] for r in rows]
    finally:
        cl(h)
    specs.append(dict(id='npi-oncv2024', label='Nepali — Open Contemporary Version 2024', language='ne', iso='npi', script='Devanagari', family='Indo-European', branch='Indo-Aryan', countries=['Nepal', 'India', 'Bhutan'], continents=['Asia'], aliases=['नेपाली', 'Nepali', 'ONCV', 'Open Nepali Contemporary'], books=books, labels={}, raw_files=[folder / '!books.xml', *files], attribution='© 2024 Biblica. Licensed under CC BY-SA 4.0. Biblica Open Nepali Contemporary Version, supplied with Scripture App Builder. Source USFM retained. Plain-verse extraction and ICU Devanagari-to-Latin written transliteration by this project; headings/footnotes omitted from display. These adaptations are CC BY-SA 4.0. Transliteration is mechanical, not a pronunciation guide; no endorsement implied.'))
    src = Path('/workspace/reader-new-sources')
    compact_specs = [
        ('czech-bkr1613.json', 'cs_bkr', 'ces-bkr1613', 'Czech — Bible Kralická 1613', 'cs', 'ces', 'Latin', 'czebkr', 'Indo-European', 'Slavic', ['Czechia'], ['Europe'], ['čeština', 'cestina', 'Bible Kralická', 'Kralicka']),
        ('korean-krv.json', 'ko_krv', 'kor-krv', 'Korean — Korean Revised (historical)', 'ko', 'kor', 'Hangul', 'korrv', 'Koreanic', 'Korean', ['South Korea', 'North Korea'], ['Asia'], ['한국어', '조선말', '개역성경', 'Korean Revised']),
        ('tagalog-angbiblia1905.json', 'tl_abtag', 'tgl-angbiblia1905', 'Tagalog — Ang Biblia 1905', 'tl', 'tgl', 'Latin', 'tagangbiblia', 'Austronesian', 'Malayo-Polynesian', ['Philippines'], ['Asia'], ['Tagalog', 'Filipino', 'Ang Dating Biblia', 'Ang Biblia']),
    ]
    abbreviations = 'gn ex lv nm dt js jz rt 1sm 2sm 1rs 2rs 1cr 2cr ed ne et jó sl pv ec ct is jr lm ez dn os jl am ob jn mq na hc sf ag zc ml mt mc lc jo atos rm 1co 2co gl ef fp cl 1ts 2ts 1tm 2tm tt fm hb tg 1pe 2pe 1jo 2jo 3jo jd ap'.split()
    canonical = 'GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV'.split()
    mapping = dict(zip(abbreviations, canonical))
    with tarfile.open(src / 'Brenton-catalog.tgz') as t:
        for filename, source_id, id, label, lang, iso, script, module, family, branch, countries, continents, aliases in compact_specs:
            conf = t.extractfile(next(n for n in t.getnames() if n.lower().endswith('/' + module + '.conf'))).read().decode()
            assert 'DistributionLicense=Public Domain' in conf, module
            proof_file = OUT / 'sources' / (module + '-rights.conf')
            proof_file.write_text(conf)
            data = json.loads((src / filename).read_text())
            assert len(data) == 66 and {b['abbrev'] for b in data} == set(abbreviations)
            books, labels = {}, {}
            h = handle('Hangul-Latin') if script == 'Hangul' else None
            try:
                for b in data:
                    book = mapping[b['abbrev']]
                    labels[book] = b['name']
                    books[book] = [[c, v, text, latin(h, text) if h else text] for c, chapter in enumerate(b['chapters'], 1) for v, text in enumerate(chapter, 1) if text.strip()]
            finally:
                if h:
                    cl(h)
            source = 'https://github.com/thiagobodruk/bible/blob/master/json/' + source_id + '.json'
            attribution = label + '. Historical translation; corresponding CrossWire ' + module + ' module declares Public Domain. JSON snapshot from thiagobodruk/bible; source version identity and rights declaration retained. Original spelling retained; source array positions are chapter/verse references, with no verified cross-edition alignment. ' + ('ICU Hangul-to-Latin written transliteration is mechanical, not a phonetic guide. ' if h else '') + 'No matched audio has been verified.'
            specs.append(dict(id=id, label=label, language=lang, iso=iso, script=script, family=family, branch=branch, countries=countries, continents=continents, aliases=aliases, books=books, labels=labels, raw_files=[src / filename, src / 'thiago-selected-index.json', proof_file], attribution=attribution, license='Public Domain', source=source))
    overlays = {}
    reports = []
    licenses = (OUT / 'LICENSES.md').read_text().split('\n<!-- 1.13 additions -->')[0]
    licenses += '\n<!-- 1.13 additions -->\n'
    for spec in specs:
        id, books = spec['id'], spec['books']
        assert len(books) == 66, (id, len(books))
        assert set(books) <= dict(cat['books']).keys()
        for book, rows in books.items():
            assert rows and len({(r[0], r[1]) for r in rows}) == len(rows), (id, book)
            overlays.setdefault(book, {})[id] = rows
        license = spec.get('license', 'CC BY-SA 4.0')
        source = spec.get('source', 'https://software.sil.org/scriptureappbuilder/')
        meta = dict(id=id, label=spec['label'], title=spec['label'], language=spec['language'], latin_language=spec['language'] + '-Latn' if spec['script'] != 'Latin' else spec['language'], script=spec['script'], direction='ltr', available=True, scope='Full Bible (66 source books)', source=source, license=license, license_url='https://creativecommons.org/licenses/by-sa/4.0/' if license.startswith('CC') else 'https://creativecommons.org/publicdomain/mark/1.0/', attribution=spec['attribution'], method='Original Latin script.' if spec['script'] == 'Latin' else 'ICU written Latin transliteration; not phonetic speech.', has_transliteration=spec['script'] != 'Latin', book_codes=[b for b, _ in cat['books'] if b in books], positions=[[b, c] for b, _ in cat['books'] if b in books for c in dict.fromkeys(r[0] for r in books[b])], preserve_source_refs=True, versification_label='Source numbering retained; no verified cross-edition alignment', book_labels=spec['labels'], data_group='europe-asia-1.13')
        cat['editions'] = [e for e in cat['editions'] if e['id'] != id] + [meta]
        directory = [e for e in directory if e['id'] != id] + [dict(id=id, language={'por': 'Portuguese', 'npi': 'Nepali', 'ces': 'Czech', 'kor': 'Korean', 'tgl': 'Tagalog'}[spec['iso']], iso6393=spec['iso'], aliases=spec['aliases'], family=spec['family'], branch=spec['branch'], countries=spec['countries'], continents=spec['continents'], states=[], script=spec['script'], variety=spec['label'], classification_source='ISO language identity and project browsing groups; no asserted UBS identifier', ubs_id=None)]
        with ZipFile(OUT / 'sources' / (id + '-raw.zip'), 'w', ZIP_DEFLATED, strict_timestamps=False) as z:
            for f in spec['raw_files']:
                z.write(f, f.name)
        with ZipFile(OUT / 'sources' / (id + '-display-usfm.zip'), 'w', ZIP_DEFLATED, strict_timestamps=False) as z:
            z.writestr('PROVENANCE.txt', spec['attribution'] + '\nLicense: ' + license + '\n')
            for book, rows in books.items():
                text = ['\\id ' + book, '\\usfm 3.0', '\\ide UTF-8']
                last = None
                for row in rows:
                    if row[0] != last:
                        text.append('\\c ' + str(row[0]))
                        last = row[0]
                    text.append('\\v ' + str(row[1]) + ('-' + str(row[4]) if len(row) > 4 and row[4] else '') + ' ' + row[2])
                z.writestr(book + '.usfm', '\n'.join(text) + '\n')
        licenses += '\n## ' + spec['label'] + '\n\n' + spec['attribution'] + '\n\n' + license + '\nRaw and derived USFM: sources/' + id + '-raw.zip and sources/' + id + '-display-usfm.zip.\n'
        reports.append(dict(id=id, books=len(books), units=sum(map(len, books.values())), license=license, source=source, raw=[dict(file=f.name, sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in spec['raw_files']]))
    for book, editions in overlays.items():
        (OUT / 'extra-data' / (book + '.js')).write_text('window.ExtraBibleBooks=window.ExtraBibleBooks||{};window.ExtraBibleBooks[' + json.dumps(book) + ']=' + json.dumps(dict(book=book, editions=editions), ensure_ascii=False, separators=(',', ':')) + ';')
    (OUT / 'catalog.js').write_text('window.BibleCatalog=' + json.dumps(cat, ensure_ascii=False, separators=(',', ':')) + ';')
    (OUT / 'translations/metadata.js').write_text('window.TranslationDirectory=' + json.dumps(directory, ensure_ascii=False, separators=(',', ':')) + ';')
    (OUT / 'LICENSES.md').write_text(licenses)
    (OUT / 'sources/europe-asia-import.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps([{k: v for k, v in r.items() if k != 'raw'} for r in reports], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
