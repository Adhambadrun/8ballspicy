# Warning register — session arena/734fc10e-8ballspicy (2026-10-09)

Basis: the 10 `WARN` results that `tools/verify_release_state.py` reported at the session base
commit `98a6163`, reproduced in a clone of that commit (26 PASS / 10 WARN / 0 FAIL, exit 0).
The same 10 WARNs are reported at the session's current `HEAD`, with 28 PASS / 10 WARN / 0 FAIL
(exit 0). Historical records are not rewritten. The gate checks and their thresholds were not
changed to alter any WARN; see "Gate changes" below.

**Discrepancy in the historical record.** `validation/reports/session-a4ebad6a-verification.md`
(section 4) states "27 PASS, 7 WARN, 0 FAIL". That figure is not reproducible at `98a6163`.
The gate there reports 26 PASS, 10 WARN, 0 FAIL. The cause of the difference is not recorded in
that report. It is kept as written, and this register supersedes its count.

## Summary

| Status | Count | Meaning |
|---|---|---|
| CLOSED | 0 | No historical WARN was closed by this session. |
| OPEN — needs CI on current trees | 9 | Source-provenance WARNs. Closes only when a CI run on a commit with these trees is recorded. Needs the workflow installed (see `validation/ci/installable/INSTALL.md`). |
| PERMANENT — historical | 1 | The failed run `37927299718` has no artifact. This WARN is correct and must not be repaired. |

No WARN was converted to PASS, hidden, or re-labelled. No FAIL exists.

## Register

Current trees at HEAD (the commit that holds this register, excluding `validation/`):
`MrSpicyUI` `595091cb…`, `HostApp` `8704ef1e…`, `tools` `6c77ff8f…`.

| # | Gate check and subject | Historical root cause | Current status | Action in this session | Final status and closure requirement |
|---|---|---|---|---|---|
| W1 | `component_artifact[37927299718-component]` — "artifact or provenance missing for this run" | Run `37927299718` failed on source `51f0ba1` (hostless close-button assertion) before the device build. `validation/ci/runs/37927299718-component/` has `provenance.json` but no `dist/MrSpicyUI-iphoneos-arm64-unsigned.zip`. | WARN, still correct | None. Historical evidence is not rewritten. The assertion was moved to the hosted test `testCloseButtonNotifiesBridgeAndCloses` in `fae2937`. Run `37928629998` passed on `fae2937` and produced the artifact. | **PERMANENT.** This run did not produce an artifact and will not. Closure is not possible and not needed. The current component claim rests on `37928629998`. |
| W2 | `source_provenance[37925407220-component]` — recorded a different source tree | Run tested `2d17a44`: MrSpicyUI `c94bd5bf…`, tools `9616459e…`. | WARN | Not analysed. The code delta between `2d17a44` and HEAD was not reviewed in this session, so no claim is made about it. | **OPEN.** Historical revision, kept on purpose. Retained as provenance, not as a claim about HEAD. Closure only through a CI run on current trees. |
| W3 | `source_provenance[37925407220-hosted-tests]` | Same as W2 (`2d17a44`). | WARN | Not analysed. | **OPEN** (same as W2). |
| W4 | `source_provenance[37926156116-component]` | Run tested `902ec19f`: MrSpicyUI `99749f3e…`, tools `02452f07…`. | WARN | Not analysed. | **OPEN** (same as W2). |
| W5 | `source_provenance[37926156116-hosted-tests]` | Same as W4 (`902ec19f`). | WARN | Not analysed. | **OPEN** (same as W2). |
| W6 | `source_provenance[37927299718-component]` | Run tested `51f0ba1`: MrSpicyUI `144daf5b…`, tools `18d176a1…`. | WARN | Not analysed. | **OPEN** (same as W2). Note that this run is also W1. |
| W7 | `source_provenance[37927299718-hosted-tests]` | Same as W6 (`51f0ba1`). | WARN | Not analysed. | **OPEN** (same as W2). |
| W8 | `source_provenance[37928629998-component]` | The run that produced the verified artifact tested `fae2937`: MrSpicyUI `3a775121…`, HostApp `8704ef1e…`, tools `18d176a1…`. At HEAD MrSpicyUI is `595091cb…` and tools is `6c77ff8f…`. | WARN | Verified this session with `git diff fae2937 -- MrSpicyUI/Package.swift MrSpicyUI/Sources`. Every changed line in the executable Swift is a `//` comment, with no blank-line changes. Other changed MrSpicyUI files are `README.md` (documentation) and `SpicyBrand.swift` and `SpicyHostBridge.swift` (comments). `HostApp` is identical. `tools/` is not part of the component build. | **OPEN.** The compiled component is the same code, but the gate does not treat that as provenance. The gate compares trees, not code, so a CI run on HEAD is required. |
| W9 | `source_provenance[37928629998-hosted-tests]` | Same as W8 (`fae2937`). | WARN | Same as W8. `HostApp` identical. | **OPEN** (same as W8). |
| W10 | `source_provenance` (aggregate) — "no CI run recorded the current working-copy trees" | Consequence of W2–W9: no recorded run has the current trees. | WARN | None possible without CI. | **OPEN.** Closes when any CI run records `MrSpicyUI` `595091cb…` and `tools` `6c77ff8f…`, or the trees of the commit that gets CI, whichever is final. |

## Why W2–W10 cannot be closed in this session

The trees they compare are produced only by a CI run on a commit that contains the current
sources. That requires `.github/workflows/component-ci.yml` on the session branch. This session's
push of that file was refused: `refusing to allow a GitHub App to create or update workflow
… without workflows permission`. The same refusal was recorded in session a4ebad6a (HTTP 403 on
the contents API). Closing these WARNs requires E6 (a maintainer with `workflows` permission) to
install the patch. The gate has no route to PASS that avoids a real run.

## Gate changes made in this session (not weakening)

* Added `manifest_source_snapshot` (FAIL when the manifest's recorded trees differ from HEAD).
* Added `pro_entitlement_scope` (FAIL if any Pro entitlement or purchase mechanism appears in the
  component or host sources).
* Fixed the test file so its `__main__` block runs the gate tests. The block was placed before
  the `ProvenanceTests` class, so those tests were skipped when the file was run directly.
* No existing WARN, FAIL or UNVERIFIED condition was relaxed. See the git diff of
  `tools/verify_release_state.py` between `98a6163` and this commit.

## Result after the session's changes

Gate: `python3 tools/verify_release_state.py` → exit 0, `summary: {'PASS': 28, 'WARN': 10}`.
The 10 WARNs are exactly W1–W10 above. Confirmed by the output in the verification report.
