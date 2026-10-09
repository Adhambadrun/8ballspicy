# Advertised feature verification matrix

**Audit date:** 2026-10-09. **Public-description provenance:** user-supplied inventory, not independently fetched public marketing or release notes. No URL was supplied; no public feature claim is independently confirmed.

IPA evidence is from `Payload/pool.app/Frameworks/libloader.framework/libloader`, SHA-256 `bc6e41931e80a1fb7832612626ac05aacc7a45ecfbe7d73b45adbb889929823a`. Full exact search terms, offsets, and excerpts: [`../evidence/feature-string-search.json`](../evidence/feature-string-search.json). Offsets are decimal file offsets. The loader is unrelated third-party binary content; no corresponding source was recovered. Strings, selectors, fields, and linked frameworks do **not** prove functioning features.

The Mr. Spicy UI has a dedicated, localized **read-only Pro/reference disclosure**. This is not an entitlement, activation, prediction overlay, gameplay control, slider, or installed game integration. No unsupported feature has a misleading enabled switch.

| Feature | Advertised description | Observed evidence | Feature source available | Current Mr. Spicy feature UI | Actual functionality verified | Integration requirements | Final status |
|---|---|---|---|---|---|---|---|
| Prediction Lines | Shot-path and trajectory guides | `GBPredictionDrawView` @ 9961311 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Opponent Prediction | Possible opponent shot estimates | `_cachedOpponentResult` @ 9978733 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Pocket Hints | Pocket visual indicators | `GBMenuPocketStylePanel` @ 9960856; `_drawPockets` @ 9978902 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Table Outline | Prediction table boundary guides | `feature.table_outline` @ 10036905 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| End Dots / Impact Indicators | Predicted endpoints / impacts | `_drawImpactDots` @ 9960297; `_impactDotLayers` @ 9987249 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Precise Paths | Detailed configurable prediction paths | `lineThickness` @ 9998930; `lineOpacity` @ 9998944 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Scratch Alerts | Predicted cue-ball scratch warnings | `_scratchWarning` @ 9967182; `scratchAlertEnabled` @ 10003879 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Wrong-Ball / Foul Alerts | Predicted wrong contact / foul warnings | `_wrongBallWarning` @ 9987708; `wrongBallAlertEnabled` @ 10003899 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Golden Shot Support | Golden Shot category | `goldenOrLucky` @ 10124876 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Lucky Shot Support | Lucky Shot category | `goldenOrLucky` @ 10124876 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Best-Shot Ghost Line | Suggested-shot visual path | `_ghostTrajectoryLayers` @ 9987187; `_cachedGhostLayout` @ 9978660 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Aim Mode | Aim configuration | `Aim Mode` @ 10038551 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Aim Strength | Aim intensity setting | `Aim Strength` @ 10038665 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Maximum Aim Speed | Maximum aim movement speed | `Max Aim Speed` @ 10038698 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Aim-speed adjustment | Adjust aim speed | `Max Aim Speed` @ 10038698 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Initial pull-length adjustment | Initial power / pull setting | `meter.initial_pull` @ 10038450 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Wait-time adjustment | Automation delay setting | `Wait Time` @ 10038728 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Automatic angle-setting mode | Automatic angle configuration | No match for listed exact terms (not proof of absence) | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Single-shot mode | Single-shot operation | No match for listed exact terms (not proof of absence) | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Multi-shot mode | Multi-shot operation | No match for listed exact terms (not proof of absence) | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Normal graphics mode | Normal graphics preset | `lightGraphics` @ 10028571 | No | No; category disclosure only | Not tested | Owner host configuration API. Existing component theme tokens are not game graphics controls. | unavailable |
| High graphics mode | High graphics preset | No match for listed exact terms (not proof of absence) | No | No; category disclosure only | Not tested | Owner host configuration API. Existing component theme tokens are not game graphics controls. | unavailable |
| Auto Aim | Suggestion / assistance / guidance | `autoAimEnabled` @ 10028678; `autoAimMode` @ 10028693 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Auto Play — casual | Casual-labelled automation | `autoPlaySkill` @ 10028797 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Auto Play — Pro | Pro-labelled automation | `autoPlayEnabled` @ 10028781; `autoPlaySkill` @ 10028797 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Auto Play — stealth | Stealth-labelled automation | No match for listed exact terms (not proof of absence) | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Humanized movement — low | Low movement setting | `humanization` @ 10028705 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Humanized movement — medium | Medium movement setting | `humanization` @ 10028705 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Humanized movement — high | High movement setting | `humanization` @ 10028705 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Ball-in-Hand assistance | Automatic cue-ball positioning | `autoBallInHand` @ 10028931 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Floating play/pause | Floating automation control | No match for listed exact terms (not proof of absence) | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Pause-on-touch | Pause automation when touched | `autoPauseOnTouch` @ 10028946 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Automatic queuing | Queue matches automatically | `GBAutoQueueCountdownOverlay` @ 9959864; `com.i3rby.8poolmod.autoqueue.tiercode.v1` @ 10028341 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Improved automation accuracy | Advertised later-version accuracy | No match for listed exact terms (not proof of absence) | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Arabic menu | Arabic translation + RTL | Component resources only: `ar.lproj/Localizable.strings`, `SpicyLocalization.rightToLeftLanguages`, `forceRightToLeft` layout (see `validation/evidence/component-feature-evidence.json`). The earlier game-binary citations `useArabic` and `isArabic` were unrelated to the component and were removed | Yes — `SpicyLocalization`, en/ar resources | Yes — component menu | Component tests; see build report. Game runtime: not tested | Authorized host presentation via `SpicyHostBridge` | implemented (component only) |
| English menu | English translation | Component resources only: `en.lproj/Localizable.strings` (see `validation/evidence/component-feature-evidence.json`). No game-binary citation: the earlier `Aim Mode` citation was unrelated game text and was removed | Yes — `SpicyLocalization`, en/ar resources | Yes — component menu | Component tests; see build report. Game runtime: not tested | Authorized host presentation via `SpicyHostBridge` | implemented (component only) |
| Basic settings mode | Basic menu mode | No match for listed exact terms (not proof of absence) | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Advanced settings mode | Advanced menu mode | `segment.ui_mode.advanced` @ 10040056 | No | No; category disclosure only | Not tested | Owner-authorized host source/SDK and permitted noncompetitive scope; no online aim/automation implementation | unavailable |
| Graphics and presentation options | Graphics configuration | `lightGraphics` @ 10028571 | No | No; category disclosure only | Not tested | Owner host configuration API. Existing component theme tokens are not game graphics controls. | unavailable |
| Streaming display mode | Visibility in recording / streaming | `streamProof` @ 10028643 | No | No; category disclosure only | Not tested | Transparent owner-authorized platform implementation; no capture evasion or undocumented screen-hiding tricks | unavailable |
| Pro access | Subscription / key-gated access | `PRO key` @ 10045166; `activate a key in Account` @ 10045207 | No | Yes — read-only unavailable status | Disclosure localization tested; entitlement not tested | Owner-authorized entitlement service, legitimate license/test credentials, permitted feature source, hosted integration | UI-only |
| Ad-free experience | No intrusive advertisements | `Watch an ad for +1h` @ 10040475; game ad SDK bundles (forensic report) | No | No ads or ad-loading code in component | Component source inspected; game-wide ad-free not tested | Official game ad-free entitlement/configuration and owner host access; integrated runtime verification | awaiting verification |

## Status taxonomy

Each of the 42 rows has exactly one category in
[`../evidence/feature-status-taxonomy.json`](../evidence/feature-status-taxonomy.json).
`tools/audit_feature_matrix.py` checks coverage and that each category is
compatible with the row's final status. Categories describe what is established,
not what is advertised.

| Category | Meaning | Rows | Count |
|---|---|---|---|
| Implemented and tested | Implemented and exercised by tests in the environment it is claimed for (component, host or game). | none | 0 |
| Implemented but incompletely tested | Implemented in the component and covered by component tests; no host-integrated or game runtime test. | Arabic menu, English menu | 2 |
| UI representation only | A visible read-only disclosure or control; no underlying capability exists. | Pro access | 1 |
| Explicitly unavailable | The component states the feature is unavailable. Not implemented. Several are excluded by policy (online prediction or aim aids, automation, capture evasion). | 29 rows: Prediction Lines through Wait-time adjustment; Auto Aim through Automatic queuing; Streaming display mode | 29 |
| Blocked by host integration | Cannot be implemented or tested until an owner-authorized host exposes a configuration interface (E1). | Normal graphics mode, High graphics mode, Basic settings mode, Advanced settings mode, Graphics and presentation options | 5 |
| Dependent on external authorization | Requires an official entitlement or configuration source (E4) that does not exist in the available material. | Ad-free experience | 1 |
| Not implemented | No implementation and no loader evidence located. "No match" is not proof of absence. | Automatic angle-setting mode, Single-shot mode, Multi-shot mode, Improved automation accuracy | 4 |

Pro access is the only row that is both "UI representation only" and dependent on
E4: no entitlement signal is read, so no Pro state can be active.

## Settings effect inside the component

These controls exist in the component UI. Each one persists its value and
reports the change through `SpicyHostBridge`. The table records what the
component itself does with that value. Every effect listed as "none" is a stored
preference only and is categorized "UI representation only", not as a working
feature.

| Control | Persists to `SpicyPreferences` | Reports through bridge | Effect inside the component |
|---|---|---|---|
| Sound effects | yes | yes | none; no audio code exists |
| Haptic feedback | yes | yes | none; no haptic generator exists |
| Haptic intensity | yes | yes | none; disabled in the UI when haptics is off |
| Match notifications | yes | yes | none; no notification permission request or scheduling code exists |
| Personalized tips | yes | yes | none; no tip content exists |
| Player nickname | yes | yes | none beyond storage |
| Reset to defaults | restores defaults | yes | restores defaults in the model and the UI (component-level behaviour, not a matrix row) |

## Independently implemented component controls

| Control | Available source/UI | Verified behavior | Not claimed |
|---|---|---|---|
| Sound, haptics + intensity, match notifications, personalization, nickname | `SpicyPreferences`, `SpicySettingsView` | Persistence to `SpicyPreferences` and a `SpicyHostBridge` change callback. Inside the component these are **stored preferences only** (see the effect table below) | Game audio, device haptics, device notifications or permission prompts, tracking consent, personalized tips, account nickname changes, any game behaviour |
| Reset, open/close/reopen | Existing component + regression repairs | Model/UI reset, hosted UIKit modal lifecycle | Original game navigation or integration |
| English/Arabic, RTL, accessibility, theme | Existing component + repairs | Localization/labels/direction/resource tests | Full device VoiceOver audit, all sizes, real game runtime |

## Acceptance goals kept separate

- **Original game preservation:** name/bundle/version statically verified; input bytes unchanged. Normal navigation, assets rendering, and gameplay are **NOT TESTED**; the starting dump is already anomalous, not a proven clean baseline.
- **Pro:** no Mr. Spicy Pro feature or entitlement service recovered. Binary PRO-key/ad-gating strings are a third-party reference, not a license or access proof. No activation bypass or cheat implementation performed.
- **Ad-free:** component imports no ad SDK and contains no ad-loading/network code. The game includes multiple ad SDKs; no official ad-free configuration was recovered. No game ads were removed or tested.
- Prediction aids in an online competitive game can grant an unfair advantage; they are reference-only here, even if advertised as visual. A permitted standalone/offline educational context and legitimate source would need separate scoping, not binary patching.
