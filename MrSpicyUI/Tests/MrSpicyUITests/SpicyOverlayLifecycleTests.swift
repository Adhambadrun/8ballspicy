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

    private final class AppearingPresenter: UIViewController {
        var appeared = false
        override func viewDidAppear(_ animated: Bool) {
            super.viewDidAppear(animated)
            appeared = true
        }
    }

    private var previousKeyWindow: UIWindow?
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

        // Cold simulator launch must finish before testing real animations.
        // Failure here is reported as host readiness, not a passed/skipped test.
        waitUntil(15, "UIApplication host did not become active", {
            UIApplication.shared.applicationState == .active
        })
        guard UIApplication.shared.applicationState == .active else {
            throw NSError(domain: "MrSpicyTestHostReadiness", code: 1)
        }
        let scene = UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
            .first { $0.activationState == .foregroundActive }
        previousKeyWindow = scene?.windows.first { $0.isKeyWindow }
            ?? UIApplication.shared.windows.first { $0.isKeyWindow }
        let root = AppearingPresenter()
        presenter = root
        if let scene = scene {
            window = UIWindow(windowScene: scene)
        } else {
            // The existing demo host supports the legacy app-delegate lifecycle.
            window = UIWindow(frame: UIScreen.main.bounds)
        }
        self.window.rootViewController = presenter
        self.window.makeKeyAndVisible()
        self.presenter.view.layoutIfNeeded()
        waitUntil(5, "test presenter did not appear", { root.appeared && root.view.window != nil && self.window.isKeyWindow })
        guard root.appeared else { throw NSError(domain: "MrSpicyTestHostReadiness", code: 2) }
    }

    override func tearDown() {
        if let presenter = presenter, presenter.presentedViewController != nil {
            waitUntil(5, "transition still active at teardown", { presenter.transitionCoordinator == nil })
            var dismissed = false
            presenter.dismiss(animated: false) { dismissed = true }
            waitUntil(5, "fixture dismissal did not complete", { dismissed && presenter.presentedViewController == nil })
        }
        self.window?.isHidden = true
        previousKeyWindow?.makeKey()
        previousKeyWindow = nil
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
        _ condition: @escaping () -> Bool,
        file: StaticString = #filePath,
        line: UInt = #line
    ) {
        let start = ProcessInfo.processInfo.systemUptime
        let expectation = XCTNSPredicateExpectation(predicate: NSPredicate { _, _ in condition() }, object: nil)
        let result = XCTWaiter.wait(for: [expectation], timeout: timeout)
        if result != .completed {
            let diagnostics = "elapsed=\(ProcessInfo.processInfo.systemUptime - start) app=\(UIApplication.shared.applicationState.rawValue) key=\(self.window?.isKeyWindow ?? false) scene=\(String(describing: self.window?.windowScene?.activationState)) presented=\(String(describing: self.presenter?.presentedViewController)) coordinator=\(String(describing: self.presenter?.transitionCoordinator)) animations=\(UIView.areAnimationsEnabled)"
            XCTFail("\(message); \(diagnostics)", file: file, line: line)
        }
    }

    private func openOverlay(file: StaticString = #filePath, line: UInt = #line) {
        var completed = false
        XCTAssertTrue(self.overlay.open(from: presenter, animated: false) { completed = true }, file: file, line: line)
        waitUntil(5, "overlay did not open", {
            completed && self.overlay.presentingViewController != nil && self.overlay.isOpen
        }, file: file, line: line)
    }

    private func closeOverlay(file: StaticString = #filePath, line: UInt = #line) {
        self.overlay.close(animated: false, completion: nil)
        waitUntil(5, "overlay did not close", {
            self.overlay.presentingViewController == nil && !self.overlay.isOpen
        }, file: file, line: line)
    }

    // MARK: Lifecycle

    func testOpenCloseReopenCycle() throws {
        openOverlay()
        XCTAssertEqual(self.overlay.view.accessibilityIdentifier, SpicyAccessibility.overlayIdentifier)

        closeOverlay()
        XCTAssertNil(self.overlay.presentingViewController)

        // Reopen the same instance — must work without reinitialization.
        openOverlay()
        XCTAssertEqual(self.overlay.presentingViewController, presenter)

        closeOverlay()
    }

    func testOpenIsIdempotent() {
        openOverlay()
        self.overlay.open(from: presenter, animated: false, completion: nil)
        spinRunLoop(0.1)
        XCTAssertTrue(self.overlay.isOpen)
        XCTAssertEqual(self.overlay.presentingViewController, presenter)
        closeOverlay()
    }

    func testCloseButtonNotifiesBridgeAndCloses() {
        openOverlay()
        self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)

        waitUntil(5, "close button did not dismiss via bridge+close", {
            self.bridge.closeRequests == 1 && self.overlay.presentingViewController == nil
        })
        waitUntil(5, "self.overlay.isOpen did not clear after dismissal", {
            !self.overlay.isOpen
        })
    }

    func testControlDispatchViaSendActionsReachesPersistenceAndBridge() {
        openOverlay()
        self.overlay.settingsView.soundSwitch.isOn = false
        self.overlay.settingsView.soundSwitch.sendActions(for: .valueChanged)

        XCTAssertFalse(preferences.soundEnabled)
        XCTAssertEqual(self.bridge.settingsChanges.count, 1)
        XCTAssertFalse(SpicyPreferences(suiteName: suiteName).soundEnabled, "setting must persist")
        closeOverlay()
    }

    func testCloseIsIdempotent() {
        self.overlay.close(animated: false, completion: nil)
        spinRunLoop(0.1)
        XCTAssertFalse(self.overlay.isOpen)
        XCTAssertNil(self.overlay.presentingViewController)
    }
    func testExternalDismissalClearsStateAndAllowsReopen() {
        openOverlay()
        self.presenter.dismiss(animated: false)
        waitUntil(5, "external dismissal did not clear state", { !self.overlay.isOpen && self.overlay.presentingViewController == nil })
        openOverlay()
        closeOverlay()
    }

    func testBusyPresenterIsRejectedWithoutFalseOpenState() {
        let blocker = UIViewController()
        self.presenter.present(blocker, animated: false)
        waitUntil(5, "blocker not presented", { self.presenter.presentedViewController === blocker })
        XCTAssertFalse(self.overlay.open(from: presenter, animated: false))
        XCTAssertFalse(self.overlay.isOpen)
        XCTAssertNil(self.overlay.presentingViewController)
        self.presenter.dismiss(animated: false)
    }

    func testPreferencesReloadWhenReopened() {
        openOverlay()
        closeOverlay()
        preferences.soundEnabled = false
        openOverlay()
        XCTAssertFalse(self.overlay.settingsView.soundSwitch.isOn)
        closeOverlay()
    }

    func testAnimatedTransitionRejectsDuplicateRequests() {
        var opened = false
        XCTAssertTrue(self.overlay.open(from: presenter, animated: true) { opened = true })
        XCTAssertFalse(self.overlay.open(from: presenter, animated: true))
        XCTAssertFalse(self.overlay.close(animated: true))
        waitUntil(5, "animated presentation completion missing", { opened })
        var closed = false
        XCTAssertTrue(self.overlay.close(animated: true) { closed = true })
        XCTAssertFalse(self.overlay.close(animated: true))
        XCTAssertFalse(self.overlay.open(from: presenter, animated: true))
        waitUntil(5, "animated dismissal completion missing", { closed && !self.overlay.isOpen })
    }

    func testArabicHeaderActuallyMirrorsAndCanClose() {
        self.overlay.refreshLocalization(language: "ar")
        openOverlay()
        self.overlay.view.layoutIfNeeded()
        let header = self.overlay.headerView!
        let mark = header.markImageView.convert(header.markImageView.bounds, to: self.overlay.view)
        let close = header.closeButton.convert(header.closeButton.bounds, to: self.overlay.view)
        XCTAssertGreaterThan(mark.midX, close.midX, "Arabic leading/trailing geometry must mirror, not just translate text")
        XCTAssertGreaterThanOrEqual(close.width, 44)
        XCTAssertGreaterThanOrEqual(close.height, 44)
        XCTAssertGreaterThan(mark.width, 0)
        closeOverlay()
    }

    func testUserCloseDuringOpeningIsQueuedOnceAndAllowsReopen() {
        XCTAssertTrue(self.overlay.open(from: presenter, animated: true))
        self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(self.bridge.closeRequests, 1, "Repeated user taps during opening must not duplicate the bridge request")
        waitUntil(5, "queued user close was dropped", { self.overlay.presentingViewController == nil && !self.overlay.isOpen })
        openOverlay()
        closeOverlay()
    }

    func testReopenInsideCloseCompletionUsesFreshCycle() {
        openOverlay()
        var closedCount = 0
        var openedCount = 0
        XCTAssertTrue(self.overlay.close(animated: true) {
            closedCount += 1
            XCTAssertTrue(self.overlay.open(from: self.presenter, animated: true) { openedCount += 1 })
        })
        waitUntil(5, "reentrant reopen did not finish", { closedCount == 1 && openedCount == 1 && self.overlay.isOpen })
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
        self.window.rootViewController = rejecting
        rejecting.view.layoutIfNeeded()
        spinRunLoop(0.2)
        var completions = 0
        XCTAssertFalse(self.overlay.open(from: rejecting, animated: true) { completions += 1 })
        XCTAssertEqual(completions, 1)
        XCTAssertFalse(self.overlay.isOpen)
        rejecting.deferredCompletion?()
        XCTAssertEqual(completions, 1, "Rejected presentation must not complete twice")
        openOverlayAfterRestoringPresenter()
    }

    private func openOverlayAfterRestoringPresenter() {
        self.window.rootViewController = presenter
        self.presenter.view.layoutIfNeeded()
        spinRunLoop(0.2)
        openOverlay()
        closeOverlay()
    }

    func testReentrantBridgeCloseRequestIsDeduplicatedWhileOpening() {
        var nested = false
        self.bridge.onCloseRequest = {
            if !nested {
                nested = true
                self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
            }
        }
        XCTAssertTrue(self.overlay.open(from: presenter, animated: true))
        self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(self.bridge.closeRequests, 1)
        waitUntil(5, "reentrant user close did not finish", { self.overlay.presentingViewController == nil && !self.overlay.isOpen })
        self.bridge.onCloseRequest = nil
        openOverlay()
        closeOverlay()
    }

    func testReentrantCloseBridgeWhileOpenFiresOncePerCycle() {
        openOverlay()
        var nested = false
        self.bridge.onCloseRequest = {
            if !nested {
                nested = true
                self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
            }
        }
        self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(self.bridge.closeRequests, 1)
        waitUntil(5, "reentrant open-state close did not finish", { self.overlay.presentingViewController == nil && !self.overlay.isOpen })
        self.bridge.onCloseRequest = nil
        openOverlay()
        self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(self.bridge.closeRequests, 2, "New presentation must re-arm the user-close event")
        waitUntil(5, "second-cycle user close did not finish", { self.overlay.presentingViewController == nil && !self.overlay.isOpen })
    }

    func testDetachedCloseButtonDoesNotNotifyBridge() {
        self.overlay.loadViewIfNeeded()
        self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(self.bridge.closeRequests, 0)
        openOverlay()
        closeOverlay()
        self.overlay.headerView.closeButton.sendActions(for: .touchUpInside)
        XCTAssertEqual(self.bridge.closeRequests, 0, "Programmatic dismissal and stale control events are not user close requests")
    }

    func testNonanimatedOpenCompletionMayCloseWithoutFalseRejection() {
        var opened = 0
        var closed = 0
        let accepted = self.overlay.open(from: presenter, animated: false) {
            opened += 1
            XCTAssertTrue(self.overlay.close(animated: false) { closed += 1 })
        }
        XCTAssertTrue(accepted, "Accepted nonanimated presentation may finish and close before open returns")
        waitUntil(5, "completion-driven dismissal did not finish", { opened == 1 && closed == 1 && self.overlay.presentingViewController == nil })
        XCTAssertEqual(opened, 1)
        XCTAssertEqual(closed, 1)
        openOverlay()
        closeOverlay()
    }

}
