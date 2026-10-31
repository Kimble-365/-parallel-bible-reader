"""Export source-qualified CollateX input; does not run CollateX or select readings."""
from pathlib import Path
import argparse, gzip, json, unicodedata
ROOT = Path(__file__).resolve().parents[1] / 'releases/v1.23'


def packet(book, chapter, verse):
    witnesses = []
    for edition in ['syc-peshitta-ot', 'syc-etcbc-biblical']:
        path = ROOT / 'syriac-data' / edition / (book + '.json.gz')
        if not path.exists():
            continue
        data = json.loads(gzip.decompress(path.read_bytes()))
        row = next((r for r in data['editions'][edition] if r[:2] == [chapter, verse]), None)
        if row:
            # Whitespace tokens are collation input, not manuscript token identities.
            tokens = [{'t': word, 'n': ''.join(c for c in unicodedata.normalize('NFD', word) if unicodedata.category(c) != 'Mn')} for word in row[2].split()]
            witnesses.append(dict(id=edition, tokens=tokens))
    if len(witnesses) < 2:
        raise ValueError('Two edition-text sources at the requested source label are required')
    return dict(witnesses=witnesses)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Edition texts may share ancestry and labels do not establish passage equivalence. This is not manuscript attestation.')
    p.add_argument('book');p.add_argument('chapter', type=int);p.add_argument('verse', type=int)
    a = p.parse_args()
    print(json.dumps(packet(a.book, a.chapter, a.verse), ensure_ascii=False))
