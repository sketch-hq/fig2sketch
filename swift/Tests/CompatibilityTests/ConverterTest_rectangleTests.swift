import FigFormat
import XCTest

final class ConverterTest_rectangleTests: XCTestCase {
    func test__converter__test_rectangle__TestCorners__test_straight_corners() throws {
        // Port of tests/converter/test_rectangle.py::TestCorners.test_straight_corners
        let node = try rectangleNode(extra: [:])
        XCTAssertNil(node.style?.corners)
    }

    func test__converter__test_rectangle__TestCorners__test_round_corners() throws {
        // Port of tests/converter/test_rectangle.py::TestCorners.test_round_corners
        let node = try rectangleNode(extra: [
            "cornerRadius": .float(5),
            "rectangleCornerRadiiIndependent": .bool(false),
        ])

        let corners = try XCTUnwrap(node.style?.corners)
        XCTAssertEqual(corners.radii, [5, 5, 5, 5])
    }

    func test__converter__test_rectangle__TestCorners__test_uneven_corners() throws {
        // Port of tests/converter/test_rectangle.py::TestCorners.test_uneven_corners
        let node = try rectangleNode(extra: [
            "rectangleTopLeftCornerRadius": .float(5),
            "rectangleBottomRightCornerRadius": .float(7),
            "fixedRadius": .float(10),
            "rectangleCornerRadiiIndependent": .bool(true),
        ])

        let corners = try XCTUnwrap(node.style?.corners)
        XCTAssertEqual(corners.radii, [5, 0, 7, 0])
    }

    private func rectangleNode(extra: [String: KiwiValue]) throws -> FigNode {
        var rect: [String: KiwiValue] = [
            "guid": .object(["sessionID": .uint(7), "localID": .uint(8)]),
            "parentIndex": .object([
                "guid": .object(["sessionID": .uint(0), "localID": .uint(1)]),
                "position": .uint(0),
            ]),
            "type": .string("RECTANGLE"),
            "name": .string("Rect"),
            "size": .object(["x": .float(100), "y": .float(100)]),
        ]
        for (key, value) in extra {
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
        return try XCTUnwrap(page.children.first?.node)
    }
}
