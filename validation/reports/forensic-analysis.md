# Forensic Analysis — immutable `pool8Signed.ipa`

**Audit date:** 2026-10-09. **Session:** `arena/6264dd0a-8ballspicy`.
**Scope:** read-only static investigation; no game execution, DRM work, binary
patching, library injection, activation bypass, or redistribution performed.
This report supersedes conflicting conclusions in the earlier project reports.

## 1. Reproducible evidence and confidence

```bash
python3 tools/inspect_ipa.py pool8Signed.ipa \
  --output validation/evidence/ipa-inspection.json
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py' -v
sha256sum pool8Signed.ipa
```

- [`../evidence/ipa-inspection.json`](../evidence/ipa-inspection.json): stdlib
  ZIP/CRC, plist, Mach-O commands/sections/nlist, CodeDirectory ordinary and
  pre-encrypt hashes, entitlements, and declared resource hashes. All relevant
  paths, binary sizes, hashes, dependencies, extensions and anomalies recorded.
- [`../evidence/independent-macho-verification.json`](../evidence/independent-macho-verification.json):
  independent **LIEF 0.17.6** in-memory metadata inspection of the main executable
  and loader. No binary extracted to disk by either Python inspection.
- [`../evidence/feature-string-search.json`](../evidence/feature-string-search.json):
  exact substring search terms, byte offsets, excerpts. Limited static samples,
  not executable payloads or reconstructed original source.
- `tools/inspect_ipa_apple.sh`: macOS CI static `lipo`, `otool`, and
  `codesign --verify --deep --strict` validation of the **input**, never signing.
  Run **37926156116** executed it: **exit 1**, `invalid Info.plist (plist or
  signature have been modified)`. Before/after input hashes match. See
  `../ci/runs/37926156116-component/input-apple-verification.txt`.
  This is actual Apple verification failure, not just a Python inference.
  The step intentionally records signature failure without failing independent
  component compilation; a green inspection step is not a valid-signature claim.
- The Python parser has four passing synthetic-fixture unit tests, including
  detecting a mutated code page. The fixtures are **not** Apple signatures.
  CodeDirectory layout was cross-checked against Apple's published XNU
  `osfmk/kern/cs_blobs.h` (github.com/apple-oss-distributions/xnu).

**Confidence:** high for recorded bytes/metadata/hash comparisons, medium for
interpretation of mod-related strings, none for unexecuted game behavior.
Hash comparisons do not replace Apple CMS trust validation. No known-clean
owner-supplied baseline exists for a byte-by-byte provenance comparison.

## 2. Input and host identity — VERIFIED FACT

| Property | Observed value / method |
|---|---|
| Exact path | `/home/user/8ballspicy/pool8Signed.ipa` |
| Size | **99,010,014 bytes** (`stat`, Python) |
| SHA-256 before and after analysis | `6b4dfd3bd63a1ee5e649d98c44077e5d48f8a013255082287bef4514f6abdc84` |
| ZIP | CRC **PASS**, **3,527 entries** (`zipfile.testzip`) |
| Main bundle / executable | `Payload/pool.app/` / `pool` |
| Display name / bundle name | **8 Ball Pool** / **8 Ball Pool** |
| Bundle ID | **com.miniclip.8ballpoolmult** |
| Version / build | **56.31.0 / 5330** |
| Minimum iOS | **13.0** (plist and Mach-O) |
| Architecture | **arm64**, thin 64-bit little-endian Mach-O |
| Supported devices / orientations | iPhone and iPad; landscape left/right |
| Reported original toolchain | Xcode 26.2 / SDK iphoneos26.2 (plist metadata) |

All user-supplied input identity references match. The tracked input was never
changed or overwritten. This proves byte preservation in this session, **not**
that the starting archive was a pristine official game or works normally.
There is **no output IPA**. Required eventual output is
`output/pool8Signed.ipa`, not the outdated `output/Mr Spicy.ipa` contract.

## 3. Package and binary architecture — VERIFIED FACT

- **25 framework bundles**, **4 app extensions**, **1 embedded Swift dylib**
  (`libswift_Concurrency.dylib`). All inspected executables are thin arm64;
  the exact per-binary metadata and hashes are in `ipa-inspection.json`.
- Extensions: `NotificationContent.appex`, `NotificationService.appex`,
  `PoolWidgetExtension.appex`, `PooliMessage.appex`. Their IDs remain under
  `com.miniclip.8ballpoolmult`; widget minimum iOS is 14.0, others 13.0.
- Resource inventory records localizations, CocosBuilder `.ccbi` files,
  PNGs, plists and other assets. Resources were inspected, not rendered.
  Opaque private blobs were not executed, decrypted or attributed as fact.
- Main executable: **81,997,008 bytes**, SHA-256
  `4654de9a52345e27397a7e0714c5efa0f51a3af53313e4bc068f02417aba84b3`,
  `MH_EXECUTE`, **125 load commands**, minimum iOS 13.0 / SDK 26.2.
- **105 linked-library commands**, rpaths `/usr/lib/swift` and
  `@executable_path/Frameworks`. The complete linkage list is recorded.
- nlist: **4,222 entries**; **30 defined external**, **4,191 undefined**
  non-debug named entries (remaining entry not classified as named).
  LIEF independently records imported/exported symbol metadata.
  `UIApplication`, `UIViewController`, notification and `dlopen` references
  establish dependencies only, not an application initialization call graph.
- `LC_LOAD_DYLIB` for
  `@executable_path/Frameworks/libloader.framework/libloader` is present at
  main-file command offset **13,800**. This declares a dependency; whether
  dyld successfully loads it, executes initializers, or presents UI is
  **NOT TESTED**. No original host integration hook is established by this.

## 4. Decryption and code-signature integrity — VERIFIED STRUCTURE / FAILED HASHES

- `Info.plist` contains `DecryptedBy = @FastDecryptBot - https://t.me/FastDecryptBot`.
  `SC_Info/` contains only `.keep`; 61 missing app-seal entries refer to
  FairPlay supplemental files. These are evidence of a third-party dump,
  not authorization, a legitimate decryption operation here, or distribution rights.
- Main **`LC_ENCRYPTION_INFO_64` is PRESENT**, cryptoff **237,568**, cryptsize
  **4,096**, **crypt_id=0**. LIEF independently agrees. Unencrypted status is
  consistent with the watermark/stripped metadata; absence of a command
  must not be reported. No FairPlay bypass was performed in this session.
- Main **`LC_CODE_SIGNATURE` is PRESENT** at **79,904,240**, size **2,092,768**.
  Two CodeDirectories, requirements, XML/DER entitlements and CMS wrapper
  remain. Presence is not validity, ownership of keys, or a signing identity
  available for this project.
- Both CodeDirectories identify `com.miniclip.8ballpoolmult` and team
  `HLSX4DMBX6`. These are **embedded assertions**, not an independently
  authenticated certificate ownership claim. Recorded entitlements include
  application ID, game center, production push, associated domains,
  Apple sign-in, declared age range and app group.
- Ordinary hash tables: **593 mismatching pages per CodeDirectory** out of
  **19,928** declared pages. **172 wholly precede the current signature**;
  **421 overlap the current signature region** because codeLimit
  **81,623,008** exceeds the signature offset. Do not characterize all 593
  as gameplay patches. Optional pre-encrypt tables also give 593 mismatches.
- Special-slot comparisons: **Info.plist MISMATCH**, **CodeResources MISMATCH**;
  requirements and both entitlement blobs **MATCH**. These independent
  mismatches establish stale seals even apart from decrypted code pages.
- App resource seal: **6,624 matching hash comparisons**, **98 mismatching
  hash comparisons**, **61 missing entries**. Counts are hash comparisons,
  not 98 distinct files. Changed loader executable/plist and AppLovinSDK
  executable each mismatch recorded SHA-1 and SHA-256 seals. All exact
  anomalies and optional flags are in the evidence JSON. Nested-code rules
  are not fully emulated by the Python file-hash check.
- **No embedded provisioning profile** is present. Absence alone is not
  proof an App Store build is unsigned; here stale hashes and an unsigned
  nested loader are separate integrity evidence.

## 5. Loader anomaly / existing third-party modifications

`Payload/pool.app/Frameworks/libloader.framework/libloader` is **12,265,804
bytes**, SHA-256
`bc6e41931e80a1fb7832612626ac05aacc7a45ecfbe7d73b45adbb889929823a`.
It is arm64 `MH_DYLIB` with **45 commands**, `crypt_id=0`, **no
LC_CODE_SIGNATURE** (confirmed independently with LIEF). Its plist says
`com.appdome.libloader` 1.0.0, but that name **does not authenticate its contents
as Appdome protection**. Its bytes contain:

| Static observation | Decimal file offset |
|---|---:|
| `com.i3rby.8poolmod.autoqueue.tiercode.v1` | 10028341 |
| `com.i3rby.8poolmod.autobreak.illegal.v1` | 10029530 |
| `com.i3rby.autoplay` prefix | 10034542 |
| `GBModMenuDelegate` | 9965433 |
| `Aim Mode` / `Aim Strength` / `Max Aim Speed` | 10038551 / 10038665 / 10038698 |
| `Free Auto Queue time or a PRO key. Watch an ad to add time, or activate a key in Account.` | 10045796 |

**Static inference (medium/high confidence):** this framework contains
third-party mod-menu-related material, including prediction/automation/paid
activation references. The main dependency and stale seals are consistent
with an altered package. Without a clean baseline or runtime, do **not**
assert exactly who injected it, how it bypasses protection, that every named
feature is implemented, or that gameplay automation runs.
No loader code was used in MrSpicyUI; no key/activation/anti-cheat bypass was
implemented. Full category audit: `feature-verification-matrix.md`.

### Advertising-source distinction

- **Supplied game bundle:** static framework paths include `AdSurgeSDK`,
  `AppLovinSDK`, `BigoADS`, `DTBiOSSDK`, `FBAudienceNetwork`, `InMobiSDK`,
  `MolocoSDK`, `OMSDK_Appodeal`, and `GoogleAdsOnDeviceConversion` under
  `Payload/pool.app/Frameworks/`. Exact plist identities, hashes and declared
  dependencies are in `ipa-inspection.json`. This proves embedded SDK material,
  not an ad impression or which service is active. `AppLovinSDK` hash mismatches
  also mean this dump cannot establish a pristine original implementation.
- **Existing third-party loader:** PRO-key / rewarded-ad queue-time text is
  present (offsets above and in the matrix). Whether it actually loads an ad
  or gates a feature was not executed or verified. Do not attribute this
  monetization to the original game or to our component.
- **MR. SPICY component:** inspected Swift source/resources and Package.swift
  contain no ad SDK dependency, ad-loading API or network client. No adverts
  are added. This is a source/component-scope claim only.

No SDK removal, DNS/network blocking, entitlement bypass or ad-free host
configuration was performed. Game-wide ad-free requires an official supported
configuration or entitlement and integrated runtime tests. Analytics, crash
reporting and essential networking were not disabled or presumed advertising.

## 6. Runtime architecture and source distinctions

| Artifact / question | What is established | Limitation |
|---|---|---|
| Original game source | **NOT AVAILABLE** in examined trees/history | Binary/symbols are not original source |
| Decompiled/disassembled source | None recovered or fabricated | No guessed host call graph |
| Main/loader metadata | Declared dependencies, ObjC/Swift symbol references, sections | Cannot prove initialization sequence, UI reachability or callbacks |
| Existing third-party loader | Binary and static strings | Not authorized source, SDK, or component provenance |
| `MrSpicyUI/` | Existing original Swift/UIKit package continued and repaired | Independent library, not loaded by game |
| `HostApp/` | Existing UIApplication demo/test host | **Not 8 Ball Pool** |
| `SpicyHostBridge` | Component-owned callback protocol | Game does not acquire this interface by its existence |
| Compiled component ZIP | Independent unsigned device build; see build report | Not a framework injection payload or installable IPA |
| Actual game navigation/gameplay/ad behavior | **NOT TESTED** | No authorized runtime/clean baseline/device |
| Integrated host source / signed final IPA | **NOT PRODUCED** | Required authorization, source/SDK and signing absent |

## 7. GitHub recovery / discrepancies corrected

- `abadrun/8ballspicy`: accessible, main
  `7e59c3a733b53d8b16725ad82e05eab03de14dca` (merged PR #1).
  Component introduced at `109072df115bd12a0ea9ce5dea256037843e1f03`;
  subsequent compile/lifecycle/host/packaging fixes retained. Complete
  reachable history fetched; no Miniclip host source or authorized SDK found.
- Existing component, demo host, en/ar resources, S mark and tests recovered.
  The mark is the **existing generated replacement** from the previous
  implementation, not the missing historical brand asset. No new mark generated.
- `Adhambadrun/8ballspicy` and `arena/f4b84726-8ballspicy` **are accessible**.
  That branch's tip `10ad313616895ef75e1d269c7ff323809e105671` contains IPA
  and reports, **no component/host source**. Its claim that main signature
  and encryption commands are absent is **incorrect for the exact supplied
  hash**; direct parsing and LIEF both establish their presence.
- The prior abadrun report correctly observed main commands but incorrectly
  generalized valid signature structures to all binaries and asserted an
  Appdome loader identity from its plist. The loader has no signature command;
  mod strings and mismatched seals were missed. Current findings replace those.
- Prior report's four-commit/no-source inventory described the repository
  **before** component introduction, not its current state. Existing component
  work was reused, not discarded.
- Current account listing exposes only `abadrun/8ballspicy`; earlier
  `8ball`–`8ball7` content was not recovered. Historical claims about their
  disappearance remain **NOT INDEPENDENTLY REVERIFIED** as an event.
- Both inspected repos show no releases; abadrun historical Actions artifacts
  exist but the useful successful build packages/logs are on `ci/artifacts`.
  Latest prior run **37916687975**, source
  `114b9aedfb04f34651afb1c14cde636612347bc3`, succeeded; its logs were fetched
  via git and independently inspected. Older run **37915278092** package
  hash `1a57bab96031dc78abde5eec594eb8ca9f1121ebc47819a67cd2ed7df97c034d`
  independently matched; it is not the new repaired build.
- Direct `gh run view --log` download failed at
  `results-receiver.actions.githubusercontent.com` (**EOF**). Existing git
  evidence remained fetchable. New CI uses one publisher on the **fixed
  session branch only**, records full source/run provenance, and fails on
  publication errors rather than masking a push failure.

## 8. Technical conclusion

**Modified/untrusted dump preserved as evidence; independent component work
is legitimate and testable. Host integration remains BLOCKED.** Possession
of the IPA and embedded Miniclip entitlement strings does not grant source,
keys, license, or redistribution permission. Supply a clean owner-authorized
host source/SDK and written integration scope first; then perform source-level
presentation/settings integration, authorized build/sign/export and real-device
regression tests without using the third-party loader or tampering with the dump.
