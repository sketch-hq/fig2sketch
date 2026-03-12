import Foundation
import XCTest
@testable import Fig2SketchCore

final class ConverterUtilsTests: XCTestCase {
    func testSHAKE128VectorsMatchPythonHashlib() {
        XCTAssertEqual(
            SHAKE128.digest(data: Data(), outputByteCount: 32).hexString,
            "7f9c2ba4e88f827d616045507605853ed73b8093f6efbc88eb1a6eacfa66ef26"
        )
        XCTAssertEqual(
            SHAKE128.digest(data: Data("hello".utf8), outputByteCount: 32).hexString,
            "8eb4b6a932f280335ee1a279f8c208a349e7bc65daf831d3021c213825292463"
        )
        XCTAssertEqual(
            SHAKE128.digest(data: Data("fig2sketch".utf8), outputByteCount: 32).hexString,
            "89b549666243fd139f900c66b6f56743b275b6dbf71b8e589dd95cc0bc508d36"
        )
        XCTAssertEqual(
            SHAKE128.digest(data: Data((0..<32).map(UInt8.init)), outputByteCount: 32).hexString,
            "066a361dc675f856cecdc02b25218a10cec0cecf79859ec0fec3d409e5847a92"
        )
    }

    func testGenerateFileRefMatchesPythonForKnownInputs() {
        XCTAssertEqual(
            ConverterUtils.generateFileRef(Data()),
            "be1bdec0aa74b4dcb079943e70528096cca985f8"
        )
        XCTAssertEqual(
            ConverterUtils.generateFileRef(Data("hello".utf8)),
            "6b4f89a54e2d27ecd7e8da05b4ab8fd9d1d8b119"
        )
        XCTAssertEqual(
            ConverterUtils.generateFileRef(Data("fig2sketch".utf8)),
            "f1652631950be8c4dc9b8869a01515a176901a9d"
        )
    }

    func testSafeDivReturnsZeroOnDivisionByZero() {
        XCTAssertEqual(ConverterUtils.safeDiv(123, 0), 0)
        XCTAssertEqual(ConverterUtils.safeDiv(0, 0), 0)
    }

    func testSafeDivReturnsQuotientOtherwise() {
        XCTAssertEqual(ConverterUtils.safeDiv(6, 2), 3)
        XCTAssertEqual(ConverterUtils.safeDiv(1, 4), 0.25)
    }

    func testWarningRecorderDeduplicatesPerNodeAndCode() {
        var recorder = WarningRecorder()

        XCTAssertTrue(recorder.shouldEmit(warningCode: "IMG001", nodeID: "node-a"))
        XCTAssertFalse(recorder.shouldEmit(warningCode: "IMG001", nodeID: "node-a"))
        XCTAssertTrue(recorder.shouldEmit(warningCode: "IMG002", nodeID: "node-a"))
        XCTAssertTrue(recorder.shouldEmit(warningCode: "IMG001", nodeID: "node-b"))
    }

    func testGenObjectIDMatchesPythonForKnownVectors() {
        XCTAssertEqual(
            ConverterUtils.genObjectID(figID: [123, 456], salt: Data()),
            "AC96097E-A510-450D-BC2B-29B7C632F860"
        )
        XCTAssertEqual(
            ConverterUtils.genObjectID(figID: [0, 0], salt: Data(repeating: 0, count: 16)),
            "A2BD3F00-7CF6-453A-ACCA-65907C30ADA0"
        )
        XCTAssertEqual(
            ConverterUtils.genObjectID(figID: [1, 2], salt: Data("1234".utf8)),
            "60CDCBD8-345A-4796-804B-C6A97C9C0587"
        )
        XCTAssertEqual(
            ConverterUtils.genObjectID(figID: [789, 112], salt: Data("abcdefghijklmnop".utf8)),
            "9329D576-213F-4377-BEDD-D491BF67592A"
        )
        XCTAssertEqual(
            ConverterUtils.genObjectID(
                figID: [1, 2, 3],
                salt: Data("pepper".utf8),
                suffix: Data([0xDE, 0xAD, 0xBE, 0xEF])
            ),
            "0D27A764-9C11-4350-A793-5BBBF7B57397"
        )
    }
}

private extension Data {
    var hexString: String {
        map { String(format: "%02x", $0) }.joined()
    }
}
