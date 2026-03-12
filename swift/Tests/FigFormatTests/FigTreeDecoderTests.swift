import Foundation
import XCTest
import ZIPFoundation
@testable import FigFormat

final class FigTreeDecoderTests: XCTestCase {
    func testDecodeCanvasFigFromZipAndBuildTree() throws {
        let tempURL = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathExtension("fig")
        defer { try? FileManager.default.removeItem(at: tempURL) }

        let archive = try Archive(url: tempURL, accessMode: .create)
        let canvas = SyntheticKiwiFixture.canvasData
        try archive.addEntry(
            with: "canvas.fig",
            type: .file,
            uncompressedSize: Int64(canvas.count),
            compressionMethod: .none,
            provider: { position, size in
                let start = Int(position)
                let end = min(start + size, canvas.count)
                return canvas.subdata(in: start..<end)
            }
        )

        let decoded = try FigTreeDecoder.decodeFigFile(url: tempURL)
        let tree = try FigTreeDecoder.buildTree(from: decoded.rootMessage)

        XCTAssertEqual(tree.root.node.type, "CANVAS")
        XCTAssertEqual(tree.root.node.name, "Page 1")
        XCTAssertEqual(tree.root.children.count, 1)

        let rect = try XCTUnwrap(tree.root.children.first)
        XCTAssertEqual(rect.node.type, "RECTANGLE")
        XCTAssertEqual(rect.node.name, "Rect")
        XCTAssertEqual(rect.node.x, 10.0)
        XCTAssertEqual(rect.node.y, 20.0)
        XCTAssertEqual(rect.node.width, 100.0)
        XCTAssertEqual(rect.node.height, 50.0)
    }

    func testBuildTreeParsesGuidObjectsParentIndexAndTransformFrame() throws {
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
                        "position": .string("!"),
                    ]),
                    "type": .string("CANVAS"),
                    "name": .string("Page 1"),
                ]),
                .object([
                    "guid": .object(["sessionID": .uint(2016), "localID": .uint(9)]),
                    "parentIndex": .object([
                        "guid": .object(["sessionID": .uint(0), "localID": .uint(1)]),
                        "position": .string("!"),
                    ]),
                    "type": .string("ROUNDED_RECTANGLE"),
                    "name": .string("Rectangle 1"),
                    "fillPaints": .array([
                        .object([
                            "type": .string("SOLID"),
                            "visible": .bool(true),
                            "blendMode": .string("MULTIPLY"),
                            "opacity": .float(0.75),
                            "color": .object([
                                "r": .float(0.85),
                                "g": .float(0.85),
                                "b": .float(0.85),
                                "a": .float(1.0),
                            ]),
                        ]),
                        .object([
                            "type": .string("IMAGE"),
                            "visible": .bool(false),
                        ]),
                    ]),
                    "strokePaints": .array([
                        .object([
                            "type": .string("SOLID"),
                            "visible": .bool(true),
                            "blendMode": .string("SCREEN"),
                            "opacity": .float(0.5),
                            "color": .object([
                                "r": .float(0.1),
                                "g": .float(0.2),
                                "b": .float(0.3),
                                "a": .float(1.0),
                            ]),
                        ]),
                    ]),
                    "strokeWeight": .float(2.5),
                    "strokeAlign": .string("INSIDE"),
                    "blendMode": .string("OVERLAY"),
                    "opacity": .float(0.6),
                    "size": .object(["x": .float(254), "y": .float(207)]),
                    "transform": .object([
                        "m00": .float(1), "m01": .float(0), "m02": .float(187),
                        "m10": .float(0), "m11": .float(1), "m12": .float(-15),
                    ]),
                ]),
            ]),
        ])

        let tree = try FigTreeDecoder.buildTree(from: root)
        XCTAssertEqual(tree.root.node.type, "DOCUMENT")
        XCTAssertEqual(tree.root.node.guid, [0, 0])

        let page = try XCTUnwrap(tree.root.children.first)
        XCTAssertEqual(page.node.type, "CANVAS")
        XCTAssertEqual(page.node.guid, [0, 1])

        let rect = try XCTUnwrap(page.children.first)
        XCTAssertEqual(rect.node.type, "ROUNDED_RECTANGLE")
        XCTAssertEqual(rect.node.guid, [2016, 9])
        XCTAssertEqual(rect.node.parentGuid, [0, 1])
        XCTAssertEqual(rect.node.parentPosition, UInt32("!".unicodeScalars.first!.value))
        XCTAssertEqual(rect.node.x, 187.0)
        XCTAssertEqual(rect.node.y, -15.0)
        XCTAssertEqual(rect.node.width, 254.0)
        XCTAssertEqual(rect.node.height, 207.0)
        XCTAssertEqual(try XCTUnwrap(rect.node.transform).m02, 187.0, accuracy: 0.000_001)
        XCTAssertEqual(try XCTUnwrap(rect.node.transform).m12, -15.0, accuracy: 0.000_001)
        let style = try XCTUnwrap(rect.node.style)
        XCTAssertEqual(style.blendMode, .overlay)
        XCTAssertEqual(style.opacity, 0.6)
        XCTAssertEqual(style.fills.count, 2)
        XCTAssertEqual(style.borders.count, 1)

        guard case .solid(let fillColor) = style.fills[0].kind else {
            return XCTFail("Expected first fill to be solid")
        }
        XCTAssertEqual(fillColor, FigColor(red: 0.85, green: 0.85, blue: 0.85, alpha: 0.75))
        XCTAssertEqual(style.fills[0].isEnabled, true)
        XCTAssertEqual(style.fills[0].blendMode, .multiply)

        guard case .unsupported(let paintType) = style.fills[1].kind else {
            return XCTFail("Expected second fill to be unsupported paint")
        }
        XCTAssertEqual(paintType, "IMAGE")
        XCTAssertEqual(style.fills[1].isEnabled, false)

        let border = style.borders[0]
        guard case .solid(let strokeColor) = border.paint.kind else {
            return XCTFail("Expected border to be solid")
        }
        XCTAssertEqual(strokeColor, FigColor(red: 0.1, green: 0.2, blue: 0.3, alpha: 0.5))
        XCTAssertEqual(border.thickness, 2.5)
        XCTAssertEqual(border.position, .inside)
        XCTAssertEqual(border.paint.blendMode, .screen)
    }

    func testBuildTreeParsesGradientPaintsAndStops() throws {
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
                .object([
                    "guid": .object(["sessionID": .uint(1), "localID": .uint(2)]),
                    "parentIndex": .object([
                        "guid": .object(["sessionID": .uint(0), "localID": .uint(1)]),
                        "position": .uint(0),
                    ]),
                    "type": .string("RECTANGLE"),
                    "name": .string("Rect"),
                    "size": .object(["x": .float(10), "y": .float(5)]),
                    "fillPaints": .array([
                        .object([
                            "type": .string("GRADIENT_LINEAR"),
                            "visible": .bool(true),
                            "opacity": .float(0.7),
                            "transform": .object([
                                "m00": .float(1), "m01": .float(0), "m02": .float(0),
                                "m10": .float(0), "m11": .float(1), "m12": .float(0),
                            ]),
                            "stops": .array([
                                .object([
                                    "position": .float(0.25),
                                    "color": .object(["r": .float(1), "g": .float(0), "b": .float(0), "a": .float(0.5)]),
                                ]),
                                .object([
                                    "position": .float(0.75),
                                    "color": .object(["r": .float(0), "g": .float(1), "b": .float(0), "a": .float(1)]),
                                ]),
                            ]),
                        ]),
                        .object([
                            "type": .string("IMAGE"),
                            "visible": .bool(true),
                            "blendMode": .string("DARKEN"),
                            "opacity": .float(0.25),
                            "imageScaleMode": .string("FIT"),
                            "scale": .float(2.5),
                            "originalImageWidth": .float(128),
                            "originalImageHeight": .float(64),
                            "transform": .object([
                                "m00": .float(1), "m01": .float(0), "m02": .float(0.1),
                                "m10": .float(0), "m11": .float(1), "m12": .float(0),
                            ]),
                            "image": .object([
                                "hash": .array([.byte(0xAA), .byte(0xBB), .byte(0xCC)]),
                                "dataBlob": .uint(0),
                            ]),
                        ]),
                        .object([
                            "type": .string("GRADIENT_ANGULAR"),
                            "visible": .bool(true),
                            "transform": .object([
                                "m00": .float(0), "m01": .float(-1), "m02": .float(0),
                                "m10": .float(1), "m11": .float(0), "m12": .float(0),
                            ]),
                            "stops": .array([
                                .object([
                                    "position": .float(0),
                                    "color": .object(["r": .float(0), "g": .float(0), "b": .float(1), "a": .float(1)]),
                                ]),
                                .object([
                                    "position": .float(1),
                                    "color": .object(["r": .float(1), "g": .float(1), "b": .float(1), "a": .float(1)]),
                                ]),
                            ]),
                        ]),
                    ]),
                    "strokePaints": .array([
                        .object([
                            "type": .string("GRADIENT_RADIAL"),
                            "visible": .bool(true),
                            "blendMode": .string("SCREEN"),
                            "opacity": .float(0.4),
                            "transform": .object([
                                "m00": .float(1), "m01": .float(0), "m02": .float(0),
                                "m10": .float(0), "m11": .float(1), "m12": .float(0),
                            ]),
                            "stops": .array([
                                .object([
                                    "position": .float(0),
                                    "color": .object(["r": .float(0), "g": .float(0), "b": .float(0), "a": .float(1)]),
                                ]),
                                .object([
                                    "position": .float(1),
                                    "color": .object(["r": .float(1), "g": .float(1), "b": .float(1), "a": .float(1)]),
                                ]),
                            ]),
                        ]),
                    ]),
                    "strokeWeight": .float(1),
                    "strokeCap": .string("ARROW_LINES"),
                    "strokeJoin": .string("BEVEL"),
                    "dashPattern": .array([.float(3), .float(1.5)]),
                    "miterLimit": .float(4),
                    "fillRule": .string("ODD"),
                    "effects": .array([
                        .object([
                            "type": .string("DROP_SHADOW"),
                            "radius": .float(5),
                            "offset": .object(["x": .float(3), "y": .float(6)]),
                            "spread": .float(2),
                            "visible": .bool(true),
                            "color": .object(["r": .float(0.2), "g": .float(0.3), "b": .float(0.4), "a": .float(0.5)]),
                        ]),
                        .object([
                            "type": .string("INNER_SHADOW"),
                            "radius": .float(4),
                            "offset": .object(["x": .float(-1), "y": .float(2)]),
                            "visible": .bool(false),
                            "color": .object(["r": .float(1), "g": .float(0), "b": .float(0), "a": .float(1)]),
                        ]),
                        .object([
                            "type": .string("FOREGROUND_BLUR"),
                            "radius": .float(8),
                            "visible": .bool(true),
                        ]),
                        .object([
                            "type": .string("BACKGROUND_BLUR"),
                            "radius": .float(10),
                            "visible": .bool(false),
                        ]),
                    ]),
                ]),
            ]),
        ])

        let tree = try FigTreeDecoder.buildTree(from: root)
        let page = try XCTUnwrap(tree.root.children.first)
        let rect = try XCTUnwrap(page.children.first)
        let style = try XCTUnwrap(rect.node.style)
        XCTAssertEqual(style.fills.count, 3)
        XCTAssertEqual(style.borders.count, 1)
        XCTAssertEqual(style.shadows.count, 2)
        XCTAssertEqual(style.blurs.count, 2)
        XCTAssertEqual(style.borderOptions.lineCapStyle, .square)
        XCTAssertEqual(style.borderOptions.lineJoinStyle, .bevel)
        XCTAssertEqual(style.borderOptions.dashPattern, [3, 1.5])
        XCTAssertEqual(style.miterLimit, 4, accuracy: 0.000_001)
        XCTAssertEqual(style.windingRule, .evenOdd)

        guard case .gradient(let linear) = style.fills[0].kind else {
            return XCTFail("Expected first fill gradient")
        }
        XCTAssertEqual(linear.type, .linear)
        XCTAssertEqual(style.fills[0].opacity, 0.7, accuracy: 0.000_001)
        XCTAssertEqual(linear.from.x, 0, accuracy: 0.000_001)
        XCTAssertEqual(linear.from.y, 0.5, accuracy: 0.000_001)
        XCTAssertEqual(linear.to.x, 1, accuracy: 0.000_001)
        XCTAssertEqual(linear.to.y, 0.5, accuracy: 0.000_001)
        XCTAssertEqual(linear.stops.count, 4)
        XCTAssertEqual(try XCTUnwrap(linear.stops.first).position, 0, accuracy: 0.000_001)
        XCTAssertEqual(linear.stops[1].position, 0.25, accuracy: 0.000_001)
        XCTAssertEqual(linear.stops[2].position, 0.75, accuracy: 0.000_001)
        XCTAssertEqual(try XCTUnwrap(linear.stops.last).position, 1, accuracy: 0.000_001)
        XCTAssertEqual(linear.stops[1].color.alpha, 0.5, accuracy: 0.000_001)

        guard case .image(let imagePaint) = style.fills[1].kind else {
            return XCTFail("Expected second fill image paint")
        }
        XCTAssertEqual(imagePaint.sourceName, "aabbcc")
        XCTAssertEqual(imagePaint.patternFillType, .fit)
        XCTAssertEqual(imagePaint.patternTileScale, 2.5, accuracy: 0.000_001)
        XCTAssertEqual(imagePaint.embeddedBlobIndex, 0)
        XCTAssertTrue(imagePaint.hasCropTransform)
        XCTAssertEqual(try XCTUnwrap(imagePaint.originalImageWidth), 128, accuracy: 0.000_001)
        XCTAssertEqual(try XCTUnwrap(imagePaint.originalImageHeight), 64, accuracy: 0.000_001)
        XCTAssertEqual(try XCTUnwrap(imagePaint.transform).m02, 0.1, accuracy: 0.000_001)
        XCTAssertEqual(style.fills[1].blendMode, .darken)
        XCTAssertEqual(style.fills[1].opacity, 0.25, accuracy: 0.000_001)

        guard case .gradient(let angular) = style.fills[2].kind else {
            return XCTFail("Expected third fill angular gradient")
        }
        XCTAssertEqual(angular.type, .angular)
        XCTAssertEqual(angular.stops.count, 2)
        XCTAssertEqual(angular.stops[0].position, 0.75, accuracy: 0.000_001)
        XCTAssertEqual(angular.stops[1].position, 0.74999, accuracy: 0.000_001)

        let border = style.borders[0]
        guard case .gradient(let radial) = border.paint.kind else {
            return XCTFail("Expected radial gradient border")
        }
        XCTAssertEqual(radial.type, .radial)
        XCTAssertEqual(border.paint.opacity, 0.4, accuracy: 0.000_001)
        XCTAssertEqual(radial.from.x, 0.5, accuracy: 0.000_001)
        XCTAssertEqual(radial.from.y, 0.5, accuracy: 0.000_001)
        XCTAssertEqual(radial.to.x, 1.0, accuracy: 0.000_001)
        XCTAssertEqual(radial.to.y, 0.5, accuracy: 0.000_001)
        XCTAssertEqual(radial.ellipseLength, 7.0 / 12.0, accuracy: 0.000_001)

        let dropShadow = style.shadows[0]
        XCTAssertEqual(dropShadow.blurRadius, 5, accuracy: 0.000_001)
        XCTAssertEqual(dropShadow.offsetX, 3, accuracy: 0.000_001)
        XCTAssertEqual(dropShadow.offsetY, 6, accuracy: 0.000_001)
        XCTAssertEqual(dropShadow.spread, 2, accuracy: 0.000_001)
        XCTAssertEqual(dropShadow.isInnerShadow, false)
        XCTAssertEqual(dropShadow.isEnabled, true)
        XCTAssertEqual(dropShadow.color, FigColor(red: 0.2, green: 0.3, blue: 0.4, alpha: 0.5))

        let innerShadow = style.shadows[1]
        XCTAssertEqual(innerShadow.isInnerShadow, true)
        XCTAssertEqual(innerShadow.isEnabled, false)
        XCTAssertEqual(innerShadow.spread, 0, accuracy: 0.000_001)

        XCTAssertEqual(style.blurs[0], FigBlur(isEnabled: true, radius: 4, type: .gaussian))
        XCTAssertEqual(style.blurs[1], FigBlur(isEnabled: false, radius: 5, type: .background))
    }

    func testBuildTreeParsesCornersDiamondGradientProgressiveAndGlassEffects() throws {
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
                .object([
                    "guid": .object(["sessionID": .uint(5), "localID": .uint(9)]),
                    "parentIndex": .object([
                        "guid": .object(["sessionID": .uint(0), "localID": .uint(1)]),
                        "position": .uint(0),
                    ]),
                    "type": .string("RECTANGLE"),
                    "name": .string("Styled Rect"),
                    "blendMode": .string("NORMAL"),
                    "opacity": .float(1),
                    "size": .object(["x": .float(100), "y": .float(50)]),
                    "cornerRadius": .float(10),
                    "rectangleTopRightCornerRadius": .float(20),
                    "cornerSmoothing": .float(0.7),
                    "fillPaints": .array([
                        .object([
                            "type": .string("GRADIENT_DIAMOND"),
                            "visible": .bool(true),
                            "transform": .object([
                                "m00": .float(1), "m01": .float(0), "m02": .float(0),
                                "m10": .float(0), "m11": .float(1), "m12": .float(0),
                            ]),
                            "stops": .array([
                                .object([
                                    "position": .float(0.3),
                                    "color": .object(["r": .float(1), "g": .float(0), "b": .float(0), "a": .float(1)]),
                                ]),
                                .object([
                                    "position": .float(0.8),
                                    "color": .object(["r": .float(0), "g": .float(0), "b": .float(1), "a": .float(1)]),
                                ]),
                            ]),
                        ]),
                        .object([
                            "type": .string("IMAGE"),
                            "visible": .bool(true),
                            "imageScaleMode": .string("FILL"),
                            "paintFilter": .object([String: KiwiValue]()),
                            "image": .object([
                                "filename": .string("img.png"),
                            ]),
                        ]),
                    ]),
                    "effects": .array([
                        .object([
                            "type": .string("FOREGROUND_BLUR"),
                            "radius": .float(12),
                            "visible": .bool(true),
                            "blurOpType": .string("PROGRESSIVE"),
                            "startOffset": .object(["x": .float(0.1), "y": .float(0.2)]),
                            "endOffset": .object(["x": .float(0.9), "y": .float(0.8)]),
                            "startRadius": .float(4),
                        ]),
                        .object([
                            "type": .string("GLASS"),
                            "visible": .bool(true),
                            "radius": .float(8),
                            "refractionRadius": .float(30),
                            "chromaticAberration": .float(1.5),
                        ]),
                    ]),
                ]),
            ]),
        ])

        let tree = try FigTreeDecoder.buildTree(from: root)
        let page = try XCTUnwrap(tree.root.children.first)
        let rect = try XCTUnwrap(page.children.first)
        let style = try XCTUnwrap(rect.node.style)

        XCTAssertTrue(style.blendModeWasExplicit)
        XCTAssertEqual(style.blendMode, .normal)
        XCTAssertEqual(style.opacity, 1, accuracy: 0.000_001)

        let corners = try XCTUnwrap(style.corners)
        XCTAssertEqual(corners.radii, [10, 20, 10, 10])
        XCTAssertEqual(corners.style, .smooth)

        guard case .gradient(let gradient) = style.fills[0].kind else {
            return XCTFail("Expected diamond gradient fill")
        }
        XCTAssertEqual(gradient.type, .radial)
        XCTAssertTrue(gradient.usesDiamondFallback)
        XCTAssertEqual(try XCTUnwrap(gradient.stops.first).position, 0, accuracy: 0.000_001)
        XCTAssertEqual(try XCTUnwrap(gradient.stops.last).position, 1, accuracy: 0.000_001)

        guard case .image(let imagePaint) = style.fills[1].kind else {
            return XCTFail("Expected image paint")
        }
        XCTAssertEqual(imagePaint.sourceName, "img.png")
        XCTAssertEqual(imagePaint.patternFillType, .fill)
        XCTAssertTrue(imagePaint.hasPaintFilter)

        XCTAssertEqual(style.blurs.count, 2)
        let progressive = style.blurs[0]
        XCTAssertTrue(progressive.isProgressive)
        XCTAssertEqual(progressive.radius, 6, accuracy: 0.000_001)
        XCTAssertEqual(progressive.progressiveFrom, FigPoint(x: 0.1, y: 0.2))
        XCTAssertEqual(progressive.progressiveTo, FigPoint(x: 0.9, y: 0.8))
        XCTAssertEqual(try XCTUnwrap(progressive.progressiveStartRadiusRatio), 1.0 / 3.0, accuracy: 0.000_001)

        let glass = style.blurs[1]
        XCTAssertTrue(glass.isCustomGlass)
        XCTAssertEqual(glass.radius, 4, accuracy: 0.000_001)
        XCTAssertEqual(glass.glassDistortion, 0.3, accuracy: 0.000_001)
        XCTAssertEqual(glass.glassDepth, 0.6, accuracy: 0.000_001)
        XCTAssertEqual(glass.glassChromaticAberrationMultiplier, 0.5, accuracy: 0.000_001)
    }

    func testGradientAndBorderSemanticsMatchPythonStyleVectors() throws {
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
                .object([
                    "guid": .object(["sessionID": .uint(9), "localID": .uint(9)]),
                    "parentIndex": .object([
                        "guid": .object(["sessionID": .uint(0), "localID": .uint(1)]),
                        "position": .uint(0),
                    ]),
                    "type": .string("RECTANGLE"),
                    "name": .string("Rect"),
                    "size": .object(["x": .float(50), "y": .float(0)]),
                    "strokeWeight": .float(1),
                    "strokePaints": .array([
                        .object([
                            "type": .string("GRADIENT_RADIAL"),
                            "visible": .bool(true),
                            "transform": .object([
                                "m00": .float(1), "m01": .float(0), "m02": .float(0.5),
                                "m10": .float(0), "m11": .float(1), "m12": .float(2),
                            ]),
                            "stops": .array([
                                .object(["position": .float(0), "color": .object(["r": .float(1), "g": .float(0), "b": .float(0), "a": .float(1)])]),
                                .object(["position": .float(1), "color": .object(["r": .float(0), "g": .float(1), "b": .float(0), "a": .float(1)])]),
                            ]),
                        ]),
                    ]),
                    "fillPaints": .array([
                        .object([
                            "type": .string("GRADIENT_ANGULAR"),
                            "visible": .bool(true),
                            "transform": .object([
                                "m00": .float(0.7071), "m01": .float(-0.7071), "m02": .float(0.6),
                                "m10": .float(0.7071), "m11": .float(0.7071), "m12": .float(-0.1),
                            ]),
                            "stops": .array([
                                .object(["position": .float(0), "color": .object(["r": .float(1), "g": .float(0), "b": .float(0), "a": .float(1)])]),
                                .object(["position": .float(0.4), "color": .object(["r": .float(0), "g": .float(1), "b": .float(0), "a": .float(1)])]),
                                .object(["position": .float(1), "color": .object(["r": .float(0), "g": .float(0), "b": .float(1), "a": .float(1)])]),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ])

        let tree = try FigTreeDecoder.buildTree(from: root)
        let page = try XCTUnwrap(tree.root.children.first)
        let rect = try XCTUnwrap(page.children.first)
        let style = try XCTUnwrap(rect.node.style)

        let border = try XCTUnwrap(style.borders.first)
        XCTAssertEqual(border.position, .center, "strokeAlign omitted should default to CENTER")
        guard case .gradient(let radial) = border.paint.kind else {
            return XCTFail("Expected radial border gradient")
        }
        XCTAssertEqual(radial.from, FigPoint(x: 0.0, y: -1.5))
        XCTAssertEqual(radial.to, FigPoint(x: 0.5, y: -1.5))
        XCTAssertEqual(radial.ellipseLength, 2.0 / 52.0, accuracy: 0.000_001)

        guard case .gradient(let angular) = style.fills[0].kind else {
            return XCTFail("Expected angular fill gradient")
        }
        XCTAssertArrayEqual(angular.stops.map(\.position), [0.875, 0.275, 0.87499], accuracy: 0.000_02)
    }

    func testEffectsDefaultAndScaleSemanticsMatchPythonStyleVectors() throws {
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
                .object([
                    "guid": .object(["sessionID": .uint(11), "localID": .uint(12)]),
                    "parentIndex": .object([
                        "guid": .object(["sessionID": .uint(0), "localID": .uint(1)]),
                        "position": .uint(0),
                    ]),
                    "type": .string("RECTANGLE"),
                    "name": .string("Rect"),
                    "effects": .array([
                        .object([
                            "type": .string("DROP_SHADOW"),
                            "radius": .float(5),
                            "offset": .object(["x": .float(3), "y": .float(6)]),
                            "visible": .bool(false),
                            "color": .object(["r": .float(0), "g": .float(1), "b": .float(0.5), "a": .float(0.7)]),
                        ]),
                        .object([
                            "type": .string("FOREGROUND_BLUR"),
                            "radius": .float(5),
                        ]),
                        .object([
                            "type": .string("BACKGROUND_BLUR"),
                            "radius": .float(5),
                        ]),
                    ]),
                ]),
            ]),
        ])

        let tree = try FigTreeDecoder.buildTree(from: root)
        let page = try XCTUnwrap(tree.root.children.first)
        let rect = try XCTUnwrap(page.children.first)
        let style = try XCTUnwrap(rect.node.style)

        let shadow = try XCTUnwrap(style.shadows.first)
        XCTAssertEqual(shadow.blurRadius, 5, accuracy: 0.000_001)
        XCTAssertEqual(shadow.offsetX, 3, accuracy: 0.000_001)
        XCTAssertEqual(shadow.offsetY, 6, accuracy: 0.000_001)
        XCTAssertEqual(shadow.spread, 0, accuracy: 0.000_001, "Missing spread should default to 0")
        XCTAssertFalse(shadow.isEnabled, "visible: false should disable the shadow")
        XCTAssertEqual(shadow.color, FigColor(red: 0, green: 1, blue: 0.5, alpha: 0.7))

        XCTAssertEqual(style.blurs.count, 2)
        XCTAssertEqual(style.blurs[0], FigBlur(isEnabled: true, radius: 2.5, type: .gaussian))
        XCTAssertEqual(style.blurs[1], FigBlur(isEnabled: true, radius: 2.5, type: .background))
    }
}

private func XCTAssertArrayEqual(
    _ lhs: [Double],
    _ rhs: [Double],
    accuracy: Double,
    file: StaticString = #filePath,
    line: UInt = #line
) {
    guard lhs.count == rhs.count else {
        return XCTFail("Count mismatch \(lhs.count) vs \(rhs.count)", file: file, line: line)
    }
    for (idx, pair) in zip(lhs, rhs).enumerated() {
        if abs(pair.0 - pair.1) > accuracy {
            XCTFail("Mismatch at index \(idx): \(pair.0) vs \(pair.1)", file: file, line: line)
            return
        }
    }
}
