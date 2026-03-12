import FigFormat
import XCTest
@testable import Fig2SketchCore

final class FigTreeToDocumentMapperTests: XCTestCase {
    func testMapsFirstCanvasAndRectangle() throws {
        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 0], type: "DOCUMENT", name: "Document"),
                children: [
                    FigTreeNode(
                        node: .init(guid: [0, 1], type: "CANVAS", name: "Page 1"),
                        children: [
                            FigTreeNode(
                                node: .init(
                                    guid: [1, 2],
                                    type: "ROUNDED_RECTANGLE",
                                    name: "Rect",
                                    x: 10,
                                    y: 20,
                                    width: 100,
                                    height: 50,
                                    style: FigLayerStyle(
                                        fills: [
                                            FigPaint(kind: .solid(FigColor(red: 0.1, green: 0.2, blue: 0.3, alpha: 0.4))),
                                            FigPaint(
                                                kind: .gradient(
                                                    FigGradient(
                                                        type: .linear,
                                                        from: FigPoint(x: 0, y: 0.5),
                                                        to: FigPoint(x: 1, y: 0.5),
                                                        stops: [
                                                            FigGradientStop(
                                                                color: FigColor(red: 1, green: 0, blue: 0, alpha: 1),
                                                                position: 0
                                                            ),
                                                            FigGradientStop(
                                                                color: FigColor(red: 0, green: 0, blue: 1, alpha: 0.5),
                                                                position: 1
                                                            ),
                                                        ]
                                                    )
                                                ),
                                                blendMode: .screen,
                                                opacity: 0.4
                                            ),
                                            FigPaint(
                                                kind: .image(
                                                    FigImagePaint(
                                                        sourceName: "abc123",
                                                        patternFillType: .fit,
                                                        patternTileScale: 1.5
                                                    )
                                                ),
                                                blendMode: .darken,
                                                opacity: 0.25
                                            ),
                                            FigPaint(kind: .unsupported(type: "IMAGE"), isEnabled: false, blendMode: .multiply),
                                        ],
                                        borders: [
                                            FigBorder(
                                                paint: FigPaint(kind: .solid(FigColor(red: 0.9, green: 0.8, blue: 0.7, alpha: 0.6)), blendMode: .screen),
                                                thickness: 3,
                                                position: .outside
                                            ),
                                        ],
                                        blurs: [
                                            FigBlur(isEnabled: true, radius: 2.5, type: .gaussian),
                                            FigBlur(isEnabled: false, radius: 3, type: .background),
                                        ],
                                        shadows: [
                                            FigShadow(
                                                blurRadius: 5,
                                                offsetX: 3,
                                                offsetY: 6,
                                                spread: 2,
                                                isInnerShadow: false,
                                                isEnabled: true,
                                                color: FigColor(red: 0.2, green: 0.3, blue: 0.4, alpha: 0.5)
                                            ),
                                            FigShadow(
                                                blurRadius: 4,
                                                offsetX: -1,
                                                offsetY: 2,
                                                spread: 0,
                                                isInnerShadow: true,
                                                isEnabled: false,
                                                color: FigColor(red: 1, green: 0, blue: 0, alpha: 1)
                                            ),
                                        ],
                                        borderOptions: FigBorderOptions(
                                            lineCapStyle: .square,
                                            lineJoinStyle: .bevel,
                                            dashPattern: [4, 2]
                                        ),
                                        miterLimit: 8,
                                        windingRule: .evenOdd,
                                        blendMode: .overlay,
                                        opacity: 0.5
                                    )
                                ),
                                children: []
                            ),
                        ]
                    ),
                ]
            )
        )

        let document = try FigTreeToDocumentMapper.makeConversionDocument(from: tree)
        XCTAssertEqual(document.pages.count, 1)
        let page = try XCTUnwrap(document.pages.first)
        XCTAssertEqual(page.guid, [0, 1])
        XCTAssertEqual(page.name, "Page 1")
        XCTAssertEqual(page.layers.count, 1)

        guard case .rectangle(let rect) = try XCTUnwrap(page.layers.first) else {
            return XCTFail("Expected rectangle layer")
        }
        XCTAssertEqual(rect.guid, [1, 2])
        XCTAssertEqual(rect.name, "Rect")
        XCTAssertEqual(rect.x, 10)
        XCTAssertEqual(rect.y, 20)
        XCTAssertEqual(rect.width, 100)
        XCTAssertEqual(rect.height, 50)
        let style = try XCTUnwrap(rect.style)
        XCTAssertEqual(style.blendMode, .overlay)
        XCTAssertEqual(style.opacity, 0.5)
        XCTAssertEqual(style.fills.count, 4)
        XCTAssertEqual(style.borders.count, 1)
        XCTAssertEqual(style.blurs.count, 2)
        XCTAssertEqual(style.shadows.count, 2)
        XCTAssertEqual(style.fills[1].blendMode, .screen)
        XCTAssertEqual(style.fills[1].opacity, 0.4)
        XCTAssertEqual(style.fills[2].blendMode, .darken)
        XCTAssertEqual(style.fills[2].opacity, 0.25)
        XCTAssertEqual(style.fills[3].blendMode, .multiply)
        XCTAssertEqual(style.fills[3].isEnabled, false)
        XCTAssertEqual(style.borders[0].position, .outside)
        XCTAssertEqual(style.borders[0].thickness, 3)
        XCTAssertEqual(style.borders[0].paint.blendMode, .screen)
        XCTAssertEqual(style.borderOptions.lineCapStyle, .square)
        XCTAssertEqual(style.borderOptions.lineJoinStyle, .bevel)
        XCTAssertEqual(style.borderOptions.dashPattern, [4, 2])
        XCTAssertEqual(style.miterLimit, 10)
        XCTAssertEqual(style.windingRule, .nonZero)

        guard case .solid(let fillColor) = style.fills[0].kind else {
            return XCTFail("Expected solid fill")
        }
        XCTAssertEqual(fillColor, ConversionColor(red: 0.1, green: 0.2, blue: 0.3, alpha: 0.4))

        guard case .solid(let strokeColor) = style.borders[0].paint.kind else {
            return XCTFail("Expected solid border")
        }
        XCTAssertEqual(strokeColor, ConversionColor(red: 0.9, green: 0.8, blue: 0.7, alpha: 0.6))

        guard case .gradient(let gradient) = style.fills[1].kind else {
            return XCTFail("Expected gradient fill")
        }
        XCTAssertEqual(gradient.type, .linear)
        XCTAssertEqual(gradient.from, ConversionPoint(x: 0, y: 0.5))
        XCTAssertEqual(gradient.to, ConversionPoint(x: 1, y: 0.5))
        XCTAssertEqual(gradient.stops.count, 2)
        XCTAssertEqual(gradient.stops[1].color.alpha, 0.5)

        guard case .image(let imagePaint) = style.fills[2].kind else {
            return XCTFail("Expected image fill")
        }
        XCTAssertEqual(imagePaint.sourceName, "abc123")
        XCTAssertEqual(imagePaint.patternFillType, .fit)
        XCTAssertEqual(imagePaint.patternTileScale, 1.5)

        XCTAssertEqual(style.blurs[0], ConversionBlur(isEnabled: true, radius: 2.5, type: .gaussian))
        XCTAssertEqual(style.blurs[1], ConversionBlur(isEnabled: false, radius: 3, type: .background))
        XCTAssertEqual(style.shadows[0].blurRadius, 5)
        XCTAssertEqual(style.shadows[0].isInnerShadow, false)
        XCTAssertEqual(style.shadows[1].isInnerShadow, true)
        XCTAssertEqual(style.shadows[1].isEnabled, false)
    }

    func testKeepsNestedLayerCoordinatesRelativeToParent() throws {
        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 1], type: "CANVAS", name: "Page 1", x: 0, y: 0),
                children: [
                    FigTreeNode(
                        node: .init(guid: [0, 2], type: "FRAME", name: "Frame", x: 50, y: 100),
                        children: [
                            FigTreeNode(
                                node: .init(
                                    guid: [0, 3],
                                    type: "RECTANGLE",
                                    name: "Rect",
                                    x: 10,
                                    y: 20,
                                    width: 30,
                                    height: 40
                                ),
                                children: []
                            ),
                        ]
                    ),
                ]
            )
        )

        let document = try FigTreeToDocumentMapper.makeConversionDocument(from: tree)
        let page = try XCTUnwrap(document.pages.first)
        guard case .rectangle(let rect) = try XCTUnwrap(page.layers.first) else {
            return XCTFail("Expected rectangle layer")
        }

        XCTAssertEqual(rect.x, 10)
        XCTAssertEqual(rect.y, 20)
        XCTAssertEqual(rect.width, 30)
        XCTAssertEqual(rect.height, 40)
    }

    func testMapsRotationFromNodeTransform() throws {
        let angle = -45.0 * Double.pi / 180
        let transform = FigAffineTransform(
            m00: cos(angle),
            m01: -sin(angle),
            m02: 10,
            m10: sin(angle),
            m11: cos(angle),
            m12: 20
        )

        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 0], type: "DOCUMENT", name: "Document"),
                children: [
                    FigTreeNode(
                        node: .init(guid: [0, 1], type: "CANVAS", name: "Page 1"),
                        children: [
                            FigTreeNode(
                                node: .init(
                                    guid: [9, 9],
                                    type: "GROUP_CONTAINER",
                                    name: "Rotated Group",
                                    x: 10,
                                    y: 20,
                                    width: 100,
                                    height: 50,
                                    transform: transform
                                ),
                                children: []
                            ),
                        ]
                    ),
                ]
            )
        )

        let document = try FigTreeToDocumentMapper.makeConversionDocument(from: tree)
        let page = try XCTUnwrap(document.pages.first)
        guard case .group(let group) = try XCTUnwrap(page.layers.first) else {
            return XCTFail("Expected group layer")
        }

        XCTAssertEqual(group.rotation, 45, accuracy: 0.000_001)
    }

    func testRewritesCroppedImageFillIntoMaskGroup() throws {
        let croppedImagePaint = FigPaint(
            kind: .image(
                FigImagePaint(
                    sourceName: "crop.png",
                    patternFillType: .fill,
                    embeddedBlobIndex: nil,
                    transform: FigAffineTransform(m00: 1, m01: 0, m02: 0.1, m10: 0, m11: 1, m12: 0),
                    originalImageWidth: 200,
                    originalImageHeight: 100
                )
            )
        )

        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 0], type: "DOCUMENT", name: "Doc"),
                children: [
                    FigTreeNode(
                        node: .init(guid: [0, 1], type: "CANVAS", name: "Page 1"),
                        children: [
                            FigTreeNode(
                                node: .init(
                                    guid: [7, 8],
                                    type: "RECTANGLE",
                                    name: "Photo",
                                    x: 10,
                                    y: 20,
                                    width: 100,
                                    height: 50,
                                    style: FigLayerStyle(
                                        fills: [
                                            FigPaint(kind: .solid(FigColor(red: 1, green: 0, blue: 0, alpha: 1))),
                                            croppedImagePaint,
                                        ],
                                        corners: FigStyleCorners(radii: [4, 4, 4, 4], style: .rounded)
                                    )
                                ),
                                children: []
                            ),
                        ]
                    ),
                ]
            )
        )

        let document = try FigTreeToDocumentMapper.makeConversionDocument(from: tree)
        let page = try XCTUnwrap(document.pages.first)
        XCTAssertEqual(page.layers.count, 1)

        guard case .group(let group) = try XCTUnwrap(page.layers.first) else {
            return XCTFail("Expected cropped image rewrite to produce a group")
        }
        XCTAssertEqual(group.name, "Photo (crop group)")
        XCTAssertEqual(group.x, 10)
        XCTAssertEqual(group.y, 20)
        XCTAssertEqual(group.width, 100)
        XCTAssertEqual(group.height, 50)
        XCTAssertEqual(group.layers.count, 2)

        guard case .rectangle(let mask) = group.layers[0] else {
            return XCTFail("Expected first child to be mask rectangle")
        }
        XCTAssertTrue(mask.hasClippingMask)
        XCTAssertEqual(mask.clippingMaskMode, .outline)
        let maskStyle = try XCTUnwrap(mask.style)
        XCTAssertEqual(maskStyle.corners, ConversionStyleCorners(radii: [4, 4, 4, 4], style: .rounded))
        XCTAssertEqual(maskStyle.fills.count, 1, "Mask should keep non-cropped fills only")
        guard case .solid = maskStyle.fills[0].kind else {
            return XCTFail("Expected mask fill to be the non-cropped solid fill")
        }

        guard case .rectangle(let imageRect) = group.layers[1] else {
            return XCTFail("Expected second child to be generated image rectangle")
        }
        XCTAssertEqual(imageRect.name, "Photo (cropped image)")
        XCTAssertGreaterThan(imageRect.width, 0)
        XCTAssertGreaterThan(imageRect.height, 0)
        let imageStyle = try XCTUnwrap(imageRect.style)
        XCTAssertEqual(imageStyle.fills.count, 1)
        guard case .image(let imagePaint) = imageStyle.fills[0].kind else {
            return XCTFail("Expected generated image rectangle to contain image fill")
        }
        XCTAssertEqual(imagePaint.sourceName, "crop.png")
    }

    func testCroppedImageGeometryMatchesPythonStyleVector() throws {
        let croppedImagePaint = FigPaint(
            kind: .image(
                FigImagePaint(
                    sourceName: "abcdef",
                    patternFillType: .fit,
                    transform: FigAffineTransform(m00: 2, m01: 0, m02: 1, m10: 0, m11: 0.5, m12: -2),
                    originalImageWidth: 100,
                    originalImageHeight: 100
                )
            )
        )

        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 0], type: "DOCUMENT", name: "Doc"),
                children: [
                    FigTreeNode(
                        node: .init(guid: [0, 1], type: "CANVAS", name: "Page 1"),
                        children: [
                            FigTreeNode(
                                node: .init(
                                    guid: [123, 456],
                                    type: "ROUNDED_RECTANGLE",
                                    name: "thing",
                                    x: 0,
                                    y: 0,
                                    width: 100,
                                    height: 100,
                                    style: FigLayerStyle(
                                        fills: [
                                            croppedImagePaint,
                                            FigPaint(kind: .solid(FigColor(red: 1, green: 0, blue: 0.5, alpha: 0.9))),
                                        ],
                                        blendMode: .normal,
                                        blendModeWasExplicit: true,
                                        opacity: 1
                                    )
                                ),
                                children: []
                            ),
                        ]
                    ),
                ]
            )
        )

        let document = try FigTreeToDocumentMapper.makeConversionDocument(from: tree)
        let page = try XCTUnwrap(document.pages.first)
        guard case .group(let group) = try XCTUnwrap(page.layers.first) else {
            return XCTFail("Expected crop group")
        }

        XCTAssertEqual(group.layers.count, 2)
        guard case .rectangle(let imageRect) = group.layers[1] else {
            return XCTFail("Expected generated cropped image layer")
        }

        // Mirrors tests/converter/test_style.py::TestConvertImageFill.test_cropped_image
        XCTAssertEqual(imageRect.width, 50, accuracy: 0.000_001)
        XCTAssertEqual(imageRect.height, 200, accuracy: 0.000_001)
        XCTAssertEqual(imageRect.x, -50, accuracy: 0.000_001)
        XCTAssertEqual(imageRect.y, 400, accuracy: 0.000_001)
    }

    func testMapsCornersAndAdvancedBlurFields() throws {
        let style = FigLayerStyle(
            blurs: [
                FigBlur(
                    isEnabled: true,
                    radius: 4,
                    type: .gaussian,
                    isProgressive: true,
                    progressiveFrom: FigPoint(x: 0.1, y: 0.2),
                    progressiveTo: FigPoint(x: 0.9, y: 0.8),
                    progressiveStartRadiusRatio: 0.3
                ),
                FigBlur(
                    isEnabled: true,
                    radius: 3,
                    type: .gaussian,
                    isCustomGlass: true,
                    glassDistortion: 0.4,
                    glassDepth: 0.8,
                    glassChromaticAberrationMultiplier: 0.25
                ),
            ],
            corners: FigStyleCorners(radii: [1, 2, 3, 4], style: .smooth),
            blendMode: .normal,
            blendModeWasExplicit: true,
            opacity: 1
        )

        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 0], type: "DOCUMENT", name: "Doc"),
                children: [
                    FigTreeNode(
                        node: .init(guid: [0, 1], type: "CANVAS", name: "Page 1"),
                        children: [
                            FigTreeNode(
                                node: .init(guid: [1, 2], type: "RECTANGLE", name: "Rect", width: 10, height: 20, style: style),
                                children: []
                            ),
                        ]
                    ),
                ]
            )
        )

        let document = try FigTreeToDocumentMapper.makeConversionDocument(from: tree)
        let page = try XCTUnwrap(document.pages.first)
        guard case .rectangle(let rect) = try XCTUnwrap(page.layers.first) else {
            return XCTFail("Expected rectangle layer")
        }
        let mappedStyle = try XCTUnwrap(rect.style)
        XCTAssertEqual(mappedStyle.corners, ConversionStyleCorners(radii: [1, 2, 3, 4], style: .smooth))
        XCTAssertTrue(mappedStyle.blendModeWasExplicit)
        XCTAssertEqual(mappedStyle.blendMode, .normal)
        XCTAssertEqual(mappedStyle.blurs.count, 2)
        XCTAssertTrue(mappedStyle.blurs[0].isProgressive)
        XCTAssertEqual(mappedStyle.blurs[0].progressiveFrom, ConversionPoint(x: 0.1, y: 0.2))
        XCTAssertEqual(mappedStyle.blurs[0].progressiveTo, ConversionPoint(x: 0.9, y: 0.8))
        XCTAssertEqual(try XCTUnwrap(mappedStyle.blurs[0].progressiveStartRadiusRatio), 0.3, accuracy: 0.000_001)
        XCTAssertTrue(mappedStyle.blurs[1].isCustomGlass)
        XCTAssertEqual(mappedStyle.blurs[1].glassDistortion, 0.4, accuracy: 0.000_001)
        XCTAssertEqual(mappedStyle.blurs[1].glassDepth, 0.8, accuracy: 0.000_001)
        XCTAssertEqual(mappedStyle.blurs[1].glassChromaticAberrationMultiplier, 0.25, accuracy: 0.000_001)
    }
}
