# Build & Signing Report — Mr. Spicy component

**Date:** 2026-10-09 (UTC)
**Session:** `arena/50b0a530-8ballspicy`
**Scope:** Build/test of the `MrSpicyUI` component. The 8 Ball Pool host
application is NOT built, modified, or re-signed (see
`integration-validation.md`).

---

## 1. Toolchain environments used

### 1.1 Analysis host (session sandbox)

| Property | Value |
|---|---|
| OS | Debian GNU/Linux 12 (x86_64) |
| Xcode / Swift / iOS SDK | **NOT AVAILABLE** (Linux; no Apple toolchain exists for this platform) |
| `codesign`/`otool`/`lipo`/`plutil`/`dwarfdump` | **NOT AVAILABLE** |
| Equivalent tooling used for static analysis | Python 3.11 + `plistlib`, `lief` 1.0.0 (Mach-O), `unzip`, `sha256sum`, `strings` |

Conclusion: no local iOS compilation, signing, or export can occur on the
analysis host. Any "build" claim from this host alone would be false.

### 1.2 GitHub Actions macOS runner (real Apple toolchain)

Executed via `.github/workflows/component-ci.yml` on
https://github.com/abadrun/8ballspicy/actions (run IDs listed in §5; raw logs
and products archived on the repository's `ci/artifacts` branch under
`runs/<run-id>-<job>/`). Runner toolchain (from `toolchain.txt`):

```
ProductName:     macOS
ProductVersion:  26.6.2
BuildVersion:    25G83
Xcode 26.6
Build version 17F113
Apple Swift version 6.3.3 (swiftlang-6.3.3.1.3 clang-2100.1.1.101)
Target: arm64-apple-macosx26.0
```

Build SDK for device products: **iPhoneOS26.5.sdk**, deployment target
**iOS 13.0**, target triple **arm64-apple-ios13.0**.

## 2. Unit tests (iOS Simulator, `xcodebuild test`)

Test sources: `MrSpicyUI/Tests/MrSpicyUITests/` — 33 tests across
`SpicyPreferencesTests`, `SpicyLocalizationTests`, `SpicyThemeTests`,
`SpicyOverlayControlTests`, `SpicyOverlayLifecycleTests`. Coverage: factory
defaults, persistence across instances, persisted reset, snapshot
completeness, haptic intensity round trip, en/ar key-set parity, RTL
detection, language normalization, unknown-key fallback, theme invariants,
brand resource presence, control→handler wiring for every UI control,
handler behavior (persistence + bridge notification + UI reload), close
button → bridge callback, accessibility identifiers/labels, RTL layout
attribute, version label, and the modal open → close → reopen lifecycle.

### 2.1 Package suite (hostless `xctest` runner)

Command: `xcodebuild test -scheme MrSpicyUI -destination 'platform=iOS Simulator,name=iPhone 17 Pro'`

**Result: PASSED** — `Executed 33 tests, with 5 tests skipped and 0 failures`.

The 5 skipped tests are exactly the modal-presentation/control-dispatch
group (`SpicyOverlayLifecycleTests`). Hostless `xctest` has no
`UIApplicationMain`; UIKit itself reports *"UIApp is nil which means we cannot
dispatch control actions to their targets"*. Each skip logs that reason
(evidence: `runs/37914185839-component/xcodebuild-test.log`). They are **not**
reported as passes. Equivalent functionality is executed for real by the
hosted suite (§2.2).

### 2.2 Hosted suite (real UIApplicationMain via `HostApp/MrSpicyDemoHost`)

Command: `xcodebuild test -project HostApp/MrSpicyDemoHost.xcodeproj -scheme MrSpicyDemoHost -destination 'platform=iOS Simulator,name=<sim>'`

**Result: PASSED** — `Executed 33 tests, with 0 failures (0 unexpected)`
(evidence: `runs/37914185839-hosted-tests/xcodebuild-hosted.log`).

This run includes, on a live UIKit presentation stack inside a real app:

| Verified behavior | Test |
|---|---|
| open → close → **reopen** on one instance | `testOpenCloseReopenCycle` |
| open is idempotent (already-open open keeps interface on screen) | `testOpenIsIdempotent` |
| close button dispatch (`sendActions`) → bridge callback → dismissal | `testCloseButtonNotifiesBridgeAndCloses` |
| `sendActions` control dispatch → `UserDefaults` persistence + bridge | `testControlDispatchViaSendActionsReachesPersistenceAndBridge` |
| close is idempotent | `testCloseIsIdempotent` |

## 3. Device-architecture build (generic/platform=iOS, arm64)

Command: `xcodebuild build -scheme MrSpicyUI -configuration Release -destination 'generic/platform=iOS' -derivedDataPath build-device CODE_SIGNING_ALLOWED=NO`

**Result: `** BUILD SUCCEEDED **`** (evidence:
`runs/37914185839-component/xcodebuild-device.log`).

Produced products (Release-iphoneos):

| Product | Verification |
|---|---|
| `MrSpicyUI.o` (static link unit, `-target arm64-apple-ios13.0`) | `lipo -archs` → **arm64** (recorded in `products.txt`) |
| `MrSpicyUI.swiftmodule/arm64-apple-ios.swiftmodule` (+`.swiftdoc`, `.abi.json`, swiftsourceinfo) | arm64-apple-ios module interface |
| `MrSpicyUI_MrSpicyUI.bundle/` (`spicy-s-mark.png`, `Info.plist`) | component resources |

This is a genuine iphoneos-SDK build targeting physical arm64 devices —
**not** a simulator-only build. It is a **library component**, not an
application archive; it is unsigned (`CODE_SIGNING_ALLOWED=NO`) and is not
claimed installable.

## 4. Signing

| Requirement | Status | Evidence |
|---|---|---|
| Apple-issued signing identity (distribution or development) | **NOT AVAILABLE** | No keychain/certificates exist on any host in this session; GitHub-hosted runners have none (builds run `CODE_SIGNING_ALLOWED=NO`) |
| Provisioning profile for target bundle ID | **NOT AVAILABLE** | None present in the workspace or reachable repos |
| Owner-authorized entitlements for `com.miniclip.8ballpoolmult` | **NOT AVAILABLE** | Entitlements belong to Miniclip team `HLSX4DMBX6` |
| Legitimate export (`xcodebuild -exportArchive`) of an installable IPA | **NOT RUN** | Requires all of the above |

Per mission rules, no other developer's signing keys are used, the original
developer's signature is not reproduced or faked, and no unsigned/ad-hoc
product is presented as an installable release. `output/Mr Spicy.ipa` and
`output/Mr Spicy.sha256` are therefore **intentionally absent** (see
`release-manifest.json` for machine-readable status).

## 5. What WAS produced (honest inventory)

**Final CI run:** `37915278092` — both jobs green
(`Build & test MrSpicyUI` 2m19s, `Hosted lifecycle tests` 5m3s):
https://github.com/abadrun/8ballspicy/actions/runs/37915278092

| Artifact | SHA-256 / size | Where |
|---|---|---|
| `MrSpicyUI-iphoneos-arm64-unsigned.zip` (device build: `MrSpicyUI.o`, `MrSpicyUI.swiftmodule/`, `MrSpicyUI_MrSpicyUI.bundle/`) | `1a57bab96031dc78abde5eec594eb8ca9f1121ebc47819a67cd2ed7df97c034d`, 1,712,887 bytes | repository branch `ci/artifacts`, `runs/37915278092-component/dist/` |
| `MrSpicyUI-iphoneos-arm64-unsigned.sha256` | checksum manifest produced on the runner with `shasum -a 256` | same directory |
| `xcodebuild-test.log`, `xcodebuild-device.log`, `xcodebuild-hosted.log`, `toolchain.txt`, `products.txt`, `test-status.txt` | run logs | `runs/37915278092-component/`, `runs/37915278092-hosted-tests/` |

Independent verification on the analysis host (not trusting the runner):
`sha256sum` of the retrieved zip matches the runner-produced checksum
(`1a57bab9…c034d`), and `MrSpicyUI.o` inside the archive parses as Mach-O
64-bit `CPU_TYPE_ARM64` (magic `cf fa ed fe`, cputype `0x0100000c`).

**Deliberately NOT produced:** `output/Mr Spicy.ipa`, `output/Mr Spicy.sha256`
— the mission defines these as the *integrated, signed* game release; neither
authorized host source nor signing material exists (§4), so creating anything
at those paths would be a placeholder/fake release (prohibited).

## 6. Verdict

The Mr. Spicy component is **built and tested on a real Apple toolchain**
(package tests, hosted lifecycle tests in a UIApplication host, and an
arm64/iphoneos device build — all green). **Release signing and export are
blocked** on the absence of any Apple-issued identity, and the mission's
release IPA (the integrated game) additionally requires authorized host
source. Status recorded in `release-manifest.json`.
