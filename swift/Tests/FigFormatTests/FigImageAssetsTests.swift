import XCTest
@testable import FigFormat

final class FigImageAssetsTests: XCTestCase {
    func testCollectReferencesDeduplicatesAndPreservesBlobFallbackAndCropFlag() {
        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 0], type: "CANVAS", name: "Page"),
                children: [
                    FigTreeNode(
                        node: .init(
                            guid: [1, 1],
                            type: "RECTANGLE",
                            name: "Rect",
                            style: FigLayerStyle(
                                fills: [
                                    FigPaint(kind: .image(FigImagePaint(
                                        sourceName: "imgA",
                                        patternFillType: .fit,
                                        embeddedBlobIndex: 1,
                                        transform: .init(m00: 1, m01: 0, m02: 0.1, m10: 0, m11: 1, m12: 0)
                                    ))),
                                    FigPaint(kind: .image(FigImagePaint(
                                        sourceName: "imgA",
                                        patternFillType: .tile
                                    ))),
                                ]
                            )
                        ),
                        children: []
                    ),
                ]
            )
        )

        let refs = FigImageAssetScanner.collectReferences(from: tree)
        XCTAssertEqual(refs.count, 1)
        XCTAssertEqual(refs[0].sourceName, "imgA")
        XCTAssertEqual(refs[0].embeddedBlobIndex, 1)
        XCTAssertTrue(refs[0].hasCropTransform)
    }

    func testExtractEmbeddedBlobsReadsBytesListFromDecodedCanvasRoot() {
        let decoded = DecodedCanvasFig(
            version: 70,
            schema: KiwiSchema(types: []),
            rootMessage: .object([
                "nodeChanges": .array([]),
                "blobs": .array([
                    .object(["bytes": .array([.byte(0x01), .byte(0x02), .uint(0x03)])]),
                    .object(["bytes": .array([.byte(0xAA)])]),
                ]),
            ]),
            isSchemaZstd: false,
            isDataZstd: false
        )

        let blobs = FigImageAssetScanner.extractEmbeddedBlobs(from: decoded)
        XCTAssertEqual(blobs[0], Data([0x01, 0x02, 0x03]))
        XCTAssertEqual(blobs[1], Data([0xAA]))
    }
}
