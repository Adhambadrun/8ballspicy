# CI workflow is preserved here as text, not installed

Two workflow definitions live in this directory:

| File | Status |
|---|---|
| `component-ci.workflow.yml.txt` | Verbatim copy of the working GitHub Actions workflow from `.github/workflows/component-ci.yml` at `08937925a` on `abadrun/8ballspicy` (branch `arena/6264dd0a-8ballspicy`) — the historical source of record. Kept unchanged so the original definition stays auditable. |
| `component-ci.release-gated.yml.txt` | **Recommended installation.** The same workflow plus a `release-gate` job and a publication guard, retargeted to `arena/a4ebad6a-8ballspicy`. Install this one. |

Both define the original three jobs — `component` (forensic parser unit tests,
read-only Apple inspection of the immutable input, toolchain record, hostless
simulator tests, unsigned `generic/platform=iOS` arm64 build, architecture
verification, package + hash, provenance, artifact upload), `hosted-tests` (the
same test sources inside the real `UIApplicationMain` host, plus a repeat pass
of the animated-transition regressions), and `publish-evidence` (writes the
verified logs and artifact back to the session branch).

## What the release gate adds

`component-ci.release-gated.yml.txt` adds a fourth job, `release-gate`, that
runs on `ubuntu-latest` and executes:

```bash
python3 tools/verify_release_state.py     # every delivery claim vs. the real files
python3 tools/audit_feature_matrix.py     # re-derive the 42-category evidence from the IPA
```

and then makes `publish-evidence` `needs: [component, hosted-tests, release-gate]`
with an explicit guard that exits non-zero unless the gate succeeded. The
consequence is that a failed test, a missing integration prerequisite, a
placeholder `output/pool8Signed.ipa`, a renamed demo application, an unsigned
component ZIP labelled as a release, a manifest claiming a delivery the
filesystem does not support, or a feature row advertising an implementation the
project has not established **cannot be published as a successful run**.

`tools/verify_release_state.py` is covered by `tools/test_verify_release_state.py`,
which includes negative cases proving the gate fails for each of those
violations. Those tests run in the existing `component` job, so the gate itself
is enforced rather than assumed.

## Why the workflow is not under `.github/workflows/`

These files are stored as `.txt` in this directory — **not** under
`.github/workflows/` — because the GitHub App token available to this session is
rejected when pushing any commit that creates or updates a workflow file. This
was **re-verified on 2026-10-09 during session `arena/a4ebad6a-8ballspicy`**, with
the exact rejection reproduced twice:

```
# git push
 ! [remote rejected] arena/a4ebad6a-8ballspicy -> arena/a4ebad6a-8ballspicy
   (refusing to allow a GitHub App to create or update workflow
   `.github/workflows/component-ci.yml` without `workflows` permission)

# GitHub contents API (PUT /repos/Adhambadrun/8ballspicy/contents/.github/workflows/component-ci.yml)
HTTP 403
{"message":"Resource not accessible by integration","status":"403"}
```

Consequences, stated plainly:

* This session branch (`arena/a4ebad6a-8ballspicy` on `Adhambadrun/8ballspicy`)
  **cannot run the macOS component CI itself**, and therefore cannot produce its
  own new build/test evidence. `Adhambadrun/8ballspicy` currently reports
  **0 workflow runs**.
* All build and test evidence cited by this project was produced by runs on
  `abadrun/8ballspicy` and was **independently re-verified** here: artifact ZIPs
  were downloaded, their SHA-256 recomputed and compared to the recorded values,
  the Mach-O outputs re-parsed, the raw `xcodebuild` logs re-read for the actual
  executed / failed / skipped counts, and the source trees compared by git tree
  ID against the run provenance.
* To re-enable CI on a branch, a maintainer with the `workflows` scope must copy
  `component-ci.release-gated.yml.txt` to `.github/workflows/component-ci.yml`
  and update the two references to the session branch name (the
  `on.push.branches` filter and the `test "$SESSION_BRANCH" = ...` guard in the
  publish job).

The workflow only builds and tests the independent `MrSpicyUI` component,
performs read-only static inspection of the input IPA, and verifies the
repository's delivery claims. It never modifies, re-signs, or repackages the
8 Ball Pool application.
