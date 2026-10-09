import XCTest
@testable import MrSpicyUI

/// Lifecycle and integration-behavior tests for `SpicyOverlayViewController`.
///
/// These run on an iOS Simulator (see .github/workflows/component-ci.yml) and
/// exercise the real UIKit presentation lifecycle: open → close → reopen,
/// bridge callbacks, persistence writes, and accessibility wiring.
final class SpicyOverlayLifecycleTests: XCTestCase {

    private final class SpyBridge: SpicyHostBridge {
        var closeRequests = 0
        var settingsChanges: [[String: Any]] = []

        func spicyOverlayDidRequestClose(_ overlay: SpicyOverlayViewController) {
            closeRequests += 1
        }

        func spicyPreferencesDidChange(_ preferences: SpicyPreferences) {
            settingsChanges.append(preferences.snapshot())
        }
    }

    private var window: UIWindow!
    private var presenter: UIViewController!
    private var suiteName: String!
    private var preferences: SpicyPreferences!
    private var bridge: SpyBridge!
    private var overlay: SpicyOverlayViewController!

    override func setUp() {
        super.setUp()
        suiteName = "com.mrspicy.tests.overlay.\(UUID().uuidString)"
        preferences = SpicyPreferences(suiteName: suiteName)
        bridge = SpyBridge()
        overlay = SpicyOverlayViewController(preferences: preferences, bridge: bridge)

        presenter = UIViewController()
        window = UIWindow(frame: UIScreen.main.bounds)
        window.rootViewController = presenter
        window.makeKeyAndVisible()
    }

    override func tearDown() {
        overlay.close(animated: false, completion: nil)
        window.isHidden = true
        window = nil
        presenter = nil
        overlay = nil
        bridge = nil
        UserDefaults().removePersistentDomain(forName: suiteName)
        preferences = nil
        suiteName = nil
        super.tearDown()
    }

    // MARK: Helpers

    private func openOverlay(file: StaticString = #filePath, line: UInt = #line) {
        let done = expectation(description: "open completed")
        overlay.open(from: presenter, animated: false) { done.fulfill() }
        wait(for: [done], timeout: 5)
        XCTAssertTrue(overlay.isOpen, file: file, line: line)
    }

    private func closeOverlay(file: StaticString = #filePath, line: UInt = #line) {
        let done = expectation(description: "close completed")
        overlay.close(animated: false) { done.fulfill() }
        wait(for: [done], timeout: 5)
        XCTAssertFalse(overlay.isOpen, file: file, line: line)
    }

    // MARK: Lifecycle

    func testOpenCloseReopenCycle() {
        openOverlay()
        XCTAssertTrue(overlay.viewIfLoaded?.accessibilityIdentifier == SpicyAccessibility.overlayIdentifier)

        closeOverlay()
        XCTAssertNil(overlay.presentingViewController)

        // Reopen the same instance — must work without reinitialization.
        openOverlay()
        XCTAssertEqual(overlay.presentingViewController, presenter)

        closeOverlay()
    }

    func testOpenIsIdempotent() {
        openOverlay()
        let done = expectation(description: "second open completed")
        overlay.open(from: presenter, animated: false) { done.fulfill() }
        wait(for: [done], timeout: 5)
        XCTAssertTrue(overlay.isOpen)
        closeOverlay()
    }

    func testCloseIsIdempotent() {
        let done = expectation(description: "close on unopened overlay")
        overlay.close(animated: false) { done.fulfill() }
        wait(for: [done], timeout: 5)
        XCTAssertFalse(overlay.isOpen)
    }

    // MARK: Bridge behavior

    func testCloseButtonNotifiesBridgeAndCloses() {
        openOverlay()
        overlay.headerView.closeButton.sendActions(for: .touchUpInside)

        let settled = expectation(description: "dismissal settled")
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { settled.fulfill() }
        wait(for: [settled], timeout: 5)

        XCTAssertEqual(bridge.closeRequests, 1)
        XCTAssertFalse(overlay.isOpen)
    }

    func testSettingsControlWritesThroughToPersistenceAndBridge() {
        openOverlay()

        overlay.settingsView.soundSwitch.isOn = false
        overlay.settingsView.soundSwitch.sendActions(for: .valueChanged)

        XCTAssertFalse(preferences.soundEnabled)
        XCTAssertEqual(bridge.settingsChanges.count, 1)

        let reopened = SpicyPreferences(suiteName: suiteName)
        XCTAssertFalse(reopened.soundEnabled, "setting must persist to UserDefaults")

        closeOverlay()
    }

    func testHapticIntensityControlIsEnabledOnlyWhenHapticsOn() {
        openOverlay()
        XCTAssertTrue(overlay.settingsView.intensityControl.isEnabled)

        overlay.settingsView.hapticsSwitch.isOn = false
        overlay.settingsView.hapticsSwitch.sendActions(for: .valueChanged)
        XCTAssertFalse(overlay.settingsView.intensityControl.isEnabled)

        overlay.settingsView.hapticsSwitch.isOn = true
        overlay.settingsView.hapticsSwitch.sendActions(for: .valueChanged)
        XCTAssertTrue(overlay.settingsView.intensityControl.isEnabled)

        closeOverlay()
    }

    func testResetButtonRestoresDefaultsInModelAndUI() {
        openOverlay()

        preferences.soundEnabled = false
        preferences.playerNickname = "temp-name"
        overlay.settingsView.reloadFromPreferences()
        XCTAssertFalse(overlay.settingsView.soundSwitch.isOn)

        overlay.settingsView.resetButton.sendActions(for: .touchUpInside)

        XCTAssertTrue(preferences.soundEnabled)
        XCTAssertEqual(preferences.playerNickname, "")
        XCTAssertTrue(overlay.settingsView.soundSwitch.isOn, "UI must reload after reset")
        XCTAssertFalse(bridge.settingsChanges.isEmpty, "reset must notify the bridge")
    }

    // MARK: Accessibility & layout

    func testAccessibilityIdentifiersAreInstalled() {
        openOverlay()
        XCTAssertEqual(overlay.view.accessibilityIdentifier, SpicyAccessibility.overlayIdentifier)
        XCTAssertEqual(overlay.headerView.accessibilityIdentifier, SpicyAccessibility.headerIdentifier)
        XCTAssertEqual(overlay.headerView.closeButton.accessibilityIdentifier, SpicyAccessibility.closeIdentifier)
        XCTAssertEqual(overlay.settingsView.accessibilityIdentifier, SpicyAccessibility.settingsIdentifier)
        XCTAssertEqual(overlay.settingsView.resetButton.accessibilityIdentifier, SpicyAccessibility.resetIdentifier)
        XCTAssertEqual(overlay.versionLabel.accessibilityIdentifier, SpicyAccessibility.versionIdentifier)

        XCTAssertFalse(overlay.headerView.closeButton.accessibilityLabel?.isEmpty ?? true)
        XCTAssertFalse(overlay.settingsView.resetButton.accessibilityLabel?.isEmpty ?? true)
    }

    func testLayoutDirectionFollowsLocalization() {
        openOverlay()
        let expected: UISemanticContentAttribute =
            SpicyLocalization.isRightToLeft() ? .forceRightToLeft : .forceLeftToRight
        XCTAssertEqual(overlay.view.semanticContentAttribute, expected)
        closeOverlay()
    }

    func testVersionLabelShowsComponentVersion() {
        openOverlay()
        XCTAssertEqual(overlay.versionLabel.text, SpicyVersion.displayString)
    }
}
