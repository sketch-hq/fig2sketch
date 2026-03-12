import FigFormat
import Foundation
import XCTest
import ZIPFoundation

final class FigformatTest_kiwiTests: XCTestCase {
    func test__figformat__test_kiwi__test_kiwi_decoders() throws {
        // Port of tests/figformat/test_kiwi.py::test_kiwi_decoders
        let figURL = fixtureURL(named: "structure.fig")

        let decodedFromFig = try FigTreeDecoder.decodeFigFile(url: figURL)
        let canvasData = try loadCanvasFigData(from: figURL)
        let decodedCanvas = try KiwiCanvasDecoder.decodeCanvasFig(data: canvasData)

        XCTAssertEqual(decodedFromFig.version, decodedCanvas.version)
        XCTAssertEqual(decodedFromFig.rootMessage, decodedCanvas.rootMessage)
        XCTAssertEqual(decodedFromFig.isDataZstd, decodedCanvas.isDataZstd)
        XCTAssertEqual(decodedFromFig.isSchemaZstd, decodedCanvas.isSchemaZstd)
    }

    func test__figformat__test_kiwi__test_kiwi_type_converters() throws {
        // Port of tests/figformat/test_kiwi.py::test_kiwi_type_converters
        let figURL = fixtureURL(named: "structure.fig")
        let decoded = try FigTreeDecoder.decodeFigFile(url: figURL)
        let tree = try FigTreeDecoder.buildTree(from: decoded.rootMessage)

        let allNodes = flattenedNodes(from: tree.root)
        XCTAssertFalse(allNodes.isEmpty)
        XCTAssertTrue(allNodes.allSatisfy { $0.guid.count == 2 }, "GUID converter should produce 2-part IDs")

        let firstRectLike = allNodes.first { $0.type == "RECTANGLE" || $0.type == "ROUNDED_RECTANGLE" }
        let rect = try XCTUnwrap(firstRectLike)
        XCTAssertNotNil(rect.x)
        XCTAssertNotNil(rect.y)
        XCTAssertNotNil(rect.width)
        XCTAssertNotNil(rect.height)

        XCTAssertTrue((rect.x ?? .nan).isFinite)
        XCTAssertTrue((rect.y ?? .nan).isFinite)
        XCTAssertTrue((rect.width ?? .nan).isFinite)
        XCTAssertTrue((rect.height ?? .nan).isFinite)
    }

    private func flattenedNodes(from node: FigTreeNode) -> [FigNode] {
        var output: [FigNode] = [node.node]
        for child in node.children {
            output.append(contentsOf: flattenedNodes(from: child))
        }
        return output
    }

    private func fixtureURL(named name: String) -> URL {
        let file = URL(fileURLWithPath: #filePath)
        let repoRoot = file
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
        return repoRoot.appendingPathComponent("tests/data/\(name)")
    }

    private func loadCanvasFigData(from figURL: URL) throws -> Data {
        let archive = try Archive(url: figURL, accessMode: .read)
        guard let entry = archive["canvas.fig"] else {
            throw NSError(domain: "FigformatTest_kiwiTests", code: 1)
        }

        var data = Data()
        _ = try archive.extract(entry) { chunk in
            data.append(chunk)
        }
        return data
    }
}
