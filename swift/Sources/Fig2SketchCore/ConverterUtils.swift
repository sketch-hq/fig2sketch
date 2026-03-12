import CryptoKit
import Foundation

public enum ConverterUtils {
    public static let uintMax: UInt32 = .max

    public static func safeDiv(_ x: Double, _ y: Double) -> Double {
        guard y != 0 else { return 0 }
        return x / y
    }

    public static func generateFileRef(_ data: Data) -> String {
        let first = Insecure.SHA1.hash(data: data)
        let second = Insecure.SHA1.hash(data: Data(first))
        return second.map { String(format: "%02x", $0) }.joined()
    }

    public static func genObjectID(
        figID: [UInt32],
        salt: Data,
        suffix: Data = Data()
    ) -> String {
        var saltedID = Data()
        saltedID.append(salt)
        for value in figID {
            var littleEndian = value.littleEndian
            withUnsafeBytes(of: &littleEndian) { bytes in
                saltedID.append(contentsOf: bytes)
            }
        }
        saltedID.append(suffix)

        var digest = [UInt8](SHAKE128.digest(data: saltedID, outputByteCount: 16))
        digest[6] = (digest[6] & 0x0F) | 0x40
        digest[8] = (digest[8] & 0x3F) | 0x80

        let uuid = UUID(uuid: (
            digest[0], digest[1], digest[2], digest[3],
            digest[4], digest[5], digest[6], digest[7],
            digest[8], digest[9], digest[10], digest[11],
            digest[12], digest[13], digest[14], digest[15]
        ))
        return uuid.uuidString.uppercased()
    }
}

public struct WarningRecorder: Sendable {
    private var issuedWarningsByNodeID: [String: Set<String>] = [:]

    public init() {}

    @discardableResult
    public mutating func shouldEmit(warningCode: String, nodeID: String) -> Bool {
        if issuedWarningsByNodeID[nodeID] == nil {
            issuedWarningsByNodeID[nodeID] = [warningCode]
            return true
        }

        if issuedWarningsByNodeID[nodeID]!.contains(warningCode) {
            return false
        }

        issuedWarningsByNodeID[nodeID]!.insert(warningCode)
        return true
    }
}
