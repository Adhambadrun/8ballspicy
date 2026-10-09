import Foundation

/// Localization support for the Mr. Spicy interface.
///
/// Strings are loaded from the component bundle (`en.lproj`, `ar.lproj`).
/// Lookups are explicit-language capable so that hosts and unit tests can
/// verify every supported locale deterministically.
public enum SpicyLocalization {

    /// Language codes supported by this component.
    public static let supportedLanguages = ["en", "ar"]

    /// Default language used when a requested language is unsupported.
    public static let defaultLanguage = "en"

    /// Right-to-left languages supported by this component.
    public static let rightToLeftLanguages: Set<String> = ["ar"]

    /// Returns the localized string for `key`.
    ///
    /// Resolution order: requested language → English → the key itself
    /// (a missing key never crashes the UI).
    public static func string(_ key: String, language: String? = nil) -> String {
        let lang = normalizedLanguage(language ?? preferredLanguage())
        if let value = lookup(key, language: lang) {
            return value
        }
        if lang != defaultLanguage, let fallback = lookup(key, language: defaultLanguage) {
            return fallback
        }
        return key
    }

    /// Whether `language` (or the preferred language when `nil`) is RTL.
    public static func isRightToLeft(language: String? = nil) -> Bool {
        let lang = normalizedLanguage(language ?? preferredLanguage())
        return rightToLeftLanguages.contains(lang)
    }

    /// The device-preferred language restricted to supported languages.
    public static func preferredLanguage() -> String {
        for candidate in Locale.preferredLanguages {
            let lang = candidate.lowercased().split(whereSeparator: { $0 == "-" || $0 == "_" }).first.map(String.init) ?? candidate
            if supportedLanguages.contains(lang) {
                return lang
            }
        }
        return defaultLanguage
    }

    /// Maps tags such as `ar-SA` or `en_US` onto a supported language code.
    static func normalizedLanguage(_ tag: String) -> String {
        let lowered = tag.lowercased()
        if supportedLanguages.contains(lowered) {
            return lowered
        }
        let prefix = lowered.split(whereSeparator: { $0 == "-" || $0 == "_" }).first.map(String.init) ?? lowered
        return supportedLanguages.contains(prefix) ? prefix : defaultLanguage
    }

    /// All keys defined for a language (used by tests and host diagnostics).
    public static func keys(in language: String) -> [String] {
        guard let table = stringsTable(language: normalizedLanguage(language)) else { return [] }
        return Array(table.keys).sorted()
    }

    private static func lookup(_ key: String, language: String) -> String? {
        stringsTable(language: language)?[key]
    }

    private static func stringsTable(language: String) -> [String: String]? {
        guard let url = Bundle.module.url(
            forResource: "Localizable",
            withExtension: "strings",
            subdirectory: "\(language).lproj"
        ) ?? Bundle.module.url(
            forResource: "Localizable",
            withExtension: "strings",
            subdirectory: nil
        ) else {
            return nil
        }
        // `inDirectory: "\(language).lproj"` is handled above via subdirectory.
        guard let table = NSDictionary(contentsOf: url) as? [String: String] else {
            return nil
        }
        return table
    }
}
