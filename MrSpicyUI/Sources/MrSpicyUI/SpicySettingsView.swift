import UIKit

/// Settings panel bound to `SpicyPreferences`.
///
/// Every control writes straight through to persistent storage and reports the
/// change through `onSettingsChanged`; there are no decorative controls.
public final class SpicySettingsView: UIView {

    /// Called after any user-driven settings mutation (including reset).
    public var onSettingsChanged: ((SpicyPreferences) -> Void)?

    public let preferences: SpicyPreferences
    private let theme: SpicyTheme

    private let stack = UIStackView()
    private var localizedRows: [(key: String, label: UILabel, control: UIView)] = []
    private var language: String?
    public private(set) var soundSwitch = UISwitch()
    public private(set) var hapticsSwitch = UISwitch()
    public private(set) var intensityControl = UISegmentedControl(items: [])
    public private(set) var notificationsSwitch = UISwitch()
    public private(set) var personalizationSwitch = UISwitch()
    public private(set) var nicknameField = UITextField()
    public private(set) var resetButton = UIButton(type: .system)

    public init(preferences: SpicyPreferences, theme: SpicyTheme = .default) {
        self.preferences = preferences
        self.theme = theme
        super.init(frame: .zero)
        buildLayout()
        reloadFromPreferences()
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) is not supported")
    }

    private func buildLayout() {
        translatesAutoresizingMaskIntoConstraints = false
        accessibilityIdentifier = SpicyAccessibility.settingsIdentifier

        stack.translatesAutoresizingMaskIntoConstraints = false
        stack.axis = .vertical
        stack.spacing = 14
        addSubview(stack)

        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: topAnchor, constant: 8),
            stack.leadingAnchor.constraint(equalTo: leadingAnchor, constant: theme.contentInset),
            stack.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -theme.contentInset),
            stack.bottomAnchor.constraint(equalTo: bottomAnchor, constant: -8)
        ])

        stack.addArrangedSubview(makeSwitchRow(
            titleKey: "mr.spicy.settings.sound",
            toggle: soundSwitch,
            key: .soundEnabled,
            action: #selector(soundChanged)
        ))
        stack.addArrangedSubview(makeSwitchRow(
            titleKey: "mr.spicy.settings.haptics",
            toggle: hapticsSwitch,
            key: .hapticsEnabled,
            action: #selector(hapticsChanged)
        ))

        intensityControl.accessibilityIdentifier = "mr.spicy.hapticIntensity"
        intensityControl.translatesAutoresizingMaskIntoConstraints = false
        intensityControl.addTarget(self, action: #selector(intensityChanged), for: .valueChanged)
        stack.addArrangedSubview(makeRow(
            titleKey: "mr.spicy.settings.hapticIntensity",
            control: intensityControl
        ))

        stack.addArrangedSubview(makeSwitchRow(
            titleKey: "mr.spicy.settings.notifications",
            toggle: notificationsSwitch,
            key: .notificationsEnabled,
            action: #selector(notificationsChanged)
        ))
        stack.addArrangedSubview(makeSwitchRow(
            titleKey: "mr.spicy.settings.personalization",
            toggle: personalizationSwitch,
            key: .personalizationEnabled,
            action: #selector(personalizationChanged)
        ))

        nicknameField.accessibilityIdentifier = "mr.spicy.nickname"
        nicknameField.textColor = theme.textPrimary
        nicknameField.backgroundColor = theme.background
        nicknameField.textAlignment = .natural
        nicknameField.translatesAutoresizingMaskIntoConstraints = false
        nicknameField.borderStyle = .roundedRect
        nicknameField.addTarget(self, action: #selector(nicknameChanged), for: .editingChanged)
        stack.addArrangedSubview(makeRow(
            titleKey: "mr.spicy.settings.nickname",
            control: nicknameField
        ))

        resetButton.translatesAutoresizingMaskIntoConstraints = false
        resetButton.setTitle(SpicyLocalization.string("mr.spicy.settings.reset", language: language), for: .normal)
        resetButton.setTitleColor(theme.destructive, for: .normal)
        resetButton.titleLabel?.font = .systemFont(ofSize: 16, weight: .semibold)
        resetButton.accessibilityIdentifier = SpicyAccessibility.resetIdentifier
        resetButton.accessibilityLabel = SpicyLocalization.string("mr.spicy.a11y.reset", language: language)
        resetButton.addTarget(self, action: #selector(resetTapped), for: .touchUpInside)
        stack.addArrangedSubview(resetButton)
    }

    // MARK: Row builders

    private func makeSwitchRow(
        titleKey: String,
        toggle: UISwitch,
        key: SpicyPreferences.Key,
        action: Selector
    ) -> UIView {
        toggle.translatesAutoresizingMaskIntoConstraints = false
        toggle.onTintColor = theme.switchTint
        toggle.accessibilityIdentifier = SpicyAccessibility.switchIdentifier(key)
        toggle.addTarget(self, action: action, for: .valueChanged)
        return makeRow(titleKey: titleKey, control: toggle)
    }

    private func makeRow(titleKey: String, control: UIView) -> UIView {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: .systemFont(ofSize: 16, weight: .regular))
        label.numberOfLines = 0
        label.textColor = theme.textPrimary
        label.text = SpicyLocalization.string(titleKey)
        label.adjustsFontForContentSizeCategory = true
        label.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)

        control.accessibilityLabel = label.text
        label.isAccessibilityElement = false
        localizedRows.append((titleKey, label, control))
        let row = UIStackView(arrangedSubviews: [label, control])
        row.axis = .horizontal
        row.alignment = .center
        row.spacing = 12
        return row
    }

    // MARK: Bindings

    /// Pushes the current persisted values into the controls.
    public func reloadFromPreferences() {
        soundSwitch.isOn = preferences.soundEnabled
        hapticsSwitch.isOn = preferences.hapticsEnabled
        notificationsSwitch.isOn = preferences.notificationsEnabled
        personalizationSwitch.isOn = preferences.personalizationEnabled
        nicknameField.text = preferences.playerNickname

        intensityControl.removeAllSegments()
        for (index, intensity) in SpicyHapticIntensity.allCases.enumerated() {
            intensityControl.insertSegment(
                withTitle: SpicyLocalization.string("mr.spicy.settings.haptic.\(intensity.rawValue)", language: language),
                at: index,
                animated: false
            )
            if intensity == preferences.hapticIntensity {
                intensityControl.selectedSegmentIndex = index
            }
        }
        intensityControl.isEnabled = preferences.hapticsEnabled
    }

    /// Re-resolves localized strings after a language change.
    public func refreshLocalization(language: String? = nil) {
        self.language = language
        semanticContentAttribute = SpicyLocalization.isRightToLeft(language: language) ? .forceRightToLeft : .forceLeftToRight
        for row in localizedRows {
            let text = SpicyLocalization.string(row.key, language: language)
            row.label.text = text
            row.control.accessibilityLabel = text
        }
        resetButton.setTitle(SpicyLocalization.string("mr.spicy.settings.reset", language: language), for: .normal)
        resetButton.accessibilityLabel = SpicyLocalization.string("mr.spicy.a11y.reset", language: language)
        reloadFromPreferences()
    }

    private func notifyChange() {
        onSettingsChanged?(preferences)
    }

    // MARK: Actions

    @objc func soundChanged() {
        preferences.soundEnabled = soundSwitch.isOn
        notifyChange()
    }

    @objc func hapticsChanged() {
        preferences.hapticsEnabled = hapticsSwitch.isOn
        intensityControl.isEnabled = hapticsSwitch.isOn
        notifyChange()
    }

    @objc func intensityChanged() {
        let index = intensityControl.selectedSegmentIndex
        let cases = SpicyHapticIntensity.allCases
        guard index >= 0, index < cases.count else { return }
        preferences.hapticIntensity = cases[index]
        notifyChange()
    }

    @objc func notificationsChanged() {
        preferences.notificationsEnabled = notificationsSwitch.isOn
        notifyChange()
    }

    @objc func personalizationChanged() {
        preferences.personalizationEnabled = personalizationSwitch.isOn
        notifyChange()
    }

    @objc func nicknameChanged() {
        preferences.playerNickname = nicknameField.text ?? ""
        notifyChange()
    }

    @objc func resetTapped() {
        preferences.reset()
        reloadFromPreferences()
        notifyChange()
    }
}
