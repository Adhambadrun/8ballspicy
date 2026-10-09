import XCTest
@testable import MrSpicyUI

final class SpicyLocalizationTests: XCTestCase {

    /// Every key the shipped UI reads. Adding a UI string without adding it
    /// here (and to both .strings files) fails the suite.
    private let uiKeys = [
        "mr.spicy.header.title",
        "mr.spicy.header.subtitle",
        "mr.spicy.settings.sound",
        "mr.spicy.settings.haptics",
        "mr.spicy.settings.hapticIntensity",
        "mr.spicy.settings.haptic.off",
        "mr.spicy.settings.haptic.light",
        "mr.spicy.settings.haptic.medium",
        "mr.spicy.settings.haptic.strong",
        "mr.spicy.settings.notifications",
        "mr.spicy.settings.personalization",
        "mr.spicy.settings.nickname",
        "mr.spicy.settings.reset",
        "mr.spicy.a11y.close",
        "mr.spicy.a11y.reset"
    ]

    func testEnglishDefinesEveryUIKey() {
        let keys = Set(SpicyLocalization.keys(in: "en"))
        for key in uiKeys {
            XCTAssertTrue(keys.contains(key), "en missing \(key)")
        }
    }

    func testArabicDefinesEveryUIKey() {
        let keys = Set(SpicyLocalization.keys(in: "ar"))
        for key in uiKeys {
            XCTAssertTrue(keys.contains(key), "ar missing \(key)")
        }
    }

    func testEnglishAndArabicKeySetsMatch() {
        XCTAssertEqual(
            Set(SpicyLocalization.keys(in: "en")),
            Set(SpicyLocalization.keys(in: "ar")),
            "en/ar key sets diverged"
        )
    }

    func testTranslationsAreNonEmptyAndDifferWhereExpected() {
        for key in uiKeys {
            let en = SpicyLocalization.string(key, language: "en")
            let ar = SpicyLocalization.string(key, language: "ar")
            XCTAssertFalse(en.isEmpty, "empty en string for \(key)")
            XCTAssertFalse(ar.isEmpty, "empty ar string for \(key)")
            // A resolved string must never equal the raw key (that would mean
            // the lookup silently failed).
            XCTAssertNotEqual(en, key, "en lookup returned the key for \(key)")
            XCTAssertNotEqual(ar, key, "ar lookup returned the key for \(key)")
        }
    }

    func testUnknownKeyFallsBackToKeyItself() {
        XCTAssertEqual(
            SpicyLocalization.string("mr.spicy.does.not.exist", language: "en"),
            "mr.spicy.does.not.exist"
        )
    }

    func testUnknownLanguageFallsBackToEnglish() {
        let value = SpicyLocalization.string("mr.spicy.header.title", language: "zz-ZZ")
        XCTAssertEqual(value, SpicyLocalization.string("mr.spicy.header.title", language: "en"))
    }

    func testArabicIsRightToLeftAndEnglishIsNot() {
        XCTAssertTrue(SpicyLocalization.isRightToLeft(language: "ar"))
        XCTAssertTrue(SpicyLocalization.isRightToLeft(language: "ar-EG"))
        XCTAssertFalse(SpicyLocalization.isRightToLeft(language: "en"))
        XCTAssertFalse(SpicyLocalization.isRightToLeft(language: "en-GB"))
    }

    func testLanguageNormalization() {
        XCTAssertEqual(SpicyLocalization.normalizedLanguage("ar-SA"), "ar")
        XCTAssertEqual(SpicyLocalization.normalizedLanguage("EN_us"), "en")
        XCTAssertEqual(SpicyLocalization.normalizedLanguage("fr"), "en")
    }
}
