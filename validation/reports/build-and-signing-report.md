# Build and Signing Report — Mr. Spicy component (not game)

**Date:** 2026-10-09. **Session:** `arena/6264dd0a-8ballspicy`; results below
re-verified and appended by session `arena/627c356f-8ballspicy`.
**Current repaired build:** **COMPLETE AND GREEN** — CI run **37928629998**,
source commit `fae2937905395c425c777c38cbc05e115b2e1d71`, evidence published by
`dbc070bba16c4d9b5deba7fed2e6e97ed0365c30`. See "Current repaired build — verified
results" below.

## Current repaired build — verified results

Run **37928629998** on `abadrun/8ballspicy` / `arena/6264dd0a-8ballspicy`
completed **success**; all three jobs succeeded (`Build & test MrSpicyUI`,
`Hosted lifecycle tests (UIApplication host)`, `Publish auditable evidence on
session branch`). Status file records `test_status=0`, `device_status=0`,
`arch_status=0`, `hosted_status=0`, `animated_repeat_status=0`.

Counts below were re-read from the raw `xcodebuild` logs by this session, not
copied from a summary:

| Suite | Executed | Passed | Failed | Skipped | Result |
|---|---:|---:|---:|---:|---|
| Hostless Swift package | 51 | 34 | 0 | 17 | TEST SUCCEEDED |
| Hosted UIApplication demo | 51 | 51 | 0 | 0 | TEST SUCCEEDED |
| Animated-transition repeat (hosted) | 10 | 10 | 0 | 0 | TEST SUCCEEDED |

The suite grew from 33 to 51 tests during the repair, and the 17 hostless skips
are the modal-presentation tests that require `UIApplicationMain`; every one of
them executes for real in the hosted suite (51/51, 0 skipped). Skips are
reported by XCTest with reasons and are not counted as passes.

Component artifact for this run, downloaded and re-hashed independently:

| Run | Component ZIP SHA-256 | Size | Recomputed here |
|---|---|---:|---|
| 37915278092 | `1a57bab96031dc78abde5eec594eb8ca9f1121ebc47819a67cd2ed7df97c034d` | 1,712,887 | match |
| 37916599818 | `1b2d4b176dbf8ec7da55e54cd9885bd332fe4e7485240f91a9fc5bcd7d7b0c68` | 1,712,888 | match |
| 37916687975 | `2d34b9d00c8f3aad00ffcf5ec0419a42bf16a8d02ba4c8b702966ba8b3399b2c` | 1,712,890 | match |
| **37928629998** | **`3a872657371e155a2bda05deeb73342e2e848e6ca0d99e1c484c4e651a90c5a6`** | **1,729,023** | **match** |

**`3a872657371e155a2bda05deeb73342e2e848e6ca0d99e1c484c4e651a90c5a6` is the
current authoritative component artifact**, at
`validation/ci/runs/37928629998-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip`.
The three earlier hashes remain valid for their own runs; the older values cited
elsewhere in this repository are superseded, not wrong.

### Regression history (truthful, including the failures)

| Run | Source | Hosted result | Note |
|---|---|---|---|
| 37916687975 | `114b9ae` | 33/33 pass | last green before the hardening work |
| 37925407220 | `2d17a44` | **43 executed, 8 FAILED** | hardening regressed dismissal: "overlay did not close" in `SpicyOverlayLifecycleTests` |
| 37926156116 | `902ec19` | failure | |
| 37926624594 / 37926754837 / 37927042105 | `ee0c082`…`d3c4e8b` | cancelled | superseded by newer pushes |
| 37927299718 | `51f0ba1` | **51 executed, 1 FAILED** | lifecycle fixed; residual hostless failure in `SpicyOverlayControlTests.testCloseButtonNotifiesBridgeThenRequestsClose` (expected 1 bridge close request, got 0) |
| **37928629998** | **`fae2937`** | **51/51 pass** | **green** |

**Test-integrity check on the 1→0 expectation change.** Commit `fae2937`
renamed that hostless test to `testDetachedCloseHandlerDoesNotNotifyBridge` and
changed its expectation from 1 to 0. This session verified the change is a
legitimate re-scoping and **not** green-washing:

* `git show fae2937 -- MrSpicyUI/Sources/` is **empty** — no component source
  was altered to satisfy the test.
* The suite is hostless: the overlay is never presented, so a close tap cannot
  represent a real user close request, and notifying the host would be spurious.
* The real requirement is asserted in the hosted suite, where a genuine
  `UIApplicationMain` presentation exists: `testCloseButtonNotifiesBridgeAndCloses`
  (bridge notified **and** overlay dismissed), `testUserCloseDuringOpeningIsQueuedOnceAndAllowsReopen`,
  `testReentrantBridgeCloseRequestIsDeduplicatedWhileOpening`,
  `testReentrantCloseBridgeWhileOpenFiresOncePerCycle` (1 per cycle, then 2 after
  re-presentation — "must re-arm the user-close event"), and
  `testDetachedCloseButtonDoesNotNotifyBridge`.
* Net coverage **increased** (33 → 51 tests, plus a 10-test animated repeat).

### Apple tooling verification of the immutable input (from the same run)

Job step "Inspect immutable input with Apple tooling (no execution)" ran
`tools/inspect_ipa_apple.sh` on the macOS runner. Evidence:
`validation/ci/runs/37928629998-component/input-apple-verification.txt`.

* `input_sha256_before` = `input_sha256_after` =
  `6b4dfd3bd63a1ee5e649d98c44077e5d48f8a013255082287bef4514f6abdc84` — the input
  survived CI **byte-identical**.
* `unzip -tq`: "No errors detected in compressed data".
* `lipo -archs`: `arm64`. `otool -hv`: `MH_MAGIC_64 ARM64 … EXECUTE ncmds=125`.
* **`codesign --verify --deep --strict --verbose=4` → exit 1**:
  `Payload/pool.app: invalid Info.plist (plist or signature have been modified)`.

This is Apple's own verification, and it confirms the input's signature is
**invalid**. The failure mode (modified `Info.plist`) is consistent with the
`DecryptedBy = "@FastDecryptBot - https://t.me/FastDecryptBot"` key that this
session found injected into `Payload/pool.app/Info.plist`, which breaks the
resource seal. It validates the *original input's* signature state only — it is
**not** release signing, and it signs nothing.

## Recovered prior evidence — independently verified

Latest prior successful run **37916687975**, full source commit
`114b9aedfb04f34651afb1c14cde636612347bc3`, was examined via GitHub jobs API
and fetched git evidence `ci/artifacts` tip
`a1da653f942be70df30f578a75b78d1a9f53349a`.

| Suite | XCTest executed (includes skips) | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|
| Hostless Swift package | 33 | 28 | 0 | 5 |
| Hosted UIApplication demo | 33 | 33 | 0 | 0 |

Five lifecycle tests explicitly skipped without UIApplicationMain. Hosted
`sendActions` and modal tests executed. Logs show **TEST SUCCEEDED** and
**BUILD SUCCEEDED**. Nonfatal AppIntents metadata warnings and empty supported
scheme destination diagnostics were present; no component test failures.

Recovered artifacts independently CRC-tested and hashed:

| Run | Component ZIP SHA-256 |
|---|---|
| 37915278092 | `1a57bab96031dc78abde5eec594eb8ca9f1121ebc47819a67cd2ed7df97c034d` |
| 37916687975 | `2d34b9d00c8f3aad00ffcf5ec0419a42bf16a8d02ba4c8b702966ba8b3399b2c` |

They are historical **unsigned component** artifacts, not the current repaired
source or installable apps. Sources `MrSpicyUI`/`HostApp` matched the prior
verified build revision before repairs. Direct log download failed with EOF
at the unavailable Actions results-receiver host; git-published logs worked.

## Current changes and verification scope

Continued existing code: refreshed all localized rows/accessibility labels,
explicit Arabic RTL switching, Dynamic Type-scaled text, 44-point close target,
safe-area constrained scroll card, persisted-state reload on reopen, main-thread
presentation preconditions, busy/detached/transition rejection, and localized
read-only Pro/unavailable disclosure. Added meaningful regression tests, not
skips to conceal defects. No third-party loader or gameplay logic reused.

Current workflow uses the real GitHub `macos-latest` runner, device destination
`generic/platform=iOS`, Release, minimum target iOS 13.0 and
**CODE_SIGNING_ALLOWED=NO**. Provenance records full checked-out SHA, source
Git tree IDs, run/attempt, toolchain, SDK and archive hash. One publisher writes
only the session branch and does not mask git push failures. Small component
package/log evidence is deliberately retained there; game bytes are not
published as an artifact. Four forensic parser unit tests also run in CI.

## Signing / export — BLOCKED

No host integration build/archive/export or Apple signing performed.
Local environment is Linux x86_64 with no Xcode/codesign/Swift SDK. macOS CI
can compile/test components and statically verify the input signature; that is
not a signing credential or successful installable build. No local certificate
or provisioning profile found. Repository secret metadata request returned
403; remote signing secrets are **unknown**, not established nonexistent.

Final `output/pool8Signed.ipa` and `output/pool8Signed.sha256` are **NOT PRODUCED**.
No placeholder, renamed demo, unsigned ZIP mislabeled IPA or release uploaded.
