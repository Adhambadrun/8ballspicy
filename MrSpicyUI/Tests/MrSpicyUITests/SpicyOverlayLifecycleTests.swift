import XCTest
@testable import MrSpicyUI

/// Modal presentation lifecycle tests: open → close → reopen on one instance,
/// plus end-to-end control dispatch through `sendActions`.
///
/// Both facilities require UIApplicationMain (a host application). In the
/// hostless `xctest` process used for Swift package tests UIKit asserts
/// "UIApp is nil which means we cannot dispatch control actions to their
/// targets" and modal transitions never complete. When no UIApplication is
/// present these tests SKIP with that documented reason instead of producing
/// false results; on a hosted test runner (or a UI test target) they execute
/// in full.
final class SpicyOverlayLifecycleTests: XCTestCase {

    private final class SpyBridge: SpicyHostBridge {
        var closeRequests = 0
        var onCloseRequest: (() -> Void)?
        var settingsChanges: [[String: Any]] = []
        func spicyOverlayDidRequestClose(_ overlay: SpicyOverlayViewController) {
            closeRequests += 1
            onCloseRequest?()
        }
        func spicyPreferencesDidChange(_ preferences: SpicyPreferences) {
            settingsChanges.append(preferences.snapshot())
        }
    }

    /// True only when the tests run inside a real UIApplication (host app).
    ///
    /// Hosted unit-test bundles execute inside the host app (.app main bundle);
    /// Swift-package tests execute in the bare `xctest` runner, where UIKit
    /// asserts "UIApp is nil which means we cannot dispatch control actions to
    /// their targets" and modal transitions never complete.
    private func requireApplicationHost() throws {
        let hosted = Bundle.main.bundleURL.pathExtension == "app"
        try XCTSkipUnless(
            hosted,
            "Requires a UIApplication host app: hostless xctest cannot run UIKit modal presentation or control event dispatch (UIKit: 'UIApp is nil which means we cannot dispatch control actions to their targets')"
        )
    }

    private var window: UIWindow!
    private var presenter: UIViewController!
    private var suiteName: String!
    private var preferences: SpicyPreferences!
    private var bridge: SpyBridge!
    private var overlay: SpicyOverlayViewController!

    override func setUpWithError() throws {
        try super.setUpWithError()
        try requireApplicationHost()

        suiteName = "com.mrspicy.tests.overlay.\(UUID().uuidString)"
        preferences = SpicyPreferences(suiteName: suiteName)
        bridge = SpyBridge()
        overlay = SpicyOverlayViewController(preferences: preferences, bridge: bridge)

        presenter = UIViewController()
        window = UIWindow(frame: UIScreen.main.bounds)
        window.rootViewController = presenter
        window.makeKeyAndVisible()
        // Let UIKit complete the root view controller's appearance transition
        // before attempting modal presentations.
        presenter.view.layoutIfNeeded()
        spinRunLoop(0.2)
    }

    override func tearDown() {
        overlay?.close(animated: false, completion: nil)
        spinRunLoop(0.1)
        window?.isHidden = true
        window = nil
        presenter = nil
        overlay = nil
        bridge = nil
        if let suiteName = suiteName {
            UserDefaults().removePersistentDomain(forName: suiteName)
        }
        preferences = nil
        suiteName = nil
        super.tearDown()
    }

    // MARK: Helpers

    private func spinRunLoop(_ seconds: TimeInterval) {
        let end = Date().addingTimeInterval(seconds)
        while Date() < end {
            RunLoop.main.run(until: Date().addingTimeInterval(0.02))
        }
    }

    private func waitUntil(
        _ timeout: TimeInterval = 5,
        _ message: String = "condition not met",
        _ condition: () -> Bool,
        file: StaticString = #filePath,
        line: UInt = #line
    ) {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline {
            if condition() { return }
            RunLoop.main.run(until: Date().addingTimeInterval(0.02))
        }
        if !condition() {
            XCTFail(message, file: file, line: line)
        }
    }

    private func openOverlay(file: StaticString = #filePath, line: UInt = #line) {
        var completed = false
        XCTAssertTrue(overlay.open(from: presenter, animated: false) { completed = true }, file: file, line: line)
        waitUntil(5, "overlay did not open", {
            completed && overlay.presentingViewController != nil && overlay.isOpen
        }, file: file, line: line)
    }

    private func closeOverlay(file: StaticString = #filePath, line: UInt = #line) {
        overlay.close(animated: false, completion: nil)
        waitUntil(5, "overlay did not close", {
            overlay.presentingViewController == nil && !overlay.isOpen
        }, file: file, line: line)
    }

    // MARK: Lifecycle

    func testOpenCloseReopenCycle() throws {
        openOverlay()
        XCTAssertEqual(overlay.view.accessibilityIdentifier, SpicyAccessibility.overlayIdentifier)

        closeOverlay()
        XCTAssertNil(overlay.presentingViewController)

        // Reopen the same instance — must work without reinitialization.
        openOverlay()
        XCTAssertEqual(overlay.presentingViewController, presenter)

        closeOverlay()
    }

    func testOpenIsIdempotent() {
        openOverlay()
        overlay.open(from: presenter, animated: false, completion: nil)
        spinRunLoop(0.1)
        XCTAssertTrue(overlay.isOpen)
        XCTAssertEqual(overlay.presentingViewController, presenter)
        closeOverlay()
    }

    func testCloseButtonNotifiesBridgeAndCloses() {
        openOverlay()
        overlay.headerView.closeButton.sendActions(for: .touchUpInside)

        waitUntil(5, "close button did not dismiss via bridge+close", {
            bridge.closeRequests == 1 && overlay.presentingViewController == nil
        })
        waitUntil(5, "overlay.isOpen did not clear after dismissal", {
            !overlay.isOpen
        })
    }

    func testControlDispatchViaSendActionsReachesPersistenceAndBridge() {
        openOverlay()
        overlay.settingsView.soundSwitch.isOn = false
        overlay.settingsView.soundSwitch.sendActions(for: .valueChanged)

        XCTAssertFalse(preferences.soundEnabled)
        XCTAssertEqual(bridge.settingsChanges.count, 1)
        XCTAssertFalse(SpicyPreferences(suiteName: suiteName).soundEnabled, "setting must persist")
        closeOverlay()
    }

    func testCloseIsIdempotent() {
        overlay.close(animated: false, completion: nil)
        spinRunLoop(0.1)
        XCTAssertFalse(overlay.isOpen)
        XCTAssertNil(overlay.presentingViewController)
    }
    func testExternalDismissalClearsStateAndAllowsReopen() {
        openOverlay()
        presenter.dismiss(animated: false)
        waitUntil(5, "external dismissal did not clear state", { !overlay.isOpen && overlay.presentingViewController == nil })
        openOverlay()
        closeOverlay()
    }

    func testBusyPresenterIsRejectedWithoutFalseOpenState() {
        let blocker = UIViewController()
        presenter.present(blocker, animated: false)
        waitUntil(5, "blocker not presented", { presenter.presentedViewController === blocker })
        XCTAssertFalse(overlay.open(from: presenter, animated: false))
        XCTAssertFalse(overlay.isOpen)
        XCTAssertNil(overlay.presentingViewController)
        presenter.dismiss(animated: false)
    }

    func testPreferencesReloadWhenReopened() {
        openOverlay()
        closeOverlay()
        preferences.soundEnabled = false
        openOverlay()
        XCTAssertFalse(overlay.settingsView.soundSwitch.isOn)
        closeOverlay()
    }

    func testAnimatedTransitionRejectsDuplicateRequests() {
        var opened = false
        XCTAssertTrue(overlay.open(from: presenter, animated: true) { opened = true })
        XCTAssertFalse(overlay.open(from: presenter, animated: true))
        XCTAssertFalse(overlay.close(animated: true))
        waitUntil(5, "animated presentation completion missing", { opened })
        var closed = false
        XCTAssertTrue(overlay.close(animated: true) { closed = true })
        XCTAssertFalse(overlay.close(animated: true))
        XCTAssertFalse(overlay.open(from: presenter, animated: true))
        waitUntil(5, "animated dismissal completion missing", { closed && !overlay.isOpen })
    }

    func testArabicHeaderActuallyMirrorsAndCanClose() {
        overlay.refreshLocalization(language: "ar")
        openOverlay()
        overlay.view.layoutIfNeeded()
        let header = overlay.headerView!
        let mark = header.markImageView.convert(header.markImageView.bounds, to: overlay.view)
        let close = header.closeButton.convert(header.closeButton.bounds, to: overlay.view)
        XCTAssertGreaterThan(mark.midX, close.midX, "Arabic leading/trailing geometry must mirror, not just translate text")
        XCTAssertGreaterThanOrEqual(close.width, 44)
        XCTAssertGreaterThanOrEqual(close.height, 44)
        XCTAssertGreaterThan(mark.width, 0)
        closeOverlay()
    }

    func testUserCloseDuringOpeningIsQueuedOnceAndAllowsReopen() {
        XCTAssertTrue(overlay.open(from: presenter, animated: true))
        overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(bridge.closeRequests, 1, "Repeated user taps during opening must not duplicate the bridge request")
        waitUntil(5, "queued user close was dropped", { overlay.presentingViewController == nil && !overlay.isOpen })
        openOverlay()
        closeOverlay()
    }

    func testReopenInsideCloseCompletionUsesFreshCycle() {
        openOverlay()
        var closedCount = 0
        var openedCount = 0
        XCTAssertTrue(overlay.close(animated: true) {
            closedCount += 1
            XCTAssertTrue(self.overlay.open(from: self.presenter, animated: true) { openedCount += 1 })
        })
        waitUntil(5, "reentrant reopen did not finish", { closedCount == 1 && openedCount == 1 && overlay.isOpen })
        XCTAssertEqual(closedCount, 1)
        XCTAssertEqual(openedCount, 1)
        closeOverlay()
    }

    // A deliberate failure-path stub, NOT proof of real modal presentation.
    private final class DeferredRejectingPresenter: UIViewController {
        var deferredCompletion: (() -> Void)?
        override func present(_ viewControllerToPresent: UIViewController, animated flag: Bool, completion: (() -> Void)? = nil) {
            deferredCompletion = completion
        }
    }

    func testRejectedPresentationLateCompletionIsDeliveredOnlyOnce() {
        let rejecting = DeferredRejectingPresenter()
        window.rootViewController = rejecting
        rejecting.view.layoutIfNeeded()
        spinRunLoop(0.2)
        var completions = 0
        XCTAssertFalse(overlay.open(from: rejecting, animated: true) { completions += 1 })
        XCTAssertEqual(completions, 1)
        XCTAssertFalse(overlay.isOpen)
        rejecting.deferredCompletion?()
        XCTAssertEqual(completions, 1, "Rejected presentation must not complete twice")
        openOverlayAfterRestoringPresenter()
    }

    private func openOverlayAfterRestoringPresenter() {
        window.rootViewController = presenter
        presenter.view.layoutIfNeeded()
        spinRunLoop(0.2)
        openOverlay()
        closeOverlay()
    }

    func testReentrantBridgeCloseRequestIsDeduplicatedWhileOpening() {
        var nested = false
        bridge.onCloseRequest = {
            if !nested {
                nested = true
                self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
            }
        }
        XCTAssertTrue(overlay.open(from: presenter, animated: true))
        overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(bridge.closeRequests, 1)
        waitUntil(5, "reentrant user close did not finish", { overlay.presentingViewController == nil && !overlay.isOpen })
        bridge.onCloseRequest = nil
        openOverlay()
        closeOverlay()
    }

    func testReentrantCloseBridgeWhileOpenFiresOncePerCycle() {
        openOverlay()
        var nested = false
        bridge.onCloseRequest = {
            if !nested {
                nested = true
                self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
            }
        }
        overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(bridge.closeRequests, 1)
        waitUntil(5, "reentrant open-state close did not finish", { overlay.presentingViewController == nil && !overlay.isOpen })
        bridge.onCloseRequest = nil
        openOverlay()
        overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(bridge.closeRequests, 2, "New presentation must re-arm the user-close event")
        waitUntil(5, "second-cycle user close did not finish", { overlay.presentingViewController == nil && !overlay.isOpen })
    }

    func testDetachedCloseButtonDoesNotNotifyBridge() {
        overlay.loadViewIfNeeded()
        overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(bridge.closeRequests, 0)
        openOverlay()
        closeOverlay()
        overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(bridge.closeRequests, 0, "Programmatic dismissal and stale control events are not user close requests")
    }

    func testNonanimatedOpenCompletionMayCloseWithoutFalseRejection() {
        var opened = 0
        var closed = 0
        let accepted = overlay.open(from: presenter, animated: false) {
            opened += 1
            XCTAssertTrue(self.overlay.close(animated: false) { closed += 1 })
        }
        XCTAssertTrue(accepted, "Accepted nonanimated presentation may finish and close before open returns")
        waitUntil(5, "completion-driven dismissal did not finish", { opened == 1 && closed == 1 && overlay.presentingViewController == nil })
        XCTAssertEqual(opened, 1)
        XCTAssertEqual(closed, 1)
        openOverlay()
        closeOverlay()
    }

}
