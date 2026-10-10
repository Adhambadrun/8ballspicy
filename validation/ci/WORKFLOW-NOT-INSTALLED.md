# CI workflow status: NOT INSTALLED (as of session arena/a8ab557d-8ballspicy, 2026-10-09)

**Current state, stated plainly:** no component CI workflow runs on this repository. The
release-gated workflow is ready as a tested patch, but this session's GitHub App token cannot
add it. Install instructions are in `validation/ci/installable/INSTALL.md`.

This file replaces the session 734fc10e version. That version is preserved in git history at
commit `bd5520d` (`git show bd5520d:validation/ci/WORKFLOW-NOT-INSTALLED.md`).

## Files

| File | Status |
|---|---|
| `component-ci.workflow.yml.txt` | Verbatim copy of the original workflow from `abadrun/8ballspicy` at `08937925a`. Historical source of record; unchanged. |
| `component-ci.release-gated.yml.txt` | Superseded proposal (a4ebad6a). Retained; its header now points to the canonical text. |
| `installable/component-ci.yml` | **Canonical text for the installed workflow.** Retargeted to `arena/a8ab557d-8ballspicy`, with the local unit-test step, the scope statement and no masked failures. |
| `installable/install-component-ci.patch` | Git patch that adds `.github/workflows/component-ci.yml` with exactly the canonical text. Checked by `tools/test_ci_workflow.py`. |
| `installable/INSTALL.md` | Installation steps and the status of each piece. |

## Why it is not under `.github/workflows/`

On 2026-10-09 in session a8ab557d, `git push origin arena/a8ab557d-8ballspicy` was refused for
the commit that added `.github/workflows/component-ci.yml`:

```
! [remote rejected] arena/a8ab557d-8ballspicy -> arena/a8ab557d-8ballspicy
  (refusing to allow a GitHub App to create or update workflow
  `.github/workflows/component-ci.yml` without `workflows` permission)
```

The same refusal was recorded in sessions 734fc10e and a4ebad6a. In this session a
contents-API `PUT` of the workflow file was also attempted and returned HTTP 403
"Resource not accessible by integration". The environment holds exactly one credential
(`GH_TOKEN` == `GITHUB_TOKEN`, a GitHub App installation token); no personal access token
exists. The restriction is a permission of the GitHub App token. It was not worked around,
and no credential was requested or stored.

Because of this, the workflow was never installed under `.github/workflows/`, and
`Adhambadrun/8ballspicy` has no workflow runs for this branch. Build and test evidence cited by
the project comes from runs on `abadrun/8ballspicy` (see `validation/ci/runs/` and
`validation/manifests/release-manifest.json`). That evidence was re-verified locally against
the artifact, source trees and logs. It is historical evidence for historical source trees.

## What the installed workflow would do

* `component`: forensic parser unit tests, read-only Apple inspection of the immutable input,
  hostless simulator tests, unsigned arm64 device build, architecture check, package and hash.
* `hosted-tests`: the same sources inside a real `UIApplicationMain` host, plus a repeat of the
  animated-transition regressions.
* `release-gate` (Ubuntu): the local Python suite, `tools/verify_release_state.py` and
  `tools/audit_feature_matrix.py`. Failures are not masked.
* `publish-evidence`: runs only if `release-gate` succeeded. It refuses to publish otherwise.
  Its trigger excludes `validation/ci/**` so that its own commit cannot start a new run.

A green run proves that the component builds and its tests pass on that commit. It does not
produce the release IPA and does not establish game release readiness. The output
`output/pool8Signed.ipa` stays NOT PRODUCED until the external prerequisites E1 to E5 in the
release manifest are met.
