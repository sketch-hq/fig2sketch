import Foundation
@testable import FigFormat

enum SyntheticKiwiFixture {
    static let canvasHex = """
    00000000000000000f00000063000000258db10e833010439d008588cf62e844d55f889453720317d45c55f8fb1e62b1fd3cd8fe5513c187fce584116e8f1f127ddee46f7ad7c6ca55ace9f4dc09337a89dbe5c38180c76932fe3869b13015e25cd45258a9b5986dde89bd2c254aa60638f7074100000063646264647176f40b730c66600d484c4f55306460606462626466600972750e71f473f77165600d4a4d2e61606b626070606f06121cad0c0c13385b8004030300
    """

    static var canvasData: Data {
        Data(hex: canvasHex)!
    }

    static var expectedRootMessage: KiwiValue {
        .object([
            "nodeChanges": .array([
                .object([
                    "guid": .uint(1),
                    "type": .string("CANVAS"),
                    "name": .string("Page 1"),
                ]),
                .object([
                    "guid": .uint(2),
                    "parentGuid": .uint(1),
                    "parentPosition": .uint(0),
                    "type": .string("RECTANGLE"),
                    "name": .string("Rect"),
                    "x": .float(10.0),
                    "y": .float(20.0),
                    "width": .float(100.0),
                    "height": .float(50.0),
                ]),
            ]),
        ])
    }
}

extension Data {
    init?(hex: String) {
        let filtered = hex.filter { !$0.isWhitespace }
        guard filtered.count.isMultiple(of: 2) else { return nil }
        var bytes: [UInt8] = []
        bytes.reserveCapacity(filtered.count / 2)
        var index = filtered.startIndex
        while index < filtered.endIndex {
            let next = filtered.index(index, offsetBy: 2)
            guard let byte = UInt8(filtered[index..<next], radix: 16) else { return nil }
            bytes.append(byte)
            index = next
        }
        self.init(bytes)
    }
}
