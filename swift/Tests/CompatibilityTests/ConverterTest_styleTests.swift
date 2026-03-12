import FigFormat
import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_styleTests: XCTestCase {
    func test__converter__test_style__TestConvertColor__test_color() throws {
        // Port of tests/converter/test_style.py::TestConvertColor.test_color
        let style = try decodeRectangleStyle(fillPaints: [
            .object([
                "type": .string("SOLID"),
                "color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9),
                "visible": .bool(true),
                "opacity": .float(0.9),
            ]),
        ])

        guard case .solid(let color) = try XCTUnwrap(style.fills.first).kind else {
            return XCTFail("Expected solid fill")
        }
        XCTAssertEqual(color, FigColor(red: 1, green: 0, blue: 0.5, alpha: 0.9))
    }

    func test__converter__test_style__TestConvertColor__test_opacity() throws {
        // Port of tests/converter/test_style.py::TestConvertColor.test_opacity
        let style = try decodeRectangleStyle(fillPaints: [
            .object([
                "type": .string("SOLID"),
                "color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9),
                "visible": .bool(true),
                "opacity": .float(0.3),
            ]),
        ])

        guard case .solid(let color) = try XCTUnwrap(style.fills.first).kind else {
            return XCTFail("Expected solid fill")
        }
        XCTAssertEqual(color, FigColor(red: 1, green: 0, blue: 0.5, alpha: 0.3))
    }

    func test__converter__test_style__TestConvertFill__test_solid() throws {
        // Port of tests/converter/test_style.py::TestConvertFill.test_solid
        let style = try decodeRectangleStyle(fillPaints: [
            .object([
                "type": .string("SOLID"),
                "color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9),
                "visible": .bool(true),
                "opacity": .float(0.9),
            ]),
        ])

        let fill = try XCTUnwrap(style.fills.first)
        XCTAssertTrue(fill.isEnabled)
        guard case .solid(let color) = fill.kind else {
            return XCTFail("Expected solid fill")
        }
        XCTAssertEqual(color, FigColor(red: 1, green: 0, blue: 0.5, alpha: 0.9))
    }

    func test__converter__test_style__TestConvertFill__test_disabled() throws {
        // Port of tests/converter/test_style.py::TestConvertFill.test_disabled
        let style = try decodeRectangleStyle(fillPaints: [
            .object([
                "type": .string("SOLID"),
                "color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9),
                "visible": .bool(false),
                "opacity": .float(0.9),
            ]),
        ])

        let fill = try XCTUnwrap(style.fills.first)
        XCTAssertFalse(fill.isEnabled)
    }

    func test__converter__test_style__TestConvertFill__test_image() throws {
        // Port of tests/converter/test_style.py::TestConvertFill.test_image
        let style = try decodeRectangleStyle(fillPaints: [
            .object([
                "type": .string("IMAGE"),
                "image": .object(["filename": .string("abcdef")]),
                "visible": .bool(true),
                "imageScaleMode": .string("FIT"),
            ]),
        ])

        let fill = try XCTUnwrap(style.fills.first)
        XCTAssertTrue(fill.isEnabled)
        guard case .image(let image) = fill.kind else {
            return XCTFail("Expected image fill")
        }
        XCTAssertEqual(image.sourceName, "abcdef")
        XCTAssertEqual(image.patternFillType, .fit)
    }

    func test__converter__test_style__TestConvertFill__test_transparent_image() throws {
        // Port of tests/converter/test_style.py::TestConvertFill.test_transparent_image
        let style = try decodeRectangleStyle(fillPaints: [
            .object([
                "type": .string("IMAGE"),
                "image": .object(["filename": .string("abcdef")]),
                "visible": .bool(true),
                "imageScaleMode": .string("FIT"),
                "opacity": .float(0.5),
            ]),
        ])

        let fill = try XCTUnwrap(style.fills.first)
        XCTAssertTrue(fill.isEnabled)
        XCTAssertEqual(fill.opacity, 0.5, accuracy: 0.000_001)
        guard case .image(let image) = fill.kind else {
            return XCTFail("Expected image fill")
        }
        XCTAssertEqual(image.sourceName, "abcdef")
        XCTAssertEqual(image.patternFillType, .fit)
    }

    func test__converter__test_style__TestConvertFill__test_linear_gradient() throws {
        // Port of tests/converter/test_style.py::TestConvertFill.test_linear_gradient
        let style = try decodeRectangleStyle(fillPaints: [
            .object([
                "type": .string("GRADIENT_LINEAR"),
                "transform": matrix(m00: 0.7071, m01: -0.7071, m02: 0.6, m10: 0.7071, m11: 0.7071, m12: -0.1),
                "stops": .array([
                    .object(["color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9), "position": .float(0)]),
                    .object(["color": figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7), "position": .float(0.4)]),
                    .object(["color": figColor(red: 0, green: 0, blue: 1, alpha: 1), "position": .float(1)]),
                ]),
                "visible": .bool(true),
            ]),
        ], size: (10, 5))

        let fill = try XCTUnwrap(style.fills.first)
        XCTAssertTrue(fill.isEnabled)
        guard case .gradient(let gradient) = fill.kind else {
            return XCTFail("Expected gradient fill")
        }
        XCTAssertEqual(gradient.type, .linear)
        assertPoint(gradient.to, x: 0.7071135624381276, y: 0.1414227124876255)
        assertPoint(gradient.from, x: 0, y: 0.8485362749257531)
        XCTAssertEqual(gradient.stops, [
            FigGradientStop(color: FigColor(red: 1, green: 0, blue: 0.5, alpha: 0.9), position: 0),
            FigGradientStop(color: FigColor(red: 0, green: 1, blue: 0.5, alpha: 0.7), position: 0.4),
            FigGradientStop(color: FigColor(red: 0, green: 0, blue: 1, alpha: 1), position: 1),
        ])
    }

    func test__converter__test_style__TestConvertFill__test_radial_gradient() throws {
        // Port of tests/converter/test_style.py::TestConvertFill.test_radial_gradient
        let style = try decodeRectangleStyle(fillPaints: [
            .object([
                "type": .string("GRADIENT_RADIAL"),
                "transform": matrix(m00: 0.7071, m01: -0.7071, m02: 0.6, m10: 0.7071, m11: 0.7071, m12: -0.1),
                "stops": .array([
                    .object(["color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9), "position": .float(0)]),
                    .object(["color": figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7), "position": .float(0.4)]),
                    .object(["color": figColor(red: 0, green: 0, blue: 1, alpha: 1), "position": .float(1)]),
                ]),
                "visible": .bool(true),
            ]),
        ], size: (10, 5))

        let fill = try XCTUnwrap(style.fills.first)
        guard case .gradient(let gradient) = fill.kind else {
            return XCTFail("Expected gradient fill")
        }
        XCTAssertEqual(gradient.type, .radial)
        assertPoint(gradient.to, x: 0.7071135624381276, y: 0.1414227124876255)
        assertPoint(gradient.from, x: 0.3535567812190638, y: 0.4949794937066893)
        XCTAssertEqual(gradient.ellipseLength, 1, accuracy: 0.000_001)
        XCTAssertEqual(gradient.stops, [
            FigGradientStop(color: FigColor(red: 1, green: 0, blue: 0.5, alpha: 0.9), position: 0),
            FigGradientStop(color: FigColor(red: 0, green: 1, blue: 0.5, alpha: 0.7), position: 0.4),
            FigGradientStop(color: FigColor(red: 0, green: 0, blue: 1, alpha: 1), position: 1),
        ])
    }

    func test__converter__test_style__TestConvertFill__test_angular_gradient() throws {
        // Port of tests/converter/test_style.py::TestConvertFill.test_angular_gradient
        let style = try decodeRectangleStyle(fillPaints: [
            .object([
                "type": .string("GRADIENT_ANGULAR"),
                "transform": matrix(m00: 0.7071, m01: -0.7071, m02: 0.6, m10: 0.7071, m11: 0.7071, m12: -0.1),
                "stops": .array([
                    .object(["color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9), "position": .float(0)]),
                    .object(["color": figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7), "position": .float(0.4)]),
                    .object(["color": figColor(red: 0, green: 0, blue: 1, alpha: 1), "position": .float(1)]),
                ]),
                "visible": .bool(true),
            ]),
        ], size: (10, 5))

        let fill = try XCTUnwrap(style.fills.first)
        guard case .gradient(let gradient) = fill.kind else {
            return XCTFail("Expected gradient fill")
        }
        XCTAssertEqual(gradient.type, .angular)
        assertPositions(gradient.stops.map(\.position), [0.875, 0.275, 0.87499], accuracy: 0.000_02)
    }

    func test__converter__test_style__TestConvertFill__test_offset_gradient() throws {
        // Port of tests/converter/test_style.py::TestConvertFill.test_offset_gradient
        let style = try decodeRectangleStyle(fillPaints: [
            .object([
                "type": .string("GRADIENT_RADIAL"),
                "transform": matrix(m00: 0.7071, m01: -0.7071, m02: 0.6, m10: 0.7071, m11: 0.7071, m12: -0.1),
                "stops": .array([
                    .object(["color": figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7), "position": .float(0.4)]),
                    .object(["color": figColor(red: 0, green: 0, blue: 1, alpha: 1), "position": .float(0.8)]),
                ]),
                "visible": .bool(true),
            ]),
        ], size: (10, 5))

        let fill = try XCTUnwrap(style.fills.first)
        guard case .gradient(let gradient) = fill.kind else {
            return XCTFail("Expected gradient fill")
        }
        XCTAssertEqual(gradient.stops, [
            FigGradientStop(color: FigColor(red: 0, green: 1, blue: 0.5, alpha: 0.7), position: 0),
            FigGradientStop(color: FigColor(red: 0, green: 1, blue: 0.5, alpha: 0.7), position: 0.4),
            FigGradientStop(color: FigColor(red: 0, green: 0, blue: 1, alpha: 1), position: 0.8),
            FigGradientStop(color: FigColor(red: 0, green: 0, blue: 1, alpha: 1), position: 1),
        ])
    }

    func test__converter__test_style__TestConvertBorder__test_convert_border() throws {
        // Port of tests/converter/test_style.py::TestConvertBorder.test_convert_border
        let style = try decodeRectangleStyle(
            strokePaints: [
                .object([
                    "type": .string("SOLID"),
                    "color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9),
                    "visible": .bool(true),
                    "opacity": .float(0.9),
                ]),
            ],
            extraNode: [
                "strokeAlign": .string("CENTER"),
                "strokeWeight": .float(5),
            ]
        )

        let border = try XCTUnwrap(style.borders.first)
        XCTAssertEqual(border.position, .center)
        XCTAssertEqual(border.thickness, 5)
        XCTAssertTrue(border.paint.isEnabled)
        guard case .solid(let color) = border.paint.kind else {
            return XCTFail("Expected solid border")
        }
        XCTAssertEqual(color, FigColor(red: 1, green: 0, blue: 0.5, alpha: 0.9))
    }

    func test__converter__test_style__TestConvertBorder__test_convert_border_without_align() throws {
        // Port of tests/converter/test_style.py::TestConvertBorder.test_convert_border_without_align
        let style = try decodeRectangleStyle(
            strokePaints: [
                .object([
                    "type": .string("SOLID"),
                    "color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9),
                    "visible": .bool(true),
                    "opacity": .float(0.9),
                ]),
            ],
            extraNode: ["strokeWeight": .float(5)]
        )

        let border = try XCTUnwrap(style.borders.first)
        XCTAssertEqual(border.position, .center)
        XCTAssertEqual(border.thickness, 5)
    }

    func test__converter__test_style__TestConvertBorder__test_disabled_border() throws {
        // Port of tests/converter/test_style.py::TestConvertBorder.test_disabled_border
        let style = try decodeRectangleStyle(
            strokePaints: [
                .object([
                    "type": .string("SOLID"),
                    "color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9),
                    "visible": .bool(false),
                    "opacity": .float(0.9),
                ]),
            ],
            extraNode: [
                "strokeAlign": .string("CENTER"),
                "strokeWeight": .float(5),
            ]
        )

        let border = try XCTUnwrap(style.borders.first)
        XCTAssertFalse(border.paint.isEnabled)
    }

    func test__converter__test_style__TestConvertBorder__test_border_gradient() throws {
        // Port of tests/converter/test_style.py::TestConvertBorder.test_border_gradient
        let style = try decodeRectangleStyle(
            strokePaints: [
                .object([
                    "type": .string("GRADIENT_RADIAL"),
                    "transform": matrix(m00: 1, m01: 0, m02: 0.5, m10: 0, m11: 1, m12: 2),
                    "stops": .array([
                        .object(["color": figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9), "position": .float(0)]),
                        .object(["color": figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7), "position": .float(1)]),
                    ]),
                    "visible": .bool(true),
                ]),
            ],
            extraNode: [
                "strokeAlign": .string("CENTER"),
                "strokeWeight": .float(1),
            ],
            size: (50, 0)
        )

        let border = try XCTUnwrap(style.borders.first)
        XCTAssertEqual(border.position, .center)
        guard case .gradient(let gradient) = border.paint.kind else {
            return XCTFail("Expected border gradient")
        }
        XCTAssertEqual(gradient.type, .radial)
        assertPoint(gradient.to, x: 0.5, y: -1.5)
        assertPoint(gradient.from, x: 0, y: -1.5)
        XCTAssertEqual(gradient.ellipseLength, 2.0 / 52.0, accuracy: 0.000_001)
    }

    func test__converter__test_style__TestConvertContextSettings__test_blend() throws {
        // Port of tests/converter/test_style.py::TestConvertContextSettings.test_blend
        let json = try pageJSON(for: ConversionLayerStyle(blendMode: .darken, opacity: 0.7))
        XCTAssertTrue(json.contains("\"contextSettings\":{\"_class\":\"graphicsContextSettings\",\"blendMode\":1,\"opacity\":0.7}"))
    }

    func test__converter__test_style__TestConvertContextSettings__test_pass_through() throws {
        // Port of tests/converter/test_style.py::TestConvertContextSettings.test_pass_through
        let json = try pageJSON(for: ConversionLayerStyle(blendMode: .normal, opacity: 0.5))
        XCTAssertTrue(json.contains("\"contextSettings\":{\"_class\":\"graphicsContextSettings\",\"blendMode\":0,\"opacity\":0.5}"))
    }

    func test__converter__test_style__TestConvertContextSettings__test_solid() throws {
        // Port of tests/converter/test_style.py::TestConvertContextSettings.test_solid
        let json = try pageJSON(for: ConversionLayerStyle(blendMode: .normal, blendModeWasExplicit: true, opacity: 1))
        XCTAssertTrue(json.contains("\"contextSettings\":{\"_class\":\"graphicsContextSettings\",\"blendMode\":0,\"opacity\":0.99}"))
    }

    func test__converter__test_style__TestConvertEffects__test_inner_shadow() throws {
        // Port of tests/converter/test_style.py::TestConvertEffects.test_inner_shadow
        let style = try decodeRectangleStyle(effects: [
            .object([
                "type": .string("INNER_SHADOW"),
                "radius": .float(5),
                "offset": .object(["x": .float(3), "y": .float(6)]),
                "spread": .float(2),
                "color": figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7),
                "visible": .bool(true),
            ]),
        ])

        let shadow = try XCTUnwrap(style.shadows.first)
        XCTAssertEqual(shadow.blurRadius, 5, accuracy: 0.000_001)
        XCTAssertEqual(shadow.offsetX, 3, accuracy: 0.000_001)
        XCTAssertEqual(shadow.offsetY, 6, accuracy: 0.000_001)
        XCTAssertEqual(shadow.spread, 2, accuracy: 0.000_001)
        XCTAssertEqual(shadow.color, FigColor(red: 0, green: 1, blue: 0.5, alpha: 0.7))
        XCTAssertTrue(shadow.isInnerShadow)
        XCTAssertTrue(shadow.isEnabled)
    }

    func test__converter__test_style__TestConvertEffects__test_shadow() throws {
        // Port of tests/converter/test_style.py::TestConvertEffects.test_shadow
        let style = try decodeRectangleStyle(effects: [
            .object([
                "type": .string("DROP_SHADOW"),
                "radius": .float(5),
                "offset": .object(["x": .float(3), "y": .float(6)]),
                "spread": .float(2),
                "color": figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7),
                "visible": .bool(true),
            ]),
        ])

        let shadow = try XCTUnwrap(style.shadows.first)
        XCTAssertEqual(shadow.blurRadius, 5, accuracy: 0.000_001)
        XCTAssertEqual(shadow.offsetX, 3, accuracy: 0.000_001)
        XCTAssertEqual(shadow.offsetY, 6, accuracy: 0.000_001)
        XCTAssertEqual(shadow.spread, 2, accuracy: 0.000_001)
        XCTAssertEqual(shadow.color, FigColor(red: 0, green: 1, blue: 0.5, alpha: 0.7))
        XCTAssertTrue(shadow.isEnabled)
        XCTAssertFalse(shadow.isInnerShadow)
    }

    func test__converter__test_style__TestConvertEffects__test_hidden_shadow() throws {
        // Port of tests/converter/test_style.py::TestConvertEffects.test_hidden_shadow
        let style = try decodeRectangleStyle(effects: [
            .object([
                "type": .string("DROP_SHADOW"),
                "radius": .float(5),
                "offset": .object(["x": .float(3), "y": .float(6)]),
                "spread": .float(2),
                "color": figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7),
                "visible": .bool(false),
            ]),
        ])

        let shadow = try XCTUnwrap(style.shadows.first)
        XCTAssertEqual(shadow.blurRadius, 5, accuracy: 0.000_001)
        XCTAssertEqual(shadow.offsetX, 3, accuracy: 0.000_001)
        XCTAssertEqual(shadow.offsetY, 6, accuracy: 0.000_001)
        XCTAssertEqual(shadow.spread, 2, accuracy: 0.000_001)
        XCTAssertEqual(shadow.color, FigColor(red: 0, green: 1, blue: 0.5, alpha: 0.7))
        XCTAssertFalse(shadow.isEnabled)
    }

    func test__converter__test_style__TestConvertEffects__test_shadow_spread_is_optional() throws {
        // Port of tests/converter/test_style.py::TestConvertEffects.test_shadow_spread_is_optional
        let style = try decodeRectangleStyle(effects: [
            .object([
                "type": .string("DROP_SHADOW"),
                "radius": .float(5),
                "offset": .object(["x": .float(3), "y": .float(6)]),
                "color": figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7),
                "visible": .bool(true),
            ]),
        ])

        let shadow = try XCTUnwrap(style.shadows.first)
        XCTAssertEqual(shadow.spread, 0, accuracy: 0.000_001)
    }

    func test__converter__test_style__TestConvertEffects__test_blur() throws {
        // Port of tests/converter/test_style.py::TestConvertEffects.test_blur
        let style = try decodeRectangleStyle(effects: [
            .object([
                "type": .string("FOREGROUND_BLUR"),
                "radius": .float(5),
            ]),
        ])

        let blur = try XCTUnwrap(style.blurs.first)
        XCTAssertTrue(blur.isEnabled)
        XCTAssertEqual(blur.type, .gaussian)
        XCTAssertEqual(blur.radius, 2.5, accuracy: 0.000_001)
    }

    func test__converter__test_style__TestConvertEffects__test_bg_blur() throws {
        // Port of tests/converter/test_style.py::TestConvertEffects.test_bg_blur
        let style = try decodeRectangleStyle(effects: [
            .object([
                "type": .string("BACKGROUND_BLUR"),
                "radius": .float(5),
            ]),
        ])

        let blur = try XCTUnwrap(style.blurs.first)
        XCTAssertTrue(blur.isEnabled)
        XCTAssertEqual(blur.type, .background)
        XCTAssertEqual(blur.radius, 2.5, accuracy: 0.000_001)
    }

    func test__converter__test_style__TestConvertImageFill__test_cropped_image() throws {
        // Port of tests/converter/test_style.py::TestConvertImageFill.test_cropped_image
        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 0], type: "DOCUMENT", name: "Doc"),
                children: [
                    FigTreeNode(
                        node: .init(guid: [0, 1], type: "CANVAS", name: "Page 1"),
                        children: [
                            FigTreeNode(
                                node: .init(
                                    guid: [1, 2],
                                    type: "ELLIPSE",
                                    name: "thing",
                                    x: 0,
                                    y: 0,
                                    width: 100,
                                    height: 100,
                                    style: FigLayerStyle(
                                        fills: [
                                            FigPaint(
                                                kind: .image(
                                                    FigImagePaint(
                                                        sourceName: "abcdef",
                                                        patternFillType: .fit,
                                                        transform: .init(m00: 2, m01: 0, m02: 1, m10: 0, m11: 0.5, m12: -2),
                                                        originalImageWidth: 100,
                                                        originalImageHeight: 100
                                                    )
                                                )
                                            ),
                                            FigPaint(kind: .solid(.init(red: 1, green: 0, blue: 0.5, alpha: 0.9))),
                                        ]
                                    )
                                ),
                                children: []
                            ),
                        ]
                    ),
                ]
            )
        )

        let document: ConversionDocument
        do {
            document = try FigTreeToDocumentMapper.makeConversionDocument(from: tree)
        } catch {
            return XCTFail("Expected cropped-image conversion for ELLIPSE, got error: \(error)")
        }
        let page = try XCTUnwrap(document.pages.first)
        guard case .group(let group) = try XCTUnwrap(page.layers.first) else {
            return XCTFail("Expected cropped-image group")
        }
        XCTAssertEqual(group.layers.count, 2)

        guard case .rectangle(let maskLayer) = group.layers[0] else {
            return XCTFail("Expected mask layer")
        }
        XCTAssertTrue(maskLayer.hasClippingMask)
        guard case .solid(let maskColor) = try XCTUnwrap(maskLayer.style?.fills.first).kind else {
            return XCTFail("Expected solid mask fill")
        }
        XCTAssertEqual(maskColor, .init(red: 1, green: 0, blue: 0.5, alpha: 0.9))

        guard case .rectangle(let imageLayer) = group.layers[1] else {
            return XCTFail("Expected image layer")
        }
        guard case .image(let imageFill) = try XCTUnwrap(imageLayer.style?.fills.first).kind else {
            return XCTFail("Expected image fill")
        }
        XCTAssertEqual(imageFill.sourceName, "abcdef")
        XCTAssertEqual(imageFill.patternFillType, .fit)

        XCTAssertEqual(imageLayer.width, 50, accuracy: 0.000_001)
        XCTAssertEqual(imageLayer.height, 200, accuracy: 0.000_001)
        XCTAssertEqual(imageLayer.x, -50, accuracy: 0.000_001)
        XCTAssertEqual(imageLayer.y, 400, accuracy: 0.000_001)
    }

    private func decodeRectangleStyle(
        fillPaints: [KiwiValue] = [],
        strokePaints: [KiwiValue] = [],
        effects: [KiwiValue] = [],
        extraNode: [String: KiwiValue] = [:],
        size: (Double, Double) = (10, 5)
    ) throws -> FigLayerStyle {
        var rect: [String: KiwiValue] = [
            "guid": .object(["sessionID": .uint(9), "localID": .uint(9)]),
            "parentIndex": .object([
                "guid": .object(["sessionID": .uint(0), "localID": .uint(1)]),
                "position": .uint(0),
            ]),
            "type": .string("RECTANGLE"),
            "name": .string("Rect"),
            "size": .object(["x": .float(size.0), "y": .float(size.1)]),
        ]

        if !fillPaints.isEmpty {
            rect["fillPaints"] = .array(fillPaints)
        }
        if !strokePaints.isEmpty {
            rect["strokePaints"] = .array(strokePaints)
        }
        if !effects.isEmpty {
            rect["effects"] = .array(effects)
        }
        for (key, value) in extraNode {
            rect[key] = value
        }

        let root = KiwiValue.object([
            "nodeChanges": .array([
                .object([
                    "guid": .object(["sessionID": .uint(0), "localID": .uint(0)]),
                    "type": .string("DOCUMENT"),
                    "name": .string("Document"),
                ]),
                .object([
                    "guid": .object(["sessionID": .uint(0), "localID": .uint(1)]),
                    "parentIndex": .object([
                        "guid": .object(["sessionID": .uint(0), "localID": .uint(0)]),
                        "position": .uint(0),
                    ]),
                    "type": .string("CANVAS"),
                    "name": .string("Page 1"),
                ]),
                .object(rect),
            ]),
        ])

        let tree = try FigTreeDecoder.buildTree(from: root)
        let page = try XCTUnwrap(tree.root.children.first)
        let node = try XCTUnwrap(page.children.first)
        return try XCTUnwrap(node.node.style)
    }

    private func figColor(red: Double, green: Double, blue: Double, alpha: Double) -> KiwiValue {
        .object([
            "r": .float(red),
            "g": .float(green),
            "b": .float(blue),
            "a": .float(alpha),
        ])
    }

    private func matrix(m00: Double, m01: Double, m02: Double, m10: Double, m11: Double, m12: Double) -> KiwiValue {
        .object([
            "m00": .float(m00),
            "m01": .float(m01),
            "m02": .float(m02),
            "m10": .float(m10),
            "m11": .float(m11),
            "m12": .float(m12),
        ])
    }

    private func assertPoint(
        _ point: FigPoint,
        x: Double,
        y: Double,
        file: StaticString = #filePath,
        line: UInt = #line
    ) {
        XCTAssertEqual(point.x, x, accuracy: 0.000_001, file: file, line: line)
        XCTAssertEqual(point.y, y, accuracy: 0.000_001, file: file, line: line)
    }

    private func assertPositions(
        _ lhs: [Double],
        _ rhs: [Double],
        accuracy: Double,
        file: StaticString = #filePath,
        line: UInt = #line
    ) {
        XCTAssertEqual(lhs.count, rhs.count, file: file, line: line)
        for (index, pair) in zip(lhs, rhs).enumerated() {
            if abs(pair.0 - pair.1) > accuracy {
                XCTFail("Mismatch at index \(index): \(pair.0) vs \(pair.1)", file: file, line: line)
                return
            }
        }
    }

    private func pageJSON(for style: ConversionLayerStyle) throws -> String {
        let salt = Data("style-tests".utf8)
        let document = ConversionDocument(
            pages: [
                ConversionPage(
                    guid: [1, 1],
                    name: "Page 1",
                    layers: [
                        .rectangle(
                            ConversionRectangle(
                                guid: [2, 2],
                                name: "Rect",
                                x: 0,
                                y: 0,
                                width: 10,
                                height: 10,
                                style: style
                            )
                        ),
                    ]
                ),
            ]
        )

        let bundle = SketchBundleBuilder.build(from: document, salt: salt)
        let pageID = ConverterUtils.genObjectID(figID: [1, 1], salt: salt)
        return try XCTUnwrap(bundle["pages/\(pageID).json"]).utf8String
    }
}

private extension Data {
    var utf8String: String {
        String(decoding: self, as: UTF8.self)
    }
}
