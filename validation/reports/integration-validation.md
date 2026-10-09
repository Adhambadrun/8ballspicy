# Integration Validation — Mr. Spicy × 8 Ball Pool

**Date:** 2026-10-09. **Session:** `arena/6264dd0a-8ballspicy`.
**Status:** **BLOCKED — actual game integration NOT IMPLEMENTED.**

## Addendum — session `arena/a4ebad6a-8ballspicy` (2026-10-09)

Everything above was re-verified against the live repositories, bytes and logs;
see `session-a4ebad6a-verification.md` for the command-by-command evidence. No
status below changed. What this session added:

- **A release-integrity gate.** `tools/verify_release_state.py` re-derives every
  delivery claim from the files that actually exist. It fails the build if a
  release artifact appears without a genuine integration, if the immutable input
  IPA changes, if the manifest claims a delivery the filesystem does not support,
  if a feature row advertises an implementation that was not established, or if
  the component gains advertising, networking or host-loading code. Current
  result on this repository: **26 PASS, 10 WARN, 0 FAIL**.
- **Negative tests for the gate.** `tools/test_verify_release_state.py` (26
  tests) proves the gate fails for a placeholder `output/pool8Signed.ipa`, a
  renamed demo app, an unsigned component ZIP labelled as a release, a manifest
  claiming delivery or overstating Pro/ad-free, a matrix row claiming an
  implemented game feature, an ad SDK in the component, and `dlopen`
  host-loading code. A gate that cannot fail would be worthless.
- **A CI variant that enforces it.**
  `validation/ci/component-ci.release-gated.yml.txt` adds a `release-gate` job
  and makes `publish-evidence` refuse to publish unless the gate succeeded, so a
  failing gate can no longer be published as a successful run.
- **A reproducible feature-matrix auditor.** `tools/audit_feature_matrix.py`
  reads the loader bytes out of the immutable IPA and confirms every citation in
  the matrix and in `validation/evidence/feature-string-search.json`. It found
  four case-drifted citations (`wait time` where the bytes read `Wait Time`, and
  a duplicate `watch an ad` alongside `Watch an ad` where the bytes read
  `Watch an ad for +1h`) which have been corrected; the auditor now reports
  **96 citations, 96 PASS, 0 WARN, 0 FAIL**.
- **A re-verified CI limitation.** The GitHub App token still cannot create or
  update workflow files: `git push` is rejected with *"refusing to allow a
  GitHub App to create or update workflow `.github/workflows/component-ci.yml`
  without `workflows` permission"*, and the contents API returns **403 Resource
  not accessible by integration**. `Adhambadrun/8ballspicy` reports **0 workflow
  runs**, so this branch cannot produce its own build evidence.

None of this changes the integration blockers listed below; it makes them
impossible to paper over.

## Verified available artifacts

- Existing `MrSpicyUI/` Swift/UIKit source, original component-owned
  `SpicyHostBridge`, en/ar resources, S replacement mark and tests recovered
  from abadrun history and continued rather than rebuilt from scratch.
- Existing `HostApp/MrSpicyDemoHost` is a **component TEST HOST**, bundle ID
  `com.mrspicy.demo.host`. It is not 8 Ball Pool and is not an IPA replacement.
- `pool8Signed.ipa` metadata still names **8 Ball Pool**, bundle ID
  **com.miniclip.8ballpoolmult**, version **56.31.0 / 5330**, minimum iOS 13.0.
  Input bytes preserved. This is not runtime proof of game preservation.
- Both named GitHub repositories and the reported historical branch were
  inspected. No Miniclip game source, owner-authorized overlay SDK, license
  agreement or documented host extension point found in examined artifacts.
  The third-party `libloader` is **not** an authorized integration SDK.
- Component build/test evidence is in `build-and-signing-report.md`.
  Passing component tests is not evidence of game integration.

## Available component seam (not a game hook)

An owner-authorized host must add `MrSpicyUI` as a local Swift package/library,
retain its host adapter, and present `SpicyOverlayViewController` from a visible
UIKit controller on the main thread. `SpicyHostBridge` reports close-button
requests and persisted preferences. It does not locate the game, hook dyld,
read game state, change aim, grant Pro access or remove advertising.

- `open`/`close` return a discardable Bool; false rejects detached/busy
  presenters or in-flight transitions without duplicate UIKit requests.
- Host retains the adapter; component holds the bridge weakly.
- Close-button taps during opening queue once; reentrant bridge callbacks are
  deduplicated per presentation. Programmatic/detached close calls do not emit
  a user-close event. Accepted completion reports the transition finishing,
  not continued visibility. Reopen from host dismissal completion.
- Reload stored values on reopening; refresh explicit `en`/`ar` content and RTL.
- Audio, haptics, notification permission, personalization consent and account
  nickname must each be wired only to the owner's documented, allowed APIs.
  Current controls verify component persistence/callbacks, not host effects.
- Initial application of stored settings is the host's responsibility. The
  adapter must not infer notification/tracking consent from stored booleans.
- Current Pro/reference section is localized read-only **unavailable** status,
  not licensed Pro functionality. Feature matrix lists every advertised item.

## Evidence required before integration can be called completed

1. Owner-authorized host source/build project or official integration SDK with
   documented presentation/settings APIs and written permitted feature scope.
2. Source-level integration diff and a successful **actual host build**.
3. Build products demonstrating package resources/code inclusion and an
   authorized runtime trace/test showing it loads and opens/closes/reopens.
4. Regression tests for ordinary game screens, navigation, gameplay, account
   and network behavior, plus English/Arabic layout and accessibility.
5. Authorized App ID/team signing and every extension's matching entitlements
   and provisioning; Apple verification and real IPA export.
6. A manifest/hash for `output/pool8Signed.ipa`, with physical-device launch
   and feature/ad-free verification or prominent disclosure of missing tests.

**None of (1)–(6) has been completed for the game.** No injection, archive
surgery, plist rebranding, DRM/app-protection work or replacement game performed.
No authorized integration attempt was made against an invented interface.

## Three requested goals — independent status

| Goal | Completed evidence | Missing evidence / status |
|---|---|---|
| Original game preservation | Identity statically verified, original SHA-256 unchanged | Game navigation/screens/gameplay NOT TESTED; input already anomalous |
| Mr. Spicy Pro | Read-only honest status; feature/source/strings audit; component preference tests | No entitlement service, permitted feature implementation or actual host integration; BLOCKED |
| Ad-free | Component has no ad SDK, ad-loading or network code | Game ad SDKs remain; no official ad-free API/entitlement found, integrated behavior NOT TESTED |

## Smallest legitimate next steps

1. Obtain **Miniclip/owner written authorization plus a buildable source tree
   or official SDK** supporting in-app UI presentation and benign settings.
   A certificate alone, the dumped IPA, or an external key cannot supply this.
2. Provide a **clean owner baseline and documented protection/build pipeline**
   for regressions and protected-build requirements; do not reuse the altered
   third-party loader. Exact current protection attribution remains unverified.
3. Supply Apple-issued identity and matching profiles for
   `com.miniclip.8ballpoolmult` and four extensions via secure CI/environment
   only. Local material absent; secrets-list API returned **403**, so remote
   secrets availability is **UNKNOWN**, not independently proven absent.
4. For Pro/ad-free requests, supply official permitted feature source and
   entitlement/configuration APIs plus legitimate test access. No bypass.
5. Attach an authorized physical iOS device to a macOS developer/self-hosted
   environment for installation, launch, normal-game regressions and ads tests.
