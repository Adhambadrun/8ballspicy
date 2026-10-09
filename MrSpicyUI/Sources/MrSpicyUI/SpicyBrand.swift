import UIKit

/// Brand marks for the Mr. Spicy interface.
///
/// Asset provenance (verified 2026-10-09, see `validation/reports/forensic-analysis.md`
/// and `validation/manifests/release-manifest.json`): `spicy-s-mark.png` is the
/// **existing generated replacement** carried forward from the earlier
/// implementation of this component. It is *not* a recovered copy of the
/// historical Spicy S brand asset, and no new mark was generated for this
/// repository. The bundled file is byte-identical to the one that was built and
/// tested in the verified CI run, and its SHA-256 is recorded in the release
/// manifest so provenance stays checkable.
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
