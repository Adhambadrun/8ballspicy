# MrSpicyUI

Premium overlay UI component for the “Mr. Spicy” experience (8 Ball Pool /
Mr. Spicy project identity).

## Provenance (important)

The mission brief referenced existing work under
`ExistingIPAWorkspace/OverlaySource/` and a prior device-component checksum
`c0e66b306465fb0093a83893664982a54a914f6b49f69a2c1f001cb6f751088b`.
That exact source/checksum was not recovered from the examined trees/history.
The accessible `Adhambadrun/8ballspicy` historical branch contains the input
and reports but no overlay/host source. See the forensic report for scope and
uncertainty; earlier claims that this named repository was unreachable are
superseded.

This session **continues the existing original component** introduced in the
`abadrun/8ballspicy` history, rather than rebuilding it from scratch. It is not
recovered Miniclip or i3rby source. The bundled
`Resources/Branding/spicy-s-mark.png` is the **existing AI-generated replacement**
from the earlier implementation, not a recovered historical brand asset and
not a new image generated during this continuation.

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

Controls update component preferences or lifecycle only. They do not apply
game audio, haptics, permissions, consent, graphics, account or Pro effects.
A localized read-only unavailable disclosure replaces unsupported Pro controls.
No ads or network code are added by the component; game-wide ad-free behavior
is not implemented or verified.

## Delivery-integrity checks (run from the repository root)

These verify the repository's delivery claims against the files that actually
exist. They need only Python 3 — no Xcode — and they exit non-zero on any
violation.

```bash
python3 tools/verify_release_state.py     # release status, provenance, localization, scope
python3 tools/audit_feature_matrix.py     # re-derive the 42-category evidence from the IPA
PYTHONPATH=tools python3 -m unittest discover -s tools -p 'test_*.py'
```

`tools/verify_release_state.py` fails if `output/pool8Signed.ipa` or
`output/pool8Signed.sha256` appears without a genuine integration, if any other
`.ipa`/app bundle/`Payload/` tree/provisioning profile appears in the repository,
if the immutable input IPA changes, if the release manifest claims a delivery the
filesystem does not support, if a feature row advertises an implementation that
was not established, or if the component gains advertising, networking or
host-loading code. CI enforcement is prepared in
`../validation/ci/component-ci.release-gated.yml.txt`; see
`../validation/ci/WORKFLOW-NOT-INSTALLED.md` for why it is not installed on this
branch. Current result: 27 PASS / 7 WARN / 0 FAIL; 36/36 local tests.

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
        // optional authorized host UI response; component dismisses itself
    }
    func spicyPreferencesDidChange(_ preferences: SpicyPreferences) {
        // apply settings to authorized host functionality
    }
}

let adapter = HostAdapter() // retain for at least the overlay lifetime
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

Close-button requests during opening are queued once rather than silently
lost. Programmatic calls during transitions still reject explicitly. A
presentation completion means the accepted transition finished, not that the
menu remains visible: a queued user close may immediately begin dismissal.
Per-presentation cycle tokens prevent old asynchronous completions mutating
state after a new open. External host dismissals do not synthesize user-button
bridge events. Host-driven reopen should occur from dismissal completion.

Close bridge events are deduplicated per presentation before invoking host code;
reentrant callbacks cannot dismiss a newer presentation. Detached close-button
events are ignored. Rejected presentations deliver completion at most once.
