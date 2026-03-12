import FigFormat
import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_symbolTests: XCTestCase {
    func test__converter__test_symbol__test_rounded_corners() throws {
        // Port of tests/converter/test_symbol.py::test_rounded_corners
        let symbol: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("SYMBOL"),
            "name": .string("Symbol"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "rectangleTopLeftCornerRadius": .float(5),
        ]

        let childRect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 3),
            "parentIndex": FixtureSupport.parentIndex(0, 2),
            "type": .string("ROUNDED_RECTANGLE"),
            "name": .string("Rect"),
            "size": .object(["x": .float(100), "y": .float(100)]),
        ]

        let root = FixtureSupport.makeRootMessage(nodes: [symbol, childRect])
        let document = try FixtureSupport.mapDocument(from: root)
        let pageJSON = try FixtureSupport.pageJSONString(from: document)
        let symbolsPageJSON = try FixtureSupport.pageJSONString(from: document, pageIndex: 1)

        XCTAssertTrue(pageJSON.contains("\"_class\":\"symbolInstance\""))
        XCTAssertTrue(pageJSON.contains("\"symbolID\""))
        XCTAssertTrue(symbolsPageJSON.contains("\"_class\":\"symbolMaster\""))
        XCTAssertTrue(symbolsPageJSON.contains("\"corners\":{\"_class\":\"MSImmutableStyleCorners\",\"radii\":[5.0,0.0,0.0,0.0]"))
    }

    func test__converter__test_symbol__test_inner_shadows_children_of_symbol() throws {
        // Port of tests/converter/test_symbol.py::test_inner_shadows_children_of_symbol
        let symbol: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("SYMBOL"),
            "name": .string("Symbol"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "effects": .array([
                .object([
                    "type": .string("INNER_SHADOW"),
                    "radius": .float(4),
                    "spread": .float(0),
                    "offset": .object(["x": .float(1), "y": .float(3)]),
                    "color": FixtureSupport.figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7),
                    "visible": .bool(true),
                ]),
            ]),
        ]

        let childRect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 3),
            "parentIndex": FixtureSupport.parentIndex(0, 2),
            "type": .string("ROUNDED_RECTANGLE"),
            "name": .string("Rect"),
            "size": .object(["x": .float(100), "y": .float(100)]),
        ]

        let root = FixtureSupport.makeRootMessage(nodes: [symbol, childRect])
        let document = try FixtureSupport.mapDocument(from: root)
        let symbolsPageJSON = try FixtureSupport.pageJSONString(from: document, pageIndex: 1)

        XCTAssertTrue(symbolsPageJSON.contains("\"_class\":\"symbolMaster\""))
        XCTAssertTrue(symbolsPageJSON.contains("\"isInnerShadow\":true"))
        XCTAssertTrue(symbolsPageJSON.contains("\"blurRadius\":4"))
        XCTAssertTrue(symbolsPageJSON.contains("\"offsetX\":1"))
        XCTAssertTrue(symbolsPageJSON.contains("\"offsetY\":3"))
    }

    func test__converter__test_symbol__test_variant_name() throws {
        // Port of tests/converter/test_symbol.py::test_variant_name
        let variants: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(22, 22),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("FRAME"),
            "name": .string("Starch"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "isStateGroup": .bool(true),
            "stateGroupPropertyValueOrders": .array([
                .object([
                    "property": .string("Property 1"),
                    "values": .array([.string("Potato"), .string("Orange")]),
                ]),
                .object([
                    "property": .string("Property 2"),
                    "values": .array([.string("Something"), .string("Another")]),
                ]),
            ]),
        ]

        let symbol: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(22, 23),
            "parentIndex": FixtureSupport.parentIndex(22, 22),
            "type": .string("SYMBOL"),
            "name": .string("Property 1=Potato, Property 2=Another"),
            "size": .object(["x": .float(100), "y": .float(100)]),
        ]

        let childRect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(22, 24),
            "parentIndex": FixtureSupport.parentIndex(22, 23),
            "type": .string("ROUNDED_RECTANGLE"),
            "name": .string("Rect"),
            "size": .object(["x": .float(30), "y": .float(30)]),
        ]

        let root = FixtureSupport.makeRootMessage(nodes: [variants, symbol, childRect])
        let document = try FixtureSupport.mapDocument(from: root)
        let symbolsPageJSON = try FixtureSupport.pageJSONString(from: document, pageIndex: 1)

        XCTAssertTrue(symbolsPageJSON.contains("Starch/Potato/Another"))
    }
}
