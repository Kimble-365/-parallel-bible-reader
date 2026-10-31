"""TF format regression fixtures and independently specified alignment checks."""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from import_syriac import feature, span_ranges


class TextFabricTests(unittest.TestCase):
    def test_empty_implicit_token_preserves_subsequent_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'word.tf'
            path.write_text('@node\n@valueType=str\n\nfirst\n\nthird\n')
            self.assertEqual(feature(path), {1: 'first', 2: '', 3: 'third'})

    def test_sparse_nodes_ranges_escapes_and_space(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'word.tf'
            path.write_text('@node\n\n5-6\tܐ\n8\t \n9\tline\\nnext\n')
            self.assertEqual(feature(path), {5: 'ܐ', 6: 'ܐ', 8: ' ', 9: 'line\nnext'})
        self.assertEqual(span_ranges('10-11,15-16'), [(10, 11), (15, 16)])


if __name__ == '__main__':
    unittest.main()
