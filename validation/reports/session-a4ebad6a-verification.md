# Session verification report — `arena/a4ebad6a-8ballspicy`

**Date:** 2026-10-09. **Session branch:** `arena/a4ebad6a-8ballspicy` (on `Adhambadrun/8ballspicy`).
**Overall status: PARTIALLY COMPLETED — component verified and now gated; game
integration, signing and device validation remain BLOCKED on external
prerequisites.**

This report supersedes nothing. It re-verifies the previous phase's claims
against the actual repositories, bytes and logs, records the engineering work
completed in this session, and states exactly what still blocks a release.

---

## 1. Repositories, branches and commits inspected

| Item | Value | How verified |
|---|---|---|
| Local workspace | `/home/user/8ballspicy` | `pwd`, `git status` |
| Local branch / commit | `arena/a4ebad6a-8ballspicy` @ `0fee3e9625d1e3ba108d8552355cd5d001590683` ("Merge pull request #1 from Adhambadrun/arena/627c356f-8ballspicy") | `git log -1` |
| Remote (auth) | `github.com/Adhambadrun/8ballspicy`, authenticated as `Adhambadrun` (admin, maintain, push) | `gh auth status`, `gh api repos/...` |
| Remote (upstream evidence) | `github.com/abadrun/8ballspicy`, default branch `main` | `gh api` |
| Verified component source commit | `fae2937905395c425c777c38cbc05e115b2e1d71`, dated 2026-10-09T12:13:24Z | `gh api repos/abadrun/8ballspicy/commits/fae2937…` |
| Evidence publication commit | `dbc070bba16c4d9b5deba7fed2e6e97ed0365c30` | referenced by manifest; artifact URL fetched |
| CI run | [`37928629998`](https://github.com/abadrun/8ballspicy/actions/runs/37928629998), attempt 1, `push`, `success` | `gh api …/actions/runs/37928629998` |
| Upstream fetch | `git fetch https://github.com/abadrun/8ballspicy.git fae2937…` | completed; tree IDs compared below |

**Local analysis host:** Linux x86_64, Python 3.11.2. **No** Swift, Xcode,
`codesign`, `lipo` or LIEF are installed here, so no Apple build, sign or
runtime step was attempted or claimed in this session.

## 2. Claims re-verified, with the command and the observed result

| # | Historical claim | Command | Observed |
|---|---|---|---|
| 1 | Source IPA 99,010,014 bytes / SHA-256 `6b4dfd3b…` | `sha256sum pool8Signed.ipa`; `stat -c %s` | **MATCH** — 99,010,014 bytes, `6b4dfd3bd63a1ee5e649d98c44077e5d48f8a013255082287bef4514f6abdc84` |
| 2 | ZIP CRC PASS, 3,527 entries | `tools/verify_release_state.py` (`input_zip_crc`) | **PASS** |
| 3 | Component artifact 1,729,023 bytes / `3a872657…` | `sha256sum validation/ci/runs/37928629998-component/dist/*.zip` | **MATCH** — 1,729,023 bytes, `3a872657371e155a2bda05deeb73342e2e848e6ca0d99e1c484c4e651a90c5a6` |
| 4 | Artifact is a thin arm64 `MH_OBJECT`, not an app | gate `component_artifact[…]` (Mach-O header parse) | **PASS** — `MH_OBJECT`, `CPU_TYPE_ARM64`, ZIP CRC PASS |
| 5 | Brand mark SHA-256 `7c6b53e4…` | `sha256sum MrSpicyUI/…/spicy-s-mark.png` | **MATCH** |
| 6 | Source trees `3a775121…` / `8704ef1e…` / `18d176a1…` | `git rev-parse HEAD:MrSpicyUI` etc. | **MATCH**, and identical to `git rev-parse FETCH_HEAD:<tree>` at `fae2937` |
| 7 | Hostless 34 pass / 0 fail / 17 skip (51 executed) | `python3 tools/verify_component_evidence.py 37928629998` | **MATCH** (log re-parsed) |
| 8 | Hosted 51 pass / 0 fail / 0 skip | same | **MATCH** |
| 9 | Ten repeated animation passes | `validation/evidence/animated-repeat-37928629998.json`; repeat log | **MATCH** — 10 × `testAnimatedTransitionRejectsDuplicateRequests` passed, `** TEST SUCCEEDED **` |
| 10 | Four parser tests | `PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'` | **MATCH** (4/4) |
| 11 | Device build succeeded, all CI statuses 0 | `test-status.txt` (component + hosted) | **MATCH** — `test_status=0 device_status=0 arch_status=0 hosted_status=0 animated_repeat_status=0` |
| 12 | Three jobs succeeded | `gh api …/runs/37928629998/jobs` | **MATCH** — 113814283708, 113815315287, 113819116622, all `success` |
| 13 | Artifacts still present, unexpired | `gh api …/runs/37928629998/artifacts` | **MATCH** — `component-evidence` 1,747,747 B, `hosted-evidence` 21,750 B |
| 14 | Apple input-signature verification failed (exit 1) | `validation/ci/runs/37928629998-component/input-apple-verification.txt` | **MATCH** — `invalid Info.plist (plist or signature have been modified)`, `input_codesign_verify_exit=1`, input hash identical before/after |
| 15 | Loader SHA-256 `bc6e4193…`, 12,265,804 bytes | new `tools/audit_feature_matrix.py` | **MATCH** |
| 16 | Matrix has 42 advertised categories | `tools/audit_feature_matrix.py` / gate | **MATCH** — exactly 42 feature rows |
| 17 | No GitHub release created | `gh api repos/…/releases` (both repos) | **MATCH** — none |

**Claim 17 detail:** the "42-category" count, the honest status column, the
`advertised_categories: 42` manifest field, the Pro `UI-only` status and the
ad-free `awaiting verification` status were all re-derived from the files rather
than read from the reports.

## 3. Defects found and corrected in this session

These are real defects in the *evidence*, found by re-deriving it, not
cosmetic edits.

1. **Four case-drifted citations in the advertised-feature evidence.** The
   matrix and `validation/evidence/feature-string-search.json` quoted
   `wait time` @ 10038728 and `watch an ad` @ 10040475. The actual bytes at
   those offsets are `Wait Time` and `Watch an ad for +1h`. Offsets were
   correct; the quoted terms were not byte-exact, and `watch an ad` was a
   duplicate citation of the same offset as `Watch an ad`. Corrected in both
   files; the underlying finding is unchanged. After the correction the auditor
   reports **96 citations, 96 PASS, 0 WARN, 0 FAIL**.
2. **`tools/ci_provenance.py` crashed on a non-macOS runner** and could not
   express an unavailable toolchain. It now records
   `unavailable (<tool> not installed on this runner)` instead of failing or
   inventing a value, still fails loudly outside a GitHub Actions environment,
   and preserves the original field set, field order and artifact-path format
   for macOS runs. A latent `('sw_vers')` string-vs-tuple bug was fixed.
3. **`MrSpicyUI/Sources/MrSpicyUI/SpicyBrand.swift` contradicted the verified
   provenance.** Its comment claimed the bundled S mark was "a NEW monogram
   generated for this repository on 2026-10-09"; the forensic report and the
   release manifest both record it as the **existing generated replacement**
   carried forward, with no new mark generated. The comment now matches the
   evidence and points at the manifest hash. `MrSpicyUI/Package.swift` carried a
   similarly stale "original implementation / sibling repositories unreachable"
   provenance note; it now records the verified `abadrun` lineage and the
   matching source-tree IDs.

## 4. Engineering work completed in this session

| Deliverable | What it does |
|---|---|
| **`tools/verify_release_state.py`** | Release-integrity gate. Re-derives every delivery claim from the actual repository: input immutability, `output/` emptiness, absence of any `.ipa`/app bundle/Payload tree/mobileprovision that could impersonate a release, component artifact hash + CRC + Mach-O type, source-tree provenance against CI provenance, manifest-vs-filesystem consistency (including the recorded signature failure and the Pro/ad-free/automation claims), en↔ar localization key parity and resolution, component scope (no ad SDK, no networking, no host-loading), feature-matrix honesty, and report presence. Exits non-zero on any `FAIL`. |
| **`tools/test_verify_release_state.py`** | 26 tests: the real repository must pass, plus negative cases proving the gate **fails** for a placeholder release artifact, a renamed demo app, an unsigned component packaged as an `.ipa`, a manifest claiming delivery, a manifest overstating Pro/ad-free, a manifest hiding the signature failure, a category-count mismatch, a matrix row claiming an implemented game feature, an ad SDK in the component, `dlopen` host-loading code, localization key divergence, an empty Arabic value, an unresolved key, a tampered artifact, and an `MH_EXECUTE` packaged as the component. Plus 4 `ci_provenance` tests. |
| **`tools/audit_feature_matrix.py`** | Re-derives the 42-category evidence by reading the loader bytes out of the immutable IPA and confirming every citation in the matrix and the evidence JSON. Distinguishes `PASS` (exact bytes), `WARN` (case drift) and `FAIL` (absent). |
| **`tools/test_audit_feature_matrix.py`** | 6 tests over the real IPA, including the case-drift classifier. |
| **`validation/ci/component-ci.release-gated.yml.txt`** | The verified workflow plus a `release-gate` job on `ubuntu-latest` and a publication guard, so `publish-evidence` cannot publish evidence for a failing gate. Validated by YAML parse and job-graph inspection. |
| **`validation/ci/WORKFLOW-NOT-INSTALLED.md`** | Rewritten: documents both workflow files, what the gate adds, and the re-verified push restriction with exact error text. |

**Current gate result on this repository: 27 PASS, 7 WARN, 0 FAIL.**
The 7 warnings are legitimate: run `37927299718` failed before producing an
artifact, and runs `37925407220` / `37926156116` / `37927299718` recorded older
source trees than the working copy (historical revisions, retained on purpose).

**Local test suite: 36 tests, all passing** (4 forensic parser + 26 gate +
6 matrix auditor).

## 5. What was deliberately *not* done

- **No component rebuild.** The local source trees are byte-identical (git tree
  ID) to the source that produced the verified artifact, so rebuilding could add
  no evidence. The environment also has no Xcode.
- **No release artifact.** `output/pool8Signed.ipa` and
  `output/pool8Signed.sha256` remain absent; the manifest still records
  `NOT PRODUCED` with a null hash.
- **No game modification.** No archive surgery, plist rebranding, signature
  work, loader reuse, activation bypass, ad removal or gameplay automation. The
  new gate actively fails the build if any of that appears.
- **No new claims about the game.** Nothing here tests 8 Ball Pool's runtime
  behaviour.

## 6. Blocker table

### Code-level — resolved or not blocking

| Item | Status | Evidence |
|---|---|---|
| Component build reproducibility | **RESOLVED** | Working-copy tree IDs == CI provenance == upstream `fae2937` |
| Component test suite | **PASSING** | 34/0/17 hostless, 51/0/0 hosted, 10/10 repeat, 4/4 parser, 36/36 local gate tests |
| Feature-evidence citation accuracy | **RESOLVED** | 96/96 citations byte-exact |
| Release could be faked by CI | **RESOLVED (pending workflow install)** | `component-ci.release-gated.yml.txt` + 26 negative gate tests |
| Provenance on non-macOS runners | **RESOLVED** | `tools/ci_provenance.py` honest unavailability |
| Provenance-comment contradictions | **RESOLVED** | `SpicyBrand.swift`, `Package.swift` |

### External prerequisites — BLOCKING the release

| # | Missing prerequisite | Why it is required | Evidence that it is missing |
|---|---|---|---|
| E1 | **Owner-authorized buildable game source, or an official integration SDK with a documented presentation/settings API, plus written permitted UI scope** | Without it there is no host to present `SpicyOverlayViewController` in; a static library, object file or UI bundle is not integration | Full reachable `abadrun/8ballspicy` history fetched; `Adhambadrun/8ballspicy` history fetched. No Miniclip source, no overlay SDK, no documented extension point. Forensic report §6/§7. `SpicyHostBridge` is component-owned; the game does not acquire it. |
| E2 | **A clean owner baseline and the documented protection/build pipeline** | The supplied IPA is already anomalous, so it cannot serve as a trusted baseline for regression comparison | Apple `codesign --verify --deep --strict` → **exit 1**, `invalid Info.plist (plist or signature have been modified)`; 593 mismatching CodeDirectory pages per CD (172 wholly before the signature, 421 overlapping it); Info.plist and CodeResources special slots MISMATCH; 98 mismatching resource-hash comparisons, 61 missing entries; `libloader.framework/libloader` is 12,265,804 bytes with **no** `LC_CODE_SIGNATURE` and mod-menu strings. |
| E3 | **Apple-issued signing identity and matching provisioning profiles for `com.miniclip.8ballpoolmult` and its four extensions** | Required for any archive, export or install | No certificate or profile in this environment (`codesign` absent). No `embedded.mobileprovision` in the IPA. The GitHub secrets-list API returns **403**, so remote secret availability is **UNKNOWN**, not proven absent. |
| E4 | **Official permitted Pro and ad-free feature APIs, entitlement source/configuration, and legitimate test access** | Pro activation and game-wide ad-free cannot be implemented or verified without them | Only third-party PRO-key / rewarded-ad strings exist in `libloader` (offsets in the matrix). No entitlement service, no official ad-free configuration. No bypass was implemented or attempted. |
| E5 | **An authorized physical iOS device in developer mode, with documented model/iOS/UDID provisioning** | Installation, launch, normal-game regression and ad behaviour can only be tested on device | No device access from this Linux sandbox. `codesign`/Xcode absent. |
| E6 | **A maintainer with the GitHub App `workflows` permission** | Without it this session branch cannot run CI and cannot produce its own build/test evidence | Re-verified this session: `git push` rejected with *"refusing to allow a GitHub App to create or update workflow `.github/workflows/component-ci.yml` without `workflows` permission"*, and the contents API returned **403 Resource not accessible by integration**. `Adhambadrun/8ballspicy` reports **0 workflow runs**. |

## 7. Integration, signing and device status

| Area | Status | Evidence |
|---|---|---|
| Actual game integration | **NOT IMPLEMENTED — BLOCKED (E1)** | No host source/SDK; `HostApp/MrSpicyDemoHost` is `com.mrspicy.demo.host`, explicitly not 8 Ball Pool |
| Original game preservation | **Statically preserved only** | Identity and input bytes unchanged; navigation/screens/gameplay **NOT TESTED** (E1, E2, E5) |
| Mr. Spicy Pro | **UI-only, honest disclosure** | Localized read-only unavailable text; no entitlement, no activation, no paid feature (E4) |
| Game-wide ad-free | **NOT VERIFIED** | Component adds no ad SDK/network code; the game links AdSurgeSDK, AppLovinSDK, InMobiSDK, FBAudienceNetwork, DTBiOSSDK, MolocoSDK. No ad was removed or tested (E4) |
| Signing / export | **NOT RUN — BLOCKED (E3)** | No identity, no profile, no macOS toolchain |
| Physical-device install/launch | **NOT RUN — BLOCKED (E3, E5)** | No device, no signed IPA |
| Release artifact | **NOT PRODUCED** | `output/pool8Signed.ipa` and `output/pool8Signed.sha256` absent; gate enforces this |

## 8. Artifacts actually produced in this session

No release artifact. The verified deliverables are source, tooling and
documentation in this repository:

- `tools/verify_release_state.py`
- `tools/test_verify_release_state.py`
- `tools/audit_feature_matrix.py`
- `tools/test_audit_feature_matrix.py`
- `validation/ci/component-ci.release-gated.yml.txt`
- Modified: `tools/ci_provenance.py`, `validation/reports/feature-verification-matrix.md`,
  `validation/evidence/feature-string-search.json`, `MrSpicyUI/Package.swift`,
  `MrSpicyUI/Sources/MrSpicyUI/SpicyBrand.swift`,
  `validation/ci/WORKFLOW-NOT-INSTALLED.md`,
  `validation/reports/integration-validation.md`,
  `validation/reports/device-test-report.md`,
  `validation/manifests/release-manifest.json`, `output/README.md`

The pre-existing verified component artifact is unchanged and still
`NOT PRODUCED` as a release:
`validation/ci/runs/37928629998-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip`
— 1,729,023 bytes, SHA-256 `3a872657371e155a2bda05deeb73342e2e848e6ca0d99e1c484c4e651a90c5a6`,
an unsigned relocatable object, **not installable**.

## 9. Single most important next step

**Obtain owner authorization for a real integration path (E1) — buildable game
source or an official SDK with a documented presentation/settings API and
written permitted feature scope — together with a clean baseline (E2).** Nothing
else can produce `output/pool8Signed.ipa`: without an authorized host there is
nothing to integrate into, sign, install or test. Everything that does not
require that authorization is now done and gated, so the moment E1 and E2 land,
the remaining work is mechanical: source-level presentation integration, an
actual host build, authorized signing (E3), and device regression (E5).

The cheapest immediately actionable item is **E6**: a maintainer with the
`workflows` scope copies `validation/ci/component-ci.release-gated.yml.txt` to
`.github/workflows/component-ci.yml`, which lets this branch build, test and
gate itself instead of relying on fetched evidence.
