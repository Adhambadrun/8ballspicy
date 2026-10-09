import Foundation

/// Bridge between the Mr. Spicy UI and an authorized host application.
///
/// The host owns the game logic; this protocol is the *only* supported
/// integration seam. Hosts (or adapters around them) implement it to observe
/// close requests and settings changes, and drive the overlay through
/// `SpicyOverlayViewController`. Every settings control persists its value to
/// `SpicyPreferences` and reports the change through this bridge. Persistence is
/// the whole effect inside this component: sound, haptic, notification and
/// personalization preferences do not play audio, trigger haptics, post
/// notifications or change behavior here. A host that reads them must implement
/// that behavior itself, and only after an authorized integration.
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
