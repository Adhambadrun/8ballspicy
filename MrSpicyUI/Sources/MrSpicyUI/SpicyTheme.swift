import UIKit

/// Premium design tokens for the Mr. Spicy interface.
///
/// The palette is intentionally small and semantic; host applications can
/// override individual values through `SpicyTheme` instances rather than
/// editing views.
public struct SpicyTheme {

    public static let `default` = SpicyTheme()

    // MARK: Surfaces

    /// Deep charcoal-navy app background.
    public var background: UIColor
    /// Elevated card / sheet surface.
    public var surface: UIColor
    /// Hairline separators.
    public var separator: UIColor

    // MARK: Brand accents

    /// Ember red primary accent.
    public var ember: UIColor
    /// Molten gold secondary accent.
    public var gold: UIColor

    // MARK: Text

    public var textPrimary: UIColor
    public var textSecondary: UIColor
    public var textOnAccent: UIColor

    // MARK: Controls

    public var switchTint: UIColor
    public var destructive: UIColor

    public init(
        background: UIColor = UIColor(red: 0.07, green: 0.08, blue: 0.11, alpha: 1),
        surface: UIColor = UIColor(red: 0.12, green: 0.13, blue: 0.18, alpha: 1),
        separator: UIColor = UIColor(white: 1, alpha: 0.10),
        ember: UIColor = UIColor(red: 0.90, green: 0.27, blue: 0.18, alpha: 1),
        gold: UIColor = UIColor(red: 0.96, green: 0.72, blue: 0.28, alpha: 1),
        textPrimary: UIColor = UIColor(white: 0.97, alpha: 1),
        textSecondary: UIColor = UIColor(white: 0.72, alpha: 1),
        textOnAccent: UIColor = UIColor(white: 0.08, alpha: 1),
        switchTint: UIColor = UIColor(red: 0.90, green: 0.27, blue: 0.18, alpha: 1),
        destructive: UIColor = UIColor(red: 0.85, green: 0.22, blue: 0.22, alpha: 1)
    ) {
        self.background = background
        self.surface = surface
        self.separator = separator
        self.ember = ember
        self.gold = gold
        self.textPrimary = textPrimary
        self.textSecondary = textSecondary
        self.textOnAccent = textOnAccent
        self.switchTint = switchTint
        self.destructive = destructive
    }

    /// Corner radius used by cards and buttons.
    public var cornerRadius: CGFloat { 16 }

    /// Standard content padding (leading/trailing/top/bottom).
    public var contentInset: CGFloat { 20 }
}
