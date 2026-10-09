import XCTest
@testable import MrSpicyUI

/// Control wiring and behavior tests.
///
/// These run in a hostless `xctest` process (no UIApplicationMain — confirmed
/// by the UIKit assert "UIApp is nil which means we cannot dispatch control
/// actions to their targets" when `sendActions` is used there). Therefore:
///  - wiring is asserted through `UIControl.actions(forTarget:forControlEvent:)`
///    (the same registry `sendActions` consults), and
///  - behavior is asserted by invoking the registered handler methods
///    directly (`@objc` handlers are the actual target-action entry points).
/// End-to-end event dispatch and modal presentation require a UIApplication
/// host and are covered by `SpicyOverlayLifecycleTests` (skipped when
/// hostless).
final class SpicyOverlayControlTests: XCTestCase {

    private final class SpyBridge: SpicyHostBridge {
        var closeRequests = 0
        var settingsChanges: [[String: Any]] = []
        func spicyOverlayDidRequestClose(_ overlay: SpicyOverlayViewController) { closeRequests += 1 }
        func spicyPreferencesDidChange(_ preferences: SpicyPreferences) {
            settingsChanges.append(preferences.snapshot())
        }
    }

    private var suiteName: String!
    private var preferences: SpicyPreferences!
    private var bridge: SpyBridge!
    private var overlay: SpicyOverlayViewController!

    override func setUp() {
        super.setUp()
        suiteName = "com.mrspicy.tests.controls.\(UUID().uuidString)"
        preferences = SpicyPreferences(suiteName: suiteName)
        bridge = SpyBridge()
        overlay = SpicyOverlayViewController(preferences: preferences, bridge: bridge)
        overlay.loadViewIfNeeded()
    }

    override func tearDown() {
        overlay = nil
        bridge = nil
        UserDefaults().removePersistentDomain(forName: suiteName)
        preferences = nil
        suiteName = nil
        super.tearDown()
    }

    // MARK: Wiring (what sendActions would dispatch)

    private func assertWired(
        _ control: UIControl,
        to target: AnyObject,
        selectorName: String,
        event: UIControl.Event = .valueChanged,
        file: StaticString = #filePath,
        line: UInt = #line
    ) {
        let actions = control.actions(forTarget: target, forControlEvent: event) ?? []
        XCTAssertTrue(
            actions.contains(selectorName),
            "\(control) is not wired to \(selectorName) for \(event); wired: \(actions)",
            file: file,
            line: line
        )
    }

    func testEveryControlIsWiredToItsHandler() {
        let settings = overlay.settingsView!
        assertWired(settings.soundSwitch, to: settings, selectorName: "soundChanged")
        assertWired(settings.hapticsSwitch, to: settings, selectorName: "hapticsChanged")
        assertWired(settings.intensityControl, to: settings, selectorName: "intensityChanged")
        assertWired(settings.notificationsSwitch, to: settings, selectorName: "notificationsChanged")
        assertWired(settings.personalizationSwitch, to: settings, selectorName: "personalizationChanged")
        assertWired(settings.nicknameField, to: settings, selectorName: "nicknameChanged", event: .editingChanged)
        assertWired(settings.resetButton, to: settings, selectorName: "resetTapped", event: .touchUpInside)
        assertWired(overlay.headerView.closeButton, to: overlay.headerView, selectorName: "closeTapped", event: .touchUpInside)
    }

    // MARK: Behavior (handler entry points)

    func testSoundHandlerWritesPersistenceAndNotifiesBridge() {
        let settings = overlay.settingsView!
        settings.soundSwitch.isOn = false
        settings.soundChanged()
        XCTAssertFalse(preferences.soundEnabled)
        XCTAssertEqual(bridge.settingsChanges.count, 1)
        XCTAssertFalse(SpicyPreferences(suiteName: suiteName).soundEnabled, "must persist")
    }

    func testHapticsHandlerTogglesIntensityControl() {
        let settings = overlay.settingsView!
        XCTAssertTrue(settings.intensityControl.isEnabled)

        settings.hapticsSwitch.isOn = false
        settings.hapticsChanged()
        XCTAssertFalse(settings.intensityControl.isEnabled)
        XCTAssertFalse(preferences.hapticsEnabled)

        settings.hapticsSwitch.isOn = true
        settings.hapticsChanged()
        XCTAssertTrue(settings.intensityControl.isEnabled)
        XCTAssertTrue(preferences.hapticsEnabled)
    }

    func testIntensityHandlerPersistsSelection() {
        let settings = overlay.settingsView!
        let index = SpicyHapticIntensity.allCases.firstIndex(of: .strong)!
        settings.intensityControl.selectedSegmentIndex = index
        settings.intensityChanged()
        XCTAssertEqual(preferences.hapticIntensity, .strong)
        XCTAssertEqual(bridge.settingsChanges.count, 1)
    }

    func testNicknameHandlerPersistsText() {
        let settings = overlay.settingsView!
        settings.nicknameField.text = "SpicyOne"
        settings.nicknameChanged()
        XCTAssertEqual(preferences.playerNickname, "SpicyOne")
    }

    func testResetHandlerRestoresDefaultsInModelAndUI() {
        let settings = overlay.settingsView!
        preferences.soundEnabled = false
        preferences.playerNickname = "temp-name"
        settings.reloadFromPreferences()
        XCTAssertFalse(settings.soundSwitch.isOn)

        settings.resetTapped()

        XCTAssertTrue(preferences.soundEnabled)
        XCTAssertEqual(preferences.playerNickname, "")
        XCTAssertTrue(settings.soundSwitch.isOn, "UI must reload after reset")
        XCTAssertFalse(bridge.settingsChanges.isEmpty, "reset must notify the bridge")
    }

    func testDetachedCloseHandlerDoesNotNotifyBridge() {
        // No modal presentation in this suite. Real user-close dispatch is
        // covered in hosted lifecycle tests; stale detached handlers do nothing.
        overlay.headerView.closeTapped()
        XCTAssertEqual(bridge.closeRequests, 0, "detached handler must not notify the host bridge")
    }

    // MARK: View-level configuration (no presentation required)

    func testAccessibilityIdentifiersAreInstalled() {
        let view = overlay.view!
        XCTAssertEqual(view.accessibilityIdentifier, SpicyAccessibility.overlayIdentifier)
        XCTAssertEqual(overlay.headerView.accessibilityIdentifier, SpicyAccessibility.headerIdentifier)
        XCTAssertEqual(overlay.headerView.closeButton.accessibilityIdentifier, SpicyAccessibility.closeIdentifier)
        XCTAssertEqual(overlay.settingsView.accessibilityIdentifier, SpicyAccessibility.settingsIdentifier)
        XCTAssertEqual(overlay.settingsView.resetButton.accessibilityIdentifier, SpicyAccessibility.resetIdentifier)
        XCTAssertEqual(overlay.versionLabel.accessibilityIdentifier, SpicyAccessibility.versionIdentifier)
        XCTAssertFalse(overlay.headerView.closeButton.accessibilityLabel?.isEmpty ?? true)
        XCTAssertFalse(overlay.settingsView.resetButton.accessibilityLabel?.isEmpty ?? true)
    }

    func testLayoutDirectionFollowsLocalization() {
        let expected: UISemanticContentAttribute =
            SpicyLocalization.isRightToLeft() ? .forceRightToLeft : .forceLeftToRight
        XCTAssertEqual(overlay.view.semanticContentAttribute, expected)
    }

    func testVersionLabelShowsComponentVersion() {
        XCTAssertEqual(overlay.versionLabel.text, SpicyVersion.displayString)
    }
    func testArabicRefreshUpdatesEveryControlAndDirection() {
        overlay.refreshLocalization(language: "ar")
        let settings = overlay.settingsView!
        XCTAssertEqual(overlay.view.semanticContentAttribute, .forceRightToLeft)
        XCTAssertEqual(overlay.headerView.titleLabel.text, SpicyLocalization.string("mr.spicy.header.title", language: "ar"))
        XCTAssertEqual(settings.soundSwitch.accessibilityLabel, SpicyLocalization.string("mr.spicy.settings.sound", language: "ar"))
        XCTAssertEqual(settings.nicknameField.accessibilityLabel, SpicyLocalization.string("mr.spicy.settings.nickname", language: "ar"))
        XCTAssertEqual(settings.intensityControl.titleForSegment(at: 0), SpicyLocalization.string("mr.spicy.settings.haptic.off", language: "ar"))
        overlay.refreshLocalization(language: "en")
        XCTAssertEqual(overlay.view.semanticContentAttribute, .forceLeftToRight)
        XCTAssertEqual(settings.soundSwitch.accessibilityLabel, SpicyLocalization.string("mr.spicy.settings.sound", language: "en"))
    }

    func testAllSettingsHaveAccessibilityLabels() {
        let settings = overlay.settingsView!
        for control in [settings.soundSwitch, settings.hapticsSwitch, settings.notificationsSwitch,
                        settings.personalizationSwitch, settings.intensityControl, settings.nicknameField,
                        settings.resetButton] as [UIView] {
            XCTAssertFalse(control.accessibilityLabel?.isEmpty ?? true)
            XCTAssertNotNil(control.accessibilityIdentifier)
        }
        XCTAssertTrue(overlay.view.accessibilityViewIsModal)
    }

    func testInvalidIntensityDoesNotMutateOrNotify() {
        overlay.settingsView.intensityControl.selectedSegmentIndex = UISegmentedControl.noSegment
        overlay.settingsView.intensityChanged()
        XCTAssertEqual(preferences.hapticIntensity, .medium)
        XCTAssertTrue(bridge.settingsChanges.isEmpty)
    }

    func testDetachedPresenterIsRejectedAndCompletionRuns() {
        var completed = false
        XCTAssertFalse(overlay.open(from: UIViewController(), animated: false) { completed = true })
        XCTAssertTrue(completed)
        XCTAssertFalse(overlay.isOpen)
        XCTAssertNil(overlay.presentingViewController)
    }

    func testLanguageSelectedBeforeLoadingIsRetained() {
        let fresh = SpicyOverlayViewController(preferences: preferences)
        fresh.refreshLocalization(language: "ar")
        fresh.loadViewIfNeeded()
        XCTAssertEqual(fresh.view.semanticContentAttribute, .forceRightToLeft)
        XCTAssertEqual(fresh.settingsView.soundSwitch.accessibilityLabel, SpicyLocalization.string("mr.spicy.settings.sound", language: "ar"))
    }

    func testProReferenceDisclosesUnavailableWithoutActivationControls() {
        overlay.refreshLocalization(language: "en")
        func findLabel(_ view: UIView) -> UILabel? {
            if view.accessibilityIdentifier == "mr.spicy.pro.reference" { return view as? UILabel }
            for child in view.subviews { if let label = findLabel(child) { return label } }
            return nil
        }
        let label = findLabel(overlay.view)
        XCTAssertEqual(label?.text, SpicyLocalization.string("mr.spicy.pro.reference", language: "en"))
        XCTAssertTrue(label?.text?.contains("unavailable") ?? false)
        XCTAssertFalse(label?.isUserInteractionEnabled ?? true)
        overlay.refreshLocalization(language: "ar")
        XCTAssertEqual(label?.text, SpicyLocalization.string("mr.spicy.pro.reference", language: "ar"))
    }

}
