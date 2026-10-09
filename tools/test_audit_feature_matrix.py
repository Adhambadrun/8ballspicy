"""Tests for the advertised-feature matrix auditor.

The auditor re-reads the immutable input IPA and confirms that every citation in
``validation/reports/feature-verification-matrix.md`` and
``validation/evidence/feature-string-search.json`` points at the bytes it claims.
That keeps the 42-category matrix auditable instead of a static claim.

The tests use the real IPA because the citations are byte offsets into it; the
file is tracked in the repository and is only ever read.
"""
import unittest
from pathlib import Path

import audit_feature_matrix as afm

REPO = Path(__file__).resolve().parent.parent
IPA = REPO / 'pool8Signed.ipa'
MATRIX = REPO / 'validation/reports/feature-verification-matrix.md'
EVIDENCE = REPO / 'validation/evidence/feature-string-search.json'


@unittest.skipUnless(IPA.exists(), 'immutable input IPA not present')
class MatrixAuditTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.result = afm.audit(IPA, MATRIX, EVIDENCE)

    def test_every_citation_reproduces_the_exact_bytes(self):
        bad = [f for f in self.result['findings'] if f['result'] != 'PASS']
        self.assertEqual(bad, [], 'every cited offset must reproduce its bytes verbatim')

    def test_loader_hash_matches_the_recorded_evidence(self):
        loader = self.result['loader']
        self.assertEqual(loader['sha256'], afm.EXPECTED_LOADER_SHA256)
        self.assertEqual(loader['size_bytes'], 12265804)

    def test_matrix_declares_42_categories(self):
        self.assertEqual(self.result['advertised_categories'], 42)

    def test_audit_passes(self):
        self.assertTrue(self.result['passed'])
        self.assertEqual(self.result['summary'].get('FAIL', 0), 0)

    def test_citation_check_distinguishes_case_drift(self):
        blob = b'Watch an ad for +1h'
        self.assertEqual(afm.check('Watch an ad', 0, blob), 'PASS')
        self.assertEqual(afm.check('watch an ad', 0, blob), 'WARN')
        self.assertEqual(afm.check('Watch a video', 0, blob), 'FAIL')

    def test_citation_check_handles_offsets_past_the_end(self):
        self.assertEqual(afm.check('anything', 10 ** 9, b'short'), 'FAIL')


if __name__ == '__main__':
    unittest.main()
