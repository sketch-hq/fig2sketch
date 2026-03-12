import XCTest
@testable import FigFormat

final class KiwiDecoderTests: XCTestCase {
    func testDecodesSyntheticCanvasFigSchemaAndRootMessage() throws {
        let decoded = try KiwiCanvasDecoder.decodeCanvasFig(data: SyntheticKiwiFixture.canvasData)

        XCTAssertEqual(decoded.version, 15)
        XCTAssertFalse(decoded.isSchemaZstd)
        XCTAssertFalse(decoded.isDataZstd)
        XCTAssertEqual(decoded.rootMessage, SyntheticKiwiFixture.expectedRootMessage)

        XCTAssertEqual(decoded.schema.types.count, 2)
        XCTAssertEqual(decoded.schema.types[0].name, "Node")
        XCTAssertEqual(decoded.schema.types[1].name, "Message")
    }
}
