import FigFormat
import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_baseTests: XCTestCase {
    func test__converter__test_base__TestIDs__test_avoid_duplicated_ids() throws {
        // Port of tests/converter/test_base.py::TestIDs.test_avoid_duplicated_ids
        let rectangle: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(123, 456),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("RECTANGLE"),
            "name": .string("thing"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "overrideKey": .array([.uint(789), .uint(112)]),
        ]
        let document = try FixtureSupport.mapDocumentFromSingleNode(rectangle)
        let pageJSON = try FixtureSupport.pageJSONString(from: document, salt: "compat-tests")
        let expectedID = ConverterUtils.genObjectID(figID: [123, 456], salt: Data("compat-tests".utf8))

        XCTAssertTrue(pageJSON.contains("\"\(expectedID)\""))
    }

    func test__converter__test_base__TestFrameBackgroud__test_no_background() throws {
        // Port of tests/converter/test_base.py::TestFrameBackgroud.test_no_background
        let node = try FixtureSupport.decodeSingleNode(frameNode(extra: [:]))
        XCTAssertNil(node.style)
    }

    func test__converter__test_base__TestFrameBackgroud__test_disabled_background() throws {
        // Port of tests/converter/test_base.py::TestFrameBackgroud.test_disabled_background
        let style = try FixtureSupport.decodeSingleNodeStyle(frameNode(extra: [
            "fillPaints": .array([
                .object([
                    "type": .string("SOLID"),
                    "color": color0,
                    "opacity": .float(0.9),
                    "visible": .bool(false),
                ]),
            ]),
        ]))
        XCTAssertEqual(style.fills.count, 1)
        XCTAssertFalse(try XCTUnwrap(style.fills.first).isEnabled)
    }

    func test__converter__test_base__TestFrameBackgroud__test_simple_background() throws {
        // Port of tests/converter/test_base.py::TestFrameBackgroud.test_simple_background
        let style = try FixtureSupport.decodeSingleNodeStyle(frameNode(extra: [
            "fillPaints": .array([
                .object([
                    "type": .string("SOLID"),
                    "color": color0,
                    "opacity": .float(0.9),
                    "visible": .bool(true),
                ]),
            ]),
        ]))
        let fill = try XCTUnwrap(style.fills.first)
        guard case .solid(let color) = fill.kind else {
            return XCTFail("Expected solid fill")
        }
        XCTAssertEqual(color, FigColor(red: 1, green: 0, blue: 0.5, alpha: 0.9))
    }

    func test__converter__test_base__TestFrameBackgroud__test_gradient_background() throws {
        // Port of tests/converter/test_base.py::TestFrameBackgroud.test_gradient_background
        let style = try FixtureSupport.decodeSingleNodeStyle(frameNode(extra: [
            "fillPaints": .array([
                .object([
                    "type": .string("GRADIENT_LINEAR"),
                    "transform": FixtureSupport.matrix(
                        m00: 0.7071,
                        m01: -0.7071,
                        m02: 0.6,
                        m10: 0.7071,
                        m11: 0.7071,
                        m12: -0.1
                    ),
                    "stops": .array([
                        .object(["color": color0, "position": .float(0)]),
                        .object(["color": color1, "position": .float(0.4)]),
                    ]),
                    "visible": .bool(true),
                ]),
            ]),
        ]))
        let fill = try XCTUnwrap(style.fills.first)
        guard case .gradient(let gradient) = fill.kind else {
            return XCTFail("Expected gradient fill")
        }
        XCTAssertEqual(gradient.type, .linear)
    }

    func test__converter__test_base__TestInheritStyle__test_apply_fill_override() throws {
        // Port of tests/converter/test_base.py::TestInheritStyle.test_apply_fill_override
        let styleRef: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("ROUNDED_RECTANGLE"),
            "name": .string("StyleRef"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "fillPaints": .array([
                .object([
                    "type": .string("SOLID"),
                    "color": color1,
                    "opacity": .float(0.7),
                    "visible": .bool(true),
                ]),
            ]),
        ]
        let textNode: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 3),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 1),
            "type": .string("TEXT"),
            "name": .string("Text"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "fillPaints": .array([
                .object([
                    "type": .string("SOLID"),
                    "color": color0,
                    "opacity": .float(1),
                    "visible": .bool(true),
                ]),
            ]),
            "inheritFillStyleID": FixtureSupport.guid(0, 2),
        ]
        let pageJSON = try pageJSONIncluding(nodes: [styleRef, textNode])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("\"color\":{\"_class\":\"color\",\"red\":0,\"green\":1,\"blue\":0.5,\"alpha\":0.7}"))
    }

    func test__converter__test_base__TestInheritStyle__test_apply_border_override() throws {
        // Port of tests/converter/test_base.py::TestInheritStyle.test_apply_border_override
        let styleRef: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("ROUNDED_RECTANGLE"),
            "name": .string("StyleRef"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "fillPaints": .array([
                .object([
                    "type": .string("SOLID"),
                    "color": color1,
                    "opacity": .float(0.7),
                    "visible": .bool(true),
                ]),
            ]),
        ]
        let textNode: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 3),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 1),
            "type": .string("TEXT"),
            "name": .string("Text"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "strokePaints": .array([
                .object([
                    "type": .string("SOLID"),
                    "color": color0,
                    "opacity": .float(1),
                    "visible": .bool(true),
                ]),
            ]),
            "strokeWeight": .float(1),
            "inheritFillStyleIDForStroke": FixtureSupport.guid(0, 2),
        ]
        let pageJSON = try pageJSONIncluding(nodes: [styleRef, textNode])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("\"borders\":[{\"_class\":\"border\""))
        XCTAssertTrue(pageJSON.contains("\"color\":{\"_class\":\"color\",\"red\":0,\"green\":1,\"blue\":0.5,\"alpha\":0.7}"))
    }

    func test__converter__test_base__TestInheritStyle__test_apply_text_override() throws {
        // Port of tests/converter/test_base.py::TestInheritStyle.test_apply_text_override
        let textStyleRef: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(10, 1),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("TEXT"),
            "name": .string("TextStyleRef"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "fontName": .object(["family": .string("CustomFont"), "style": .string("Normal")]),
            "fontSize": .float(16),
        ]
        let textNode: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 3),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 1),
            "type": .string("TEXT"),
            "name": .string("Text"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "fontName": .object(["family": .string("Roboto"), "style": .string("Normal")]),
            "fontSize": .float(12),
            "inheritTextStyleID": FixtureSupport.guid(10, 1),
        ]
        let pageJSON = try pageJSONIncluding(nodes: [textStyleRef, textNode])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("CustomFont"))
        XCTAssertTrue(pageJSON.contains("\"fontSize\":12"))
    }

    private var color0: KiwiValue {
        FixtureSupport.figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9)
    }

    private var color1: KiwiValue {
        FixtureSupport.figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7)
    }

    private func frameNode(extra: [String: KiwiValue]) -> [String: KiwiValue] {
        var frame: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("FRAME"),
            "name": .string("Artboard"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "resizeToFit": .bool(false),
        ]
        for (key, value) in extra {
            frame[key] = value
        }
        return frame
    }

    private func pageJSONIncluding(nodes: [[String: KiwiValue]]) throws -> String {
        // Keep one rectangle in the document so current mapper returns a document.
        let fallbackRect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 99),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 99),
            "type": .string("RECTANGLE"),
            "name": .string("Fallback"),
            "size": .object(["x": .float(1), "y": .float(1)]),
        ]
        let root = FixtureSupport.makeRootMessage(nodes: nodes + [fallbackRect])
        let document = try FixtureSupport.mapDocument(from: root)
        return try FixtureSupport.pageJSONString(from: document)
    }
}
