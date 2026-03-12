import FigFormat
import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_layoutTests: XCTestCase {
    func test__converter__test_layout__TestLayout__test_no_layout() throws {
        // Port of tests/converter/test_layout.py::TestLayout.test_no_layout
        let pageJSON = try pageJSONForLayoutFrame(extra: [:])
        XCTAssertTrue(pageJSON.contains("\"groupLayout\":{\"_class\":\"MSImmutableFreeformGroupLayout\""))
    }

    func test__converter__test_layout__TestLayout__test_horizontal_layout() throws {
        // Port of tests/converter/test_layout.py::TestLayout.test_horizontal_layout
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("HORIZONTAL"),
        ])
        XCTAssertTrue(pageJSON.contains("\"groupLayout\":{\"_class\":\"MSImmutableInferredGroupLayout\""))
        XCTAssertTrue(pageJSON.contains("\"flexDirection\":0"))
    }

    func test__converter__test_layout__TestLayout__test_vertical_layout() throws {
        // Port of tests/converter/test_layout.py::TestLayout.test_vertical_layout
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
        ])
        XCTAssertTrue(pageJSON.contains("\"groupLayout\":{\"_class\":\"MSImmutableInferredGroupLayout\""))
        XCTAssertTrue(pageJSON.contains("\"flexDirection\":1"))
    }

    func test__converter__test_layout__TestLayout__test_layout_spacing() throws {
        // Port of tests/converter/test_layout.py::TestLayout.test_layout_spacing
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackSpacing": .float(10),
        ])
        XCTAssertTrue(pageJSON.contains("\"allGuttersGap\":10"))
    }

    func test__converter__test_layout__TestLayoutJustify__test_layout_justify_min() throws {
        // Port of tests/converter/test_layout.py::TestLayoutJustify.test_layout_justify_min
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackPrimaryAlignItems": .string("MIN"),
        ])
        XCTAssertTrue(pageJSON.contains("\"justifyContent\":0"))
    }

    func test__converter__test_layout__TestLayoutJustify__test_layout_justify_center() throws {
        // Port of tests/converter/test_layout.py::TestLayoutJustify.test_layout_justify_center
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackPrimaryAlignItems": .string("CENTER"),
        ])
        XCTAssertTrue(pageJSON.contains("\"justifyContent\":1"))
    }

    func test__converter__test_layout__TestLayoutJustify__test_layout_justify_max() throws {
        // Port of tests/converter/test_layout.py::TestLayoutJustify.test_layout_justify_max
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackPrimaryAlignItems": .string("MAX"),
        ])
        XCTAssertTrue(pageJSON.contains("\"justifyContent\":2"))
    }

    func test__converter__test_layout__TestLayoutJustify__test_layout_justify_space_evenly() throws {
        // Port of tests/converter/test_layout.py::TestLayoutJustify.test_layout_justify_space_evenly
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackPrimaryAlignItems": .string("SPACE_EVENLY"),
        ])
        XCTAssertTrue(pageJSON.contains("\"justifyContent\":3"))
    }

    func test__converter__test_layout__TestLayoutAlignment__test_layout_alignment_min() throws {
        // Port of tests/converter/test_layout.py::TestLayoutAlignment.test_layout_alignment_min
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackCounterAlignItems": .string("MIN"),
        ])
        XCTAssertTrue(pageJSON.contains("\"alignItems\":0"))
    }

    func test__converter__test_layout__TestLayoutAlignment__test_layout_alignment_center() throws {
        // Port of tests/converter/test_layout.py::TestLayoutAlignment.test_layout_alignment_center
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackCounterAlignItems": .string("CENTER"),
        ])
        XCTAssertTrue(pageJSON.contains("\"alignItems\":1"))
    }

    func test__converter__test_layout__TestLayoutAlignment__test_layout_alignment_max() throws {
        // Port of tests/converter/test_layout.py::TestLayoutAlignment.test_layout_alignment_max
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackCounterAlignItems": .string("MAX"),
        ])
        XCTAssertTrue(pageJSON.contains("\"alignItems\":2"))
    }

    func test__converter__test_layout__TestLayoutAlignment__test_layout_alignment_not_set() throws {
        // Port of tests/converter/test_layout.py::TestLayoutAlignment.test_layout_alignment_not_set
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
        ])
        XCTAssertTrue(pageJSON.contains("\"alignItems\":0"))
    }

    func test__converter__test_layout__TestClipping__test_behaviour_default_when_not_set_explicitly() throws {
        // Port of tests/converter/test_layout.py::TestClipping.test_behaviour_default_when_not_set_explicitly
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
        ])
        XCTAssertTrue(pageJSON.contains("\"clippingBehavior\":0"))
    }

    func test__converter__test_layout__TestClipping__test_behaviour_none_when_mask_disabled() throws {
        // Port of tests/converter/test_layout.py::TestClipping.test_behaviour_none_when_mask_disabled
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "frameMaskDisabled": .bool(true),
        ])
        XCTAssertTrue(pageJSON.contains("\"clippingBehavior\":2"))
    }

    func test__converter__test_layout__TestClipping__test_behaviour_default_when_mask_enabled() throws {
        // Port of tests/converter/test_layout.py::TestClipping.test_behaviour_default_when_mask_enabled
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "frameMaskDisabled": .bool(false),
        ])
        XCTAssertTrue(pageJSON.contains("\"clippingBehavior\":0"))
    }

    func test__converter__test_layout__TestPadding__test_padding() throws {
        // Port of tests/converter/test_layout.py::TestPadding.test_padding
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackVerticalPadding": .float(5),
            "stackPaddingRight": .float(10),
            "stackPaddingBottom": .float(15),
            "stackHorizontalPadding": .float(20),
        ])
        XCTAssertTrue(pageJSON.contains("\"topPadding\":5"))
        XCTAssertTrue(pageJSON.contains("\"rightPadding\":10"))
        XCTAssertTrue(pageJSON.contains("\"bottomPadding\":15"))
        XCTAssertTrue(pageJSON.contains("\"leftPadding\":20"))
    }

    func test__converter__test_layout__TestPadding__test_asymetrical_padding() throws {
        // Port of tests/converter/test_layout.py::TestPadding.test_asymetrical_padding
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackVerticalPadding": .float(5),
            "stackPaddingRight": .float(10),
            "stackPaddingBottom": .float(15),
            "stackHorizontalPadding": .float(20),
        ])
        XCTAssertTrue(pageJSON.contains("\"paddingSelection\":1"))
    }

    func test__converter__test_layout__TestPadding__test_symetrical_padding() throws {
        // Port of tests/converter/test_layout.py::TestPadding.test_symetrical_padding
        let pageJSON = try pageJSONForLayoutFrame(extra: [
            "stackMode": .string("VERTICAL"),
            "stackVerticalPadding": .float(5),
            "stackPaddingRight": .float(10),
            "stackPaddingBottom": .float(5),
            "stackHorizontalPadding": .float(10),
        ])
        XCTAssertTrue(pageJSON.contains("\"paddingSelection\":0"))
    }

    private func pageJSONForLayoutFrame(extra: [String: KiwiValue]) throws -> String {
        var frame: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("FRAME"),
            "name": .string("Layout Frame"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "resizeToFit": .bool(false),
            "children": .array([]),
        ]
        for (key, value) in extra {
            frame[key] = value
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
            nodes: [frame, fallbackRect]
        ))
        return try FixtureSupport.pageJSONString(from: document)
    }
}
