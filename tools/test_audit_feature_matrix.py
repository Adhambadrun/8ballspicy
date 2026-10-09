"""Tests for the advertised-feature matrix auditor.

The auditor re-reads the immutable input IPA and confirms that every citation in
``validation/reports/feature-verification-matrix.md`` and
``validation/evidence/feature-string-search.json`` points at the bytes it claims.
That keeps the 42-category matrix auditable instead of a static claim.

The tests use the real IPA because the citations are byte offsets into it; the
file is tracked in the repository and is only ever read.
"""
import json
import shutil
import tempfile
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
        cls.result = afm.audit(IPA, MATRIX, EVIDENCE, root=REPO)

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


def _collect():
    findings = []

    def record(kind, detail, **extra):
        findings.append({'result': kind, 'detail': detail, **extra})

    return findings, record


def _rows(*pairs):
    """Synthetic matrix rows: (feature, final status) with the status as last cell."""
    return [[name, 'advertised', 'No', status] for name, status in pairs]


class EvidenceStructureTests(unittest.TestCase):
    """Taxonomy and component-evidence checks, runnable without the IPA."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='spicy-audit-'))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.source = self.root / 'MrSpicyUI/Sources/MrSpicyUI'
        self.source.mkdir(parents=True)
        (self.source / 'Pro.swift').write_text('// mr.spicy.pro.reference\n', encoding='utf-8')

    def taxonomy(self, assignments, categories=None):
        return {'categories': list(afm.TAXONOMY) if categories is None else categories,
                'assignments': assignments}

    def run_taxonomy(self, rows, taxonomy):
        findings, record = _collect()
        afm.check_taxonomy(rows, taxonomy, record)
        return {f['check']: f['result'] for f in findings}

    def run_evidence(self, rows, spec):
        findings, record = _collect()
        afm.check_component_evidence(rows, spec, self.root, record)
        return {f['check']: f['result'] for f in findings}

    # -- taxonomy ------------------------------------------------------------

    def test_row_without_taxonomy_assignment_fails(self):
        rows = _rows(('Prediction Lines', 'unavailable'), ('Pro access', 'ui-only'))
        result = self.run_taxonomy(rows, self.taxonomy({
            'Prediction Lines': 'Explicitly unavailable'}))
        self.assertEqual(result['taxonomy_coverage'], 'FAIL')

    def test_extra_taxonomy_assignment_fails(self):
        rows = _rows(('Prediction Lines', 'unavailable'))
        result = self.run_taxonomy(rows, self.taxonomy({
            'Prediction Lines': 'Explicitly unavailable', 'Ghost feature': 'Not implemented'}))
        self.assertEqual(result['taxonomy_coverage'], 'FAIL')

    def test_game_only_row_cannot_be_labelled_implemented(self):
        rows = _rows(('Prediction Lines', 'unavailable'))
        result = self.run_taxonomy(rows, self.taxonomy({
            'Prediction Lines': 'Implemented but incompletely tested'}))
        self.assertEqual(result['taxonomy_status_consistency'], 'FAIL')

    def test_implemented_and_tested_is_not_reachable_from_any_status(self):
        rows = _rows(('English menu', 'implemented (component only)'))
        result = self.run_taxonomy(rows, self.taxonomy({
            'English menu': 'Implemented and tested'}))
        self.assertEqual(result['taxonomy_status_consistency'], 'FAIL')

    def test_unknown_category_name_fails(self):
        rows = _rows(('Prediction Lines', 'unavailable'))
        result = self.run_taxonomy(rows, self.taxonomy({'Prediction Lines': 'Probably fine'}))
        self.assertEqual(result['taxonomy_status_consistency'], 'FAIL')

    def test_altered_category_list_fails(self):
        rows = _rows(('Prediction Lines', 'unavailable'))
        result = self.run_taxonomy(rows, self.taxonomy(
            {'Prediction Lines': 'Explicitly unavailable'}, categories=['Works']))
        self.assertEqual(result['taxonomy_categories'], 'FAIL')

    # -- component evidence --------------------------------------------------

    def test_component_only_row_without_evidence_fails(self):
        rows = _rows(('English menu', 'implemented (component only)'))
        result = self.run_evidence(rows, {'features': {}})
        self.assertEqual(result['component_evidence_resolves'], 'FAIL')

    def test_evidence_token_must_be_present_in_the_file(self):
        rows = _rows(('Pro access', 'ui-only'))
        spec = {'features': {'Pro access': [
            {'file': 'MrSpicyUI/Sources/MrSpicyUI/Pro.swift', 'contains': 'entitlement service'}]}}
        result = self.run_evidence(rows, spec)
        self.assertEqual(result['component_evidence_resolves'], 'FAIL')

    def test_evidence_file_must_exist(self):
        rows = _rows(('Pro access', 'ui-only'))
        spec = {'features': {'Pro access': [
            {'file': 'MrSpicyUI/Sources/MrSpicyUI/Missing.swift', 'contains': 'x'}]}}
        result = self.run_evidence(rows, spec)
        self.assertEqual(result['component_evidence_resolves'], 'FAIL')

    def test_valid_component_evidence_passes(self):
        rows = _rows(('Pro access', 'ui-only'))
        spec = {'features': {'Pro access': [
            {'file': 'MrSpicyUI/Sources/MrSpicyUI/Pro.swift', 'contains': 'mr.spicy.pro.reference'}]}}
        result = self.run_evidence(rows, spec)
        self.assertEqual(result['component_evidence_resolves'], 'PASS')
        self.assertEqual(result['component_evidence_scope'], 'PASS')

    def test_game_only_row_may_not_carry_component_evidence(self):
        # Attaching component evidence to an unavailable game feature would
        # let a game row borrow support it does not have.
        rows = _rows(('Auto Aim', 'unavailable'))
        spec = {'features': {'Auto Aim': [
            {'file': 'MrSpicyUI/Sources/MrSpicyUI/Pro.swift', 'contains': 'mr.spicy.pro.reference'}]}}
        result = self.run_evidence(rows, spec)
        self.assertEqual(result['component_evidence_scope'], 'FAIL')

    def test_real_repository_taxonomy_and_evidence_pass(self):
        text = MATRIX.read_text(encoding='utf-8')
        rows = afm.matrix_rows(text)
        taxonomy = json.loads((REPO / afm.DEFAULT_TAXONOMY).read_text(encoding='utf-8'))
        spec = json.loads((REPO / afm.DEFAULT_COMPONENT_EVIDENCE).read_text(encoding='utf-8'))
        findings, record = _collect()
        afm.check_taxonomy(rows, taxonomy, record)
        afm.check_component_evidence(rows, spec, REPO, record)
        bad = [f for f in findings if f['result'] != 'PASS']
        self.assertEqual(bad, [])
        self.assertEqual(len(rows), 42)

    def test_real_taxonomy_counts_match_the_matrix_contract(self):
        taxonomy = json.loads((REPO / afm.DEFAULT_TAXONOMY).read_text(encoding='utf-8'))
        counts = {}
        for category in taxonomy['assignments'].values():
            counts[category] = counts.get(category, 0) + 1
        self.assertEqual(counts.get('Explicitly unavailable'), 29)
        self.assertEqual(counts.get('Blocked by host integration'), 5)
        self.assertEqual(counts.get('Not implemented'), 4)
        self.assertEqual(counts.get('Implemented but incompletely tested'), 2)
        self.assertEqual(counts.get('UI representation only'), 1)
        self.assertEqual(counts.get('Dependent on external authorization'), 1)
        self.assertNotIn('Implemented and tested', counts)


if __name__ == '__main__':
    unittest.main()
