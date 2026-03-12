import FigFormat
import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_groupTests: XCTestCase {
    func test__converter__test_group__TestFrameStyles__test_no_style() throws {
        // Port of tests/converter/test_group.py::TestFrameStyles.test_no_style
        let pageJSON = try pageJSONForGroup(extra: [
            "frameMaskDisabled": .bool(true),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"fills\":[]"))
        XCTAssertTrue(pageJSON.contains("\"borders\":[]"))
        XCTAssertTrue(pageJSON.contains("\"blurs\":[]"))
    }

    func test__converter__test_group__TestFrameStyles__test_background() throws {
        // Port of tests/converter/test_group.py::TestFrameStyles.test_background
        let pageJSON = try pageJSONForGroup(extra: [
            "fillPaints": .array([
                .object([
                    "type": .string("SOLID"),
                    "color": color0,
                    "opacity": .float(0.9),
                    "visible": .bool(true),
                ]),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"_class\":\"shapePath\""))
        XCTAssertTrue(pageJSON.contains("\"fillType\":0"))
        XCTAssertTrue(pageJSON.contains("\"color\":{\"_class\":\"color\",\"red\":1,\"green\":0,\"blue\":0.5,\"alpha\":0.9}"))
    }

    func test__converter__test_group__TestFrameStyles__test_fg_blur() throws {
        // Port of tests/converter/test_group.py::TestFrameStyles.test_fg_blur
        let pageJSON = try pageJSONForGroup(extra: [
            "effects": .array([
                .object([
                    "type": .string("FOREGROUND_BLUR"),
                    "radius": .float(4),
                ]),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"_class\":\"blur\""))
        XCTAssertTrue(pageJSON.contains("\"type\":3"))
        XCTAssertTrue(pageJSON.contains("\"radius\":2"))
    }

    func test__converter__test_group__TestFrameStyles__test_bg_blur() throws {
        // Port of tests/converter/test_group.py::TestFrameStyles.test_bg_blur
        let pageJSON = try pageJSONForGroup(extra: [
            "effects": .array([
                .object([
                    "type": .string("BACKGROUND_BLUR"),
                    "radius": .float(4),
                ]),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"_class\":\"blur\""))
        XCTAssertTrue(pageJSON.contains("\"type\":3"))
        XCTAssertTrue(pageJSON.contains("\"radius\":2"))
    }

    func test__converter__test_group__TestFrameStyles__test_shadows() throws {
        // Port of tests/converter/test_group.py::TestFrameStyles.test_shadows
        let pageJSON = try pageJSONForGroup(extra: [
            "effects": .array([
                .object([
                    "type": .string("DROP_SHADOW"),
                    "radius": .float(4),
                    "spread": .float(0),
                    "offset": .object(["x": .float(1), "y": .float(3)]),
                    "color": color1,
                    "visible": .bool(true),
                ]),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"isInnerShadow\":false"))
        XCTAssertTrue(pageJSON.contains("\"blurRadius\":4"))
        XCTAssertTrue(pageJSON.contains("\"offsetX\":1"))
        XCTAssertTrue(pageJSON.contains("\"offsetY\":3"))
    }

    func test__converter__test_group__TestFrameStyles__test_inner_shadows_children() throws {
        // Port of tests/converter/test_group.py::TestFrameStyles.test_inner_shadows_children
        let pageJSON = try pageJSONForGroup(extra: [
            "effects": .array([
                .object([
                    "type": .string("INNER_SHADOW"),
                    "radius": .float(4),
                    "spread": .float(0),
                    "offset": .object(["x": .float(1), "y": .float(3)]),
                    "color": color1,
                    "visible": .bool(true),
                ]),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"isInnerShadow\":true"))
        XCTAssertTrue(pageJSON.contains("\"blurRadius\":4"))
    }

    func test__converter__test_group__TestFrameStyles__test_inner_shadows_background() throws {
        // Port of tests/converter/test_group.py::TestFrameStyles.test_inner_shadows_background
        let pageJSON = try pageJSONForGroup(extra: [
            "effects": .array([
                .object([
                    "type": .string("INNER_SHADOW"),
                    "radius": .float(4),
                    "spread": .float(0),
                    "offset": .object(["x": .float(1), "y": .float(3)]),
                    "color": color1,
                    "visible": .bool(true),
                ]),
            ]),
            "fillPaints": .array([
                .object([
                    "type": .string("SOLID"),
                    "color": color0,
                    "opacity": .float(0.9),
                    "visible": .bool(true),
                ]),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"_class\":\"shapePath\""))
        XCTAssertTrue(pageJSON.contains("\"isInnerShadow\":true"))
        XCTAssertTrue(pageJSON.contains("\"fillType\":0"))
    }

    func test__converter__test_group__TestResizingConstraints__test_equal_resizing_constraints() throws {
        // Port of tests/converter/test_group.py::TestResizingConstraints.test_equal_resizing_constraints
        let pageJSON = try pageJSONForGroup(extra: [
            "resizeToFit": .bool(true),
        ], extraChildren: [
            rectangleChild(guid: (0, 4)),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"horizontalSizing\":1"))
        XCTAssertTrue(pageJSON.contains("\"verticalSizing\":1"))
    }

    func test__converter__test_group__TestResizingConstraints__test_mixed_resizing_constraints() throws {
        // Port of tests/converter/test_group.py::TestResizingConstraints.test_mixed_resizing_constraints
        let pageJSON = try pageJSONForGroup(extra: [
            "resizeToFit": .bool(true),
        ], extraChildren: [
            rectangleChild(guid: (0, 4), extra: [
                "horizontalConstraint": .string("MIN"),
            ]),
        ])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("GRP002"))
    }

    private var color0: KiwiValue {
        FixtureSupport.figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9)
    }

    private var color1: KiwiValue {
        FixtureSupport.figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7)
    }

    private func rectangleChild(guid: (UInt32, UInt32), extra: [String: KiwiValue] = [:]) -> [String: KiwiValue] {
        var rect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(guid.0, guid.1),
            "parentIndex": FixtureSupport.parentIndex(0, 2),
            "type": .string("ROUNDED_RECTANGLE"),
            "name": .string("Child"),
            "size": .object(["x": .float(100), "y": .float(100)]),
        ]
        for (key, value) in extra {
            rect[key] = value
        }
        return rect
    }

    private func pageJSONForGroup(
        extra: [String: KiwiValue],
        extraChildren: [[String: KiwiValue]] = []
    ) throws -> String {
        var group: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("FRAME"),
            "name": .string("Group"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "resizeToFit": .bool(true),
        ]
        for (key, value) in extra {
            group[key] = value
        }

        let nodes = [group, rectangleChild(guid: (0, 3))] + extraChildren
        let document = try FixtureSupport.mapDocument(from: FixtureSupport.makeRootMessage(nodes: nodes))
        return try FixtureSupport.pageJSONString(from: document)
    }
}
