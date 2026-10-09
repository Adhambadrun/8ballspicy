// swift-tools-version:5.9
import PackageDescription

// MrSpicyUI — premium overlay UI component ("Mr. Spicy").
//
// Provenance note (2026-10-09): the previously reported component under
// ExistingIPAWorkspace/OverlaySource/ is NOT present in this repository or its
// history. Prior sibling repositories that contained Mr. Spicy work became
// unreachable during the session that produced this package (see
// validation/reports/forensic-analysis.md §7). This package is therefore an
// original implementation of the documented Mr. Spicy component scope:
// brand-mark UI, settings with persistence/reset, en/ar localization with RTL,
// accessibility, and a host bridge protocol for an authorized integration.
let package = Package(
    name: "MrSpicyUI",
    defaultLocalization: "en",
    platforms: [
        .iOS(.v13)
    ],
    products: [
        .library(name: "MrSpicyUI", targets: ["MrSpicyUI"])
    ],
    targets: [
        .target(
            name: "MrSpicyUI",
            resources: [
                .process("Resources")
            ]
        ),
        .testTarget(
            name: "MrSpicyUITests",
            dependencies: ["MrSpicyUI"]
        )
    ]
)
