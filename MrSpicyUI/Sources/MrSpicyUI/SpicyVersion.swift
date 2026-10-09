import Foundation

/// Version of the Mr. Spicy UI component (not the host application version).
public enum SpicyVersion {
    /// Semantic version of this component.
    public static let current = "1.0.0"

    /// Build stamp for diagnostics panels.
    public static var displayString: String {
        "Mr Spicy \(current)"
    }
}
