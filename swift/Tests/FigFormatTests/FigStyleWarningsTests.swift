import XCTest
@testable import FigFormat

final class FigStyleWarningsTests: XCTestCase {
    func testScannerFindsDeduplicatedStyleWarningsAcrossFillsAndBorders() {
        let style = FigLayerStyle(
            fills: [
                FigPaint(kind: .gradient(
                    FigGradient(
                        type: .radial,
                        from: FigPoint(x: 0.5, y: 0.5),
                        to: FigPoint(x: 1, y: 0.5),
                        stops: [
                            .init(color: .init(red: 1, green: 0, blue: 0, alpha: 1), position: 0),
                            .init(color: .init(red: 0, green: 0, blue: 1, alpha: 1), position: 1),
                        ],
                        usesDiamondFallback: true
                    )
                )),
                FigPaint(kind: .image(
                    FigImagePaint(
                        sourceName: "fill-image",
                        patternFillType: .fit,
                        hasPaintFilter: true
                    )
                )),
            ],
            borders: [
                FigBorder(
                    paint: FigPaint(kind: .image(
                        FigImagePaint(
                            sourceName: "border-image",
                            patternFillType: .tile,
                            hasPaintFilter: true
                        )
                    )),
                    thickness: 1,
                    position: .center
                ),
            ],
            blurs: [
                FigBlur(isEnabled: true, radius: 4, type: .gaussian),
                FigBlur(isEnabled: true, radius: 5, type: .background),
            ]
        )

        let tree = FigTree(
            root: FigTreeNode(
                node: .init(guid: [0, 0], type: "DOCUMENT", name: "Doc"),
                children: [
                    FigTreeNode(
                        node: .init(guid: [1, 2], type: "RECTANGLE", name: "Rect", style: style),
                        children: []
                    ),
                ]
            )
        )

        let warnings = FigStyleWarningScanner.scan(tree: tree)
        XCTAssertEqual(Set(warnings.map(\.code)), Set(["STY001", "STY002", "STY005"]))
        XCTAssertEqual(warnings.filter { $0.code == "STY005" }.count, 1, "STY005 should be deduped per node")
    }

    func testMessageFormatsExpectedWarningText() {
        let warning = FigStyleWarning(code: "STY002", nodeName: "Rect", nodeGUID: [1, 2])
        XCTAssertTrue(FigStyleWarningScanner.message(for: warning).contains("diamond gradient"))
    }
}
