import UIKit

/// Accessibility identifiers and label helpers for the Mr. Spicy interface.
public enum SpicyAccessibility {

    // MARK: Identifiers (stable across releases; used by UI tests and hosts)

    public static let overlayIdentifier = "mr.spicy.overlay"
    public static let headerIdentifier = "mr.spicy.header"
    public static let closeIdentifier = "mr.spicy.close"
    public static let settingsIdentifier = "mr.spicy.settings"
    public static let resetIdentifier = "mr.spicy.reset"
    public static let versionIdentifier = "mr.spicy.version"

    public static func switchIdentifier(_ key: SpicyPreferences.Key) -> String {
        "mr.spicy.switch.\(key.rawValue)"
    }

    // MARK: Labels

    /// Applies a localized accessibility label to any accessible element.
    public static func apply(labelKey: String, to element: AnyObject) {
        let label = SpicyLocalization.string(labelKey)
        if let view = element as? UIView {
            view.accessibilityLabel = label
        } else if let item = element as? UIBarItem {
            item.accessibilityLabel = label
        }
    }
}
