import FigFormat
import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_shape_pathTests: XCTestCase {
    func test__converter__test_shape_path__TestGeometry__test_winding_rule_odd() throws {
        // Port of tests/converter/test_shape_path.py::TestGeometry.test_winding_rule_odd
        let vector: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("VECTOR"),
            "name": .string("Vector"),
            "size": .object(["x": .float(24.5), "y": .float(22)]),
            "fillRule": .string("ODD"),
            "vectorData": .object([
                "styleOverrideTable": .array([
                    .object([
                        "styleID": .uint(1),
                        "strokeCap": .string("ARROW_LINES"),
                    ]),
                ]),
            ]),
        ]

        let style = try FixtureSupport.decodeSingleNodeStyle(vector)
        XCTAssertEqual(style.windingRule, .evenOdd)
    }

    func test__converter__test_shape_path__TestArrows__test_arrow_override() throws {
        // Port of tests/converter/test_shape_path.py::TestArrows.test_arrow_override
        let vector: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("VECTOR"),
            "name": .string("Vector"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "strokeCap": .string("ROUND"),
            "vectorData": .object([
                "styleOverrideTable": .array([
                    .object([
                        "styleID": .uint(1),
                        "strokeCap": .string("ARROW_LINES"),
                    ]),
                ]),
            ]),
        ]
        let fallbackRect: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 3),
            "parentIndex": FixtureSupport.parentIndex(0, 1, position: 1),
            "type": .string("RECTANGLE"),
            "name": .string("Fallback"),
            "size": .object(["x": .float(1), "y": .float(1)]),
        ]

        let document = try FixtureSupport.mapDocument(from: FixtureSupport.makeRootMessage(
            nodes: [vector, fallbackRect]
        ))
        let pageJSON = try FixtureSupport.pageJSONString(from: document)

        XCTAssertTrue(pageJSON.contains("\"startMarkerType\":0"))
        XCTAssertTrue(pageJSON.contains("\"endMarkerType\":1"))
    }

    func test__converter__test_shape_path__test_complex_vector() throws {
        // Port of tests/converter/test_shape_path.py::test_complex_vector
        do {
            let figURL = try FixtureSupport.fixtureURL(named: "vector.fig")
            let decoded = try FigTreeDecoder.decodeFigFile(url: figURL)
            let tree = try FigTreeDecoder.buildTree(from: decoded.rootMessage)
            let document = try FigTreeToDocumentMapper.makeConversionDocument(from: tree)
            let pageJSON = try FixtureSupport.pageJSONString(from: document)
            let pageObject = try FixtureSupport.parseJSONObject(pageJSON)

            XCTAssertTrue(pageJSON.contains("\"_class\":\"shapeGroup\""))
            XCTAssertTrue(pageJSON.contains("\"_class\":\"shapePath\""))
            XCTAssertTrue(pageJSON.contains("\"booleanOperation\":-1"))

            let pageLayers = try XCTUnwrap(pageObject["layers"] as? [[String: Any]])
            var shapePaths: [[String: Any]] = []

            func collectShapePaths(from layer: [String: Any]) {
                if layer["_class"] as? String == "shapePath" {
                    shapePaths.append(layer)
                }
                for child in (layer["layers"] as? [[String: Any]]) ?? [] {
                    collectShapePaths(from: child)
                }
            }

            for layer in pageLayers {
                collectShapePaths(from: layer)
            }

            XCTAssertFalse(shapePaths.isEmpty)
            for shapePath in shapePaths {
                let points = try XCTUnwrap(shapePath["points"] as? [[String: Any]])
                XCTAssertFalse(points.isEmpty)
                XCTAssertNotNil(shapePath["isClosed"] as? Bool)
            }
        } catch {
            XCTFail("test_complex_vector setup/conversion failed: \(error)")
        }
    }

    func test__converter__test_shape_path__test_empty_path() throws {
        // Port of tests/converter/test_shape_path.py::test_empty_path
        let vector: [String: KiwiValue] = [
            "guid": FixtureSupport.guid(0, 2),
            "parentIndex": FixtureSupport.parentIndex(0, 1),
            "type": .string("VECTOR"),
            "name": .string("Vector"),
            "size": .object(["x": .float(100), "y": .float(100)]),
            "vectorNetwork": .object([
                "regions": .array([]),
                "segments": .array([]),
                "vertices": .array([]),
            ]),
        ]

        XCTAssertThrowsError(try FixtureSupport.mapDocumentFromSingleNode(vector)) { error in
            XCTAssertTrue("\(error)".contains("SHP002"))
        }
    }
}
