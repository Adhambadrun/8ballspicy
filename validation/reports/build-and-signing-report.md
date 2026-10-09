# Build and Signing Report — Mr. Spicy component (not game)

**Date:** 2026-10-09. **Session:** `arena/6264dd0a-8ballspicy`.
**Final independent component result: PASS. Actual game integration/signing: BLOCKED.**

## Final verified component build

- Workflow [**37928629998 — SUCCESS**](https://github.com/abadrun/8ballspicy/actions/runs/37928629998), attempt 1; source
  [`fae2937905395c425c777c38cbc05e115b2e1d71`](https://github.com/abadrun/8ballspicy/commit/fae2937905395c425c777c38cbc05e115b2e1d71). Component, hosted/repeat,
  and evidence publisher jobs all succeeded. Git evidence publication commit
  [`dbc070bba16c4d9b5deba7fed2e6e97ed0365c30`](https://github.com/abadrun/8ballspicy/commit/dbc070bba16c4d9b5deba7fed2e6e97ed0365c30) was fetched and verified locally.
- Toolchain: macOS **26.6.2 (25G83) arm64**, Xcode **26.6 (17F113)**,
  Swift **6.3.3**, iPhoneOS SDK **26.5**. Simulator **iPhone 17 Pro, iOS 26.4.1**.
  Release device target **arm64-apple-ios13.0**, `CODE_SIGNING_ALLOWED=NO`.
- Actual [unsigned component ZIP](https://github.com/abadrun/8ballspicy/blob/dbc070bba16c4d9b5deba7fed2e6e97ed0365c30/validation/ci/runs/37928629998-component/dist/MrSpicyUI-iphoneos-arm64-unsigned.zip): **1,729,023 bytes**.
  SHA-256 **`3a872657371e155a2bda05deeb73342e2e848e6ca0d99e1c484c4e651a90c5a6`**.
- Independent verification: ZIP CRC PASS; thin arm64 **MH_OBJECT**
  (relocatable `MrSpicyUI.o`, **not executable app/framework/IPA**), Swift module,
  en/ar strings and brand bundle present. Hash/size match recorded provenance;
  both jobs' checked-out SHA and source tree IDs match git. Package is not a
  signed release or stable binary-distribution SDK; use source-level integration.
- Evidence: `../evidence/component-verification-37928629998.json`,
  `../evidence/animated-repeat-37928629998.json`, `../evidence/jobs-37928629998.json`;
  raw logs/provenance/ZIP under `../ci/runs/37928629998-*/`.

| Suite | Counted cases (including skips) | Passed | Failed | Skipped |
|---|---:|---:|---:|---:|
| Hostless package | 51 | 34 | 0 | 17 |
| Hosted UIApplication demo | 51 | 51 | 0 | 0 |
| Animated duplicate-transition regression, repeated | 10 executions of one test | 10 | 0 | 0 |
| Python forensic parser fixtures | 4 | 4 | 0 | 0 |

The 17 hostless lifecycle skips explicitly require UIApplicationMain; all
17 execute in the hosted suite. Repeats are not ten distinct additional tests.
Hosted tests cover queued/reentrant close, exact-once rejected completion,
external dismissal, completion-driven close/reopen, actual Arabic mirrored
header geometry/44-point target, persisted-state reload and UIControl dispatch.
The deferred rejecting-presenter fixture is a **failure-path stub**; it is not
counted as proof of real presentation. Other lifecycle tests use real UIKit.
No animations disabled, failure tests removed, or new skip exemptions added.

**Warnings retained:** one hostless/two hosted AppIntents metadata warnings
(no AppIntents dependency), scheme/destination diagnostics, CI Node20 action
migration warnings and runner-capacity notices. No test-log `error:` entries
in this final run. Simulator warnings do not certify compatibility with every
device/iOS version. No full VoiceOver, all-size, or physical-device audit.

Apple input verification in this final run again returned **exit 1** for
modified Info.plist/signature; original before/after hashes are identical.
This does not contradict passing tests of our independent component.

The final delivery/report commit changes only documentation/evidence after
this tested source; `MrSpicyUI`, `HostApp`, tools and workflow are unchanged.

## Recovered prior evidence — independently verified

Earlier historical successful run **37916687975**, full source commit
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

## Repairs and verification scope

Continued existing code: refreshed all localized rows/accessibility labels,
explicit Arabic RTL switching, Dynamic Type-scaled text, 44-point close target,
safe-area constrained scroll card, persisted-state reload on reopen, main-thread
presentation preconditions, busy/detached/transition rejection, and localized
read-only Pro/unavailable disclosure. Added meaningful regression tests, not
skips to conceal defects. No third-party loader or gameplay logic reused.

The verified workflow uses the real GitHub `macos-latest` runner, device destination
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

## Repaired CI history (failures retained)

| Run | Source | Hostless pass / fail / skip | Hosted pass / fail / skip | Device |
|---|---|---|---|---|
| 37925407220 | `2d17a44d706d276ab4bac18dee274c2597f4b3b6` | 34 / 0 / 9 | 38 / 5 / 0 | unsigned build succeeded |
| 37926156116 | `902ec19f29fef712e9735fcf44c1dcc88b463c8f` | 34 / 0 / 10 | 43 / 1 / 0 | unsigned build succeeded |
| 37927299718 | `51f0ba1ae2b75f98cc6bc43ba9687bd2aef71dea` | 33 / 1 / 17 | 50 / 1 / 0 | skipped after hostless failure; no artifact |

All three overall runs **FAILED**; publisher success is not test success.
First failures were tests closing before presentation completion. After fixing
that synchronization, a real animated-presentation timeout remained in run
37926156116. Run37927299718 passed all 17 lifecycle tests, including queued
close, reentrant callbacks, RTL geometry, external dismissal and reopen; its
single failure in each suite was an old detached-handler expectation that
contradicted the corrected lifecycle contract. That expectation was explicitly
updated to require zero detached close events; real presented close callbacks
remain covered by hosted tests. No tests were deleted or additionally skipped.

The latest fixture waits for active UIApplication and presenter appearance,
uses XCTest predicate waits, restores the host key window and dismisses its
fixture during cleanup. It retains real animations and adds ten repeated
animated-transition checks. Earlier animation timing failure is retained as
historical evidence, not attributed conclusively to source or simulator load.

Intermediate queued runs 37926624594 / 37926754837 / 37927042105 were
cancelled by GitHub's single-pending concurrency replacement as further
review fixes arrived; they supply no build/test evidence. The running older
run was not cancelled. All source and evidence writes remain on the session
branch; no reset, force push or branch deletion used.

### Actual Apple verification of the original input

Run37926156116 `codesign --verify --deep --strict --verbose=4` returned **1**:
`invalid Info.plist (plist or signature have been modified)`.
`input-apple-verification.txt` records matching before/after SHA-256 and ZIP
CRC success. This independently corroborates stale signature seals; it is
not an attempt to sign/export/execute the game. The inspection step is green
because it successfully recorded the failure, not because the signature passed.
