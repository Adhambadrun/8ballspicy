import XCTest
@testable import MrSpicyUI

final class SpicyPreferencesTests: XCTestCase {

    private var suiteName: String!
    private var preferences: SpicyPreferences!

    override func setUp() {
        super.setUp()
        suiteName = "com.mrspicy.tests.\(UUID().uuidString)"
        preferences = SpicyPreferences(suiteName: suiteName)
    }

    override func tearDown() {
        UserDefaults().removePersistentDomain(forName: suiteName)
        preferences = nil
        suiteName = nil
        super.tearDown()
    }

    func testFactoryDefaults() {
        XCTAssertTrue(preferences.soundEnabled)
        XCTAssertTrue(preferences.hapticsEnabled)
        XCTAssertEqual(preferences.hapticIntensity, .medium)
        XCTAssertTrue(preferences.notificationsEnabled)
        XCTAssertFalse(preferences.personalizationEnabled)
        XCTAssertEqual(preferences.playerNickname, "")
    }

    func testSettingsPersistAcrossInstances() {
        preferences.soundEnabled = false
        preferences.hapticIntensity = .strong
        preferences.playerNickname = "SpicyOne"

        let reopened = SpicyPreferences(suiteName: suiteName)
        XCTAssertFalse(reopened.soundEnabled)
        XCTAssertEqual(reopened.hapticIntensity, .strong)
        XCTAssertEqual(reopened.playerNickname, "SpicyOne")
    }

    func testResetRestoresFactoryDefaults() {
        preferences.soundEnabled = false
        preferences.hapticsEnabled = false
        preferences.hapticIntensity = .off
        preferences.notificationsEnabled = false
        preferences.personalizationEnabled = true
        preferences.playerNickname = "temp"

        preferences.reset()

        XCTAssertTrue(preferences.soundEnabled)
        XCTAssertTrue(preferences.hapticsEnabled)
        XCTAssertEqual(preferences.hapticIntensity, .medium)
        XCTAssertTrue(preferences.notificationsEnabled)
        XCTAssertFalse(preferences.personalizationEnabled)
        XCTAssertEqual(preferences.playerNickname, "")
    }

    func testResetIsPersisted() {
        preferences.playerNickname = "keep-me-not"
        preferences.reset()
        let reopened = SpicyPreferences(suiteName: suiteName)
        XCTAssertEqual(reopened.playerNickname, "")
    }

    func testSnapshotCoversEveryKey() {
        let snapshot = preferences.snapshot()
        for key in SpicyPreferences.Key.allCases {
            XCTAssertNotNil(snapshot[key.rawValue], "snapshot missing \(key.rawValue)")
        }
        XCTAssertEqual(snapshot.count, SpicyPreferences.Key.allCases.count)
    }

    func testHapticIntensityRoundTrip() {
        for intensity in SpicyHapticIntensity.allCases {
            preferences.hapticIntensity = intensity
            XCTAssertEqual(preferences.hapticIntensity, intensity)
        }
    }
}
