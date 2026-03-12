import FigFormat
import XCTest
@testable import Fig2SketchCore

final class ConverterTest_positioningTests: XCTestCase {
    func test__converter__test_positioning__TestConvert__test_nan() throws {
        // Port of tests/converter/test_positioning.py::TestConvert.test_nan
        // Python expects POS001 warning/error for non-finite transforms.
        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 0], type: "DOCUMENT", name: "Document"),
                children: [
                    FigTreeNode(
                        node: .init(guid: [0, 1], type: "CANVAS", name: "Page 1"),
                        children: [
                            FigTreeNode(
                                node: .init(
                                    guid: [1, 1],
                                    type: "RECTANGLE",
                                    name: "Rect",
                                    x: .nan,
                                    y: .nan,
                                    width: 1,
                                    height: 2
                                ),
                                children: []
                            ),
                        ]
                    ),
                ]
            )
        )

        XCTAssertThrowsError(try FigTreeToDocumentMapper.makeConversionDocument(from: tree))
    }

    func test__converter__test_positioning__TestConvert__test_0_size() throws {
        // Port of tests/converter/test_positioning.py::TestConvert.test_0_size
        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 0], type: "DOCUMENT", name: "Document"),
                children: [
                    FigTreeNode(
                        node: .init(guid: [0, 1], type: "CANVAS", name: "Page 1"),
                        children: [
                            FigTreeNode(
                                node: .init(
                                    guid: [2, 2],
                                    type: "RECTANGLE",
                                    name: "Line",
                                    x: 90,
                                    y: -50,
                                    width: 50,
                                    height: 0
                                ),
                                children: []
                            ),
                        ]
                    ),
                ]
            )
        )

        let document = try FigTreeToDocumentMapper.makeConversionDocument(from: tree)
        let page = try XCTUnwrap(document.pages.first)
        guard case .rectangle(let rect) = try XCTUnwrap(page.layers.first) else {
            return XCTFail("Expected rectangle layer")
        }

        XCTAssertEqual(rect.height, 0.1, accuracy: 0.000_001)
    }
}
