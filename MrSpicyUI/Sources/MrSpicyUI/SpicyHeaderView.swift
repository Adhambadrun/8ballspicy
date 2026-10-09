import UIKit

/// Branded header for the Mr. Spicy interface: S mark, title, close button.
public final class SpicyHeaderView: UIView {

    public var onCloseTapped: (() -> Void)?

    public let markImageView: UIImageView = {
        let view = UIImageView()
        view.translatesAutoresizingMaskIntoConstraints = false
        view.contentMode = .scaleAspectFit
        view.isAccessibilityElement = false
        return view
    }()

    public let titleLabel: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        label.font = UIFontMetrics(forTextStyle: .title2).scaledFont(for: .systemFont(ofSize: 24, weight: .bold))
        label.numberOfLines = 0
        label.adjustsFontForContentSizeCategory = true
        return label
    }()

    public let subtitleLabel: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        label.font = UIFontMetrics(forTextStyle: .caption1).scaledFont(for: .systemFont(ofSize: 13, weight: .medium))
        label.numberOfLines = 0
        label.adjustsFontForContentSizeCategory = true
        return label
    }()

    public let closeButton: UIButton = {
        let button = UIButton(type: .system)
        button.translatesAutoresizingMaskIntoConstraints = false
        button.setImage(UIImage(systemName: "xmark.circle.fill"), for: .normal)
        button.accessibilityIdentifier = SpicyAccessibility.closeIdentifier
        return button
    }()

    private let theme: SpicyTheme

    public init(theme: SpicyTheme = .default) {
        self.theme = theme
        super.init(frame: .zero)
        buildLayout()
        applyContent()
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) is not supported")
    }

    private func buildLayout() {
        translatesAutoresizingMaskIntoConstraints = false
        accessibilityIdentifier = SpicyAccessibility.headerIdentifier

        let textStack = UIStackView(arrangedSubviews: [titleLabel, subtitleLabel])
        textStack.translatesAutoresizingMaskIntoConstraints = false
        textStack.axis = .vertical
        textStack.spacing = 2

        addSubview(markImageView)
        addSubview(textStack)
        addSubview(closeButton)

        NSLayoutConstraint.activate([
            markImageView.leadingAnchor.constraint(equalTo: leadingAnchor, constant: theme.contentInset),
            markImageView.centerYAnchor.constraint(equalTo: centerYAnchor),
            markImageView.widthAnchor.constraint(equalToConstant: 48),
            markImageView.heightAnchor.constraint(equalToConstant: 48),

            textStack.leadingAnchor.constraint(equalTo: markImageView.trailingAnchor, constant: 12),
            textStack.centerYAnchor.constraint(equalTo: centerYAnchor),
            textStack.topAnchor.constraint(greaterThanOrEqualTo: topAnchor, constant: 12),
            textStack.bottomAnchor.constraint(lessThanOrEqualTo: bottomAnchor, constant: -12),
            textStack.trailingAnchor.constraint(lessThanOrEqualTo: closeButton.leadingAnchor, constant: -12),

            closeButton.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -theme.contentInset),
            closeButton.centerYAnchor.constraint(equalTo: centerYAnchor),
            closeButton.widthAnchor.constraint(equalToConstant: 44),
            closeButton.heightAnchor.constraint(equalToConstant: 44),

            heightAnchor.constraint(greaterThanOrEqualToConstant: 92)
        ])

        closeButton.addTarget(self, action: #selector(closeTapped), for: .touchUpInside)
    }

    private func applyContent(language: String? = nil) {
        semanticContentAttribute = SpicyLocalization.isRightToLeft(language: language) ? .forceRightToLeft : .forceLeftToRight
        backgroundColor = theme.surface
        titleLabel.textColor = theme.textPrimary
        subtitleLabel.textColor = theme.textSecondary
        closeButton.tintColor = theme.textSecondary

        markImageView.image = SpicyBrand.markImage()
        titleLabel.text = SpicyLocalization.string("mr.spicy.header.title", language: language)
        subtitleLabel.text = SpicyLocalization.string("mr.spicy.header.subtitle", language: language)

        closeButton.accessibilityLabel = SpicyLocalization.string("mr.spicy.a11y.close", language: language)
    }

    /// Re-resolves localized strings (after a language change) without
    /// rebuilding the view hierarchy.
    public func refreshLocalization(language: String? = nil) {
        applyContent(language: language)
    }

    @objc func closeTapped() {
        onCloseTapped?()
    }
}
