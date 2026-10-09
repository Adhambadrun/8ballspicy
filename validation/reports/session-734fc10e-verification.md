# Verification report — session arena/734fc10e-8ballspicy (2026-10-09)

Base: `98a6163` (`main`). Continues `validation/reports/session-a4ebad6a-verification.md`, which is
kept unchanged. Companion documents: `warning-register-734fc10e.md`, `change-log-734fc10e.md`,
`validation/ci/installable/INSTALL.md`, `validation/manifests/release-manifest.json`.

Measurements below were taken on the session tree. The tree IDs are in the manifest under
`source_tree_snapshot`. The gate's `manifest_source_snapshot` check compares the manifest with
HEAD, so it can only PASS once the session commit exists. The post-commit results are recorded in
the change log.

## A. Overall status

| Question | Answer |
|---|---|
| Is a release IPA produced? | **No.** `output/pool8Signed.ipa` and `output/pool8Signed.sha256` are absent. `output/` contains only `README.md`. |
| Is the game released or release-ready? | **No.** Blocked by external prerequisites E1–E5 (see section I). |
| Is the component verified? | **Historically, yes, for `fae2937`.** Run `37928629998` produced an artifact whose bytes, CRC, Mach-O type and tests were re-verified here. **Not verified for current HEAD**, because no CI has run on it. |
| Is component CI installed? | **No.** Push of `.github/workflows/component-ci.yml` was refused (`workflows` permission). A tested patch is provided. No CI run exists for this branch. |
| Gate result | 27 PASS / 10 WARN / 1 FAIL before the session commit (the FAIL is `manifest_source_snapshot`, which needs the commit). Expected to be 28 / 10 / 0 after it. See section B. |

Component CI success is component evidence only. It is not game release readiness.

## B. Verification totals

Commands run from the repository root. Exit codes are the shell's.

| Command | Exit | Result |
|---|---|---|
| `python3 tools/verify_release_state.py` | 1 pre-commit / see change log | `summary: {'PASS': 27, 'WARN': 10, 'FAIL': 1}`. FAIL: `manifest_source_snapshot`, expected before the commit exists. |
| `PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'` | 1 pre-commit / see change log | 69 run, 68 passed, 0 failed, 1 skipped. The one failure is `test_real_repository_passes_the_gate`, for the same snapshot reason. |
| per module | — | `test_inspect_ipa` 4 OK; `test_verify_release_state` 33 (1 failure, same reason); `test_audit_feature_matrix` 19 OK; `test_ci_workflow` 13 (1 skipped). |
| `python3 tools/audit_feature_matrix.py` | 0 | 98 PASS / 0 WARN / 0 FAIL on the real IPA, 42 categories. |
| `python3 tools/verify_component_evidence.py 37928629998 --output /tmp/component-verification.json` | 0 | Source `fae2937…`; zip sha256 `3a872657…c5a6`, 1,729,023 bytes; CRC PASS; thin arm64 MH_OBJECT; hostless 34 pass / 0 fail / 17 skip; hosted 51 pass / 0 fail; device build succeeded. Copy kept at `validation/evidence/component-verification-recheck-734fc10e-37928629998.json`. |
| `sha256sum validation/ci/runs/37928629998-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip` | 0 | `3a872657371e155a2bda05deeb73342e2e848e6ca0d99e1c484c4e651a90c5a6`, matching the verified value. |
| `sha256sum pool8Signed.ipa` | 0 | `6b4dfd3bd63a1ee5e649d98c44077e5d48f8a013255082287bef4514f6abdc84`, 99,010,014 bytes. Unchanged from baseline. Not modified, copied or repackaged. |
| YAML parse of `installable/component-ci.yml` (pyyaml in `/tmp/yamlvenv`) | 0 | Parses. Triggers only on `arena/734fc10e-8ballspicy`. Jobs: `component`, `hosted-tests`, `release-gate`, `publish-evidence`. Publication needs all three. Top-level `contents: read`. |
| `git apply --check` of the install patch onto the session commit | see change log | Recorded in the change log. |

Two items that the earlier session described differently are now measured:

* **The baseline gate was 26 PASS / 10 WARN, not 27 / 7.** Reproduced in a clone of `98a6163` (exit 0). The `27/7` in the a4ebad6a report cannot be reproduced. See the warning register.
* **The historical audit count of 96 is reproduced** at `98a6163` (exit 0, 96 PASS). Its 45 matrix citations became 42 (three game-binary citations removed). With five new structural findings, 96 − 3 + 5 = 98.

## C. Warning register

Full register: `validation/reports/warning-register-734fc10e.md`.

| Status | Count | IDs |
|---|---|---|
| CLOSED | 0 | — |
| OPEN, needs CI on the current trees | 9 | W2–W10 (source-provenance WARNs for four historical runs, plus the aggregate) |
| PERMANENT (historical) | 1 | W1 (`37927299718`, failed before producing an artifact) |

None was converted to PASS, hidden or relabelled. The gate checks were not changed to alter any WARN. The gate diff has no removed lines.

## D. CI activation

* Attempted: `git push origin arena/734fc10e-8ballspicy` with `.github/workflows/component-ci.yml` in the commit.
* Result: **rejected**.
  ```
  ! [remote rejected] arena/734fc10e-8ballspicy -> arena/734fc10e-8ballspicy
    (refusing to allow a GitHub App to create or update workflow
    `.github/workflows/component-ci.yml` without `workflows` permission)
  ```
* Same refusal as session a4ebad6a. It is a permission limit of the GitHub App token. It was not worked around.
* Delivered instead: canonical text `validation/ci/installable/component-ci.yml`, patch `validation/ci/installable/install-component-ci.patch`, instructions `validation/ci/installable/INSTALL.md`.
* `tools/test_ci_workflow.py` checks that the workflow triggers only on the session branch, never on `validation/ci/**` (so publish commits cannot loop), runs the gate, audit and Python suite, does not mask failures (the one permitted `|| true` is on the informational `xcodebuild -list` line), publishes only after the gate succeeded, and grants write permission only to the publish job. It also checks that the patch adds exactly the canonical text. Once the patch is applied, it checks that the installed copy is identical.
* **CI runs for this branch: 0.** No run ID exists for this session. Existing run IDs `37925407220`, `37926156116`, `37927299718`, `37928629998` were produced on `abadrun/8ballspicy`, not on this branch.
* The CI status is therefore **NOT INSTALLED**. This report does not claim otherwise.

## E. Feature audit

* Matrix: `validation/reports/feature-verification-matrix.md`, 42 categories. Evidence re-derived from the immutable IPA by `tools/audit_feature_matrix.py`: 98 PASS, 0 FAIL.
* New in this session: status taxonomy (`validation/evidence/feature-status-taxonomy.json`), with 42 assignments:

  | Category | Count |
  |---|---|
  | Implemented and tested | 0 |
  | Implemented but incompletely tested | 2 |
  | UI representation only | 1 (Pro access) |
  | Explicitly unavailable | 29 |
  | Blocked by host integration | 5 |
  | Dependent on external authorization | 1 (ad-free) |
  | Not implemented | 4 |

* New: component-evidence file `validation/evidence/component-feature-evidence.json` for the English menu, Arabic menu and Pro access. The auditor resolves every token against the component source.
* The English and Arabic menu rows previously cited game-binary strings (`Aim Mode`, `useArabic`, `isArabic`) that do not evidence component localization. Those citations were removed. Component-source evidence replaces them.
* **Settings with no runtime effect.** Five settings persist and report to the host bridge, and do nothing else inside the component: **Sound effects, Haptic feedback, Haptic intensity, Match notifications, Personalized tips**. The bridge doc comment and the matrix now state this. Verified by reading `SpicySettingsView.swift` (all six setters call `notifyChange()`), the bridge call at `SpicyOverlayViewController.swift:164`, and `resetTapped`.
* **Pro** is a read-only UI label. The gate check `pro_entitlement_scope` confirms that 11 component and host source files reference no entitlement, purchase or unlock API.
* The auditor's summary key was renamed from `citations` to `findings`. It now counts all checks, not only citations. This is documented in the change log so the two numbers are not compared as if they were the same thing.

## F. Artifact evidence

| Item | Value | Source |
|---|---|---|
| Component ZIP | `MrSpicyUI-iphoneos-arm64-unsigned.zip`, 1,729,023 bytes, sha256 `3a872657…c5a6`, CRC PASS, `signed: false` | run `37928629998`, verified here |
| Component object | `MrSpicyUI.o`, arm64 thin MH_OBJECT, 415,608 bytes, sha256 `3e14286d6ba4aae56f7ca3840a8d8854e30b00f1b702aa25584799af84cf9061` | same |
| Hostless tests | 34 passed, 0 failed, 17 skipped | `verify_component_evidence.py` |
| Hosted tests | 51 passed, 0 failed | same |
| Device build | succeeded (`generic/platform=iOS`, unsigned) | same |
| Input IPA | `pool8Signed.ipa`, 99,010,014 bytes, sha256 `6b4dfd3b…abdc84`, unchanged | `sha256sum` |
| Input code-signature | `codesign --verify` exit 1: "invalid Info.plist (plist or signature have been modified)" | recorded by the CI run and stated in E2 |

The input's broken signature is a known blocker (E2), not a new finding. The component job records it and does not fail on it.

## G. Code and documentation changes

Full list with commit IDs: `validation/reports/change-log-734fc10e.md`.

Summary: new release-gate checks (`manifest_source_snapshot`, `pro_entitlement_scope`); new auditor checks (`taxonomy`, `component_evidence`); evidence files; the feature matrix's citations and taxonomy; the manifest's counts and tree snapshot; the canonical CI workflow, its patch and instructions; the workflow invariant tests; corrected comments in `MrSpicyUI`; updated warning register, this report and the change log.

## H. Integration and release status

* **Not released.** `output/` is NOT PRODUCED. The manifest records `NOT PRODUCED` with a null hash.
* The Mr. Spicy component is not integrated into the game. The only host is `HostApp`, which is a demo app with bundle ID `com.mrspicy.demo.host`, not the game.
* No signing, device run, or Apple-issued identity exists in this environment.

## I. Remaining blockers

| ID | Blocker | Status |
|---|---|---|
| E1 | Owner-authorized buildable game source or official integration SDK with documented presentation/settings API, and written permitted UI scope | BLOCKING |
| E2 | Clean owner baseline and documented protection/build pipeline (input code-signature fails) | BLOCKING |
| E3 | Apple-issued identity and matching profiles for `com.miniclip.8ballpoolmult` and four extensions | BLOCKING |
| E4 | Official permitted Pro and ad-free APIs, entitlement configuration, legitimate test access | BLOCKING |
| E5 | Authorized physical iOS device in developer mode, with documented model, iOS version and UDID | BLOCKING |
| E6 | Maintainer with the GitHub App `workflows` permission to install the CI patch | CONFIRMED BLOCKING (re-verified this session) |

Code-level items: the component is verified for `fae2937`. Current HEAD is not CI-verified (W2–W10).

## J. Next milestone

1. **Immediate (needs E6):** a maintainer applies `validation/ci/installable/install-component-ci.patch` to `arena/734fc10e-8ballspicy` and runs the workflow. The first run records provenance for the current trees and can close W2–W10. The workflow's own `release-gate` will then fail the run if any gate check fails.
2. **Release (needs E1–E5):** an owner-authorized game source or SDK with a documented presentation/settings API. Until then, no IPA is produced and none is claimed.
