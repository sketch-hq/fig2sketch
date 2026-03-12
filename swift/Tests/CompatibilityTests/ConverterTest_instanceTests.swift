import FigFormat
import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_instanceTests: XCTestCase {
    func test__converter__test_instance__TestOverrides__test_plain_instance() throws {
        // Port of tests/converter/test_instance.py::TestOverrides.test_plain_instance
        let pageJSON = try pageJSONForInstance(instanceExtra: [:])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"symbolInstance\""))
        XCTAssertTrue(pageJSON.contains("\"overrideValues\":[]"))
    }

    func test__converter__test_instance__TestOverrides__test_text_override() throws {
        // Port of tests/converter/test_instance.py::TestOverrides.test_text_override
        let pageJSON = try pageJSONForInstance(instanceExtra: [
            "symbolData": .object([
                "symbolID": FixtureSupport.guid(0, 3),
                "symbolOverrides": .array([
                    .object([
                        "guidPath": .object([
                            "guids": .array([FixtureSupport.guid(1, 9)]),
                        ]),
                        "textData": .object(["characters": .string("modified")]),
                    ]),
                ]),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"symbolInstance\""))
        XCTAssertTrue(pageJSON.contains("_stringValue"))
        XCTAssertTrue(pageJSON.contains("\"value\":\"modified\""))
    }

    func test__converter__test_instance__TestOverrides__test_text_prop_assignment() throws {
        // Port of tests/converter/test_instance.py::TestOverrides.test_text_prop_assignment
        let pageJSON = try pageJSONForInstance(instanceExtra: [
            "componentPropAssignments": .array([
                .object([
                    "defID": FixtureSupport.guid(1, 0),
                    "value": .object([
                        "textValue": .object(["characters": .string("modified")]),
                    ]),
                ]),
            ]),
        ], options: FigTreeMappingOptions(detachUnsupportedInstanceOverrides: false))

        XCTAssertTrue(pageJSON.contains("\"_class\":\"symbolInstance\""))
        XCTAssertTrue(pageJSON.contains("_stringValue"))
        XCTAssertTrue(pageJSON.contains("\"value\":\"modified\""))
    }

    func test__converter__test_instance__TestOverrides__test_color_override_detach() throws {
        // Port of tests/converter/test_instance.py::TestOverrides.test_color_override_detach
        let pageJSON = try pageJSONForInstance(instanceExtra: [
            "symbolData": .object([
                "symbolID": FixtureSupport.guid(0, 3),
                "symbolOverrides": .array([
                    .object([
                        "guidPath": .object([
                            "guids": .array([FixtureSupport.guid(1, 9)]),
                        ]),
                        "fillPaints": .array([
                            .object([
                                "type": .string("SOLID"),
                                "color": FixtureSupport.figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7),
                                "opacity": .float(0.7),
                                "visible": .bool(true),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"fillType\":0"))
        XCTAssertTrue(pageJSON.contains("\"color\":{\"_class\":\"color\",\"red\":0,\"green\":1,\"blue\":0.5,\"alpha\":0.7}"))
        XCTAssertTrue(pageJSON.contains("SYM003"))
    }

    func test__converter__test_instance__TestOverrides__test_color_override_ignored() throws {
        // Port of tests/converter/test_instance.py::TestOverrides.test_color_override_ignored
        let pageJSON = try pageJSONForInstance(instanceExtra: [
            "symbolData": .object([
                "symbolID": FixtureSupport.guid(0, 3),
                "symbolOverrides": .array([
                    .object([
                        "guidPath": .object([
                            "guids": .array([FixtureSupport.guid(0, 11)]),
                        ]),
                        "fillPaints": .array([
                            .object([
                                "type": .string("SOLID"),
                                "color": FixtureSupport.figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7),
                                "opacity": .float(0.7),
                                "visible": .bool(true),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ], options: FigTreeMappingOptions(detachUnsupportedInstanceOverrides: false))

        XCTAssertTrue(pageJSON.contains("\"_class\":\"symbolInstance\""))
        XCTAssertTrue(pageJSON.contains("\"overrideValues\":[]"))
        XCTAssertTrue(pageJSON.contains("SYM002"))
    }

    func test__converter__test_instance__TestOverrides__test_prop_and_symbol_override() throws {
        // Port of tests/converter/test_instance.py::TestOverrides.test_prop_and_symbol_override
        let pageJSON = try pageJSONForInstance(instanceExtra: [
            "symbolData": .object([
                "symbolID": FixtureSupport.guid(0, 3),
                "symbolOverrides": .array([
                    .object([
                        "guidPath": .object([
                            "guids": .array([FixtureSupport.guid(1, 9)]),
                        ]),
                        "textData": .object(["characters": .string("override")]),
                    ]),
                ]),
            ]),
            "componentPropAssignments": .array([
                .object([
                    "defID": FixtureSupport.guid(1, 0),
                    "value": .object([
                        "textValue": .object(["characters": .string("property")]),
                    ]),
                ]),
            ]),
        ], options: FigTreeMappingOptions(detachUnsupportedInstanceOverrides: false))

        XCTAssertTrue(pageJSON.contains("\"_class\":\"symbolInstance\""))
        XCTAssertTrue(pageJSON.contains("_stringValue"))
        XCTAssertTrue(pageJSON.contains("\"value\":\"property\""))
    }

    func test__converter__test_instance__TestDetach__test_convert_to_group() throws {
        // Port of tests/converter/test_instance.py::TestDetach.test_convert_to_group
        let pageJSON = try pageJSONForInstance(instanceExtra: [
            "symbolData": .object([
                "symbolID": FixtureSupport.guid(0, 3),
                "symbolOverrides": .array([
                    .object([
                        "guidPath": .object([
                            "guids": .array([FixtureSupport.guid(1, 9)]),
                        ]),
                        "fillPaints": .array([]),
                    ]),
                ]),
            ]),
            "resizeToFit": .bool(true),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
    }

    func test__converter__test_instance__TestDetach__test_convert_to_artboard() throws {
        // Port of tests/converter/test_instance.py::TestDetach.test_convert_to_artboard
        let pageJSON = try pageJSONForInstance(instanceExtra: [
            "symbolData": .object([
                "symbolID": FixtureSupport.guid(0, 3),
                "symbolOverrides": .array([
                    .object([
                        "guidPath": .object([
                            "guids": .array([FixtureSupport.guid(1, 9)]),
                        ]),
                        "fillPaints": .array([]),
                    ]),
                ]),
            ]),
            "resizeToFit": .bool(false),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
    }

    private func pageJSONForInstance(
        instanceExtra: [String: KiwiValue],
        options: FigTreeMappingOptions = .init()
    ) throws -> String {
        let textNode: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 11),
            "parentIndex": FixtureSupport.parentIndex(0, 3),
            "type": .string("TEXT"),
            "name": .string("Text"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "fontName": .object([
                "family": .string("Roboto"),
                "style": .string("Normal"),
                "postscript": .string("Roboto-Normal"),
            ]),
            "fontSize": .float(12),
            "textAlignVertical": .string("CENTER"),
            "textAlignHorizontal": .string("CENTER"),
            "fillPaints": .array([
                .object([
                    "type": .string("SOLID"),
                    "color": FixtureSupport.figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9),
                    "opacity": .float(0.9),
                    "visible": .bool(true),
                ]),
            ]),
            "textData": .object(["characters": .string("original")]),
            "overrideKey": FixtureSupport.guid(1, 9),
            "componentPropRefs": .array([
                .object([
                    "defID": FixtureSupport.guid(1, 0),
                    "componentPropNodeField": .string("TEXT_DATA"),
                    "isDeleted": .bool(false),
                ]),
            ]),
        ]

        let rectNode: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 3, position: 1),
            "type": .string("ROUNDED_RECTANGLE"),
            "name": .string("Rect"),
            "size": .object(["x": .float(100), "y": .float(100)]),
        ]

        let symbolNode: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 3),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("SYMBOL"),
            "name": .string("Symbol"),
            "size": .object(["x": .float(100), "y": .float(100)]),
        ]

        var instanceNode: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 4),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 2),
            "type": .string("INSTANCE"),
            "name": .string("Instance"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "symbolData": .object([
                "symbolID": FixtureSupport.guid(0, 3),
                "symbolOverrides": .array([]),
            ]),
            "derivedSymbolData": .array([]),
            "resizeToFit": .bool(true),
        ]
        for (key, value) in instanceExtra {
            instanceNode[key] = value
        }

        let fallbackRect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 99),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 99),
            "type": .string("RECTANGLE"),
            "name": .string("Fallback"),
            "size": .object(["x": .float(1), "y": .float(1)]),
        ]

        let root = FixtureSupport.makeRootMessage(
            nodes: [symbolNode, textNode, rectNode, instanceNode, fallbackRect]
        )
        let document = try FixtureSupport.mapDocument(from: root, options: options)
        return try FixtureSupport.pageJSONString(from: document)
    }
}
