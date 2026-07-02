import unittest
from dependency_claim_truth_checker import check

class DependencyClaimTruthCheckerTests(unittest.TestCase):
    def test_zero_dependency_claim_fails(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/'README.md').write_text('Zero dependencies and works offline')
            (root/'requirements.txt').write_text('requests==2.0')
            r=check(root, root/'README.md')
        self.assertFalse(r['passed'])
        self.assertEqual(r['findings'][0]['claim'], 'zero_dependencies')

if __name__ == '__main__':
    unittest.main()
