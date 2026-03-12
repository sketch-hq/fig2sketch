import FigFormat
import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_textTests: XCTestCase {
    func test__converter__test_text__TestOverrideStyles__test_plain_text() throws {
        // Port of tests/converter/test_text.py::TestOverrideStyles.test_plain_text
        let pageJSON = try pageJSONForText(extra: [
            "textData": .object(["characters": .string("plain")]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("\"MSAttributedStringColorAttribute\":{\"_class\":\"color\",\"red\":1,\"green\":0,\"blue\":0.5,\"alpha\":0.9}"))
        XCTAssertTrue(pageJSON.contains("\"location\":0"))
        XCTAssertTrue(pageJSON.contains("\"length\":5"))
    }

    func test__converter__test_text__TestOverrideStyles__test_multi_color_text() throws {
        // Port of tests/converter/test_text.py::TestOverrideStyles.test_multi_color_text
        let pageJSON = try pageJSONForText(extra: [
            "textData": .object([
                "characters": .string("abcdefghijklmnñopqrstuvwxyz"),
                "characterStyleIDs": .array([.uint(0), .uint(0), .uint(0), .uint(1), .uint(1), .uint(1), .uint(2), .uint(2), .uint(2)]),
                "styleOverrideTable": .array([
                    .object([
                        "styleID": .uint(1),
                        "fillPaints": .array([
                            .object([
                                "type": .string("SOLID"),
                                "color": FixtureSupport.figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7),
                            ]),
                        ]),
                    ]),
                    .object([
                        "styleID": .uint(2),
                        "fillPaints": .array([
                            .object([
                                "type": .string("SOLID"),
                                "color": FixtureSupport.figColor(red: 0, green: 0, blue: 1, alpha: 1),
                            ]),
                        ]),
                    ]),
                ]),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("\"location\":0"))
        XCTAssertTrue(pageJSON.contains("\"length\":3"))
        XCTAssertTrue(pageJSON.contains("\"red\":0,\"green\":1,\"blue\":0.5"))
        XCTAssertTrue(pageJSON.contains("\"red\":0,\"green\":0,\"blue\":1"))
    }

    func test__converter__test_text__TestOverrideStyles__test_emoji_text() throws {
        // Port of tests/converter/test_text.py::TestOverrideStyles.test_emoji_text
        let glyphs: [KiwiValue] = (0..<13).map { index in
            if index == 7 {
                return .object([
                    "firstCharacter": .uint(UInt32(index)),
                    "emojiCodePoints": .array([.uint(10084), .uint(65039)]),
                ])
            }
            return .object(["firstCharacter": .uint(UInt32(index))])
        }
        let pageJSON = try pageJSONForText(extra: [
            "textData": .object([
                "characters": .string("Sketch ❤️ you"),
                "glyphs": .array(glyphs),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("AppleColorEmoji"))
        XCTAssertTrue(pageJSON.contains("\"location\":7"))
        XCTAssertTrue(pageJSON.contains("\"length\":1"))
    }

    func test__converter__test_text__TestOverrideStyles__test_multi_code_point_text() throws {
        // Port of tests/converter/test_text.py::TestOverrideStyles.test_multi_code_point_text
        var glyphs: [KiwiValue] = (0..<16).map { index in
            .object(["firstCharacter": .uint(UInt32(index))])
        }
        glyphs[5] = .object([
            "firstCharacter": .uint(5),
            "emojiCodePoints": .array([.uint(127_987), .uint(65_039), .uint(8_205), .uint(127_752)]),
        ])
        glyphs.remove(at: 6)
        glyphs.remove(at: 6)
        glyphs.remove(at: 6)

        let pageJSON = try pageJSONForText(extra: [
            "textData": .object([
                "characters": .string("nice 🏳️‍🌈 flag"),
                "glyphs": .array(glyphs),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("AppleColorEmoji"))
        XCTAssertTrue(pageJSON.contains("\"location\":5"))
        XCTAssertTrue(pageJSON.contains("\"length\":6"))
    }

    func test__converter__test_text__TestConvert__test_no_kerning() throws {
        // Port of tests/converter/test_text.py::TestConvert.test_no_kerning
        let pageJSON = try pageJSONForText(extra: [
            "textData": .object(["characters": .string("plain")]),
        ])
        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertFalse(pageJSON.contains("\"kerning\":"))
        XCTAssertTrue(pageJSON.contains("\"width\":100"))
    }

    func test__converter__test_text__TestConvert__test_zero_kerning() throws {
        // Port of tests/converter/test_text.py::TestConvert.test_zero_kerning
        let pageJSON = try pageJSONForText(extra: [
            "textData": .object(["characters": .string("plain")]),
            "letterSpacing": .object([
                "units": .string("PIXELS"),
                "value": .float(0),
            ]),
        ])
        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertFalse(pageJSON.contains("\"kerning\":"))
        XCTAssertTrue(pageJSON.contains("\"width\":100"))
    }

    func test__converter__test_text__TestConvert__test_kerning_fixed_width() throws {
        // Port of tests/converter/test_text.py::TestConvert.test_kerning_fixed_width
        let pageJSON = try pageJSONForText(extra: [
            "textData": .object(["characters": .string("plain")]),
            "letterSpacing": .object([
                "units": .string("PIXELS"),
                "value": .float(10),
            ]),
            "textAutoResize": .string("HEIGHT"),
        ])
        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("\"kerning\":10"))
        XCTAssertTrue(pageJSON.contains("\"width\":100"))
    }

    func test__converter__test_text__TestConvert__test_kerning_flexible_width() throws {
        // Port of tests/converter/test_text.py::TestConvert.test_kerning_flexible_width
        let pageJSON = try pageJSONForText(extra: [
            "textData": .object(["characters": .string("plain")]),
            "letterSpacing": .object([
                "units": .string("PERCENT"),
                "value": .float(50),
            ]),
            "textAutoResize": .string("WIDTH_AND_HEIGHT"),
        ])
        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("\"kerning\":6"))
        XCTAssertTrue(pageJSON.contains("\"width\":106"))
    }

    func test__converter__test_text__TestFeatures__test_no_features() throws {
        // Port of tests/converter/test_text.py::TestFeatures.test_no_features
        let pageJSON = try pageJSONForText(extra: [
            "textData": .object(["characters": .string("plain")]),
        ])
        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertFalse(pageJSON.contains("featureSettings"))
    }

    func test__converter__test_text__TestFeatures__test_some_features() throws {
        // Port of tests/converter/test_text.py::TestFeatures.test_some_features
        let pageJSON = try pageJSONForText(extra: [
            "textData": .object(["characters": .string("plain")]),
            "toggledOnOTFeatures": .array([.string("SS03")]),
            "toggledOffOTFeatures": .array([.string("CALT")]),
        ])
        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("featureSettings"))
        XCTAssertTrue(pageJSON.contains("\"CTFeatureSelectorIdentifier\":6"))
        XCTAssertTrue(pageJSON.contains("\"CTFeatureTypeIdentifier\":35"))
        XCTAssertTrue(pageJSON.contains("\"CTFeatureSelectorIdentifier\":1"))
        XCTAssertTrue(pageJSON.contains("\"CTFeatureTypeIdentifier\":36"))
    }

    func test__converter__test_text__TestFeatures__test_unsupported_features() throws {
        // Port of tests/converter/test_text.py::TestFeatures.test_unsupported_features
        let pageJSON = try pageJSONForText(extra: [
            "textData": .object(["characters": .string("plain")]),
            "toggledOnOTFeatures": .array([.string("CV03"), .string("SS03")]),
        ])
        XCTAssertTrue(pageJSON.contains("\"_class\":\"text\""))
        XCTAssertTrue(pageJSON.contains("featureSettings"))
        XCTAssertTrue(pageJSON.contains("\"CTFeatureSelectorIdentifier\":6"))
        XCTAssertTrue(pageJSON.contains("\"CTFeatureTypeIdentifier\":35"))
        XCTAssertTrue(pageJSON.contains("TXT006"))
    }

    private func pageJSONForText(extra: [String: KiwiValue]) throws -> String {
        var textNode: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("TEXT"),
            "name": .string("Text"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "fontName": .object(["family": .string("Roboto"), "style": .string("Normal")]),
            "fontSize": .float(12),
            "textAlignVertical": .string("CENTER"),
            "textAlignHorizontal": .string("CENTER"),
            "fillPaints": .array([
                .object([
                    "type": .string("SOLID"),
                    "color": FixtureSupport.figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9),
                    "opacity": .float(1),
                    "visible": .bool(true),
                ]),
            ]),
        ]
        for (key, value) in extra {
            textNode[key] = value
        }

        // Keep one rectangle in the document so current mapper returns a document.
        let fallbackRect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 99),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 99),
            "type": .string("RECTANGLE"),
            "name": .string("Fallback"),
            "size": .object(["x": .float(1), "y": .float(1)]),
        ]

        let document = try FixtureSupport.mapDocument(from: FixtureSupport.makeRootMessage(
            nodes: [textNode, fallbackRect]
        ))
        return try FixtureSupport.pageJSONString(from: document)
    }
}
