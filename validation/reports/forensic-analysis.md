# Forensic Analysis — `pool8Signed.ipa`

**Date:** 2026-10-09 (UTC)
**Analyst:** Arena.ai autonomous engineering agent (session `arena/50b0a530-8ballspicy`)
**Method:** Static inspection only. All conclusions below are backed by command output produced in this session on a Debian 12 (x86_64) analysis host. No Apple-proprietary tooling (`codesign`, `otool`, `plutil`, `dwarfdump`) exists on this host; equivalents used: `unzip`, `python3` 3.11 (`plistlib`, `zipfile`), `lief` 1.0.0 (Mach-O parsing), `sha256sum`/`md5sum`, `od`, `strings`. The input file was treated as immutable evidence; all experiments ran on a copy extracted under `/home/user/work/`.

---

## 1. Input identity

| Property | Value | Evidence |
|---|---|---|
| Path | `/home/user/8ballspicy/pool8Signed.ipa` | workspace inventory |
| Size | 99,010,014 bytes | `ls -la` |
| SHA-256 | `6b4dfd3bd63a1ee5e649d98c44077e5d48f8a013255082287bef4514f6abdc84` | `sha256sum` |
| MD5 | `3bfa71c416ba3fc8ac6e167aee974d98` | `md5sum` |
| Format | Valid ZIP archive (3,527 entries, `zipfile.testzip()` → `None`, top-level `Payload/`) | `python3 -m zipfile` / `zipfile` |
| App bundle | `Payload/pool.app/` (3,366 files) | extraction inventory |

A second historical IPA exists only as a deleted git object in this repository's history (commit `f926d36`, removed in `5ab43b4`): `8-ball-pool-i3rby-IPAOMTK.COM.ipa`, blob `6011d5cd…`, SHA-256 `59607b4177f8ffdf36649d9bb3b0c5900d39f5b6b3eaa0c6e351ba353a58c2f8`. It is **not** the input for this mission and was not used.

**Important:** the supplied filename (`pool8Signed.ipa`, "signed") is not evidence of an intact, verifiable signature — see §4.

## 2. Application identity (from `Info.plist`, hash `d5de79bd…`)

| Key | Value |
|---|---|
| CFBundleDisplayName / CFBundleName | `8 Ball Pool` |
| CFBundleIdentifier | `com.miniclip.8ballpoolmult` |
| CFBundleExecutable | `pool` |
| CFBundleShortVersionString / CFBundleVersion | `56.31.0` / `5330` |
| MinimumOSVersion | `13.0` |
| UIDeviceFamily | iPhone + iPad |
| Orientation | Landscape Left/Right only, `UIRequiresFullScreen` |
| Build toolchain | Xcode 26.2 (`DTXcode` 2620, `DTXcodeBuild` 17C52), SDK `iphoneos26.2` |
| App Store app-id | `543186831` (`AppID`/`VungleAppID`) |
| Provenance marker | `DecryptedBy = "@FastDecryptBot - https://t.me/FastDecryptBot"` |

**Interpretation (confidence: high):** this is Miniclip's *8 Ball Pool* iOS application, an App Store build (56.31.0 / build 5330) that was FairPlay-decrypted by a third-party dump service. The `DecryptedBy` Info.plist key is a well-known decryption-service watermark; `SC_Info/` contains only a `.keep` placeholder (FairPlay metadata stripped).

## 3. Binary & architecture (Mach-O analysis via `lief`)

Main executable `Payload/pool.app/pool` (SHA-256 `4654de9a…`):

- Single-slice Mach-O 64-bit, `CPU_TYPE.ARM64` (little-endian magic `cf fa ed fe`), `MH_EXECUTE`, 125 load commands, flags `0xa18085` (PIE, MH_TWOLEVEL, MH_NO_HEAP_EXECUTION bits among them).
- `LC_BUILD_VERSION`: platform iOS, **min OS 13.0.0**, SDK 26.2.0, linked with `LD 1230.1.0`.
- `LC_ENCRYPTION_INFO_64`: `crypt_id = 0` → the `__TEXT` segment is **not encrypted** (consistent with a decrypted dump). cryptoff 237568 / cryptsize 4096.
- `LC_UUID` / uuid: `c235dccd-997e-3d31-a98f-eaa8bddd2bfb`.
- Symbol table: 4,222 named symbols retained (partial symbols survive, e.g. `mcwebsocketpp` C++ networking symbols, `mc::crashlytics` globals, `FBLink_*` shims). Not fully stripped; **no dSYM / DWARF** was found in the bundle (`dwarfdump` unavailable on host, but no `.dSYM`/debug companion exists in the archive).
- Exported symbols: 30 (mostly `FBLink_*`, `mcwebsocketpp` internals). Imported symbols: 4,191 (Swift stdlib/Foundation mangled names dominate → substantial Swift component alongside C++ game core).
- Rpaths: `/usr/lib/swift`, `@executable_path/Frameworks`.

**All embedded binaries (main app, 4 app extensions, 25 framework binaries, 1 Swift dylib) are single-architecture ARM64 with `crypt_id = 0`.** No simulator slices. No fat binaries.

## 4. Code signature & entitlements

`LC_CODE_SIGNATURE` at file offset 79,904,240, size 2,092,768. SuperBlob `0xfade0cc0` with 6 slots:

| Slot type | Blob magic | Notes |
|---|---|---|
| 0x0 CodeDirectory | `0xfade0c02` (797,394 B) | SHA-1 (hashType 1) CD, v2.5, 19,928 code slots, codeLimit 81,623,008, identifier `com.miniclip.8ballpoolmult`, flags `0x10000` (CS_RUNTIME / hardened runtime) |
| 0x2 | `0xfade0c01` (108 B) | small blob containing the identifier string |
| 0x5 | `0xfade7171` (953 B) | blob containing the entitlements XML (see below) |
| 0x7 | `0xfade7172` (501 B) | embedded entitlements blob |
| 0x1000 | `0xfade0c02` (1,275,750 B) | second (SHA-256-class) CodeDirectory, matching modern dual-CD layout |
| 0x10000 | `0xfade0b01` (4,392 B) | CMS wrapper (certificate chain / signature) |

CodeDirectory special slots (SHA-1): Info.plist `85760279…`, Requirements `d7e90ffc…`, ResourceDir `74d9d0f6…`, Entitlements `94fc2873…`, EntitlementsDER `ace68336…`; Application and slot −6 are zero-filled.

**Entitlements recovered from the signature blob:**

```
com.apple.developer.declared-age-range      = true
com.apple.developer.team-identifier         = HLSX4DMBX6
application-identifier                     = HLSX4DMBX6.com.miniclip.8ballpoolmult
com.apple.developer.applesignin             = [Default]
aps-environment                             = production
com.apple.developer.game-center             = true
com.apple.developer.associated-domains      = [applinks:8bp.co, applinks:poolbyminiclip.com, applinks:miniclip8ballpool.onelink.me]
com.apple.security.application-groups       = [group.com.miniclip.8ballpoolmult]
```

- **Signing identity:** Apple-issued identity of **Miniclip (team `HLSX4DMBX6`)**. `codesign -vv`-style verification is **NOT AVAILABLE** on this Linux host (no `codesign` binary exists on Linux), so cryptographic validation of the CMS chain and per-page hashes was not re-executed here — *structural* presence and internal consistency were verified only.
- **No `embedded.mobileprovision`** is present in the bundle (App Store distribution layout).
- The CMS blob is small (4,392 B) and the Info.plist carries a decryption watermark; combined with `crypt_id = 0`, the file is best described as a **decrypted App Store package with retained (original) signature structures**. Treat the filename claim "Signed" as **unverified** for installation purposes.

## 5. Dependency inventory

### 5.1 Embedded frameworks (25) + 1 dylib

Ad/analytics stack: `AdSurgeSDK` (com.AdSurge.ADN 1.0), `AppLovinSDK` 13.6.3, `BigoADS` 5.2.1, `DTBiOSSDK` (Amazon), `FBAudienceNetwork`, `InMobiSDK` 11.3.0, `MolocoSDK` 4.7.0, `OMSDK_Appodeal` 1.6.
Analytics/infra: `FirebaseAnalytics/Core/CoreExtension/CoreInternal/Crashlytics/Installations/RemoteConfigInterop/Sessions` 11.15.0, `GoogleAppMeasurement(-IdentitySupport)`, `GoogleAdsOnDeviceConversion` 2.1.0, `GoogleDataTransport` 10.1.0, `GoogleUtilities` 8.1.0, `Promises`/`FBLPromises` 2.4.0, `nanopb` 3.30910.0.
Security/hardening: **`libloader` (`com.appdome.libloader` 1.0.0)** — Appdome-secured loader (Appdome is a commercial app-hardening/threat-shielding platform). This is loaded via `@executable_path/Frameworks/libloader.framework/libloader`.
Swift: `libswift_Concurrency.dylib` (embedded back-deployed).

### 5.2 System linkage (excerpt)

`libz, libresolv, libc++, libc++abi, libbz2, libsqlite3, libxml2, libcompression, libobjc, libSystem`; frameworks incl. `UIKit, SwiftUI (weak), Foundation (weak), CoreFoundation (weak), Metal/MetalKit, GLKit, OpenGLES, GameKit, StoreKit, AVFoundation/AVKit, WebKit (weak), JavaScriptCore (weak), AuthenticationServices (weak), AppTrackingTransparency (weak), AdSupport, AdServices (weak), AdAttributionKit (weak), MarketplaceKit (weak), WidgetKit (weak), CryptoKit, Security, CoreData, CoreMotion, …`. Six in-tree ad SDKs are loaded via `@rpath` (`AdSurgeSDK, AppLovinSDK, InMobiSDK, FBAudienceNetwork, DTBiOSSDK, MolocoSDK`).

### 5.3 App extensions (4)

| Extension | Bundle id | Min OS |
|---|---|---|
| `NotificationContent.appex` | `com.miniclip.8ballpoolmult.notificationContent` | 13.0 |
| `NotificationService.appex` | `com.miniclip.8ballpoolmult.notificationService` | 13.0 |
| `PoolWidgetExtension.appex` | `com.miniclip.8ballpoolmult.poolWidget` | 14.0 |
| `PooliMessage.appex` | `com.miniclip.8ballpoolmult.PooliMessage` | 13.0 |

### 5.4 Resources

17 localizations (`ar, de, eng, es, fr, hi, id, it, ja, ko, kor, pt, pt-BR, pt-PT, ru, tr, vi` .lproj), 696 CocosBuilder `.ccbi` scene files, 742 property lists, 1,220 PNGs at app root (plus nested resources), `checksums/` (6 Miniclip asset-checksum plists), and a directory `j1O1pP4cpnaLPxs2xoSf/` containing 18 opaque blobs (all share magic `e1 1c ff 10 …` — an unidentified private format; hypothesis (confidence: medium): Appdome-protected or Miniclip-encrypted configuration/bundle data; **not executed or decrypted**).

## 6. What is confirmed vs. hypothesis

**Confirmed by direct evidence (static):**
- Bundle identity, version, architectures, min-iOS, dependency graph, extension set, entitlements text, signature-blob structure, decryption markers (`DecryptedBy`, `crypt_id=0`, `SC_Info` stripped).

**Hypotheses (not confirmed):**
- The CMS signature would validate under Apple's trust chain on-device (cannot verify without `codesign`/iOS).
- `j1O1pP4cpnaLPxs2xoSf` blob purpose (Appdome/Miniclip private format).
- Behavior at runtime (nothing in this report is execution-confirmed; this analysis host cannot run iOS binaries).

**Explicitly out of scope per mission constraints:** no DRM/FairPlay bypass work, no anti-cheat/anti-tamper defeat (Appdome), no binary patching of the game, no paid-entitlement or monetization manipulation, no competitive-gameplay modification. The Appdome-protected, third-party-owned binary is treated as immutable evidence only.

## 7. Host-source discovery (COMMAND 04 outcome)

- This repository's entire 4-commit history contains **no** `.xcodeproj`, `.xcworkspace`, `project.pbxproj`, Swift/ObjC source, entitlements, or host SDK — only two IPA blobs and `.gitattributes`.
- No `ExistingIPAWorkspace/OverlaySource/` exists anywhere in the repository, its history, or the local filesystem (searched `/` for `*Overlay*`, `*Spicy*`, `*.swift`, `*.xcodeproj`, `project.pbxproj`, `*.xcarchive` — zero hits outside the repo metadata).
- Sibling public repositories under the same account (`abadrun/8ball` … `abadrun/8ball7`) were observed early in this session via the GitHub API and contained extensive prior *Mr. Spicy* work (SwiftUI/UIKit `mr-spicy-ui` packages, a `MRSpicy.xcodeproj` demo app, branding assets, tooling, and release documentation). During this session those repositories were **deleted or made private**; every subsequent fetch attempt (git clone, `git ls-remote`, `codeload.github.com`, `raw.githubusercontent.com`, REST API) returns 404. Only file listings observed in this session survive as evidence; **no content was recovered**. The referenced device-component checksum `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b` matches no reachable artifact (searched local workspace, git object store, GitHub code search) and **could not be verified**.
- **The production host application is Miniclip's closed-source *8 Ball Pool*.** No owner-authorized source, overlay SDK, or documented integration interface exists in any reachable project artifact. Integration of the Mr. Spicy UI into the host therefore requires external authorization/source that this workspace does not contain.

## 8. Bottom line

`pool8Signed.ipa` is a decrypted (FairPlay-removed) ARM64 App Store build of *8 Ball Pool* 56.31.0 (5330) with original Miniclip team identity `HLSX4DMBX6`, Appdome hardening (`libloader`), 25 embedded third-party frameworks, and 4 extensions. It is suitable as *evidence and integration-target reference*; it is **not** a legitimate base for a re-signed release without Miniclip authorization and an Apple signing identity, and it must not be binary-patched (third-party protected game, mission constraints).
