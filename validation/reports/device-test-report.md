# Device Test Report — Mr. Spicy

**Date:** 2026-10-09 (UTC)
**Session:** `arena/50b0a530-8ballspicy`

## Summary

| Test level | Status | Evidence |
|---|---|---|
| Unit tests (iOS Simulator, real Xcode toolchain) | See `build-and-signing-report.md` for executed results | GitHub Actions macOS runner, `component-ci` workflow |
| UI lifecycle on UIKit presentation stack (open/close/reopen) | same as above | `SpicyOverlayLifecycleTests` |
| Install + launch on physical iOS device | **NOT RUN** | No physical iOS device is attached to or reachable from this environment (Linux analysis host; no `ios-deploy`/`libimobiledevice` device, no Apple Configurator, no device-UDID provisioning) |
| Exercise of integrated Mr. Spicy UI inside 8 Ball Pool on-device | **NOT RUN** | Integration itself is blocked — see `integration-validation.md` |
| On-device verification of signature/installability of any produced IPA | **NOT RUN** | No signed IPA can be produced (no Apple identity) and no device exists |

## Statements explicitly NOT made

- No claim of on-device installation, launch, or runtime behavior is made
  anywhere in this release set.
- Simulator test execution is **not** represented as device validation.
- Nothing in this report is inferred from the previous session's documents;
  every row above reflects this session's tooling state (commands used to
  establish "no device available": `find /` for deployment tooling, absence of
  any iOS device management binaries on the Debian analysis host).

## What would unblock device validation

1. An authorized physical iPhone/iPad with a developer-mode-enabled runtime.
2. An Apple-issued development certificate + provisioning profile covering the
   test bundle ID (for the standalone component demo) or the production App ID
   (for the integrated build).
3. `xcodebuild`/`devicectl` or `ios-deploy` access from a macOS host (or a CI
   runner with a connected device, e.g. a self-hosted runner).
