# Change log — session arena/734fc10e-8ballspicy (2026-10-09)

Base commit: `98a6163daca75c8d169b3096df70fd3dada880a1` (`main`).
Session branch: `arena/734fc10e-8ballspicy` (remote `origin` = `Adhambadrun/8ballspicy`).

## Commits

| Commit | Content | Pushed |
|---|---|---|
| C1 | All source, tool, evidence, manifest and documentation changes listed below | see "Push outcome" |
| C2 | Doc-only: this change log's "Commits" and "Post-commit verification" sections, and the push outcome | see "Push outcome" |

Commit IDs are written in C2 because a commit cannot contain its own ID. C2 changes no file that
is part of any source tree, so the manifest's tree snapshot still matches.

## Push outcome

* C1 push: recorded in C2 below.
* CI run for C1: **none.** The workflow is not installed. Installation is blocked (E6). See
  `validation/ci/installable/INSTALL.md`.

## Changes

### Release gate and tests (`tools/`)

* `tools/verify_release_state.py`
  * Added `check_source_snapshot` (`manifest_source_snapshot`, FAIL if the manifest's recorded trees differ from HEAD).
  * Added `check_pro_entitlement_scope` (`pro_entitlement_scope`, FAIL if entitlement, purchase or unlock APIs appear in component or host sources).
  * Both registered in `ALL_CHECKS`.
  * **No existing check was modified or removed.** `git diff 98a6163 -- tools/verify_release_state.py` has zero removed lines.
* `tools/test_verify_release_state.py`
  * Added `SourceSnapshotAndProScopeTests` (7 tests).
  * `commit_fixture` now creates `tools/keep.py` so the fixture has a `tools/` tree.
  * The `__main__` block was moved to the end of the file. Previously it sat before `ProvenanceTests`, so those 4 tests were skipped when the file was run directly. **Removed:** the earlier `__main__` block (2 lines). Behaviour when run via `unittest discover` is unchanged.
* `tools/audit_feature_matrix.py`
  * Added `check_taxonomy` and `check_component_evidence` (pure functions), with the `--taxonomy`, `--component-evidence` and `--root` flags.
  * `audit()` takes an explicit `root` keyword.
  * **Summary key renamed** from `citations` to `findings`. It now counts all checks (98), not only citations. The historical `citations: 96` and the new `findings: 98` are therefore not the same quantity; the arithmetic is 96 − 3 + 5 = 98.
  * **Removed one line** from the docstring, the phrase "This tool verifies citations, not functionality." It was replaced by "This tool verifies citations and evidence links, not functionality." The disclaimer is kept.
* `tools/test_audit_feature_matrix.py`
  * Added `EvidenceStructureTests` (taxonomy, component evidence, real-repository taxonomy and evidence, 42 matrix entries, category counts), which do not need the IPA.
  * The IPA test passes `root=REPO` explicitly.
  * **Removed one line:** the earlier call `afm.audit(IPA, MATRIX, EVIDENCE)` without a root.
* `tools/test_ci_workflow.py` (new, 13 tests)
  * Checks the canonical workflow: session-branch trigger only; `validation/ci/**` not a trigger path; trigger covers release-claim paths; job graph; publication refuses unless the gate succeeded; the gate runs all three checks; failures not masked (the only `|| true` is on `xcodebuild -list`); scope statement present; read-only default token with write only in publication; no secrets.
  * Checks that `install-component-ci.patch` adds exactly the canonical text.
  * Checks that the installed copy, if present, is identical to the canonical text (skipped while not installed).
* `tools/ci_provenance.py`, `tools/inspect_ipa.py` and `tools/verify_component_evidence.py` are **not** changed in this session.

### Workflow (`validation/ci/`)

* **Not installed.** The earlier attempt to commit `.github/workflows/component-ci.yml` was refused. The file was moved out of `.github/` before C1.
* `validation/ci/installable/component-ci.yml` (new): canonical text. Retargeted to `arena/734fc10e-8ballspicy`. Adds a local unit-test step, the scope statement, and removes the masked provenance failure.
* `validation/ci/installable/install-component-ci.patch` (new): a `git diff` that adds `.github/workflows/component-ci.yml` with exactly the canonical text.
* `validation/ci/installable/INSTALL.md` (new): installation steps and status.
* `validation/ci/WORKFLOW-NOT-INSTALLED.md`: rewritten for the current state. The previous version is in git history at `98a6163`.
* `validation/ci/component-ci.release-gated.yml.txt`: header replaced. It is marked as the superseded proposal and points to the canonical text. Workflow body unchanged.
* `validation/ci/component-ci.workflow.yml.txt` (original) and `validation/ci/runs/*`: **unchanged.**

### Evidence (`validation/evidence/`)

* `feature-status-taxonomy.json` (new): 42 assignments across 7 categories.
* `component-feature-evidence.json` (new): component-source evidence for the English menu, Arabic menu and Pro access.
* `component-verification-recheck-734fc10e-37928629998.json` (new): output of `tools/verify_component_evidence.py 37928629998`. The requested command is also run to `/tmp/component-verification.json`, which is not in the repository.
* Existing historical evidence files are **unchanged**.

### Feature matrix (`validation/reports/feature-verification-matrix.md`)

* English and Arabic menu rows: game-binary citations replaced by component evidence. **Removed:** `Aim Mode` @ 10038551, `useArabic` @ 10028655, `isArabic` @ 10001490. Matrix citations 45 → 42.
* Controls row rewritten. Settings table rewritten to state the five settings with no runtime effect.
* Added sections "Status taxonomy" and "Settings effect inside the component".
* **Not changed:** the 42-category structure and the status of any row.

### Manifest (`validation/manifests/release-manifest.json`)

* Added `source_tree_snapshot` (trees of the session commit, computed from the index; excluding `validation/`).
* Corrected `component.cross_repository_provenance.after_session_edits.current_trees`. Those values were correct only at `aa71e17`; commit `9c053e7` changed `MrSpicyUI/README.md` and `tools/verify_release_state.py` afterwards. The old values are retained under `trees_at_aa71e17_superseded`.
* `ci.workflow_installation` now states NOT INSTALLED, with the patch and instructions. Its earlier "PENDING" wording was wrong and was replaced.
* `ci.workflow_installation_blocked`: the refusal is re-verified for this session. The historical record is kept.
* Blockers: component-build and citation items updated to the measured values; "Release could be faked by CI" is "mitigated in canonical text; not installed". E6 is "confirmed blocking".
* Counts: `release_integrity_gate` now records measured values (gate 28/10/0; suite 69 tests, 68 passed, 1 skipped; audit 98 findings, 42 matrix citations).
* Added `warnings_register`, `verification_session_734fc10e`, and `features.status_taxonomy`.

### Source comments (`MrSpicyUI/`)

* `MrSpicyUI/Package.swift`: comment only. Corrected the provenance block to the measured trees.
* `MrSpicyUI/Sources/MrSpicyUI/SpicyHostBridge.swift`: comment only. Replaced "every control writes to `SpicyPreferences` and reports through this bridge" with a statement that persistence and reporting are the whole effect inside the component, and that five settings have no runtime effect.
* Verified: `git diff fae2937 -- MrSpicyUI/Package.swift MrSpicyUI/Sources` contains only `//` comment lines and no blank-line changes. The compiled code matches the CI-tested revision.
* `MrSpicyUI/README.md` and `output/README.md`: stale counts replaced with a pointer to the session report.

### Reports (`validation/reports/`)

* `session-734fc10e-verification.md` (new): verification report.
* `warning-register-734fc10e.md` (new): all 10 historical warnings with status, root cause, action and final status.
* `change-log-734fc10e.md` (new): this file.
* `session-a4ebad6a-verification.md`, `build-and-signing-report.md`, `device-test-report.md`, `forensic-analysis.md`, `integration-validation.md`: **unchanged.**

## Items that were not done

* **No CI run** was triggered. The workflow is not installed.
* **No release IPA** and no `.sha256`. `output/` remains NOT PRODUCED.
* **No change to `pool8Signed.ipa`.** It was read, hashed and inspected only.
* **No game modification**, bypass, ad removal, entitlement work or gameplay automation.
* **No signing** and **no device run**.
* **No pull request** was opened or merged.
* The manifest's `current_trees` correction is recorded, not hidden.

## Post-commit verification

To be filled in C2. These commands are run on C1 after it is committed, and the results are recorded here:

* `python3 tools/verify_release_state.py` → expected 28 PASS / 10 WARN / 0 FAIL, exit 0.
* `PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'` → expected 69 run, 68 passed, 1 skipped, exit 0.
* `python3 tools/audit_feature_matrix.py` → expected 98 PASS, exit 0.
* `git apply --check` and clean-tree application of the install patch → expected to succeed, and `test_ci_workflow` to pass with the installed-copy test active.
