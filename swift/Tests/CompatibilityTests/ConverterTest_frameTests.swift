import FigFormat
import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_frameTests: XCTestCase {
    func test__converter__test_frame__TestFrameBackgroud__test_no_background() throws {
        // Port of tests/converter/test_frame.py::TestFrameBackgroud.test_no_background
        let node = try FixtureSupport.decodeSingleNode(frameNode(extra: [:]))
        XCTAssertNil(node.style)
    }

    func test__converter__test_frame__TestFrameBackgroud__test_disabled_background() throws {
        // Port of tests/converter/test_frame.py::TestFrameBackgroud.test_disabled_background
        let style = try FixtureSupport.decodeSingleNodeStyle(frameNode(extra: [
            "fillPaints": .array([solidPaint(color: color0, opacity: 0.9, visible: false)]),
        ]))
        XCTAssertEqual(style.fills.count, 1)
        XCTAssertFalse(try XCTUnwrap(style.fills.first).isEnabled)
    }

    func test__converter__test_frame__TestFrameBackgroud__test_simple_background() throws {
        // Port of tests/converter/test_frame.py::TestFrameBackgroud.test_simple_background
        let style = try FixtureSupport.decodeSingleNodeStyle(frameNode(extra: [
            "fillPaints": .array([solidPaint(color: color0, opacity: 0.9, visible: true)]),
        ]))
        guard case .solid(let color) = try XCTUnwrap(style.fills.first).kind else {
            return XCTFail("Expected solid fill")
        }
        XCTAssertEqual(color, FigColor(red: 1, green: 0, blue: 0.5, alpha: 0.9))
    }

    func test__converter__test_frame__TestFrameBackgroud__test_gradient_background() throws {
        // Port of tests/converter/test_frame.py::TestFrameBackgroud.test_gradient_background
        let style = try FixtureSupport.decodeSingleNodeStyle(frameNode(extra: [
            "fillPaints": .array([
                .object([
                    "type": .string("GRADIENT_LINEAR"),
                    "transform": FixtureSupport.matrix(
                        m00: 0.7071, m01: -0.7071, m02: 0.6, m10: 0.7071, m11: 0.7071, m12: -0.1
                    ),
                    "stops": .array([
                        .object(["color": color0, "position": .float(0)]),
                        .object(["color": color1, "position": .float(0.4)]),
                    ]),
                    "visible": .bool(true),
                ]),
            ]),
        ]))
        guard case .gradient(let gradient) = try XCTUnwrap(style.fills.first).kind else {
            return XCTFail("Expected gradient fill")
        }
        XCTAssertEqual(gradient.type, .linear)
    }

    func test__converter__test_frame__TestFrameBackgroud__test_rounded_corners() throws {
        // Port of tests/converter/test_frame.py::TestFrameBackgroud.test_rounded_corners
        let style = try FixtureSupport.decodeSingleNodeStyle(frameNode(extra: [
            "cornerRadius": .float(5),
        ]))
        XCTAssertEqual(try XCTUnwrap(style.corners).radii, [5, 5, 5, 5])
    }

    func test__converter__test_frame__TestFrameBackgroud__test_section_as_frame() throws {
        // Port of tests/converter/test_frame.py::TestFrameBackgroud.test_section_as_frame
        let section: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("SECTION"),
            "name": .string("Section"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "fillPaints": .array([solidPaint(color: color0, opacity: 0.9, visible: true)]),
        ]
        let childRect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 3),
            "parentIndex": FixtureSupport.parentIndex(0, 2),
            "type": .string("ROUNDED_RECTANGLE"),
            "name": .string("Rect"),
            "size": .object(["x": .float(100), "y": .float(100)]),
        ]
        let pageJSON = try pageJSONForNodes([section, childRect])

        XCTAssertTrue(pageJSON.contains("\"_class\":\"group\""))
        XCTAssertTrue(pageJSON.contains("\"name\":\"Section\""))
        XCTAssertTrue(pageJSON.contains("\"fillType\":0"))
    }

    func test__converter__test_frame__TestGrid__test_single_grid() throws {
        // Port of tests/converter/test_frame.py::TestGrid.test_single_grid
        let pageJSON = try pageJSONForFrame(extra: [
            "layoutGrids": .array([grid(spacing: 20, color: color0)]),
        ])
        XCTAssertTrue(pageJSON.contains("\"grid\""))
        XCTAssertTrue(pageJSON.contains("\"gridSize\":20"))
        XCTAssertTrue(pageJSON.contains("\"thickGridTimes\":0"))
    }

    func test__converter__test_frame__TestGrid__test_dual_multiple_grid() throws {
        // Port of tests/converter/test_frame.py::TestGrid.test_dual_multiple_grid
        let pageJSON = try pageJSONForFrame(extra: [
            "layoutGrids": .array([
                grid(spacing: 20, color: color0),
                grid(spacing: 60, color: color0),
            ]),
        ])
        XCTAssertTrue(pageJSON.contains("\"gridSize\":20"))
        XCTAssertTrue(pageJSON.contains("\"thickGridTimes\":3"))
    }

    func test__converter__test_frame__TestGrid__test_dual_nonmultiple_grid() throws {
        // Port of tests/converter/test_frame.py::TestGrid.test_dual_nonmultiple_grid
        let pageJSON = try pageJSONForFrame(extra: [
            "layoutGrids": .array([
                grid(spacing: 15, color: color0),
                grid(spacing: 50, color: color0),
            ]),
        ])
        XCTAssertTrue(pageJSON.contains("\"gridSize\":15"))
        XCTAssertTrue(pageJSON.contains("\"thickGridTimes\":0"))
        XCTAssertTrue(pageJSON.contains("GRD002"))
    }

    func test__converter__test_frame__TestGrid__test_triple_grid() throws {
        // Port of tests/converter/test_frame.py::TestGrid.test_triple_grid
        let pageJSON = try pageJSONForFrame(extra: [
            "layoutGrids": .array([
                grid(spacing: 15, color: color0),
                grid(spacing: 30, color: color0),
                grid(spacing: 45, color: color0),
            ]),
        ])
        XCTAssertTrue(pageJSON.contains("\"gridSize\":15"))
        XCTAssertTrue(pageJSON.contains("\"thickGridTimes\":2"))
        XCTAssertTrue(pageJSON.contains("GRD003"))
    }

    func test__converter__test_frame__TestGrid__test_triple_multiple_grid() throws {
        // Port of tests/converter/test_frame.py::TestGrid.test_triple_multiple_grid
        let pageJSON = try pageJSONForFrame(extra: [
            "layoutGrids": .array([
                grid(spacing: 15, color: color0),
                grid(spacing: 25, color: color0),
                grid(spacing: 45, color: color0),
            ]),
        ])
        XCTAssertTrue(pageJSON.contains("\"gridSize\":15"))
        XCTAssertTrue(pageJSON.contains("\"thickGridTimes\":3"))
    }

    func test__converter__test_frame__TestLayout__test_4_columns() throws {
        // Port of tests/converter/test_frame.py::TestLayout.test_4_columns
        let pageJSON = try pageJSONForFrame(extra: [
            "layoutGrids": .array([layout()]),
        ])
        XCTAssertTrue(pageJSON.contains("\"drawVertical\":true"))
        XCTAssertTrue(pageJSON.contains("\"totalWidth\":110"))
        XCTAssertTrue(pageJSON.contains("\"gutterWidth\":10"))
        XCTAssertTrue(pageJSON.contains("\"columnWidth\":20"))
        XCTAssertTrue(pageJSON.contains("\"numberOfColumns\":4"))
    }

    func test__converter__test_frame__TestLayout__test_centered_columns() throws {
        // Port of tests/converter/test_frame.py::TestLayout.test_centered_columns
        let pageJSON = try pageJSONForFrame(extra: [
            "layoutGrids": .array([layout(align: "CENTER")]),
        ])
        XCTAssertTrue(pageJSON.contains("\"drawVertical\":true"))
        XCTAssertTrue(pageJSON.contains("\"horizontalOffset\":45"))
    }

    func test__converter__test_frame__TestLayout__test_multiple_column_layouts() throws {
        // Port of tests/converter/test_frame.py::TestLayout.test_multiple_column_layouts
        let pageJSON = try pageJSONForFrame(extra: [
            "layoutGrids": .array([
                layout(align: "MIN", count: 2_147_483_647),
                layout(),
            ]),
        ])
        XCTAssertTrue(pageJSON.contains("\"numberOfColumns\":10"))
        XCTAssertTrue(pageJSON.contains("\"horizontalOffset\":0"))
        XCTAssertTrue(pageJSON.contains("GRD004"))
    }

    func test__converter__test_frame__TestLayout__test_row_layout() throws {
        // Port of tests/converter/test_frame.py::TestLayout.test_row_layout
        let pageJSON = try pageJSONForFrame(extra: [
            "layoutGrids": .array([layout(axis: "Y")]),
        ])
        XCTAssertTrue(pageJSON.contains("\"drawHorizontal\":true"))
        XCTAssertTrue(pageJSON.contains("\"totalWidth\":200"))
        XCTAssertTrue(pageJSON.contains("\"gutterHeight\":10"))
        XCTAssertTrue(pageJSON.contains("\"rowHeightMultiplication\":2"))
    }

    func test__converter__test_frame__TestLayout__test_float_row_layout() throws {
        // Port of tests/converter/test_frame.py::TestLayout.test_float_row_layout
        let pageJSON = try pageJSONForFrame(extra: [
            "layoutGrids": .array([layout(axis: "Y", align: "CENTER", spacing: 27)]),
        ])
        XCTAssertTrue(pageJSON.contains("GRD007"))
        XCTAssertTrue(pageJSON.contains("GRD005"))
        XCTAssertTrue(pageJSON.contains("GRD006"))
    }

    private var color0: KiwiValue {
        FixtureSupport.figColor(red: 1, green: 0, blue: 0.5, alpha: 0.9)
    }

    private var color1: KiwiValue {
        FixtureSupport.figColor(red: 0, green: 1, blue: 0.5, alpha: 0.7)
    }

    private func solidPaint(color: KiwiValue, opacity: Double, visible: Bool) -> KiwiValue {
        .object([
            "type": .string("SOLID"),
            "color": color,
            "opacity": .float(opacity),
            "visible": .bool(visible),
        ])
    }

    private func frameNode(extra: [String: KiwiValue]) -> [String: KiwiValue] {
        var frame: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("FRAME"),
            "name": .string("Artboard"),
            "size": .object(["x": .float(200), "y": .float(110)]),
            "resizeToFit": .bool(false),
            "children": .array([]),
        ]
        for (key, value) in extra {
            frame[key] = value
        }
        return frame
    }

    private func grid(spacing: Double, color: KiwiValue) -> KiwiValue {
        .object([
            "type": .string("STRETCH"),
            "axis": .string("X"),
            "visible": .bool(true),
            "numSections": .float(5),
            "offset": .float(0),
            "sectionSize": .float(spacing),
            "gutterSize": .float(20),
            "color": color,
            "pattern": .string("GRID"),
        ])
    }

    private func layout(
        axis: String = "X",
        align: String = "STRETCH",
        count: Double = 4,
        offset: Double = 0,
        spacing: Double = 20,
        gutter: Double = 10
    ) -> KiwiValue {
        .object([
            "type": .string(align),
            "axis": .string(axis),
            "visible": .bool(true),
            "numSections": .float(count),
            "offset": .float(offset),
            "sectionSize": .float(spacing),
            "gutterSize": .float(gutter),
            "color": FixtureSupport.figColor(red: 0, green: 0, blue: 0, alpha: 0),
            "pattern": .string("STRIPES"),
        ])
    }

    private func pageJSONForFrame(extra: [String: KiwiValue]) throws -> String {
        try pageJSONForNodes([frameNode(extra: extra)])
    }

    private func pageJSONForNodes(_ nodes: [[String: KiwiValue]]) throws -> String {
        // Keep one rectangle in the document so current mapper returns a document.
        let fallbackRect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 99),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 99),
            "type": .string("RECTANGLE"),
            "name": .string("Fallback"),
            "size": .object(["x": .float(1), "y": .float(1)]),
        ]
        let document = try FixtureSupport.mapDocument(from: FixtureSupport.makeRootMessage(
            nodes: nodes + [fallbackRect]
        ))
        return try FixtureSupport.pageJSONString(from: document)
    }
}
