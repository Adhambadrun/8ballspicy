import UIKit

/// The Mr. Spicy overlay interface.
///
/// Lifecycle contract for hosts:
/// 1. `open(from:animated:completion:)` presents the interface.
/// 2. The close button (or `close(animated:completion:)`) dismisses it and
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
    public private(set) var isOpen = false

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
        applyLayoutDirection()
        buildLayout()
        wireCallbacks()
        refreshLocalization()
    }

    private func applyLayoutDirection() {
        let rtl = SpicyLocalization.isRightToLeft()
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

        let contentStack = UIStackView(arrangedSubviews: [headerView, settingsView, versionLabel])
        contentStack.translatesAutoresizingMaskIntoConstraints = false
        contentStack.axis = .vertical
        contentStack.spacing = 0
        cardView.addSubview(contentStack)

        NSLayoutConstraint.activate([
            cardView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            cardView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            cardView.leadingAnchor.constraint(greaterThanOrEqualTo: view.leadingAnchor, constant: 24),
            cardView.trailingAnchor.constraint(lessThanOrEqualTo: view.trailingAnchor, constant: -24),
            cardView.widthAnchor.constraint(lessThanOrEqualToConstant: 480),
            cardView.widthAnchor.constraint(equalTo: view.widthAnchor, multiplier: 0.9).withPriority(.defaultHigh),

            contentStack.topAnchor.constraint(equalTo: cardView.topAnchor),
            contentStack.leadingAnchor.constraint(equalTo: cardView.leadingAnchor),
            contentStack.trailingAnchor.constraint(equalTo: cardView.trailingAnchor),
            contentStack.bottomAnchor.constraint(equalTo: cardView.bottomAnchor)
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
    public func refreshLocalization() {
        headerView?.refreshLocalization()
        settingsView?.refreshLocalization()
        versionLabel.text = SpicyVersion.displayString
    }

    // MARK: Open / close / reopen

    /// Presents the Mr. Spicy interface from `presenter`.
    ///
    /// Safe to call when already open (keeps the interface on screen and still
    /// invokes `completion`) and safe to call again after a close — the same
    /// instance supports unlimited open/close/reopen cycles.
    public func open(
        from presenter: UIViewController,
        animated: Bool,
        completion: (() -> Void)? = nil
    ) {
        if isOpen || presentingViewController != nil {
            isOpen = true
            completion?()
            return
        }
        presenter.present(self, animated: animated) { [weak self] in
            self?.isOpen = true
            completion?()
        }
    }

    /// Dismisses the interface. Idempotent.
    public func close(animated: Bool, completion: (() -> Void)? = nil) {
        guard isOpen || presentingViewController != nil else {
            completion?()
            return
        }
        dismiss(animated: animated) { [weak self] in
            self?.isOpen = false
            completion?()
        }
    }

    public override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        if presentingViewController == nil {
            isOpen = false
        }
    }
}

private extension NSLayoutConstraint {
    func withPriority(_ priority: UILayoutPriority) -> NSLayoutConstraint {
        self.priority = priority
        return self
    }
}
