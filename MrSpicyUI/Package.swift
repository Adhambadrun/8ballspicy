// swift-tools-version:5.9
import PackageDescription

// MrSpicyUI — premium overlay UI component ("Mr. Spicy").
//
// Provenance (verified 2026-10-09): this package is the component recovered from
// the `abadrun/8ballspicy` history and continued, not Miniclip or i3rby source.
// Its MrSpicyUI, HostApp and tools source trees are byte-identical (git tree
// IDs) to commit fae2937905395c425c777c38cbc05e115b2e1d71, the source that the
// verified CI run 37928629998 built and tested. See
// validation/reports/build-and-signing-report.md and
// validation/reports/forensic-analysis.md §7.
//
// Scope: brand-mark UI, settings with persistence/reset, en/ar localization
// with RTL, accessibility, and a host bridge protocol for an authorized
// integration. It is an independent library — it is not loaded by 8 Ball Pool.
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
