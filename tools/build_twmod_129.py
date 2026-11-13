"""Build Lithos/TheWay .twmod modules for the 116 Reader 1.29 europe-english editions.

Each .twmod is a ZIP containing module.sqlite + manifest.json, matching the
Lithos scanner contract:

  books(book, book_number, title, short_title)
  verses(book, chapter, display_verse, text, sequence)
  module_meta(key, value)  -- name/title, description, language, author, kind='bible'
  manifest.json            -- title, languages[], description

Input: releases/v1.29 europe-data packs + catalog.js + sources/europe-english-import.json.
The build is verified with the exact queries the Lithos scanner runs.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse, gzip, json, sqlite3, sys


def js(path):
    return json.loads(path.read_text(encoding='utf-8').split('=', 1)[1].rstrip(';\n'))


def build_module(sid, meta, report_entry, book_order, book_titles, packs, out_path):
    db_path = out_path.with_suffix('.sqlite.tmp')
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('CREATE TABLE books (book TEXT PRIMARY KEY, book_number INTEGER, title TEXT, short_title TEXT)')
    c.execute('CREATE TABLE verses (book TEXT, chapter INTEGER, display_verse TEXT, text TEXT, sequence INTEGER)')
    c.execute('CREATE INDEX idx_verses ON verses (book, chapter, sequence)')
    c.execute('CREATE TABLE module_meta (key TEXT PRIMARY KEY, value TEXT)')

    attribution = report_entry['attribution']
    description = (f"{report_entry['vernacular_title']} ({report_entry['title']}). "
                   f"Licence: {report_entry['license']}. Source: {report_entry['source']}. "
                   f"Plain-verse format conversion; headings, notes and cross references omitted from display. "
                   f"SHA-256 of source archive: {report_entry['source_sha256']}.")
    for key, value in [
        ('name', report_entry['vernacular_title']),
        ('title', report_entry['vernacular_title']),
        ('description', description),
        ('language', meta['language']),
        ('author', ''),
        ('kind', 'bible'),
    ]:
        c.execute('INSERT INTO module_meta VALUES (?,?)', (key, value))

    total_rows = 0
    present = []
    for book in book_order:
        rows = packs.get(book, {}).get('editions', {}).get(sid)
        if not rows:
            continue
        present.append(book)
        c.execute('INSERT INTO books VALUES (?,?,?,?)',
                  (book, book_order.index(book) + 1, book_titles.get(book, book), book))
        for seq, row in enumerate(rows, 1):
            chapter, verse, text = row[0], row[1], row[2]
            endverse = row[4] if len(row) > 4 else None
            display = str(verse) + ('-' + str(endverse) if endverse is not None else '')
            c.execute('INSERT INTO verses VALUES (?,?,?,?,?)',
                      (book, chapter, display, text, seq))
            total_rows += 1
    conn.commit()

    # Verify with the exact Lithos scanner queries.
    books_q = c.execute(
        'select b.book, coalesce(nullif(b.title,\'\'), b.short_title, b.book) as title, '
        'max(v.chapter) as chapters from books b join verses v on v.book=b.book '
        'group by b.book order by b.book_number').fetchall()
    assert len(books_q) == len(present), f'{sid}: books query mismatch'
    sample_book, _, sample_chapters = books_q[0]
    content_q = c.execute(
        'select display_verse as v, text from verses where book=? and chapter=? order by sequence',
        (sample_book, 1)).fetchall()
    assert content_q, f'{sid}: empty content query'
    conn.close()
    assert total_rows == report_entry['verse_rows'], \
        f'{sid}: rows {total_rows} != report {report_entry["verse_rows"]}'

    manifest = {
        'title': report_entry['vernacular_title'],
        'languages': [meta['language']],
        'description': description,
    }
    with ZipFile(out_path, 'w', ZIP_DEFLATED, strict_timestamps=False) as z:
        z.write(db_path, 'module.sqlite')
        z.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    db_path.unlink()
    return total_rows, len(present)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--release', type=Path, default=Path('releases/v1.29'))
    ap.add_argument('--out', type=Path, default=Path('releases/v1.29/twmod'))
    args = ap.parse_args()
    global BASE, OUTDIR
    BASE, OUTDIR = args.release, args.out
    OUTDIR.mkdir(parents=True, exist_ok=True)
    cat = js(BASE / 'catalog.js')
    book_order = [b for b, _ in cat['books']]
    book_titles = dict(cat['books'])
    editions = {e['id']: e for e in cat['editions'] if e.get('data_group') == 'europe-english-1.29'}
    report = {r['id']: r for r in json.loads((BASE / 'sources/europe-english-import.json').read_text(encoding='utf-8'))}
    assert len(editions) == 116 and len(report) == 116

    print('Loading packs...', flush=True)
    packs = {}
    for gz_path in sorted((BASE / 'europe-data').glob('*.json.gz')):
        book = gz_path.name[:-len('.json.gz')]
        packs[book] = json.loads(gzip.decompress(gz_path.read_bytes()))
    print(f'{len(packs)} packs loaded', flush=True)

    total_bytes = 0
    for i, sid in enumerate(sorted(editions), 1):
        out_path = OUTDIR / (sid + '.twmod')
        rows, nbooks = build_module(sid, editions[sid], report[sid], book_order, book_titles, packs, out_path)
        size = out_path.stat().st_size
        total_bytes += size
        print(f'{i:3}/116 {sid:16} books={nbooks:2} rows={rows:6} size={size/1e6:6.2f} MB', flush=True)
    print(f'TWMOD BUILD COMPLETE: 116 modules, {total_bytes/1e6:.1f} MB total')


if __name__ == '__main__':
    sys.exit(main())
