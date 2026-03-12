import FigFormat
import XCTest
@testable import Fig2SketchCore

final class FigImageAssetResolverTests: XCTestCase {
    func testResolveMergesZipAssetsWithEmbeddedBlobFallbackAndDiagnostics() {
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
                                    FigPaint(kind: .image(FigImagePaint(sourceName: "zipOnly", patternFillType: .fit))),
                                    FigPaint(kind: .image(FigImagePaint(sourceName: "blobOnly", patternFillType: .fit, embeddedBlobIndex: 0))),
                                    FigPaint(kind: .image(FigImagePaint(
                                        sourceName: "croppedMissing",
                                        patternFillType: .fit,
                                        embeddedBlobIndex: 10,
                                        transform: .init(m00: 1, m01: 0, m02: 0.2, m10: 0, m11: 1, m12: 0)
                                    ))),
                                ]
                            )
                        ),
                        children: []
                    ),
                ]
            )
        )

        let decoded = DecodedCanvasFig(
            version: 70,
            schema: KiwiSchema(types: []),
            rootMessage: .object([
                "nodeChanges": .array([]),
                "blobs": .array([
                    .object(["bytes": .array([.byte(0xDE), .byte(0xAD), .byte(0xBE), .byte(0xEF)])]),
                ]),
            ]),
            isSchemaZstd: false,
            isDataZstd: false
        )

        let result = FigImageAssetResolver.resolve(
            tree: tree,
            decoded: decoded,
            zipImagesBySourceName: [
                "zipOnly": Data("zip".utf8),
            ]
        )

        XCTAssertEqual(result.assets.imagesBySourceName["zipOnly"], Data("zip".utf8))
        XCTAssertEqual(result.assets.imagesBySourceName["blobOnly"], Data([0xDE, 0xAD, 0xBE, 0xEF]))
        XCTAssertEqual(result.missingSourceNames, ["croppedMissing"])
        XCTAssertEqual(result.croppedSourceNames, ["croppedMissing"])
    }
}
