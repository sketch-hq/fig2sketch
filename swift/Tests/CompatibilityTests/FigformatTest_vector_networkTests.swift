import FigFormat
import Foundation
import XCTest

final class FigformatTest_vector_networkTests: XCTestCase {
    func test__figformat__test_vector_network__test_missing_style_id() throws {
        // Port of tests/figformat/test_vector_network.py::test_missing_style_id
        let network = try XCTUnwrap(Data(hex: """
        0a0000000a0000000100000001000000a9989f3e28ae044001000000bc4fa03f0000000001000000
        55c75041000000000100000086d45f412cae0440010000001e7b074102240641010000005cacba40
        022406410100000001d5e63f0000c03f0100000006ccde404facec400100000093d6ea4051acec40
        01000000acf647410000c03f00000000000000003e0b35bf47e84ebf01000000027789bf00000000
        0000000001000000000000000000000002000000000000000000000000000000020000003877893f
        0000000003000000000b353ffce74ebf000000000300000000000000000000000400000000000000
        000000000000000004000000107d32bf98fc4b3f05000000f87c323f80fc4b3f0000000005000000
        00000000000000000000000000000000000000000000000006000000000000000000000007000000
        0000000000000000000000000700000000fdcb3d0021e93d0800000040fccbbd4020e93d00000000
        08000000000000000000000009000000000000000000000000000000090000000000000000000000
        06000000000000000000000001000000020000000600000000000000010000000200000003000000
        04000000050000000400000006000000070000000800000009000000
        """))

        let result = try VectorNetworkDecoder.decode(
            networkData: network,
            scale: VectorScale(x: 1, y: 1),
            styleOverrideTable: [0: [String: Int]()]
        )

        XCTAssertEqual(result.vertices.first?.style, .styleID(1))
        XCTAssertEqual(result.regions.first?.windingRule, .nonzero)
    }
}

private extension Data {
    init?(hex: String) {
        let filtered = hex.filter { !$0.isWhitespace }
        guard filtered.count.isMultiple(of: 2) else { return nil }

        var bytes: [UInt8] = []
        bytes.reserveCapacity(filtered.count / 2)
        var index = filtered.startIndex
        while index < filtered.endIndex {
            let nextIndex = filtered.index(index, offsetBy: 2)
            guard let byte = UInt8(filtered[index..<nextIndex], radix: 16) else { return nil }
            bytes.append(byte)
            index = nextIndex
        }

        self.init(bytes)
    }
}
