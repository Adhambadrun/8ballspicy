# Installing the release-gated component CI

Status on `arena/734fc10e-8ballspicy` (session 734fc10e, 2026-10-09): **NOT INSTALLED.**
A push of `.github/workflows/component-ci.yml` from this session was refused by GitHub:

```
! [remote rejected] arena/734fc10e-8ballspicy -> arena/734fc10e-8ballspicy
  (refusing to allow a GitHub App to create or update workflow
  `.github/workflows/component-ci.yml` without `workflows` permission)
```

The same refusal was recorded in session a4ebad6a. This is a permission limit of the
GitHub App token. It was not worked around.

## What is ready

| File | Role |
|---|---|
| `validation/ci/installable/component-ci.yml` | Canonical workflow text. Not under `.github/workflows/`, so GitHub does not run it. |
| `validation/ci/installable/install-component-ci.patch` | Git patch that adds `.github/workflows/component-ci.yml` with exactly that text. |
| `tools/test_ci_workflow.py` | Checks the safety invariants of the workflow and that the patch adds exactly the canonical text. Once installed, also checks that the installed copy is identical. |

## How to install (requires a token with the `workflows` permission)

From a checkout of `arena/734fc10e-8ballspicy` at any commit that contains `validation/ci/installable/` (the session commit history is listed in `validation/reports/session-734fc10e-verification.md`):

```bash
git apply --check validation/ci/installable/install-component-ci.patch
git apply validation/ci/installable/install-component-ci.patch
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'   # expect 0 failures, 0 skips
python3 tools/verify_release_state.py                                    # expect exit 0
git add .github/workflows/component-ci.yml
git commit -m "ci: install release-gated component workflow (arena/734fc10e-8ballspicy)"
git push origin arena/734fc10e-8ballspicy
```

The push must be made by an account whose GitHub App token includes `workflows`. The
installed workflow then runs on the next push to this branch that touches a listed path.

## What the workflow does, and what it does not claim

* `component`: forensic parser tests, read-only Apple inspection of the immutable input,
  hostless simulator tests, unsigned `generic/platform=iOS` arm64 build, architecture check,
  package and hash, provenance.
* `hosted-tests`: the same test sources inside a real `UIApplicationMain` host, plus a repeat
  pass of the animated-transition regressions.
* `release-gate`: local Python test suite, `tools/verify_release_state.py`,
  `tools/audit_feature_matrix.py`.
* `publish-evidence`: runs only if `release-gate` succeeded. Commits run logs to
  `validation/ci/runs/<id>-*` on the session branch. The trigger path list excludes
  `validation/ci/**`, so this commit cannot start another run.

A green run is **component CI evidence only**. It does not produce `output/pool8Signed.ipa`,
does not sign anything, and does not establish game release readiness. Those remain
blocked by E1 to E5 in `validation/manifests/release-manifest.json`.
