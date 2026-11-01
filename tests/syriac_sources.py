"""Validate shipped source packs, attribution boundaries, references and lexicon."""
from pathlib import Path
import collections, gzip, hashlib, json, sys, unittest
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'releases/v1.25'
sys.path.insert(0, str(ROOT / 'tools'))
from import_syriac import canonical, readjs


class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((OUT / 'sources/syriac-import.json').read_text())
        cls.manifest = readjs(OUT / 'syriac-manifest.js')
        cls.catalog = readjs(OUT / 'catalog.js')

    def test_all_shards_and_counts(self):
        for name, meta in self.report['inventory'].items():
            packed = (OUT / name).read_bytes()
            self.assertEqual(hashlib.sha256(packed).hexdigest(), meta['packed_sha256'])
            raw = gzip.decompress(packed)
            self.assertEqual(len(raw), meta['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), meta['sha256'])
        self.assertEqual({e['id']: (e['books'], e['verses']) for e in self.report['editions']}, {
            'syc-peshitta-ot': (65, 31341), 'syc-etcbc-biblical': (25, 16278),
            'syc-syrohexapla-ps': (1, 464), 'syc-dsc-nt': (27, 7957)})
        for ed in self.report['editions']:
            count = 0
            for book in self.manifest['editions'][ed['id']]['books']:
                data = json.loads(gzip.decompress((OUT / 'syriac-data' / ed['id'] / (book + '.json.gz')).read_bytes()))
                rows = data['editions'][ed['id']]
                self.assertEqual(len(rows), len({(r[0], r[1]) for r in rows}))
                count += len(rows)
            self.assertEqual(count, ed['verses'])

    def test_shared_lexicon_and_token_offsets(self):
        lexicon = {}
        for path in (OUT / 'syriac-lexicon').glob('*.gz'):
            entries = json.loads(gzip.decompress(path.read_bytes()))['entries']
            self.assertFalse(set(entries) & set(lexicon))
            lexicon.update(entries)
        self.assertEqual(len(lexicon), 5022)
        self.assertEqual(len(list((OUT / 'syriac-lexicon').glob('*.gz'))), 16)
        missing_surface = discontinuous = 0
        for path in (OUT / 'syriac-index').rglob('*.gz'):
            data = json.loads(gzip.decompress(path.read_bytes()))
            text = json.loads(gzip.decompress((OUT / 'syriac-data' / data['edition'] / path.name).read_bytes()))
            rows = {str(r[0]) + ':' + str(r[1]): r[2] for r in text['editions'][data['edition']]}
            for key, record in data['verses'].items():
                missing_surface += len(record.get('no_surface_in_source', []))
                discontinuous += len(record['slots']) > 1
                for token in record['tokens']:
                    self.assertIn(token[3], lexicon)
                    self.assertNotIsInstance(token[3], dict)
                    self.assertLessEqual(token[1] + token[2], len(rows[key]))
                    self.assertEqual(len(token), 11)
        self.assertGreater(missing_surface, 0)
        self.assertGreater(discontinuous, 0)

    def test_independent_source_examples_and_defect(self):
        def book(edition, code):
            return json.loads(gzip.decompress((OUT / 'syriac-data' / edition / (code + '.json.gz')).read_bytes()))
        gen = book('syc-peshitta-ot', 'GEN')
        self.assertEqual(gen['editions']['syc-peshitta-ot'][0][2], 'ܒܪܫܝܬ ܒܪܐ ܐܠܗܐ. ܝܬ ܫܡܝܐ ܘܝܬ ܐܪܥܐ.')
        luke = book('syc-dsc-nt', 'LUK')
        row = next(r for r in luke['editions']['syc-dsc-nt'] if r[:2] == [11, 42])
        self.assertIn('Duplicate source label', row[6])
        self.assertEqual(len(luke['source']['11:42']['source_units']), 2)
        self.assertIn('\n', row[2])
        ps = book('syc-syrohexapla-ps', 'PSA')['editions']['syc-syrohexapla-ps']
        self.assertEqual(sorted({r[0] for r in ps}), list(range(1, 33)))

    def test_license_provenance_and_no_duplicate_legacy_corpus(self):
        headers = json.loads((OUT / 'sources/dsc-items.json').read_text())
        self.assertEqual(len(headers), 27)
        self.assertTrue(all(h['status'] == 'UncorrectedTranscription' and 'CC BY 4.0' in h['rights'] for h in headers))
        for e in self.catalog['editions']:
            if e.get('data_group') == 'syriac-1.25':
                self.assertEqual(e['direction'], 'rtl')
                self.assertFalse(e['has_transliteration'])
                self.assertIn('CC BY', e['license'])
        self.assertFalse((OUT / 'related-data').exists())
        self.assertFalse((OUT / 'sources/related').exists())
        self.assertFalse(any(p.suffix in ['.png', '.jpg', '.tif'] for p in (OUT / 'sources').rglob('*')))


if __name__ == '__main__':
    unittest.main()
