import Foundation

/// Intensity of haptic feedback requested by the user.
public enum SpicyHapticIntensity: String, CaseIterable {
    case off
    case light
    case medium
    case strong
}

/// Persisted settings for the Mr. Spicy interface.
///
/// Storage is `UserDefaults` (suite-scoped so hosts can isolate or share the
/// values). Every write is immediately durable; `reset()` restores factory
/// defaults and is itself persisted.
public final class SpicyPreferences {

    /// Suite name used when a host does not provide one.
    public static let defaultSuiteName = "com.mrspicy.ui.preferences"

    /// Factory-default values, also used by `reset()` and unit tests.
    public struct Defaults {
        public static let soundEnabled = true
        public static let hapticsEnabled = true
        public static let hapticIntensity = SpicyHapticIntensity.medium
        public static let notificationsEnabled = true
        public static let personalizationEnabled = false
        public static let playerNickname = ""
        private init() {}
    }

    public enum Key: String, CaseIterable {
        case soundEnabled
        case hapticsEnabled
        case hapticIntensity
        case notificationsEnabled
        case personalizationEnabled
        case playerNickname
    }

    private let defaults: UserDefaults

    /// - Parameter suiteName: UserDefaults suite. Hosts should use their own
    ///   suite (for example an app-group suite) to control storage location.
    public init(suiteName: String = SpicyPreferences.defaultSuiteName) {
        self.defaults = UserDefaults(suiteName: suiteName) ?? .standard
        registerDefaults()
    }

    private func registerDefaults() {
        defaults.register(defaults: [
            Key.soundEnabled.rawValue: Defaults.soundEnabled,
            Key.hapticsEnabled.rawValue: Defaults.hapticsEnabled,
            Key.hapticIntensity.rawValue: Defaults.hapticIntensity.rawValue,
            Key.notificationsEnabled.rawValue: Defaults.notificationsEnabled,
            Key.personalizationEnabled.rawValue: Defaults.personalizationEnabled,
            Key.playerNickname.rawValue: Defaults.playerNickname
        ])
    }

    // MARK: Settings

    public var soundEnabled: Bool {
        get { defaults.bool(forKey: Key.soundEnabled.rawValue) }
        set { defaults.set(newValue, forKey: Key.soundEnabled.rawValue) }
    }

    public var hapticsEnabled: Bool {
        get { defaults.bool(forKey: Key.hapticsEnabled.rawValue) }
        set { defaults.set(newValue, forKey: Key.hapticsEnabled.rawValue) }
    }

    public var hapticIntensity: SpicyHapticIntensity {
        get {
            guard let raw = defaults.string(forKey: Key.hapticIntensity.rawValue),
                  let value = SpicyHapticIntensity(rawValue: raw) else {
                return Defaults.hapticIntensity
            }
            return value
        }
        set { defaults.set(newValue.rawValue, forKey: Key.hapticIntensity.rawValue) }
    }

    public var notificationsEnabled: Bool {
        get { defaults.bool(forKey: Key.notificationsEnabled.rawValue) }
        set { defaults.set(newValue, forKey: Key.notificationsEnabled.rawValue) }
    }

    public var personalizationEnabled: Bool {
        get { defaults.bool(forKey: Key.personalizationEnabled.rawValue) }
        set { defaults.set(newValue, forKey: Key.personalizationEnabled.rawValue) }
    }

    public var playerNickname: String {
        get { defaults.string(forKey: Key.playerNickname.rawValue) ?? Defaults.playerNickname }
        set { defaults.set(newValue, forKey: Key.playerNickname.rawValue) }
    }

    // MARK: Lifecycle

    /// Restores every setting to its factory default and persists the result.
    public func reset() {
        for key in Key.allCases {
            defaults.removeObject(forKey: key.rawValue)
        }
        registerDefaults()
    }

    /// Snapshot of the current values keyed by `Key.rawValue` (diagnostics).
    public func snapshot() -> [String: Any] {
        [
            Key.soundEnabled.rawValue: soundEnabled,
            Key.hapticsEnabled.rawValue: hapticsEnabled,
            Key.hapticIntensity.rawValue: hapticIntensity.rawValue,
            Key.notificationsEnabled.rawValue: notificationsEnabled,
            Key.personalizationEnabled.rawValue: personalizationEnabled,
            Key.playerNickname.rawValue: playerNickname
        ]
    }
}
