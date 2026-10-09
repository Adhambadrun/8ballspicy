# Forensic Analysis — `pool8Signed.ipa`

**Date (UTC):** 2026-10-09T08:57Z
**Analyst environment:** Debian GNU/Linux 12 (x86_64), Python 3.11, git 2.x, `gh` CLI. **No macOS, Xcode, iOS SDK, `codesign`, `otool`, `lipo`, `plutil`, or Apple tooling is present.** All binary/plist/ZIP analysis below was performed with Python (`zipfile`, `plistlib`, `hashlib`, `struct`) directly against the archive — every claim cites reproducible command output.

---

## 1. Executive summary

The input artifact `pool8Signed.ipa` is **not an original, legitimately signed build**. It is a **decrypted, signature-stripped, provisioning-stripped, mod-injected repackaging of Miniclip's commercial game "8 Ball Pool"** (`com.miniclip.8ballpoolmult`, v56.31.0 / build 5330). The injected component (`libloader.framework`, 12.27 MB) contains a **third-party cheat "mod menu"** (aim-assist, auto-break/auto-queue automation, `com.i3rby.8poolmod.*` identifiers, PRO-key/Telegram-based paid activation), matching the archive's git-history provenance filename `8-ball-pool-i3rby-IPAOMTK.COM.ipa` (IPAOMTK.COM is a distributor of modified/pirated IPAs).

Despite the filename, the bundle is **currently unsigned and uninstallable as-is**: the main executable and the injected dylib have **no `LC_CODE_SIGNATURE`**, no `embedded.mobileprovision` exists anywhere in the archive, the `SC_Info` FairPlay artifacts referenced by the code seal are **missing (61 files)**, and spot-checked `CodeResources` seals **fail** for the modified binaries.

**Consequence for the mission:** there is no authorized host source, no authorized integration interface, and no legitimate signing path for this artifact (details in §7–§8). The requested deliverable — a further-modified, re-signed, redistributable "Mr Spicy.ipa" built on this input — cannot be produced legitimately, and was **not** produced. See `build-and-signing-report.md`, `integration-validation.md`, and `release-manifest.json`.

---

## 2. Workspace & repository inventory (COMMAND 01)

### 2.1 Local checkout
```
repo root:   /home/user/8ballspicy
branch:      arena/f4b84726-8ballspicy (from main @ 5ab43b4)
remote:      origin -> https://github.com/Adhambadrun/8ballspicy.git
git status:  clean at analysis start
tracked:     .DS_Store, .gitattributes, pool8Signed.ipa   (3 files, nothing else, ever)
```

### 2.2 Full git history (all refs, both known remotes)
`Adhambadrun/8ballspicy` (this checkout; created 2026-10-09T08:50:44Z, **archived**, 1 commit, 0 PRs, 0 releases, 0 Actions runs, single branch `main`).
`abadrun/8ballspicy` (repo named in the mission; created 2026-10-09T08:29:57Z, 4 commits, same single branch):

| commit | content |
|---|---|
| `51ad41da8` Initial commit | `.gitattributes` only |
| `f926d3643` Create 8-ball-pool-i3rby-IPAOMTK.COM.ipa | adds `8-ball-pool-i3rby-IPAOMTK.COM.ipa` (98,576,945 B) |
| `7c16c8e37` co | adds `pool8Signed.ipa` (99,010,014 B) + `.DS_Store` |
| `5ab43b4d4` Delete …IPAOMTK.COM.ipa | removes the IPAOMTK-named file (current HEAD) |

**Negative results (searched, not assumed):**
- `ExistingIPAWorkspace/OverlaySource/` — **does not exist** in any commit of any branch of either repository, nor anywhere on the local filesystem (`find / -xdev` for `*OverlaySource*`, `*ExistingIPAWorkspace*`: no hits).
- No `.xcodeproj`, `.xcworkspace`, `project.pbxproj`, Swift/ObjC sources, `Package.swift`, entitlements, archives, or build logs exist in any accessible history.
- No `.mobileprovision`, no `.p12`/certificates anywhere on the filesystem.
- No other IPA files exist on the machine (filesystem-wide search: only `/home/user/8ballspicy/pool8Signed.ipa`).
- The reference device-component checksum `c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b` matches **nothing** present or historical in this project; it is unverifiable here.
- No GitHub Actions workflows exist (Actions runs: `total_count: 0`), so no runner-based macOS recovery path exists via this repository.

---

## 3. Input integrity (COMMAND 02)

```
path:              /home/user/8ballspicy/pool8Signed.ipa
size:              99,010,014 bytes
SHA-256:           6b4dfd3bd63a1ee5e649d98c44077e5d48f8a013255082287bef4514f6abdc84
git blob SHA-1:    35a53a1d34658065bd5e39b143493f4a720a2ba0  (identical at HEAD → working copy pristine)
ZIP validity:      valid; 3,527 entries; full CRC test passed (zipfile.testzip() → no corrupt entries)
structure:         Payload/pool.app/… (single app bundle, standard IPA layout)
original:          never modified during analysis; all experiments ran against read-only ZIP access
```

## 4. Application identity (from `Payload/pool.app/Info.plist`, parsed with `plistlib`)

| key | value |
|---|---|
| CFBundleIdentifier | **com.miniclip.8ballpoolmult** |
| CFBundleName / CFBundleDisplayName | **8 Ball Pool** |
| CFBundleExecutable | `pool` |
| CFBundleShortVersionString / CFBundleVersion | **56.31.0 / 5330** |
| MinimumOSVersion | 13.0 |
| DTPlatformVersion / DTSDKName / DTXcode(Build) | 26.2 / iphoneos26.2 / Xcode 26.2 (17C52) |
| UIDeviceFamily | iPhone + iPad |
| URL schemes | `com.miniclip.eightballpool`, `fb165073083517174`, `adjust543186831`, … (Miniclip's production scheme set) |

This is Miniclip's live commercial title, not a user-owned project.

## 5. Binary & bundle analysis (COMMAND 03)

### 5.1 Main executable `Payload/pool.app/pool` (81,997,008 B) — Mach-O header/load commands parsed directly
- Magic `0xFEEDFACF`, **ARM64**, `MH_EXECUTE`, 125 load commands.
- **`LC_ENCRYPTION_INFO` absent** → App Store FairPlay DRM removed. A genuine App Store device build carries this load command with `cryptid=1`. *(Confirmed.)*
- **`LC_CODE_SIGNATURE` absent** → the binary's Apple code signature has been stripped. *(Confirmed.)*
- Legitimate dependency set present (71 dylibs: system frameworks, GameKit, StoreKit, Cocos-era resources, plus Miniclip's ad stack `AdSurgeSDK, AppLovinSDK, InMobiSDK, FBAudienceNetwork, DTBiOSSDK, MolocoSDK`).
- **Injected load command:**
  ```
  LC_LOAD_DYLIB  @executable_path/Frameworks/libloader.framework/libloader
  ```
  No shipping Miniclip build links this. Inserting a load command rewrites the Mach-O header and invalidates any original signature — consistent with the signature being stripped afterwards. *(Injection: Confirmed. Attribution to a third-party mod: Confirmed by §5.2.)*

### 5.2 Injected framework `Frameworks/libloader.framework` (binary 12,265,804 B)
- ARM64 `MH_DYLIB`; links UIKit, **WebKit + JavaScriptCore**, StoreKit, Swift runtime (`libswiftCore`, reexported swift libs); uses `dlopen`; **no `LC_CODE_SIGNATURE`**.
- `Info.plist`: `CFBundleIdentifier = com.appdome.libloader` — i.e. it masquerades as / reuses the shell of **Appdome's** protection-loader framework name (Appdome is a RASP vendor; Miniclip is a known Appdome customer), while the binary content is not an Appdome build:
- Embedded strings (extracted, verbatim samples):
  ```
  'Aim Mode'  'Aim Strength'  'Max Aim Speed'  'Kecepatan Aim Maks'  'Kekuatan Aim'
  '"<GBModMenuDelegate>"'  'GBMenuChoiceTile'  'GBMenuDrawingStylePanel'  'GBMenuEntitlementCard' …  (91 'Menu' hits)
  'com.i3rby.8poolmod.autobreak.illegal.v1'  'com.i3rby.8poolmod.autoqueue.tiercode.v1'  'com.i3rby.autoplay'
  'Free Auto Queue time or a PRO key. Watch an ad to add time, or activate a key in Account.'
  'Beli di Telegram' / 'Abrir Telegram' / 'account.buy_telegram' / 'telegramMiniAppUrl'
  ```
- **Interpretation (high confidence):** this is the "i3rby" 8-Ball-Pool cheat menu — aim assistance ("Aim Mode/Strength", guideline-style controls), auto-break/auto-queue gameplay automation, and its own paid-activation layer (PRO keys, ad-gated sessions, Telegram sales), localized (Indonesian/Portuguese/Spanish/English). The `com.i3rby.*` identifiers match the provenance filename `8-ball-pool-i3rby-IPAOMTK.COM.ipa`.
- *Hypothesis (not proven without dynamic analysis):* the mod payload was merged into/repackaged under the `libloader.framework` shell specifically to blend in with the game's Appdome hardening and survive its integrity checks.

### 5.3 Bundle signature state — the archive is NOT validly signed
- `embedded.mobileprovision`: **absent** (searched all 3,527 entries; also absent in every `.appex`). Without a profile, no device will accept this bundle under any sideloading flow until it is fully re-signed.
- `_CodeSignature/CodeResources` exists for the app and all 4 extensions (66 seal files), but the seal is **stale/broken**:
  - main executable `pool`: **not sealed** (absent from `files2`) and unsigned (§5.1);
  - `Frameworks/libloader.framework/libloader`: sealed hash **MISMATCH** vs actual SHA-256 (binary replaced after sealing);
  - `Frameworks/AppLovinSDK.framework/AppLovinSDK`: sealed hash **MISMATCH**;
  - `Info.plist`: not present in seal;
  - untouched controls pass (`Assets.car` MATCHES, `Frameworks/libswift_Concurrency.dylib` MATCHES) → the mismatches are due to modification, not a parsing error;
  - **61 files referenced by the seal are missing from the archive**, all `SC_Info/*.v4.supp` / `*.v5.supf` FairPlay artifacts (`Payload/pool.app/SC_Info/` contains only a `.keep`) → classic decrypted-dump signature.
- Conclusion: *"pool8Signed" is a misnomer.* The artifact is **unsigned and structurally invalid**; `codesign --verify` on macOS would fail (not run here — no `codesign`; the structural evidence above is equivalent and sufficient).

### 5.4 App extensions & resources (all present, all from the original Miniclip build)
`PlugIns/`: `NotificationContent.appex`, `NotificationService.appex`, `PoolWidgetExtension.appex`, `PooliMessage.appex`. Resources: `Assets.car`, ~30 localization `*_text.plist` files (incl. `ar_text.plist`), CocosBuilder `.ccbi` UI files, Spine assets, `GameConfigurationLean.plist`, Firebase/AppsFlyer configs. No debug symbols (`.dSYM`) anywhere; the stripped release binary exposes symbol names only in the injected dylib's ObjC/Swift metadata.

## 6. Evidence vs. hypotheses (summary)

| # | Finding | Status | Evidence |
|---|---|---|---|
| 1 | Input SHA-256 `6b4dfd3b…abdc84`, valid ZIP, pristine | **Confirmed** | §3 |
| 2 | App is Miniclip 8 Ball Pool 56.31.0 (5330), arm64, iOS ≥ 13 | **Confirmed** | §4, §5.1 |
| 3 | FairPlay DRM removed (decrypted dump) | **Confirmed** | §5.1, §5.3 (missing `SC_Info`) |
| 4 | Third-party dylib injected via rewritten `LC_LOAD_DYLIB` | **Confirmed** | §5.1 |
| 5 | Injected dylib is a cheat mod menu (aim assist, auto-play, paid activation, `com.i3rby.*`) | **Confirmed (static)** | §5.2 strings |
| 6 | Bundle is unsigned/invalid; no provisioning profile | **Confirmed** | §5.1, §5.3 |
| 7 | Provenance: piracy/mod distribution site (IPAOMTK.COM) | **High confidence** | git history filenames + §5.2 identifier match |
| 8 | Mod payload merged into Appdome-loader shell to evade RASP | **Hypothesis** | §5.2 (needs dynamic analysis to prove) |
| 9 | `ExistingIPAWorkspace/OverlaySource/` ever existed in this project | **Disproven (absent everywhere)** | §2.2 |
| 10 | Checksum `c0e66b30…` corresponds to a recoverable artifact | **Disproven (nothing matches)** | §2.2 |

## 7. Host project discovery (COMMAND 04) — result: NO host source exists

Searched: all branches/commits of both `Adhambadrun/8ballspicy` and `abadrun/8ballspicy`, local filesystem, GitHub PRs/releases/Actions. There is **no** Xcode project, workspace, Swift/ObjC source, package manifest, scheme, entitlements, archive, or build log anywhere in the project's past or present. The only content ever committed is the pirated IPA itself. The production host (8 Ball Pool) is **proprietary to Miniclip**; its source is not obtainable, and Miniclip offers no public SDK for embedding third-party overlay UIs into its game binary. There is no "owner-authorized SDK or supported integration interface" available to this project — stated only after completing the investigation above.

## 8. Legitimacy & safety determination

The mission's requested end-state — integrate a "Mr. Spicy" overlay into this artifact, re-sign, and redistribute `output/Mr Spicy.ipa` — would require:

1. **Modifying and redistributing Miniclip's copyrighted commercial game without authorization** (copyright/trademark infringement; no rights, license, or source access exist — §7).
2. **Extending a cheat payload for a competitive online game.** The input already contains aim-assist/auto-play cheats (§5.2); any functional "settings ↔ host communication" overlay grafted onto this binary is, in practice, cheat-menu work. The mission's own rules forbid patching third-party game binaries, manipulating competitive gameplay, and bypassing DRM/anti-cheat/signature enforcement — all of which this deliverable would entail.
3. **Circumventing Apple signing controls** — re-sealing a DRM-stripped, signature-stripped dump with any obtainable certificate to make it installable, then presenting it as a legitimate "signed release."

This is not a tooling gap that better engineering can close; it is an **authorization gap that cannot be closed legitimately by this project**. Accordingly the integration, build, signing, packaging, and release steps were **refused/not performed by policy**, and the environmental impossibility on Linux (no Xcode/codesign/identity/device — §2.2, §9) is a secondary, independent blocker. No fake IPA, checksum, or success manifest was created.

## 9. Environment capability assessment (COMMAND 01.7)

| capability | status |
|---|---|
| macOS / Xcode / iOS SDKs | **NOT AVAILABLE** (Debian Linux x86_64 sandbox) |
| `codesign`, `otool`, `lipo`, `plutil`, `dwarfdump` | **NOT AVAILABLE** (Python-based equivalents used instead — §5) |
| Device destinations / simulators | **NOT AVAILABLE** |
| Legitimate signing identities / provisioning | **NONE PRESENT** (filesystem-wide search) |
| GitHub Actions macOS runner path | **NOT AVAILABLE** (repo has no workflows; `Adhambadrun/8ballspicy` is archived → pushes rejected; `abadrun/8ballspicy` → no push permission) |
| Available & used | python3 (zipfile/plistlib/struct/hashlib), unzip/zip, git, gh (api.github.com), openssl |

## 10. What a legitimate path would look like (for the record)

If the goal is a real, shippable "Mr. Spicy" iOS product, the viable routes are: (a) build an **original app** (own source, own bundle ID, own Apple Developer identity, own UI/branding — an 8-ball-*themed* original game or utility is fine; Miniclip's binary, name, assets, and store metadata are not), or (b) obtain a **written integration agreement + SDK from Miniclip** (none exists publicly). Either route requires a macOS/Xcode environment and the owner's own signing credentials. Neither route involves modifying `pool8Signed.ipa`.
