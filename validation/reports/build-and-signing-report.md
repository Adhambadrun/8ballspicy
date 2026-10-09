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

Executed via the repository workflow `.github/workflows/component-ci.yml`
(run history: https://github.com/abadrun/8ballspicy/actions). Runner log
recorded by CI on the `ci/artifacts` branch (`runs/<run-id>/toolchain.txt`):

<!-- TOOLCHAIN-BLOCK -->

## 2. Unit tests (iOS Simulator, `xcodebuild test`)

Command executed by CI:

```
xcodebuild test -scheme MrSpicyUI \
  -destination "platform=iOS Simulator,name=<auto-selected iPhone simulator>" \
  -resultBundlePath MrSpicyUI-tests.xcresult
```

Test sources: `MrSpicyUI/Tests/MrSpicyUITests/`
(`SpicyPreferencesTests`, `SpicyLocalizationTests`, `SpicyThemeTests`,
`SpicyOverlayLifecycleTests`) covering: factory defaults, persistence across
instances, persisted reset, snapshot completeness, haptic intensity round
trip, en/ar key-set parity, RTL detection, language normalization, unknown-key
fallback, theme invariants, brand resource presence, open→close→reopen
lifecycle on a real UIKit presentation stack, idempotent open/close, close
button → host-bridge callback, settings write-through to `UserDefaults` +
bridge notification, haptic-intensity enable/disable coupling, reset restoring
model and UI, accessibility identifiers/labels, RTL layout attribute,
version label.

<!-- TEST-BLOCK -->

## 3. Device-architecture build (generic/platform=iOS, arm64)

Command executed by CI:

```
xcodebuild build -scheme MrSpicyUI -configuration Release \
  -destination 'generic/platform=iOS' -derivedDataPath build-device \
  CODE_SIGNING_ALLOWED=NO
```

This is a genuine iphoneos-SDK build targeting arm64 devices (NOT a
simulator-only build). Architectures verified on the runner with
`lipo -archs` over every produced Mach-O.

<!-- DEVICE-BLOCK -->

## 4. Signing

| Requirement | Status | Evidence |
|---|---|---|
| Apple-issued signing identity (distribution or development) | **NOT AVAILABLE** | No keychain/certificates exist on any host in this session; the GitHub-hosted runner has none either (builds run with `CODE_SIGNING_ALLOWED=NO`) |
| Provisioning profile for target bundle ID | **NOT AVAILABLE** | None present in the workspace or reachable repos |
| Owner-authorized entitlements for `com.miniclip.8ballpoolmult` | **NOT AVAILABLE** | Entitlements belong to Miniclip team `HLSX4DMBX6` |
| Legitimate export (`xcodebuild -exportArchive`) of an installable IPA | **NOT RUN** | Requires all of the above |

Per mission rules, no other developer's signing keys are used, the original
developer's signature is not reproduced or faked, and no unsigned/ad-hoc
product is presented as an installable release. `output/Mr Spicy.ipa` and
`output/Mr Spicy.sha256` are therefore **intentionally absent** (see
`release-manifest.json` for machine-readable status).

## 5. What WAS produced (honest inventory)

<!-- ARTIFACT-BLOCK -->

## 6. Verdict

The component is built and tested on a real Apple toolchain; **signing and
release export are blocked** on the absence of any Apple-issued identity and
on the absence of authorized host source (the release IPA in the mission is
defined as the integrated game). Status recorded in
`release-manifest.json`.
