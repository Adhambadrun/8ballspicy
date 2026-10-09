import UIKit

/// The Mr. Spicy overlay interface.
///
/// Lifecycle contract for hosts:
/// 1. `open(from:animated:completion:)` presents the interface.
/// 2. The close button (or `close(animated:completion:)`) dismisses it. Only a user close-button request
///    notifies `SpicyHostBridge`.
/// 3. The same instance can be opened again after it closes (verified by tests).
///
/// The overlay is self-contained: it owns its theme, localization, and
/// persistent settings. Hosts integrate solely through `SpicyHostBridge` plus
/// the open/close API — there is no dependency on the host's internals.
public final class SpicyOverlayViewController: UIViewController {

    // MARK: Public state

    public let preferences: SpicyPreferences
    public let theme: SpicyTheme
    public weak var bridge: SpicyHostBridge?

    /// True while the interface is on screen (presented and not dismissed).
    public var isOpen: Bool { presentingViewController != nil && !isBeingDismissed }
    private var isOpening = false
    private var isClosing = false
    private var language: String?
    private var proReferenceLabel: UILabel!

    // MARK: Subviews

    public private(set) var headerView: SpicyHeaderView!
    public private(set) var settingsView: SpicySettingsView!

    private let cardView = UIView()
    public let versionLabel = UILabel()

    // MARK: Init

    public init(
        preferences: SpicyPreferences = SpicyPreferences(),
        theme: SpicyTheme = .default,
        bridge: SpicyHostBridge? = nil
    ) {
        self.preferences = preferences
        self.theme = theme
        self.bridge = bridge
        super.init(nibName: nil, bundle: nil)
        modalPresentationStyle = .overFullScreen
        modalTransitionStyle = .crossDissolve
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) is not supported")
    }

    // MARK: View lifecycle

    public override func viewDidLoad() {
        super.viewDidLoad()
        view.accessibilityIdentifier = SpicyAccessibility.overlayIdentifier
        view.accessibilityViewIsModal = true
        applyLayoutDirection()
        buildLayout()
        wireCallbacks()
        refreshLocalization(language: language)
    }

    private func applyLayoutDirection() {
        let rtl = SpicyLocalization.isRightToLeft(language: language)
        view.semanticContentAttribute = rtl ? .forceRightToLeft : .forceLeftToRight
    }

    private func buildLayout() {
        view.backgroundColor = theme.background.withAlphaComponent(0.92)

        cardView.translatesAutoresizingMaskIntoConstraints = false
        cardView.backgroundColor = theme.surface
        cardView.layer.cornerRadius = theme.cornerRadius
        cardView.layer.borderWidth = 1
        cardView.layer.borderColor = theme.separator.cgColor
        view.addSubview(cardView)

        headerView = SpicyHeaderView(theme: theme)
        settingsView = SpicySettingsView(preferences: preferences, theme: theme)

        versionLabel.translatesAutoresizingMaskIntoConstraints = false
        versionLabel.font = .systemFont(ofSize: 12, weight: .regular)
        versionLabel.textColor = theme.textSecondary
        versionLabel.textAlignment = .center
        versionLabel.accessibilityIdentifier = SpicyAccessibility.versionIdentifier

        let scroll = UIScrollView()
        scroll.translatesAutoresizingMaskIntoConstraints = false
        cardView.addSubview(scroll)
        proReferenceLabel = UILabel()
        proReferenceLabel.numberOfLines = 0
        proReferenceLabel.font = .preferredFont(forTextStyle: .footnote)
        proReferenceLabel.adjustsFontForContentSizeCategory = true
        proReferenceLabel.textColor = theme.textSecondary
        proReferenceLabel.accessibilityIdentifier = "mr.spicy.pro.reference"
        let referenceContainer = UIView()
        referenceContainer.addSubview(proReferenceLabel)
        proReferenceLabel.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            proReferenceLabel.topAnchor.constraint(equalTo: referenceContainer.topAnchor, constant: 8),
            proReferenceLabel.bottomAnchor.constraint(equalTo: referenceContainer.bottomAnchor, constant: -12),
            proReferenceLabel.leadingAnchor.constraint(equalTo: referenceContainer.leadingAnchor, constant: theme.contentInset),
            proReferenceLabel.trailingAnchor.constraint(equalTo: referenceContainer.trailingAnchor, constant: -theme.contentInset)
        ])
        let contentStack = UIStackView(arrangedSubviews: [headerView, settingsView, referenceContainer, versionLabel])
        contentStack.translatesAutoresizingMaskIntoConstraints = false
        contentStack.axis = .vertical
        contentStack.spacing = 0
        scroll.addSubview(contentStack)

        NSLayoutConstraint.activate([
            cardView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            cardView.centerYAnchor.constraint(equalTo: view.safeAreaLayoutGuide.centerYAnchor),
            cardView.topAnchor.constraint(greaterThanOrEqualTo: view.safeAreaLayoutGuide.topAnchor, constant: 12),
            cardView.bottomAnchor.constraint(lessThanOrEqualTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -12),
            cardView.leadingAnchor.constraint(greaterThanOrEqualTo: view.leadingAnchor, constant: 24),
            cardView.trailingAnchor.constraint(lessThanOrEqualTo: view.trailingAnchor, constant: -24),
            cardView.widthAnchor.constraint(lessThanOrEqualToConstant: 480),
            cardView.widthAnchor.constraint(equalTo: view.widthAnchor, multiplier: 0.9).withPriority(.defaultHigh),

            scroll.topAnchor.constraint(equalTo: cardView.topAnchor),
            scroll.leadingAnchor.constraint(equalTo: cardView.leadingAnchor),
            scroll.trailingAnchor.constraint(equalTo: cardView.trailingAnchor),
            scroll.bottomAnchor.constraint(equalTo: cardView.bottomAnchor),
            scroll.heightAnchor.constraint(equalTo: contentStack.heightAnchor).withPriority(.defaultHigh),
            contentStack.topAnchor.constraint(equalTo: scroll.contentLayoutGuide.topAnchor),
            contentStack.leadingAnchor.constraint(equalTo: scroll.contentLayoutGuide.leadingAnchor),
            contentStack.trailingAnchor.constraint(equalTo: scroll.contentLayoutGuide.trailingAnchor),
            contentStack.bottomAnchor.constraint(equalTo: scroll.contentLayoutGuide.bottomAnchor),
            contentStack.widthAnchor.constraint(equalTo: scroll.frameLayoutGuide.widthAnchor)
        ])
    }

    private func wireCallbacks() {
        headerView.onCloseTapped = { [weak self] in
            guard let self = self else { return }
            self.bridge?.spicyOverlayDidRequestClose(self)
            self.close(animated: true, completion: nil)
        }
        settingsView.onSettingsChanged = { [weak self] preferences in
            guard let self = self else { return }
            self.bridge?.spicyPreferencesDidChange(preferences)
        }
    }

    /// Re-resolves localized content (safe to call at any time).
    public func refreshLocalization(language: String? = nil) {
        self.language = language
        if isViewLoaded { applyLayoutDirection() }
        headerView?.refreshLocalization(language: language)
        settingsView?.refreshLocalization(language: language)
        versionLabel.text = SpicyVersion.displayString
        proReferenceLabel?.text = SpicyLocalization.string("mr.spicy.pro.reference", language: language)
    }

    // MARK: Open / close / reopen

    /// Presents the Mr. Spicy interface from `presenter`.
    ///
    /// Safe to call when already open (keeps the interface on screen and still
    /// invokes `completion`) and safe to call again after a close — the same
    /// instance supports unlimited open/close/reopen cycles.
    /// Returns false for detached/busy presenters or in-flight transitions.
    /// Completion is called even for rejected requests; inspect the Bool result.
    @discardableResult
    public func open(
        from presenter: UIViewController,
        animated: Bool,
        completion: (() -> Void)? = nil
    ) -> Bool {
        precondition(Thread.isMainThread, "UIKit presentation requires the main thread")
        // Reject ambiguous transitions; don't issue a second UIKit presentation.
        guard !isOpening, !isClosing, !isBeingDismissed else {
            completion?()
            return false
        }
        if presentingViewController != nil {
            completion?()
            return true
        }
        guard presenter !== self, presenter.viewIfLoaded?.window != nil,
              presenter.presentedViewController == nil,
              !presenter.isBeingPresented, !presenter.isBeingDismissed else {
            completion?()
            return false
        }
        loadViewIfNeeded()
        settingsView.reloadFromPreferences()
        isOpening = true
        presenter.present(self, animated: animated) { [weak self] in
            self?.isOpening = false
            completion?()
        }
        if presentingViewController == nil {
            isOpening = false
            completion?()
            return false
        }
        return true
    }

    /// Dismisses the interface. Returns false if a transition is still running.
    /// Programmatic close does not emit a user-request bridge callback.
    @discardableResult
    public func close(animated: Bool, completion: (() -> Void)? = nil) -> Bool {
        precondition(Thread.isMainThread, "UIKit dismissal requires the main thread")
        guard !isOpening, !isClosing, !isBeingDismissed else {
            completion?()
            return false
        }
        guard presentingViewController != nil else {
            completion?()
            return true
        }
        isClosing = true
        dismiss(animated: animated) { [weak self] in
            self?.isClosing = false
            completion?()
        }
        return true
    }

    public override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        if presentingViewController == nil {
            isOpening = false
            isClosing = false
        }
    }
}

private extension NSLayoutConstraint {
    func withPriority(_ priority: UILayoutPriority) -> NSLayoutConstraint {
        self.priority = priority
        return self
    }
}
