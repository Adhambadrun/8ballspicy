"""Invariant tests for the release-gated component workflow.

The workflow cannot be installed by every session (the GitHub App token may lack
the `workflows` permission), so its canonical text lives in
``validation/ci/installable/component-ci.yml`` and is delivered as
``install-component-ci.patch``. These tests check the properties the workflow must
keep, without a YAML dependency, so they run on any runner:

* the session branch filter and publish guard name the session branch;
* the trigger cannot loop: ``validation/ci/**`` is never a trigger path, because
  publish-evidence commits land there;
* the release gate runs the release-state tool, the feature audit and the local
  Python suite, and failures are not masked;
* evidence is published only when the release gate succeeded;
* the patch adds exactly the canonical text;
* once installed, the installed copy is identical to the canonical text.
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CANONICAL = REPO / 'validation/ci/installable/component-ci.yml'
PATCH = REPO / 'validation/ci/installable/install-component-ci.patch'
INSTALLED = REPO / '.github/workflows/component-ci.yml'
SESSION_BRANCH = 'arena/a8ab557d-8ballspicy'
TARGET = '.github/workflows/component-ci.yml'


def job_block(text, name):
    """Return the text of one top-level job, from its key to the next top-level job."""
    match = re.search(rf'^  {re.escape(name)}:\n(.*?)(?=^  \S[^\n]*:\n|\Z)', text, re.M | re.S)
    return match.group(1) if match else ''


def code_lines(text):
    """Workflow lines without comments, so a comment cannot satisfy an invariant."""
    return [line.split(' #', 1)[0] if not line.lstrip().startswith('#') else ''
            for line in text.splitlines()]


class WorkflowInvariantTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = CANONICAL.read_text(encoding='utf-8')
        cls.code = '\n'.join(code_lines(cls.text))

    def test_triggers_only_on_the_session_branch(self):
        block = re.search(r'^    branches:\n((?:      - .+\n)+)', self.code + '\n', re.M)
        self.assertIsNotNone(block)
        branches = re.findall(r'^      - (\S+)$', block.group(1), re.M)
        self.assertEqual(branches, [SESSION_BRANCH])

    def test_validation_ci_is_never_a_trigger_path(self):
        # publish-evidence pushes under validation/ci/runs/. Triggering on it would loop.
        self.assertIsNone(re.search(r'^\s+- "validation/ci', self.code, re.M))

    def test_trigger_covers_every_path_that_can_change_a_release_claim(self):
        for path in ('MrSpicyUI/**', 'HostApp/**', 'tools/**', 'validation/manifests/**',
                     'validation/reports/**', 'validation/evidence/**', 'output/**',
                     'pool8Signed.ipa', TARGET):
            self.assertIn(f'"{path}"', self.code, path)

    def test_job_graph(self):
        for job in ('component', 'hosted-tests', 'release-gate', 'publish-evidence'):
            self.assertTrue(job_block(self.text, job), job)
        self.assertIn('needs: [component, hosted-tests, release-gate]',
                      job_block(self.text, 'publish-evidence'))

    def test_publication_refuses_unless_the_release_gate_succeeded(self):
        publish = job_block(self.text, 'publish-evidence')
        self.assertIn('needs.release-gate.result', publish)
        self.assertIn('!= "success"', publish)
        self.assertIn(f'test "$SESSION_BRANCH" = "{SESSION_BRANCH}"', publish)

    def test_release_gate_runs_all_three_checks(self):
        gate = job_block(self.text, 'release-gate')
        self.assertIn('tools/verify_release_state.py', gate)
        self.assertIn('tools/audit_feature_matrix.py', gate)
        self.assertIn('unittest discover -s tools', gate)

    def test_release_gate_failures_are_not_masked(self):
        # The only permitted `|| true` is on the informational `xcodebuild -list` line in the
        # toolchain display. No test, build, gate or publish step may use it.
        lines = [l for l in self.code.splitlines() if '|| true' in l]
        self.assertEqual(len(lines), 1, lines)
        self.assertIn('xcodebuild -list', lines[0])
        for job in ('release-gate', 'publish-evidence'):
            self.assertNotIn('|| true', job_block(self.text, job), job)
        self.assertNotIn('continue-on-error', self.code)

    def test_release_gate_states_that_component_success_is_not_release_readiness(self):
        gate = job_block(self.text, 'release-gate')
        self.assertIn('Game release readiness is a separate question', gate)
        self.assertIn('NOT PRODUCED', gate)

    def test_default_token_is_read_only_outside_publication(self):
        top = self.code.split('\njobs:', 1)[0]
        self.assertIn('permissions:\n  contents: read', top)
        self.assertIn('contents: write', job_block(self.text, 'publish-evidence'))
        for job in ('component', 'hosted-tests', 'release-gate'):
            self.assertNotIn('contents: write', job_block(self.text, job), job)

    def test_no_secrets_or_apple_signing_material_are_required(self):
        self.assertNotIn('secrets.', self.code)
        self.assertNotIn('CODE_SIGN_IDENTITY=', self.code.replace('CODE_SIGNING_ALLOWED=NO', ''))


class PatchAndInstallationTests(unittest.TestCase):

    def test_patch_adds_exactly_the_canonical_text(self):
        lines = PATCH.read_text(encoding='utf-8').splitlines()
        self.assertIn(f'+++ b/{TARGET}', lines)
        start = lines.index('@@ -0,0 +1,' + str(len(CANONICAL.read_text(encoding='utf-8').splitlines()))
                            + ' @@')
        added = []
        for line in lines[start + 1:]:
            if line.startswith('+'):
                added.append(line[1:])
            elif line.startswith('\\'):
                continue
            else:
                break
        self.assertEqual(added, CANONICAL.read_text(encoding='utf-8').splitlines())

    def test_patch_touches_only_the_workflow_file(self):
        headers = [line for line in PATCH.read_text(encoding='utf-8').splitlines()
                   if line.startswith('diff --git ')]
        self.assertEqual(headers, [f'diff --git a/{TARGET} b/{TARGET}'])

    @unittest.skipUnless(INSTALLED.exists(), 'workflow not installed in this checkout')
    def test_installed_copy_is_identical_to_the_canonical_text(self):
        self.assertEqual(INSTALLED.read_text(encoding='utf-8'),
                         CANONICAL.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
