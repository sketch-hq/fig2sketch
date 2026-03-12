// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "fig2sketch-swift",
    platforms: [
        .macOS(.v13),
    ],
    products: [
        .executable(name: "fig2sketch", targets: ["Fig2SketchCLI"]),
        .library(name: "Fig2SketchCore", targets: ["Fig2SketchCore"]),
    ],
    dependencies: [
        .package(url: "https://github.com/weichsel/ZIPFoundation.git", from: "0.9.19"),
    ],
    targets: [
        .systemLibrary(
            name: "CZstd",
            pkgConfig: "libzstd"
        ),
        .executableTarget(
            name: "Fig2SketchCLI",
            dependencies: ["Fig2SketchCore"]
        ),
        .target(
            name: "Fig2SketchCore",
            dependencies: [
                "Converter",
                "FigFormat",
                "SketchFormat",
                .product(name: "ZIPFoundation", package: "ZIPFoundation"),
            ]
        ),
        .target(
            name: "FigFormat",
            dependencies: [
                "CZstd",
                .product(name: "ZIPFoundation", package: "ZIPFoundation"),
            ]
        ),
        .target(name: "SketchFormat"),
        .target(name: "Converter"),
        .testTarget(
            name: "Fig2SketchCoreTests",
            dependencies: [
                "Fig2SketchCore",
                "FigFormat",
                .product(name: "ZIPFoundation", package: "ZIPFoundation"),
            ]
        ),
        .testTarget(
            name: "FigFormatTests",
            dependencies: [
                "FigFormat",
                .product(name: "ZIPFoundation", package: "ZIPFoundation"),
            ]
        ),
        .testTarget(
            name: "CompatibilityTests",
            dependencies: [
                "Fig2SketchCore",
                "FigFormat",
                .product(name: "ZIPFoundation", package: "ZIPFoundation"),
            ]
        ),
    ]
)
