# MrSpicyDemoHost

Minimal iOS **test host application** for the `MrSpicyUI` component's hosted
unit tests.

Swift-package tests execute in a hostless `xctest` process where UIKit cannot
run modal presentations or dispatch control events (UIKit: *"UIApp is nil
which means we cannot dispatch control actions to their targets"*). This host
app provides a real `UIApplicationMain` context so
`MrSpicyUI/Tests/MrSpicyUITests/SpicyOverlayLifecycleTests.swift` (shared
source, reused verbatim) can execute the full open → close → reopen modal
lifecycle and `sendActions` control dispatch.

**This is not the production host.** It is not 8 Ball Pool; it exists only to
validate the component. Integration with the real game is blocked and
documented in `../validation/reports/integration-validation.md`.

## Running

```bash
xcodebuild test \
  -project MrSpicyDemoHost.xcodeproj \
  -scheme MrSpicyDemoHost \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro'
```

CI runs this automatically (job `hosted-tests` in
`.github/workflows/component-ci.yml`).
