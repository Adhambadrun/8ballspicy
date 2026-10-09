"""Tests for the release-integrity gate and the feature-matrix auditor.

These run in the same hostless `unittest` job as the forensic parser tests, so
the gate is enforced in CI rather than being a one-off script. The synthetic
cases prove the gate *fails* when the delivery contract is violated — a gate
that cannot fail would be worthless.
"""
import json
import os
import shutil
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

import ci_provenance as cp
import verify_release_state as vrs

REPO = Path(__file__).resolve().parent.parent
MATRIX_HEADER = ('| Feature | Advertised description | Observed evidence | Feature source '
                 'available | Current Mr. Spicy feature UI | Actual functionality verified | '
                 'Integration requirements | Final status |')
ROW = ('| {feature} | advertised | `GBPredictionDrawView` @ 9961311 | No | No; category '
       'disclosure only | Not tested | Owner-authorized host source/SDK | {status} |')


def matrix_text(features):
    return '\n'.join([MATRIX_HEADER,
                      '|---|---|---|---|---|---|---|---|']
                     + [ROW.format(feature=f, status=s) for f, s in features]) + '\n'


def component_tree(root):
    """A minimal but structurally valid MrSpicyUI/HostApp tree."""
    en = root / 'MrSpicyUI/Sources/MrSpicyUI/Resources/en.lproj'
    ar = root / 'MrSpicyUI/Sources/MrSpicyUI/Resources/ar.lproj'
    en.mkdir(parents=True, exist_ok=True)
    ar.mkdir(parents=True, exist_ok=True)
    keys = {'mr.spicy.header.title': 'MR. SPICY',
            'mr.spicy.settings.sound': 'Sound effects',
            'mr.spicy.settings.haptic.off': 'Off',
            'mr.spicy.settings.haptic.light': 'Light',
            'mr.spicy.settings.haptic.medium': 'Medium',
            'mr.spicy.settings.haptic.strong': 'Strong'}
    for table, values in ((en, keys), (ar, {k: 'ar-' + v for k, v in keys.items()})):
        (table / 'Localizable.strings').write_text(
            ''.join(f'"{k}" = "{v}";\n' for k, v in values.items()), encoding='utf-8')
    (root / 'MrSpicyUI/Sources/MrSpicyUI').mkdir(parents=True, exist_ok=True)
    (root / 'MrSpicyUI/Sources/MrSpicyUI/SpicySettingsView.swift').write_text(
        'import UIKit\n'
        'let a = SpicyLocalization.string("mr.spicy.header.title")\n'
        'let b = SpicyLocalization.string("mr.spicy.settings.haptic.\\(intensity.rawValue)")\n',
        encoding='utf-8')
    (root / 'HostApp').mkdir(parents=True, exist_ok=True)
    (root / 'HostApp/AppDelegate.swift').write_text('import UIKit\n', encoding='utf-8')


def object_package(path, file_type=1, cpu=0x100000c):
    """Write a relocatable-object ZIP shaped like the real component package."""
    header = struct.pack('<8I', 0xfeedfacf, cpu, 0, file_type, 1, 0, 0, 0)
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('MrSpicyUI.o', header + b'\0' * 64)


def base_tree(root):
    """A tree that satisfies every check that can be satisfied synthetically."""
    component_tree(root)
    (root / 'validation/reports').mkdir(parents=True, exist_ok=True)
    for name in ('forensic-analysis.md', 'build-and-signing-report.md',
                 'integration-validation.md', 'device-test-report.md',
                 'feature-verification-matrix.md'):
        (root / 'validation/reports' / name).write_text('# report\n', encoding='utf-8')
    (root / 'validation/manifests').mkdir(parents=True, exist_ok=True)
    features = [('Prediction Lines', 'unavailable'), ('Arabic menu', 'implemented (component only)')]
    features += [(f'Filler {i}', 'unavailable') for i in range(40)]
    (root / 'validation/reports/feature-verification-matrix.md').write_text(
        matrix_text(features), encoding='utf-8')
    run = root / 'validation/ci/runs/1-component/dist'
    run.mkdir(parents=True, exist_ok=True)
    package = run / 'MrSpicyUI-iphoneos-arm64-unsigned.zip'
    object_package(package)
    prov = {'source_commit': 'a' * 40, 'checked_out_commit': 'a' * 40, 'run_id': 1,
            'source_trees': {}, 'artifacts': [
                {'path': 'dist/MrSpicyUI-iphoneos-arm64-unsigned.zip',
                 'size_bytes': package.stat().st_size,
                 'sha256': vrs.sha256_file(package)}]}
    (run.parent / 'provenance.json').write_text(json.dumps(prov), encoding='utf-8')
    return prov


def manifest_for(root, **overrides):
    manifest = {
        'release_ipa': {'status': 'NOT PRODUCED', 'delivered': False, 'sha256': None,
                        'expected_path': 'output/pool8Signed.ipa',
                        'expected_checksum_path': 'output/pool8Signed.sha256'},
        'input_evidence': {'sha256': vrs.INPUT_SHA256, 'size_bytes': vrs.INPUT_SIZE},
        'component': {'device_build': {'path': 'validation/ci/runs/1-component/dist/'
                                               'MrSpicyUI-iphoneos-arm64-unsigned.zip',
                                       'installable': False},
                      'brand_asset': {'sha256': None}},
        'signature_validation': {'input_ipa': {'result': 'FAILED', 'exit_code': 1,
                                               'diagnostic': 'invalid Info.plist'}},
        'features': {'advertised_categories': 42,
                     'pro': 'Localized read-only unavailable disclosure',
                     'ad_free': 'Component adds no ad SDK/network code',
                     'automation': 'Reference only, not implemented'},
    }
    for section, values in overrides.items():
        manifest.setdefault(section, {}).update(values)
    (root / 'validation/manifests/release-manifest.json').write_text(
        json.dumps(manifest), encoding='utf-8')


class GateTests(unittest.TestCase):

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='spicy-gate-'))
        self.addCleanup(shutil.rmtree, self.root, True)

    def run_gate(self):
        return vrs.run_checks(self.root)

    # -- the real repository ------------------------------------------------

    def test_real_repository_passes_the_gate(self):
        report = vrs.run_checks(REPO)
        failures = [c for c in report.checks if c['result'] == 'FAIL']
        self.assertEqual(failures, [], 'the repository itself must satisfy the gate')
        self.assertTrue(report.passed)
        self.assertGreater(report.counts.get('PASS', 0), 20)
        # The release must still be recorded as not produced.
        self.assertEqual(report.result('release_ipa_not_produced'), 'PASS')

    # -- release artifact honesty ------------------------------------------

    def test_placeholder_release_artifact_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        out = self.root / 'output'
        out.mkdir(parents=True, exist_ok=True)
        (out / 'pool8Signed.ipa').write_bytes(b'placeholder')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('release_ipa_not_produced'), 'FAIL')
        self.assertEqual(report.result('no_placeholder_release'), 'FAIL')
        self.assertEqual(report.result('manifest_matches_filesystem'), 'FAIL')

    def test_renamed_demo_application_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        (self.root / 'output').mkdir(parents=True, exist_ok=True)
        (self.root / 'output' / 'Mr Spicy.ipa').write_bytes(b'demo')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('release_ipa_not_produced'), 'FAIL')
        self.assertEqual(report.result('no_placeholder_release'), 'FAIL')

    def test_unsigned_component_packaged_as_ipa_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        dist = self.root / 'dist'
        dist.mkdir(parents=True, exist_ok=True)
        object_package(dist / 'MrSpicyUI-iphoneos-arm64-unsigned.zip')
        shutil.copyfile(dist / 'MrSpicyUI-iphoneos-arm64-unsigned.zip',
                        dist / 'MrSpicyUI.ipa')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('no_placeholder_release'), 'FAIL')

    # -- manifest honesty ---------------------------------------------------

    def test_manifest_claiming_delivery_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root, release_ipa={'status': 'PRODUCED', 'delivered': True,
                                             'sha256': '0' * 64})
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('manifest_release_status'), 'FAIL')

    def test_manifest_overstating_pro_and_ad_free_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root, features={'advertised_categories': 42,
                                          'pro': 'Pro activated with a valid license key',
                                          'ad_free': 'Game-wide ad-free enabled and verified',
                                          'automation': 'Reference only, not implemented'})
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('manifest_feature_claim[pro]'), 'FAIL')
        self.assertEqual(report.result('manifest_feature_claim[ad_free]'), 'FAIL')

    def test_manifest_hiding_the_signature_failure_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root, signature_validation={'input_ipa': {'result': 'VALID',
                                                                   'exit_code': 0}})
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('manifest_signature_claim'), 'FAIL')

    def test_manifest_category_count_must_match_the_matrix(self):
        base_tree(self.root)
        manifest_for(self.root, features={'advertised_categories': 41,
                                          'pro': 'read-only unavailable disclosure',
                                          'ad_free': 'Component adds no ad SDK',
                                          'automation': 'Reference only'})
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('manifest_category_count'), 'FAIL')

    # -- feature matrix honesty --------------------------------------------

    def test_matrix_claiming_an_implemented_game_feature_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        features = [('Prediction Lines', 'implemented'),
                    ('Arabic menu', 'implemented (component only)')]
        features += [(f'Filler {i}', 'unavailable') for i in range(40)]
        (self.root / 'validation/reports/feature-verification-matrix.md').write_text(
            matrix_text(features), encoding='utf-8')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('feature_matrix_statuses'), 'FAIL')

    def test_matrix_must_contain_42_categories(self):
        base_tree(self.root)
        manifest_for(self.root, features={'advertised_categories': 41,
                                          'pro': 'read-only unavailable disclosure',
                                          'ad_free': 'Component adds no ad SDK',
                                          'automation': 'Reference only'})
        (self.root / 'validation/reports/feature-verification-matrix.md').write_text(
            matrix_text([(f'Filler {i}', 'unavailable') for i in range(41)]), encoding='utf-8')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('feature_matrix_count'), 'FAIL')

    def test_matrix_may_not_mark_game_features_as_component_only(self):
        base_tree(self.root)
        manifest_for(self.root)
        features = [('Prediction Lines', 'implemented (component only)')]
        features += [(f'Filler {i}', 'unavailable') for i in range(41)]
        (self.root / 'validation/reports/feature-verification-matrix.md').write_text(
            matrix_text(features), encoding='utf-8')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('feature_matrix_component_only_claims'), 'FAIL')

    # -- component scope ----------------------------------------------------

    def test_advertising_sdk_in_component_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        (self.root / 'MrSpicyUI/Sources/MrSpicyUI/Ads.swift').write_text(
            'import AppLovinSDK\n', encoding='utf-8')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('component_scope'), 'FAIL')

    def test_host_loading_code_in_component_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        (self.root / 'MrSpicyUI/Sources/MrSpicyUI/Loader.swift').write_text(
            'import Foundation\nlet h = dlopen("/payload", RTLD_NOW)\n', encoding='utf-8')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('component_scope'), 'FAIL')

    # -- localization -------------------------------------------------------

    def test_localization_key_divergence_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        ar = self.root / 'MrSpicyUI/Sources/MrSpicyUI/Resources/ar.lproj/Localizable.strings'
        text = ar.read_text(encoding='utf-8')
        ar.write_text(text.replace('"mr.spicy.settings.sound" = "ar-Sound effects";\n', ''),
                      encoding='utf-8')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('localization_key_parity'), 'FAIL')

    def test_missing_arabic_value_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        ar = self.root / 'MrSpicyUI/Sources/MrSpicyUI/Resources/ar.lproj/Localizable.strings'
        text = ar.read_text(encoding='utf-8')
        ar.write_text(text.replace('"mr.spicy.settings.sound" = "ar-Sound effects";',
                                   '"mr.spicy.settings.sound" = "";'), encoding='utf-8')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('localization_arabic_non_empty'), 'FAIL')

    def test_unresolved_localization_key_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        view = self.root / 'MrSpicyUI/Sources/MrSpicyUI/SpicySettingsView.swift'
        view.write_text(view.read_text(encoding='utf-8')
                        + 'let c = SpicyLocalization.string("mr.spicy.does.not.exist")\n',
                        encoding='utf-8')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('localization_keys_resolve'), 'FAIL')

    # -- component artifact provenance -------------------------------------

    def test_tampered_component_artifact_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        package = (self.root / 'validation/ci/runs/1-component/dist/'
                   'MrSpicyUI-iphoneos-arm64-unsigned.zip')
        with zipfile.ZipFile(package, 'a') as z:
            z.writestr('extra.bin', b'tampered')
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('component_artifact[1-component]'), 'FAIL')

    def test_executable_packaged_as_component_fails_the_gate(self):
        base_tree(self.root)
        manifest_for(self.root)
        run = self.root / 'validation/ci/runs/1-component'
        package = run / 'dist' / 'MrSpicyUI-iphoneos-arm64-unsigned.zip'
        object_package(package, file_type=2)  # MH_EXECUTE, not MH_OBJECT
        prov = json.loads((run / 'provenance.json').read_text(encoding='utf-8'))
        prov['artifacts'][0].update(size_bytes=package.stat().st_size,
                                    sha256=vrs.sha256_file(package))
        (run / 'provenance.json').write_text(json.dumps(prov), encoding='utf-8')
        manifest_for(self.root)
        report = self.run_gate()
        self.assertFalse(report.passed)
        self.assertEqual(report.result('component_artifact[1-component]'), 'FAIL')


class MatrixParsingTests(unittest.TestCase):

    def test_real_matrix_has_42_rows_and_an_honest_status_column(self):
        text = (REPO / 'validation/reports/feature-verification-matrix.md').read_text(encoding='utf-8')
        rows = vrs.matrix_feature_rows(text)
        self.assertEqual(len(rows), 42)
        for row in rows:
            self.assertIn(row[-1].lower(), vrs.HONEST_STATUSES)

    def test_separator_and_trailing_text_are_ignored(self):
        text = (MATRIX_HEADER + '\n|---|---|---|---|---|---|---|---|\n'
                + ROW.format(feature='Prediction Lines', status='unavailable') + '\n'
                + '\nTrailing prose, not a table row.\n')
        rows = vrs.matrix_feature_rows(text)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], 'Prediction Lines')


class ReportSemanticsTests(unittest.TestCase):

    def test_only_fail_fails_the_gate(self):
        report = vrs.Report()
        report.ok('a', 'fine')
        report.warn('b', 'historical')
        report.unverified('c', 'not evaluable')
        self.assertTrue(report.passed)
        self.assertEqual(report.counts, {'PASS': 1, 'WARN': 1, 'UNVERIFIED': 1})
        report.fail('d', 'broken')
        self.assertFalse(report.passed)

    def test_unknown_check_has_no_result(self):
        self.assertIsNone(vrs.Report().result('nope'))


if __name__ == '__main__':
    unittest.main()


class ProvenanceTests(unittest.TestCase):
    """`ci_provenance` must never invent a toolchain or hide a missing one."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='spicy-prov-'))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.saved_env = dict(os.environ)
        os.environ.update(GITHUB_SHA='a' * 40, GITHUB_RUN_ID='7',
                          GITHUB_RUN_ATTEMPT='1', GITHUB_REF='refs/heads/x')

        def restore_env():
            os.environ.clear()
            os.environ.update(self.saved_env)

        self.addCleanup(restore_env)

    def test_missing_actions_environment_fails_loudly(self):
        for name in ('GITHUB_SHA', 'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT', 'GITHUB_REF'):
            os.environ.pop(name, None)
            with self.assertRaises(SystemExit):
                cp.require_env(name)
        with self.assertRaises(SystemExit):
            cp.provenance('component')

    def test_unavailable_tools_are_recorded_not_invented(self):
        os.environ['GITHUB_SHA'] = 'a' * 40
        # A command that cannot exist records unavailability rather than crashing.
        text = cp.describe(('definitely-not-a-real-tool-xyz', '--version'))
        self.assertTrue(text.startswith('unavailable ('))
        self.assertIn('definitely-not-a-real-tool-xyz', text)

    def test_provenance_records_the_checked_out_commit_and_trees(self):
        code, head, _ = vrs.git('rev-parse', 'HEAD')
        self.assertEqual(code, 0)
        os.environ['GITHUB_SHA'] = head
        data = cp.provenance('release-gate')
        self.assertEqual(data['checked_out_commit'], head)
        self.assertEqual(data['source_commit'], head)
        self.assertEqual(data['job'], 'release-gate')
        self.assertEqual(data['run_id'], 7)
        self.assertEqual(set(data['source_trees']), set(vrs.SOURCE_TREES))
        for tree, oid in data['source_trees'].items():
            code, observed, _ = vrs.git('rev-parse', f'HEAD:{tree}')
            self.assertEqual(observed, oid)
        # Every toolchain field must be a real value or an explicit unavailability.
        for key in ('toolchain', 'swift', 'os', 'sdk'):
            self.assertTrue(data[key])
        self.assertEqual(data['component_signing'],
                         'CODE_SIGNING_ALLOWED=NO; not installable')

    def test_provenance_hashes_every_dist_artifact(self):
        # A throwaway git repository with the source directories and a dist/ tree,
        # so provenance records a real checkout and a real artifact hash.
        for d in vrs.SOURCE_TREES:
            (self.root / d).mkdir(parents=True, exist_ok=True)
            (self.root / d / 'keep.txt').write_text('x', encoding='utf-8')
        (self.root / 'dist').mkdir(parents=True, exist_ok=True)
        package = self.root / 'dist' / 'MrSpicyUI-iphoneos-arm64-unsigned.zip'
        object_package(package)
        for args in (('init', '-q', str(self.root)),
                     ('-C', str(self.root), 'add', '-A'),
                     ('-C', str(self.root), '-c', 'user.email=a@b', '-c', 'user.name=a',
                      'commit', '-qm', 'fixture')):
            code, _, err = vrs.git(*args)
            self.assertEqual(code, 0, err)
        code, head, _ = vrs.git('-C', str(self.root), 'rev-parse', 'HEAD')
        self.assertEqual(code, 0)
        os.environ['GITHUB_SHA'] = head
        cwd = os.getcwd()
        os.chdir(self.root)
        try:
            data = cp.provenance('component')
        finally:
            os.chdir(cwd)
        self.assertEqual(data['checked_out_commit'], head)
        self.assertEqual(set(data['source_trees']), set(vrs.SOURCE_TREES))
        self.assertEqual(len(data['artifacts']), 1)
        recorded = data['artifacts'][0]
        self.assertEqual(recorded['path'], 'dist/MrSpicyUI-iphoneos-arm64-unsigned.zip')
        self.assertEqual(recorded['size_bytes'], package.stat().st_size)
        self.assertEqual(recorded['sha256'], vrs.sha256_file(package))
