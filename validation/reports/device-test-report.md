# Device Test Report — independent component vs actual game

**Date:** 2026-10-09. **Session:** `arena/6264dd0a-8ballspicy`.

| Level | Status / evidence |
|---|---|
| Recovered simulator hostless tests | VERIFIED: run 37916687975, 28 passed / 0 failed / 5 skipped; 33 counted executed by XCTest |
| Recovered hosted UIKit tests | VERIFIED: same run, 33 passed / 0 failed / 0 skipped in MrSpicyDemoHost |
| Final hostless package suite | VERIFIED run 37928629998: 34 passed / 0 failed / 17 skipped (51 counted) |
| Final hosted UIKit suite | VERIFIED same run: 51 passed / 0 failed / 0 skipped |
| Repeated animated transition regression | VERIFIED same run: 10 executions / 10 passed / 0 failed / 0 skipped |
| Unsigned generic device build | SUCCESS, arm64 iOS13 target; not an installation test |
| Physical-device installation/launch | **NOT TESTED** — no authorized physical device or signed integrated IPA available |
| Actual 8 Ball Pool normal navigation/screens/gameplay | **NOT TESTED** — no authorized host/runtime; input byte preservation is not runtime verification |
| Integrated MR. SPICY access/open/close/reopen | **NOT TESTED** — actual host integration absent |
| Pro access and permitted feature behavior | **NOT TESTED** — no legitimate service/feature source/test entitlement |
| Game-wide ad-free behavior | **NOT TESTED** — no authorized game configuration/runtime verification |
| Full VoiceOver, keyboard, Dynamic Type and all iOS/device sizes | **NOT TESTED** — focused component tests are not a complete usability certification |

Final simulator: iPhone 17 Pro, iOS 26.4.1; Xcode 26.6 (17F113).
Simulator execution is not a physical-device test. The demo UIApplication is
not the game. No installation, launch, on-device signing or gameplay result
is inferred from either source inspection or component compilation.

## Addendum — session `arena/a4ebad6a-8ballspicy` (2026-10-09)

No device was available and no signed IPA exists, so **every NOT TESTED row
above remains NOT TESTED**. This session added verification that runs without a
device and without Xcode:

| Verification | Result |
|---|---|
| Release-integrity gate (`tools/verify_release_state.py`) | 27 PASS / 7 WARN / 0 FAIL |
| Gate negative tests (`tools/test_verify_release_state.py`) | 26/26 pass — the gate fails for placeholder releases, renamed demo apps, unsigned components labelled as releases, false manifest claims, dishonest feature rows, ad SDKs and `dlopen` host-loading |
| Feature-matrix auditor (`tools/audit_feature_matrix.py`) | 96 citations, 96 PASS, 0 WARN, 0 FAIL |
| Full local test suite (`unittest discover -s tools`) | 36/36 pass |
| Source provenance (working copy vs CI run 37928629998) | tree IDs identical: MrSpicyUI `3a775121…`, HostApp `8704ef1e…`, tools `18d176a1…` |
| Input IPA immutability | 99,010,014 bytes, SHA-256 `6b4dfd3b…` unchanged |
| Component artifact integrity | 1,729,023 bytes, SHA-256 `3a872657…`, ZIP CRC PASS, thin arm64 `MH_OBJECT` |
| Apple input-signature verification (from run 37928629998 log) | exit 1 — `invalid Info.plist (plist or signature have been modified)` |

The gate also enforces the device-test status: it fails if `output/` gains any
file other than `README.md`, or if the manifest stops recording the release as
undelivered. That is the strongest guarantee available without hardware.

**Still required for device validation:** E1 authorized host source/SDK, E2 clean
baseline, E3 Apple identity and profiles, E5 an authorized developer-mode iPhone
or iPad. See `session-a4ebad6a-verification.md` §6.

**Required next setup:** owner-authorized integrated host, matching Apple
certificate/profiles via secure tooling, macOS/Xcode + connected developer-mode
iPhone/iPad (or authorized device-capable self-hosted CI), documented device
model/iOS/UDID provisioning, normal-game regression cases and official Pro/ad
entitlement test access. Record real logs/results against the exact IPA hash.
