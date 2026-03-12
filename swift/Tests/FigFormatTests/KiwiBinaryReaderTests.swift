import Foundation
import XCTest
@testable import FigFormat

final class KiwiBinaryReaderTests: XCTestCase {
    func testPrimitiveDecodersMatchPythonVectors() throws {
        var uintReader = try makeReader(hex: "ac02")
        XCTAssertEqual(try uintReader.uint(), 300)

        var intReader = try makeReader(hex: "09")
        XCTAssertEqual(try intReader.int(), -5)

        var uint64Reader = try makeReader(hex: "fb8080808020")
        XCTAssertEqual(try uint64Reader.uint64(), (1 << 40) + 123)

        var int64Reader = try makeReader(hex: "a9b4de75")
        XCTAssertEqual(try int64Reader.int64(), -123_456_789)

        var floatReader1 = try makeReader(hex: "7f000080")
        XCTAssertEqual(try floatReader1.float(), 1.5)

        var floatReader2 = try makeReader(hex: "80010020")
        XCTAssertEqual(try floatReader2.float(), -2.25)

        var stringReader1 = try makeReader(hex: "686900")
        XCTAssertEqual(try stringReader1.string(), "hi")

        var stringReader2 = try makeReader(hex: "41f09f988000")
        XCTAssertEqual(try stringReader2.string(), "A😀")
    }

    func testBoolAndZeroFloat() throws {
        var boolReader = KiwiBinaryReader(data: Data([0x00, 0x01]))
        XCTAssertFalse(try boolReader.bool())
        XCTAssertTrue(try boolReader.bool())

        var floatReader = KiwiBinaryReader(data: Data([0x00]))
        XCTAssertEqual(try floatReader.float(), 0)
    }

    func testUnexpectedEOF() throws {
        var reader = KiwiBinaryReader(data: Data())
        XCTAssertThrowsError(try reader.byte()) { error in
            XCTAssertEqual(error as? KiwiBinaryReader.Error, .unexpectedEOF)
        }
    }

    private func makeReader(hex: String) throws -> KiwiBinaryReader {
        guard let data = Data(hex: hex) else {
            throw XCTSkip("invalid hex in test")
        }
        return KiwiBinaryReader(data: data)
    }
}
