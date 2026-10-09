import Foundation

/// Bridge between the Mr. Spicy UI and an authorized host application.
///
/// The host owns the game logic; this protocol is the *only* supported
/// integration seam. Hosts (or adapters around them) implement it to observe
/// close requests and settings changes, and drive the overlay through
/// `SpicyOverlayViewController`. No control in the UI is decorative: every
/// control writes to `SpicyPreferences` and reports through this bridge.
public protocol SpicyHostBridge: AnyObject {
    /// The user asked to close the Mr. Spicy interface.
    func spicyOverlayDidRequestClose(_ overlay: SpicyOverlayViewController)

    /// A persisted setting changed (including resets).
    func spicyPreferencesDidChange(_ preferences: SpicyPreferences)
}

/// Default, no-op implementations so hosts can adopt the bridge incrementally.
public extension SpicyHostBridge {
    func spicyOverlayDidRequestClose(_ overlay: SpicyOverlayViewController) {}
    func spicyPreferencesDidChange(_ preferences: SpicyPreferences) {}
}
