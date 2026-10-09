import XCTest
@testable import MrSpicyUI

final class SpicyThemeTests: XCTestCase {

    func testDefaultThemeColorsAreDistinctWhereItMatters() {
        let theme = SpicyTheme.default
        XCTAssertNotEqual(theme.background, theme.surface)
        XCTAssertNotEqual(theme.ember, theme.gold)
        XCTAssertNotEqual(theme.textPrimary, theme.textSecondary)
    }

    func testComponentVersionFormat() {
        let parts = SpicyVersion.current.split(separator: ".")
        XCTAssertEqual(parts.count, 3, "version must be semver x.y.z")
        for part in parts {
            XCTAssertNotNil(Int(part), "version component '\(part)' is not numeric")
        }
        XCTAssertTrue(SpicyVersion.displayString.contains(SpicyVersion.current))
    }

    func testBrandMarkResourceIsBundled() {
        let image = SpicyBrand.markImage()
        XCTAssertNotNil(image, "spicy-s-mark resource missing from bundle")
        if let image = image {
            XCTAssertGreaterThan(image.size.width, 0)
            XCTAssertGreaterThan(image.size.height, 0)
        }
    }

    func testHeaderGradientConfigured() {
        let layer = SpicyBrand.headerGradient(in: CGRect(x: 0, y: 0, width: 100, height: 50))
        XCTAssertEqual(layer.colors?.count, 2)
        XCTAssertEqual(layer.frame.width, 100)
    }
}
