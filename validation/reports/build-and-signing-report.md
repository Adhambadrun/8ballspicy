# Build and Signing Report — Mr. Spicy component (not game)

**Date:** 2026-10-09. **Session:** `arena/6264dd0a-8ballspicy`.
**Current repaired build:** CI in progress; final results will be appended only
when logs, full run outcome, artifact bytes and provenance are verified.

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
