import Foundation
import XCTest
@testable import Fig2SketchCore

final class SketchBundleBuilderTests: XCTestCase {
    func testSingleRectanglePageProducesExpectedSketchEntries() throws {
        let document = ConversionDocument(
            pages: [
                ConversionPage(
                    guid: [1, 2],
                    name: "Page 1",
                    layers: [
                        .rectangle(
                            ConversionRectangle(
                                guid: [3, 4],
                                name: "Rectangle",
                                x: 10,
                                y: 20,
                                width: 100,
                                height: 50,
                                style: ConversionLayerStyle(
                                    fills: [
                                        ConversionPaint(
                                            kind: .solid(ConversionColor(red: 1, green: 0.5, blue: 0.25, alpha: 0.8)),
                                            isEnabled: true,
                                            blendMode: .multiply
                                        ),
                                        ConversionPaint(
                                            kind: .gradient(
                                                ConversionGradient(
                                                    type: .linear,
                                                    from: ConversionPoint(x: 0, y: 0.5),
                                                    to: ConversionPoint(x: 1, y: 0.5),
                                                    stops: [
                                                        ConversionGradientStop(
                                                            color: ConversionColor(red: 1, green: 0, blue: 0, alpha: 1),
                                                            position: 0
                                                        ),
                                                        ConversionGradientStop(
                                                            color: ConversionColor(red: 0, green: 0, blue: 1, alpha: 0.5),
                                                            position: 1
                                                        ),
                                                    ]
                                                )
                                            ),
                                            isEnabled: true,
                                            blendMode: .screen,
                                            opacity: 0.4
                                        ),
                                        ConversionPaint(
                                            kind: .image(
                                                ConversionImagePaint(
                                                    sourceName: "img-source",
                                                    patternFillType: .fit,
                                                    patternTileScale: 1.5
                                                )
                                            ),
                                            isEnabled: true,
                                            blendMode: .darken,
                                            opacity: 0.25
                                        ),
                                        ConversionPaint(kind: .unsupported(type: "IMAGE"), isEnabled: false),
                                    ],
                                    borders: [
                                        ConversionBorder(
                                            paint: ConversionPaint(
                                                kind: .solid(ConversionColor(red: 0.2, green: 0.3, blue: 0.4, alpha: 0.9)),
                                                isEnabled: true,
                                                blendMode: .screen
                                            ),
                                            thickness: 2,
                                            position: .inside
                                        ),
                                        ConversionBorder(
                                            paint: ConversionPaint(
                                                kind: .gradient(
                                                    ConversionGradient(
                                                        type: .radial,
                                                        from: ConversionPoint(x: 0.5, y: 0.5),
                                                        to: ConversionPoint(x: 1.0, y: 0.5),
                                                        ellipseLength: 0.5,
                                                        stops: [
                                                            ConversionGradientStop(
                                                                color: ConversionColor(red: 0, green: 0, blue: 0, alpha: 1),
                                                                position: 0
                                                            ),
                                                            ConversionGradientStop(
                                                                color: ConversionColor(red: 1, green: 1, blue: 1, alpha: 1),
                                                                position: 1
                                                            ),
                                                        ]
                                                    )
                                                ),
                                                isEnabled: true,
                                                blendMode: .overlay,
                                                opacity: 0.6
                                            ),
                                            thickness: 4,
                                            position: .outside
                                        ),
                                    ],
                                    blurs: [
                                        ConversionBlur(isEnabled: true, radius: 2.5, type: .gaussian),
                                        ConversionBlur(isEnabled: false, radius: 3, type: .background),
                                    ],
                                    shadows: [
                                        ConversionShadow(
                                            blurRadius: 5,
                                            offsetX: 3,
                                            offsetY: 6,
                                            spread: 2,
                                            isInnerShadow: false,
                                            isEnabled: true,
                                            color: ConversionColor(red: 0.2, green: 0.3, blue: 0.4, alpha: 0.5)
                                        ),
                                        ConversionShadow(
                                            blurRadius: 4,
                                            offsetX: -1,
                                            offsetY: 2,
                                            spread: 0,
                                            isInnerShadow: true,
                                            isEnabled: false,
                                            color: ConversionColor(red: 1, green: 0, blue: 0, alpha: 1)
                                        ),
                                    ],
                                    borderOptions: ConversionBorderOptions(
                                        lineCapStyle: .square,
                                        lineJoinStyle: .bevel,
                                        dashPattern: [4, 2]
                                    ),
                                    miterLimit: 8,
                                    windingRule: .evenOdd,
                                    blendMode: .overlay,
                                    opacity: 0.6
                                )
                            )
                        )
                    ]
                )
            ]
        )

        let imageData = Data(base64Encoded: tinyPNGBase64)!
        let bundle = SketchBundleBuilder.build(
            from: document,
            salt: Data("1234".utf8),
            assets: ConversionAssets(imagesBySourceName: ["img-source": imageData])
        )

        let pageID = ConverterUtils.genObjectID(figID: [1, 2], salt: Data("1234".utf8))
        let rectID = ConverterUtils.genObjectID(figID: [3, 4], salt: Data("1234".utf8))
        let imageFileRef = ConverterUtils.generateFileRef(imageData)
        let imagePath = "images/\(imageFileRef).png"

        XCTAssertEqual(
            Set(bundle.paths),
            Set([
                "document.json",
                "meta.json",
                "user.json",
                imagePath,
                "pages/\(pageID).json",
            ])
        )

        let pageJSON = try XCTUnwrap(bundle["pages/\(pageID).json"]).utf8String
        XCTAssertTrue(pageJSON.contains("\"_class\":\"page\""))
        XCTAssertTrue(pageJSON.contains("\"\(pageID)\""))
        XCTAssertTrue(pageJSON.contains("\"layers\":[{\"_class\":\"rectangle\""))
        XCTAssertTrue(pageJSON.contains("\"\(rectID)\""))
        XCTAssertTrue(pageJSON.contains("\"frame\":{\"_class\":\"rect\",\"x\":10.0,\"y\":20.0,\"width\":100.0,\"height\":50.0}"))
        XCTAssertTrue(pageJSON.contains("\"style\":{\"_class\":\"style\""))
        XCTAssertTrue(pageJSON.contains("\"fills\":[{\"_class\":\"fill\",\"isEnabled\":true,\"fillType\":0"))
        XCTAssertTrue(
            pageJSON.contains("\"color\":{\"_class\":\"color\",\"red\":1.0,\"green\":0.5,\"blue\":0.25,\"alpha\":0.8}") ||
                pageJSON.contains("\"color\":{\"_class\":\"color\",\"red\":1,\"green\":0.5,\"blue\":0.25,\"alpha\":0.8}")
        )
        XCTAssertTrue(pageJSON.contains("\"contextSettings\":{\"_class\":\"graphicsContextSettings\",\"blendMode\":2,\"opacity\":1.0}"))
        XCTAssertTrue(pageJSON.contains("\"fillType\":1,\"gradient\":{\"_class\":\"gradient\",\"gradientType\":0"))
        XCTAssertTrue(pageJSON.contains("\"from\":\"{0.0, 0.5}\""))
        XCTAssertTrue(pageJSON.contains("\"to\":\"{1.0, 0.5}\""))
        XCTAssertTrue(pageJSON.contains("\"stops\":[{\"_class\":\"gradientStop\""))
        XCTAssertTrue(pageJSON.contains("\"blendMode\":5,\"opacity\":0.4"))
        XCTAssertTrue(pageJSON.contains("\"fillType\":4"))
        XCTAssertTrue(pageJSON.contains("\"patternFillType\":3"))
        XCTAssertTrue(pageJSON.contains("\"patternTileScale\":1.5"))
        XCTAssertTrue(pageJSON.contains("\"_ref\":\"\(imagePath)\""))
        XCTAssertTrue(pageJSON.contains("\"blendMode\":1,\"opacity\":0.25"))
        XCTAssertTrue(pageJSON.contains("\"borders\":[{\"_class\":\"border\",\"isEnabled\":true,\"fillType\":0,\"position\":1,\"thickness\":2.0"))
        XCTAssertTrue(pageJSON.contains("\"color\":{\"_class\":\"color\",\"red\":0.2,\"green\":0.3,\"blue\":0.4,\"alpha\":0.9}"))
        XCTAssertTrue(pageJSON.contains("\"contextSettings\":{\"_class\":\"graphicsContextSettings\",\"blendMode\":5,\"opacity\":1.0}"))
        XCTAssertTrue(pageJSON.contains("\"fillType\":1,\"position\":2,\"thickness\":4.0,\"gradient\":{\"_class\":\"gradient\",\"gradientType\":1"))
        XCTAssertTrue(pageJSON.contains("\"elipseLength\":0.5"))
        XCTAssertTrue(pageJSON.contains("\"blendMode\":7,\"opacity\":0.6"))
        XCTAssertTrue(pageJSON.contains("\"blurs\":[{\"_class\":\"blur\",\"isEnabled\":true"))
        XCTAssertTrue(pageJSON.contains("\"radius\":2.5"))
        XCTAssertTrue(pageJSON.contains("\"type\":0"))
        XCTAssertFalse(pageJSON.contains("\"isEnabled\":false,\"center\":\"{0.5, 0.5}\""))
        XCTAssertFalse(pageJSON.contains("\"type\":3"))
        XCTAssertTrue(pageJSON.contains("\"shadows\":[{\"_class\":\"shadow\",\"blurRadius\":5.0,\"offsetX\":3.0,\"offsetY\":6.0,\"spread\":2.0,\"isInnerShadow\":false"))
        XCTAssertTrue(pageJSON.contains("\"_class\":\"shadow\",\"blurRadius\":4.0,\"offsetX\":-1.0,\"offsetY\":2.0,\"spread\":0.0,\"isInnerShadow\":true,\"isEnabled\":false"))
        XCTAssertTrue(pageJSON.contains("\"borderOptions\":{\"_class\":\"borderOptions\",\"isEnabled\":true,\"lineCapStyle\":2,\"lineJoinStyle\":2,\"dashPattern\":[4.0,2.0]}"))
        XCTAssertTrue(pageJSON.contains("\"miterLimit\":8.0"))
        XCTAssertTrue(pageJSON.contains("\"windingRule\":1"))
        XCTAssertTrue(pageJSON.contains("\"contextSettings\":{\"_class\":\"graphicsContextSettings\",\"blendMode\":7,\"opacity\":0.6}"))
        XCTAssertFalse(pageJSON.contains("\"IMAGE\""))

        let documentJSON = try XCTUnwrap(bundle["document.json"]).utf8String
        XCTAssertTrue(documentJSON.contains("\"_ref\":\"pages/\(pageID)\""))
    }

    func testBuildResultSerializesGroupMaskCornersAndAdvancedBlurAndNormalOpacityNudge() throws {
        let imageData = Data(base64Encoded: tinyPNGBase64)!
        let document = ConversionDocument(
            pages: [
                ConversionPage(
                    guid: [10, 20],
                    name: "Page",
                    layers: [
                        .group(
                            ConversionGroup(
                                guid: [30, 40],
                                name: "Photo (crop group)",
                                x: 10,
                                y: 20,
                                width: 100,
                                height: 50,
                                layers: [
                                    .rectangle(
                                        ConversionRectangle(
                                            guid: [30, 40, 0, 0],
                                            name: "Photo",
                                            x: 0,
                                            y: 0,
                                            width: 100,
                                            height: 50,
                                            hasClippingMask: true,
                                            clippingMaskMode: .outline,
                                            style: ConversionLayerStyle(
                                                fills: [
                                                    .init(kind: .solid(.init(red: 1, green: 0, blue: 0, alpha: 1)))
                                                ],
                                                blurs: [
                                                    .init(isEnabled: false, radius: 2, type: .background),
                                                    .init(
                                                        isEnabled: true,
                                                        radius: 4,
                                                        type: .gaussian,
                                                        isProgressive: true,
                                                        progressiveFrom: .init(x: 0.1, y: 0.2),
                                                        progressiveTo: .init(x: 0.9, y: 0.8),
                                                        progressiveStartRadiusRatio: 0.25
                                                    ),
                                                    .init(
                                                        isEnabled: true,
                                                        radius: 3,
                                                        type: .gaussian,
                                                        isCustomGlass: true,
                                                        glassDistortion: 0.2,
                                                        glassDepth: 0.4,
                                                        glassChromaticAberrationMultiplier: 0.6
                                                    ),
                                                ],
                                                corners: .init(radii: [1, 2, 3, 4], style: .smooth),
                                                blendMode: .normal,
                                                blendModeWasExplicit: true,
                                                opacity: 1
                                            )
                                        )
                                    ),
                                    .rectangle(
                                        ConversionRectangle(
                                            guid: [30, 40, 1, 0],
                                            name: "Photo (cropped image)",
                                            x: -10,
                                            y: 0,
                                            width: 120,
                                            height: 50,
                                            rotation: 15,
                                            style: ConversionLayerStyle(
                                                fills: [
                                                    .init(kind: .image(.init(sourceName: "crop.png", patternFillType: .fill)))
                                                ]
                                            )
                                        )
                                    ),
                                ]
                            )
                        )
                    ]
                )
            ]
        )

        let result = SketchBundleBuilder.buildResult(
            from: document,
            salt: Data("seed".utf8),
            assets: .init(imagesBySourceName: ["crop.png": imageData])
        )

        let pageID = ConverterUtils.genObjectID(figID: [10, 20], salt: Data("seed".utf8))
        let pageJSON = try XCTUnwrap(result.bundle["pages/\(pageID).json"]).utf8String

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"hasClippingMask\":true"))
        XCTAssertTrue(pageJSON.contains("\"clippingMaskMode\":0"))
        XCTAssertTrue(pageJSON.contains("\"corners\":{\"_class\":\"MSImmutableStyleCorners\",\"radii\":[1.0,2.0,3.0,4.0],\"style\":1}"))
        XCTAssertTrue(pageJSON.contains("\"contextSettings\":{\"_class\":\"graphicsContextSettings\",\"blendMode\":0,\"opacity\":0.99}"))
        XCTAssertTrue(pageJSON.contains("\"rotation\":15.0"))
        XCTAssertTrue(pageJSON.contains("\"isProgressive\":true"))
        XCTAssertTrue(pageJSON.contains("\"isCustomGlass\":true"))
        XCTAssertTrue(pageJSON.contains("\"distortion\":0.2"))
        XCTAssertTrue(pageJSON.contains("\"depth\":0.4"))
        XCTAssertTrue(pageJSON.contains("\"chromaticAberrationMultiplier\":0.6"))
        XCTAssertTrue(pageJSON.contains("\"gradient\":{\"_class\":\"gradient\""))
    }

    func testBuildResultSkipsAdditionalBlursWhenFirstBlurEnabled() throws {
        let document = ConversionDocument(
            pages: [
                ConversionPage(
                    guid: [1, 1],
                    name: "Page",
                    layers: [
                        .rectangle(
                            ConversionRectangle(
                                guid: [2, 2],
                                name: "Rect",
                                x: 0,
                                y: 0,
                                width: 10,
                                height: 10,
                                style: ConversionLayerStyle(
                                    blurs: [
                                        .init(isEnabled: true, radius: 2, type: .gaussian),
                                        .init(isEnabled: true, radius: 4, type: .background),
                                    ]
                                )
                            )
                        )
                    ]
                )
            ]
        )

        let bundle = SketchBundleBuilder.build(from: document, salt: Data("blur".utf8))
        let pageID = ConverterUtils.genObjectID(figID: [1, 1], salt: Data("blur".utf8))
        let pageJSON = try XCTUnwrap(bundle["pages/\(pageID).json"]).utf8String

        XCTAssertEqual(pageJSON.occurrences(of: "\"_class\":\"blur\""), 1)
        XCTAssertFalse(pageJSON.contains("\"type\":3"))
    }

    func testBuildResultEmitsImageCorruptionWarningsAndForceFlagChangesCode() throws {
        let document = ConversionDocument(
            pages: [
                ConversionPage(
                    guid: [9, 9],
                    name: "Page",
                    layers: [
                        .rectangle(
                            ConversionRectangle(
                                guid: [8, 8],
                                name: "Rect",
                                x: 0,
                                y: 0,
                                width: 10,
                                height: 10,
                                style: ConversionLayerStyle(
                                    fills: [
                                        .init(kind: .image(.init(sourceName: "bad.bin", patternFillType: .fit)))
                                    ]
                                )
                            )
                        )
                    ]
                )
            ]
        )

        let badImageData = Data("not-an-image".utf8)
        let noForce = SketchBundleBuilder.buildResult(
            from: document,
            salt: Data("img".utf8),
            assets: .init(imagesBySourceName: ["bad.bin": badImageData]),
            options: .init(forceConvertImages: false)
        )
        let force = SketchBundleBuilder.buildResult(
            from: document,
            salt: Data("img".utf8),
            assets: .init(imagesBySourceName: ["bad.bin": badImageData]),
            options: .init(forceConvertImages: true)
        )

        XCTAssertEqual(noForce.warnings.map(\.code), ["IMG001"])
        XCTAssertEqual(force.warnings.map(\.code), ["IMG002"])
        XCTAssertTrue(noForce.warnings[0].message.contains("Try passing --force-convert-images"))
        XCTAssertTrue(force.warnings[0].message.contains("will not be converted"))

        let pageID = ConverterUtils.genObjectID(figID: [9, 9], salt: Data("img".utf8))
        let pageJSON = try XCTUnwrap(noForce.bundle["pages/\(pageID).json"]).utf8String
        XCTAssertTrue(pageJSON.contains("\"_ref\":\"images/f2s_corrupted\""))
    }
}

private extension Data {
    var utf8String: String {
        String(decoding: self, as: UTF8.self)
    }
}

private extension String {
    func occurrences(of needle: String) -> Int {
        guard !needle.isEmpty else { return 0 }
        var count = 0
        var searchStart = startIndex
        while let range = self[searchStart...].range(of: needle) {
            count += 1
            searchStart = range.upperBound
        }
        return count
    }
}

private let tinyPNGBase64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO5Wn6sAAAAASUVORK5CYII="
