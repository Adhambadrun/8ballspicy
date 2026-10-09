# Device Test Report — independent component vs actual game

**Date:** 2026-10-09. **Session:** `arena/6264dd0a-8ballspicy`.

| Level | Status / evidence |
|---|---|
| Recovered simulator hostless tests | VERIFIED: run 37916687975, 28 passed / 0 failed / 5 skipped; 33 counted executed by XCTest |
| Recovered hosted UIKit tests | VERIFIED: same run, 33 passed / 0 failed / 0 skipped in MrSpicyDemoHost |
| Current repair regression tests | CI in progress; exact verified final counts in build report/manifest |
| Physical-device installation/launch | **NOT TESTED** — no authorized physical device or signed integrated IPA available |
| Actual 8 Ball Pool normal navigation/screens/gameplay | **NOT TESTED** — no authorized host/runtime; input byte preservation is not runtime verification |
| Integrated MR. SPICY access/open/close/reopen | **NOT TESTED** — actual host integration absent |
| Pro access and permitted feature behavior | **NOT TESTED** — no legitimate service/feature source/test entitlement |
| Game-wide ad-free behavior | **NOT TESTED** — no authorized game configuration/runtime verification |
| Full VoiceOver, keyboard, Dynamic Type and all iOS/device sizes | **NOT TESTED** — focused component tests are not a complete usability certification |

Simulator execution is not a physical-device test. The demo UIApplication is
not the game. No installation, launch, on-device signing or gameplay result
is inferred from either source inspection or component compilation.

**Required next setup:** owner-authorized integrated host, matching Apple
certificate/profiles via secure tooling, macOS/Xcode + connected developer-mode
iPhone/iPad (or authorized device-capable self-hosted CI), documented device
model/iOS/UDID provisioning, normal-game regression cases and official Pro/ad
entitlement test access. Record real logs/results against the exact IPA hash.
