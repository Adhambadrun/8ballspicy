# Verification report — session arena/a8ab557d-8ballspicy (2026-10-09)

Base: `bd5520deb3b67d7867560eed5001933ddf9e3521` (`main`, merged PR #3 — the merged state of
session 734fc10e). Continues `validation/reports/session-734fc10e-verification.md`, which is
kept unchanged. Companion documents: `warning-register-a8ab557d.md`,
`change-log-a8ab557d.md`, `validation/ci/installable/INSTALL.md`,
`validation/manifests/release-manifest.json`.

All measurements below were taken in this session on this session's tree, from the
repository root. The local git history is a single grafted commit (`git rev-list --count
HEAD` = 1); historical commits such as `fae2937` were fetched from origin on demand for the
re-verifications that need them.

## A. Overall status

| Question | Answer |
|---|---|
| Is a release IPA produced? | **No.** `output/pool8Signed.ipa` and `output/pool8Signed.sha256` are absent. `output/` contains only `README.md`. |
| Is the game released or release-ready? | **No.** Blocked by external prerequisites E1–E5 (see section I). |
| Is the component verified? | **Historically, yes, for `fae2937`.** Re-verified again in this session (section B). **Not verified for current HEAD**, because no CI has run on it. |
| Is component CI installed? | **No.** Two independent installation routes were refused this session (git push and the contents API). A tested patch retargeted to this branch is provided. No CI run exists for this branch. |
| Gate result | 28 PASS / 10 WARN / 0 FAIL, exit 0 — identical to the merged 734fc10e result; re-measured here before and after this session's changes. |

Component CI success is component evidence only. It is not game release readiness.

## B. Verification totals

| Command | Exit | Result |
|---|---|---|
| `python3 tools/verify_release_state.py` | 0 | `summary: {'PASS': 28, 'WARN': 10}`, `RESULT: PASS`. The 10 WARNs are W1–W10 (section C). Re-run after this session's commit: same result. |
| `PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'` | 0 | 69 run, OK, 1 skipped (`test_installed_copy_is_identical_to_the_canonical_text`, which runs once the patch is installed). |
| `python3 tools/audit_feature_matrix.py` | 0 | 98 PASS / 0 WARN / 0 FAIL on the real IPA, 42 categories. |
| `sha256sum pool8Signed.ipa` | 0 | `6b4dfd3bd63a1ee5e649d98c44077e5d48f8a013255082287bef4514f6abdc84`, 99,010,014 bytes. Matches the immutable record. Not modified, copied or repackaged. |
| `python3 tools/verify_component_evidence.py 37928629998 --output /tmp/component-verification-a8ab557d.json` | 0 | Source `fae2937…` (fetched from origin for this check); zip sha256 `3a872657…c5a6`; hostless 34 pass / 0 fail / 17 skip; hosted 51 pass / 0 fail; device build succeeded. Matches the 734fc10e recheck. |
| `sha256sum validation/ci/runs/37928629998-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip` | 0 | `3a872657371e155a2bda05deeb73342e2e848e6ca0d99e1c484c4e651a90c5a6`, matching the verified value. |
| W8 code-delta re-verification: `git diff fae2937 -- MrSpicyUI/Package.swift MrSpicyUI/Sources` filtered to non-comment, non-blank lines | 0 | **Zero** such lines. The MrSpicyUI delta since the CI-tested commit is comments only (plus `README.md`, documentation). Claim re-confirmed. |
| Taxonomy cross-check (independent of the auditor) | 0 | `feature-status-taxonomy.json`: 42 assignments; counts 29/4/5/2/1/1 — identical to the manifest's `features.status_taxonomy.counts` and to the auditor's taxonomy check. |
| `git apply --check` + `git apply` of `validation/ci/installable/install-component-ci.patch` in a clean clone of this session's commit; `diff` installed vs canonical | 0 | Applied; **byte-identical**. With it applied: 69 tests OK, **0 skipped**; gate 28/10/0, exit 0. |
| YAML parse of `validation/ci/installable/component-ci.yml` | 0 | Parses (pyyaml). Triggers only on `arena/a8ab557d-8ballspicy`; jobs `component`, `hosted-tests`, `release-gate`, `publish-evidence`; publication needs all three; top-level `contents: read`. |
| Workflow installation attempt 1: `git push origin arena/a8ab557d-8ballspicy` (commit adding `.github/workflows/component-ci.yml`) | 1 | **Rejected:** `refusing to allow a GitHub App to create or update workflow '.github/workflows/component-ci.yml' without 'workflows' permission`. Local commit reset afterwards. |
| Workflow installation attempt 2: contents API `PUT /repos/Adhambadrun/8ballspicy/contents/.github/workflows/component-ci.yml` (branch `arena/a8ab557d-8ballspicy`) | 403 | **Rejected:** `Resource not accessible by integration`. |
| Credential inventory | — | `GH_TOKEN` and `GITHUB_TOKEN` are the same token (SHA-256 prefix `91de4a8ac1c1`); it is a GitHub App installation token. No PAT, no `.netrc`, no `.git-credentials`. `gh auth status`: logged in as `Adhambadrun`. |
| `gh api /repos/Adhambadrun/8ballspicy/actions/workflows` and `actions/runs` | 0 | 0 workflows, 0 runs on the repository. **No CI run exists.** |

## C. Warning register

Full register: `validation/reports/warning-register-a8ab557d.md` (supersedes the 734fc10e
register, which is kept unchanged).

| Status | Count | IDs |
|---|---|---|
| CLOSED | 0 | — |
| OPEN, needs CI on the current trees (E6) | 9 | W2–W10 (source-provenance WARNs for four historical runs, plus the aggregate) |
| PERMANENT (historical) | 1 | W1 (`37927299718`, failed before producing an artifact) |

Every warning was re-verified individually this session against the current repository:
W1's missing artifact confirmed by directory listing; W2–W9's recorded source trees
re-read from each `provenance.json` and confirmed to differ from HEAD; W10's aggregate
re-measured by the gate. One stale value in the superseded register was found and
corrected in the new register: it cited the HEAD `tools` tree as `6c77ff8f…`, which is not
an object in this repository; the authoritative value at `bd5520d` is `ceec8c41…`
(`git rev-parse HEAD:tools`, and the gate's `manifest_source_snapshot` PASS).

None was converted to PASS, hidden or relabelled. The gate checks were not changed to alter
any WARN.

## D. CI activation

**Push result for this session's commits (C1, C2):** accepted. `origin/arena/a8ab557d-8ballspicy`
points to C2. **CI runs: 0.**

* Attempted: `git push origin arena/a8ab557d-8ballspicy` with `.github/workflows/component-ci.yml`
  in the commit (verified locally first: patch applies, installed copy byte-identical,
  69 tests OK / 0 skipped, gate 28/10/0).
* Result: **rejected** (exact message in section B). Same refusal as sessions 734fc10e and
  a4ebad6a.
* Second route attempted: contents API `PUT` of the same file — HTTP 403 "Resource not
  accessible by integration".
* The environment holds exactly one credential, a GitHub App installation token
  (`GH_TOKEN` == `GITHUB_TOKEN`); no personal access token exists. The missing permission
  is the App's **`workflows` permission** — an owner-side setting on the GitHub App
  installation. It was not worked around; no credential was requested or stored.
* Delivered instead: canonical text `validation/ci/installable/component-ci.yml` **retargeted
  to `arena/a8ab557d-8ballspicy`** (trigger branch, publish guard, STATUS comment),
  regenerated patch `validation/ci/installable/install-component-ci.patch`, updated
  `tools/test_ci_workflow.py` (`SESSION_BRANCH`), rewritten `INSTALL.md` and
  `WORKFLOW-NOT-INSTALLED.md`. The retargeting is required for the workflow to ever trigger
  on this branch; no job, permission, path filter or gate behaviour was changed.
* Ready-to-apply verification: clean clone of this session's commit → patch applies →
  installed copy byte-identical → 69 tests OK, 0 skipped → gate 28/10/0 exit 0.
* **CI runs for this branch: 0.** The CI status is **NOT INSTALLED**. This report does not
  claim otherwise.

## E. Feature audit

* Matrix: `validation/reports/feature-verification-matrix.md`, 42 categories. Evidence
  re-derived from the immutable IPA by `tools/audit_feature_matrix.py`: 98 PASS, 0 FAIL.
* Status taxonomy (`validation/evidence/feature-status-taxonomy.json`), 42 assignments:

  | Category | Count |
  |---|---|
  | Implemented and tested | 0 |
  | Implemented but incompletely tested | 2 |
  | UI representation only | 1 (Pro access) |
  | Explicitly unavailable | 29 |
  | Blocked by host integration | 5 |
  | Dependent on external authorization | 1 (ad-free) |
  | Not implemented | 4 |

* Independently cross-checked this session: assignment counts equal the manifest's taxonomy
  counts; sum = 42.
* Settings with no runtime effect inside the component (Sound effects, Haptic feedback,
  Haptic intensity, Match notifications, Personalized tips) remain disclosed as such;
  **Pro** remains a read-only UI label (`pro_entitlement_scope` PASS); no ad-removal,
  entitlement, automation or online-game claim is made.

## F. Artifact evidence

| Item | Value | Source |
|---|---|---|
| Component ZIP | `MrSpicyUI-iphoneos-arm64-unsigned.zip`, 1,729,023 bytes, sha256 `3a872657…c5a6`, CRC PASS, `signed: false` | run `37928629998`, re-verified this session |
| Component object | `MrSpicyUI.o`, arm64 thin MH_OBJECT, 415,608 bytes, sha256 `3e14286d…9061` | same (gate check PASS) |
| Hostless tests | 34 passed, 0 failed, 17 skipped | `verify_component_evidence.py`, re-run this session |
| Hosted tests | 51 passed, 0 failed | same |
| Device build | succeeded (`generic/platform=iOS`, unsigned) | same |
| Input IPA | `pool8Signed.ipa`, 99,010,014 bytes, sha256 `6b4dfd3b…abdc84`, unchanged | `sha256sum`, this session |
| Input code-signature | `codesign --verify` exit 1: "invalid Info.plist (plist or signature have been modified)" | recorded by the CI run; remains blocker E2 |
| Source snapshot | manifest `source_tree_snapshot` matches HEAD (gate PASS); `MrSpicyUI` `595091cb…`, `HostApp` `8704ef1e…`, `tools` per manifest | gate |

The input's broken signature is a known blocker (E2), not a new finding.

## G. Code and documentation changes

Full list with commit IDs: `validation/reports/change-log-a8ab557d.md`.

Summary: the canonical CI workflow, its patch, its invariant tests and its installation
documents retargeted from `arena/734fc10e-8ballspicy` to `arena/a8ab557d-8ballspicy`; the
manifest's session fields, CI-blocker record and tree snapshot updated; new warning
register, session report and change log. **No change** to `MrSpicyUI/`, `HostApp/`, the
release-gate tool, the auditor, `pool8Signed.ipa` or `output/`.

## H. Integration and release status

* **Not released.** `output/` is NOT PRODUCED. The manifest records `NOT PRODUCED` with a null
  hash, and the gate verifies the negative state (including its negative tests).
* The Mr. Spicy component is not integrated into the game. The only host is `HostApp`, a demo
  app with bundle ID `com.mrspicy.demo.host`, not the game.
* No Apple toolchain exists on this Linux host (`swift`/`xcodebuild` absent), so no local
  build, simulator run or device test is possible here. All hostless validations that do
  not need Apple tooling were run (sections B, E, F). The component's build/test evidence
  remains the historical macOS CI run `37928629998` on `fae2937`, re-verified byte-for-byte
  this session.
* No signing, device run, or Apple-issued identity exists in this environment.

## I. Remaining blockers

| ID | Blocker | Status |
|---|---|---|
| E1 | Owner-authorized buildable game source or official integration SDK with documented presentation/settings API, and written permitted UI scope | BLOCKING |
| E2 | Clean owner baseline and documented protection/build pipeline (input code-signature fails) | BLOCKING |
| E3 | Apple-issued identity and matching profiles for `com.miniclip.8ballpoolmult` and four extensions | BLOCKING |
| E4 | Official permitted Pro and ad-free APIs, entitlement configuration, legitimate test access | BLOCKING |
| E5 | Authorized physical iOS device in developer mode, with documented model, iOS version and UDID | BLOCKING |
| E6 | Maintainer with the GitHub App `workflows` permission to install the CI patch | CONFIRMED BLOCKING (re-verified this session by git push AND contents API) |

Each blocker was re-examined this session: no game source/SDK exists anywhere in the
reachable history; no Apple identity, profile or device is present in the environment; the
only credential is the GitHub App token without `workflows`. Code-level items: the component
is verified for `fae2937`; current HEAD is not CI-verified (W2–W10).

## J. Next milestone

1. **Immediate (needs E6):** a maintainer whose GitHub App token includes `workflows`
   applies `validation/ci/installable/install-component-ci.patch` to
   `arena/a8ab557d-8ballspicy` and pushes. The push itself triggers the workflow (the
   workflow file is in the trigger path list). The first run records provenance for the
   current trees and closes W10; `publish-evidence` then commits the run evidence to this
   branch. The workflow's own `release-gate` fails the run if any gate check fails.
2. **Release (needs E1–E5):** an owner-authorized game source or SDK with a documented
   presentation/settings API. Until then, no IPA is produced and none is claimed.
