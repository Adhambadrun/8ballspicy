import UIKit

/// Brand marks for the Mr. Spicy interface.
///
/// Asset provenance: `spicy-s-mark.png` is a NEW monogram generated for this
/// repository on 2026-10-09 because the previously used Spicy S asset lived
/// only in sibling repositories that are no longer reachable. It is not a
/// recovered copy of the historical asset.
public enum SpicyBrand {

    /// Name of the bundled S-monogram image resource.
    public static let markResourceName = "spicy-s-mark"

    /// The bundled Spicy S mark, or `nil` if the resource is missing.
    public static func markImage() -> UIImage? {
        UIImage(named: markResourceName, in: .module, compatibleWith: nil)
    }

    /// Graded ember→gold vertical gradient used behind headers.
    public static func headerGradient(in bounds: CGRect, theme: SpicyTheme = .default) -> CAGradientLayer {
        let layer = CAGradientLayer()
        layer.frame = bounds
        layer.colors = [
            theme.ember.withAlphaComponent(0.85).cgColor,
            theme.gold.withAlphaComponent(0.65).cgColor
        ]
        layer.startPoint = CGPoint(x: 0, y: 0)
        layer.endPoint = CGPoint(x: 1, y: 1)
        return layer
    }
}
