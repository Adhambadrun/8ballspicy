// swift-tools-version:5.9
import PackageDescription

// MrSpicyUI — premium overlay UI component ("Mr. Spicy").
//
// Provenance: this package is the component recovered from the
// `abadrun/8ballspicy` history and continued, not Miniclip or i3rby source.
// The MrSpicyUI, HostApp and tools source trees were built and tested as they
// stood at commit fae2937905395c425c777c38cbc05e115b2e1d71 (verified CI run
// 37928629998). Later documentation and tooling edits changed the MrSpicyUI git
// tree (this file's comments included), so the current tree is NOT the tree that
// CI tested until a fresh CI run records it. The recorded trees are in
// validation/manifests/release-manifest.json (source_tree_snapshot). See
// validation/reports/session-734fc10e-verification.md and
// validation/reports/forensic-analysis.md §7.
//
// Scope: brand-mark UI, settings with persistence/reset, en/ar localization
// with RTL, accessibility, and a host bridge protocol for an authorized
// integration. It is an independent library and is not integrated with, or
// loaded by, 8 Ball Pool.
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
