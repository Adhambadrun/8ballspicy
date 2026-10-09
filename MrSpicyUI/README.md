# MrSpicyUI

Premium overlay UI component for the “Mr. Spicy” experience (8 Ball Pool /
Mr. Spicy project identity).

## Provenance (important)

The mission brief referenced existing work under
`ExistingIPAWorkspace/OverlaySource/` and a prior device-component checksum
`c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b`.
Neither exists in this repository, its git history, or any reachable
repository (see `../validation/reports/forensic-analysis.md` §7 for the full
recovery investigation, including sibling repositories that were observed and
then became unreachable during the session).

This package is therefore an **original implementation** of the documented
component scope, written in this session. The bundled
`Resources/Branding/spicy-s-mark.png` is a **newly generated** Spicy S monogram
— it is *not* a recovered copy of any historical asset.

## Scope

| Area | Implementation |
|---|---|
| Brand UI | S-mark header with ember→gold accents (`SpicyBrand`, `SpicyHeaderView`) |
| Design system | Premium dark/gold token set (`SpicyTheme`) |
| Settings | Sound, haptics + intensity, notifications, personalization, nickname — all persisted (`SpicyPreferences`) |
| Reset | Factory-reset button, persisted, mirrored in UI |
| Lifecycle | `open` → `close` → `reopen` on one instance (`SpicyOverlayViewController`) |
| Localization | English + Arabic, RTL-aware layout (`SpicyLocalization`) |
| Accessibility | Stable identifiers + localized labels (`SpicyAccessibility`) |
| Host integration | `SpicyHostBridge` protocol — the only supported seam |

Every control performs a real action (persisted write or lifecycle call). No
decorative controls.

## Requirements

- iOS 13.0+
- Swift 5.9 / Xcode 15+ (CI uses the runner-default Xcode, see
  `.github/workflows/component-ci.yml`)

## Building & testing

The package is iOS-only; tests must run on an iOS Simulator via `xcodebuild`:

```bash
# from the MrSpicyUI/ directory
xcodebuild test -scheme MrSpicyUI \
  -destination 'platform=iOS Simulator,name=iPhone 16'

# device (arm64, iphoneos) build — unsigned
xcodebuild build -scheme MrSpicyUI -configuration Release \
  -destination 'generic/platform=iOS' CODE_SIGNING_ALLOWED=NO
```

## Host integration

```swift
import MrSpicyUI

final class HostAdapter: SpicyHostBridge {
    func spicyOverlayDidRequestClose(_ overlay: SpicyOverlayViewController) {
        // host reacts (analytics, game state), UI closes itself
    }
    func spicyPreferencesDidChange(_ preferences: SpicyPreferences) {
        // apply settings to authorized host functionality
    }
}

let overlay = SpicyOverlayViewController(bridge: adapter)
overlay.open(from: hostViewController, animated: true)
// later:
overlay.close(animated: true)
// and reopen as needed — same instance supports unlimited cycles
```

**This component is not integrated into 8 Ball Pool.** The host application is
closed-source third-party software; integration requires owner-authorized
source or a supported integration interface that this workspace does not
contain (see `../validation/reports/integration-validation.md`).

## Continued audit and lifecycle contract

This session continues the existing implementation, including its bundled mark;
its original-generation provenance above is historical, not a new asset recovery.
Use all UIKit APIs on the main thread. Retain your bridge adapter (the component
holds it weakly). `open`/`close` now return a discardable Bool: `false` means an
in-flight transition or detached/busy presenter rejected the request. Wait for
completion and retry from the host's visible controller. Already-open/closed
calls remain idempotent. Only a close-button request emits the close bridge event.
`refreshLocalization(language: "ar")` refreshes all rows, controls, and RTL layout;
no host app display name or bundle identifier is changed. Persisted component
preferences do not by themselves change game behavior or system permissions.
