# Change log — session arena/a8ab557d-8ballspicy (2026-10-09)

Base commit: `bd5520deb3b67d7867560eed5001933ddf9e3521` (`main`, merged PR #3 — the merged
state of session 734fc10e). Session branch: `arena/a8ab557d-8ballspicy` (remote `origin` =
`Adhambadrun/8ballspicy`). The local history is a single grafted commit; historical commits
(e.g. `fae2937`) are fetched from origin on demand.

## Commits

| Commit | Content | Pushed |
|---|---|---|
| C1 | All source, tool, CI, evidence-manifest and documentation changes listed below. | **Pushed; accepted.** `origin/arena/a8ab557d-8ballspicy` = C1 (verified with `git ls-remote`). |
| C2 | Doc-only: this change log's commit IDs and post-commit verification section. | Pushed in the same way as C1. |

Commit IDs are written in C2 because a commit cannot contain its own ID. C2 changes no file
that is part of any source tree, so the manifest's tree snapshot still matches.

## Push outcome

* C1 push: **accepted.** `git push origin arena/a8ab557d-8ballspicy` exited 0. The GitHub App
  token accepted the commit because it contains no workflow file under `.github/`.
* Workflow installation push (a commit adding `.github/workflows/component-ci.yml`):
  **rejected** — `! [remote rejected] arena/a8ab557d-8ballspicy -> arena/a8ab557d-8ballspicy
  (refusing to allow a GitHub App to create or update workflow
  '.github/workflows/component-ci.yml' without 'workflows' permission)`. The local commit was
  reset after the rejection; the workflow file is not in the branch.
* Contents-API installation attempt (`PUT .../contents/.github/workflows/component-ci.yml`,
  branch `arena/a8ab557d-8ballspicy`): **HTTP 403** `Resource not accessible by integration`.
* CI runs for this branch: **0.** No workflow file exists on the remote branch
  (`repos/Adhambadrun/8ballspicy/contents/.github/workflows` → 404; `actions/workflows` lists
  0 workflows; `actions/runs` lists 0 runs). CI is **NOT INSTALLED**. See
  `validation/ci/installable/INSTALL.md`.

## Changes

### CI retargeting (`validation/ci/`, `tools/test_ci_workflow.py`)

The canonical workflow is session-scoped by design (its push trigger and its publish guard
pin the session branch). This session retargets it from `arena/734fc10e-8ballspicy` to
`arena/a8ab557d-8ballspicy` so that, once a maintainer with the `workflows` permission
installs it, it actually triggers on and publishes to this branch.

* `validation/ci/installable/component-ci.yml` — canonical text retargeted:
  `on.push.branches` → `arena/a8ab557d-8ballspicy`; publish guard
  `test "$SESSION_BRANCH" = "arena/a8ab557d-8ballspicy"`; STATUS comment updated to name this
  session and the re-verified refusal (git push + contents API). No job, step, permission,
  path filter or gate behaviour changed.
* `validation/ci/installable/install-component-ci.patch` — regenerated; adds exactly the new
  canonical text (checked by `tools/test_ci_workflow.py::test_patch_adds_exactly_the_canonical_text`).
* `tools/test_ci_workflow.py` — `SESSION_BRANCH` retargeted to `arena/a8ab557d-8ballspicy`.
  No invariant weakened; all 13 tests re-run.
* `validation/ci/installable/INSTALL.md` — rewritten for this session: status, both refusal
  routes, retargeted install commands.
* `validation/ci/WORKFLOW-NOT-INSTALLED.md` — rewritten for this session; the 734fc10e version
  is preserved in git history at `bd5520d`.
* `validation/ci/component-ci.release-gated.yml.txt` — header pointer retargeted (superseded
  proposal; body unchanged).
* `validation/ci/component-ci.workflow.yml.txt` and `validation/ci/runs/*` — **unchanged.**

Verified ready-to-apply: in a clean clone of C1, `git apply --check` + `git apply` of the
patch succeeds; the installed copy is byte-identical to the canonical text; the suite runs
69 tests OK with 0 skipped (the installed-copy identity test now runs); the gate reports
28 PASS / 10 WARN / 0 FAIL, exit 0.

### Manifest (`validation/manifests/release-manifest.json`)

* `session_branch` → `arena/a8ab557d-8ballspicy`; `generated_utc` updated.
* `ci.workflow_installation_blocked`: this session's re-verification added (git push error
  for this branch, contents API HTTP 403, `GH_TOKEN` == `GITHUB_TOKEN` — one GitHub App
  installation token, no PAT in the environment).
* `ci.workflow_installation.session_branch` → `arena/a8ab557d-8ballspicy`.
* `source_tree_snapshot`: `session_branch`, `recorded_utc` and the `tools` tree updated (the
  `tools` tree changed because `tools/test_ci_workflow.py` changed; `MrSpicyUI` and `HostApp`
  trees unchanged). `manifest_source_snapshot` PASSes after the update.
* `release_integrity_gate.result.note` → this session; warning-register pointer →
  `warning-register-a8ab557d.md`.
* `blockers.external_prerequisites[E6]` → CONFIRMED BLOCKING, re-verified in this session.
* `next_step.cheapest_immediately_actionable` → branch retargeted.
* Added `verification_session_a8ab557d` block.
* Release status, input evidence, component evidence, blockers E1–E5, test counts and feature
  claims: **unchanged and re-verified** (see the session report).

### Reports (`validation/reports/`)

* `warning-register-a8ab557d.md` (new): all ten warnings individually re-verified and
  classified (0 CLOSED / 9 OPEN / 1 PERMANENT). Corrects one stale value in the superseded
  register: it cited the HEAD `tools` tree as `6c77ff8f…`, which is not an object in this
  repository; the authoritative HEAD tools tree at `bd5520d` is `ceec8c41…` (verified with
  `git rev-parse HEAD:tools` and by the gate's `manifest_source_snapshot` PASS). The old
  register is kept unchanged; the correction lives in the superseding register.
* `session-a8ab557d-verification.md` (new): this session's measurements.
* `change-log-a8ab557d.md` (new): this file.
* All 734fc10e and earlier reports: **unchanged.**

### Not changed

* `MrSpicyUI/`, `HostApp/` — no source changes this session (no Apple toolchain on this Linux
  host; the component is already CI-verified for `fae2937` and its delta since then is
  comments-only, re-verified this session).
* `tools/verify_release_state.py`, `tools/audit_feature_matrix.py`, `tools/inspect_ipa.py`,
  `tools/ci_provenance.py`, `tools/verify_component_evidence.py` and the other test files —
  unchanged. No gate check was weakened.
* `pool8Signed.ipa` — unchanged (SHA-256 re-verified, see the session report).
* `output/` — unchanged; still NOT PRODUCED.
