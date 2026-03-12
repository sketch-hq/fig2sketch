import Foundation
import zlib

public struct DecodedCanvasFig: Equatable, Sendable {
    public var version: Int
    public var schema: KiwiSchema
    public var rootMessage: KiwiValue
    public var isSchemaZstd: Bool
    public var isDataZstd: Bool

    public init(version: Int, schema: KiwiSchema, rootMessage: KiwiValue, isSchemaZstd: Bool, isDataZstd: Bool) {
        self.version = version
        self.schema = schema
        self.rootMessage = rootMessage
        self.isSchemaZstd = isSchemaZstd
        self.isDataZstd = isDataZstd
    }
}

public enum KiwiCanvasDecoder {
    private static let zstdMagic = Data([0x28, 0xB5, 0x2F, 0xFD])
    public static let minimumSupportedVersion = 15
    public static let maximumSupportedVersion = 70

    public static func decodeCanvasFig(data: Data) throws -> DecodedCanvasFig {
        guard data.count >= 20 else { throw KiwiDecoderError.invalidCanvasFig }

        let version = Int(UInt32(littleEndianBytes: data[8..<12]))
        guard version >= minimumSupportedVersion else {
            throw KiwiDecoderError.unsupportedCanvasFigVersion(version)
        }

        var cursor = 12
        let schemaCompressed = try readSegment(data: data, cursor: &cursor)
        let dataCompressed = try readSegment(data: data, cursor: &cursor)

        let schemaIsZstd = schemaCompressed.starts(with: zstdMagic)
        let dataIsZstd = dataCompressed.starts(with: zstdMagic)
        let schemaData = try decompressSegment(schemaCompressed, isZstd: schemaIsZstd)
        let payloadData = try decompressSegment(dataCompressed, isZstd: dataIsZstd)

        let schema = try KiwiSchemaDecoder.decode(data: schemaData)
        let decoder = KiwiDecoder(schema: schema)
        let root = try decoder.decode(data: payloadData, rootTypeName: "Message")

        return DecodedCanvasFig(
            version: version,
            schema: schema,
            rootMessage: root,
            isSchemaZstd: schemaIsZstd,
            isDataZstd: dataIsZstd
        )
    }

    private static func readSegment(data: Data, cursor: inout Int) throws -> Data {
        guard cursor + 4 <= data.count else { throw KiwiDecoderError.invalidCanvasFig }
        let size = Int(UInt32(littleEndianBytes: data[cursor..<(cursor + 4)]))
        cursor += 4
        guard cursor + size <= data.count else { throw KiwiDecoderError.invalidCanvasFig }
        let segment = data[cursor..<(cursor + size)]
        cursor += size
        return Data(segment)
    }

    private static func decompressSegment(_ segment: Data, isZstd: Bool) throws -> Data {
        if isZstd {
            return try FramedZstd.decompress(data: segment)
        }
        return try RawDeflate.decompress(data: segment)
    }

    public static func warningMessage(forVersion version: Int) -> String? {
        guard version > maximumSupportedVersion else { return nil }
        return "[FIG001] The .fig file has version \(version) which is newer than the maximum supported (\(maximumSupportedVersion)). Some new properties may not be correctly converted"
    }

    public static func errorMessageForUnsupportedOldVersion(_ version: Int) -> String {
        "[FIG002] The .fig file has version \(version) which is older than the minimum supported (\(minimumSupportedVersion)). Cannot convert"
    }
}

private extension UInt32 {
    init(littleEndianBytes bytes: Data.SubSequence) {
        let array = Array(bytes)
        precondition(array.count == 4)
        self = UInt32(array[0])
            | (UInt32(array[1]) << 8)
            | (UInt32(array[2]) << 16)
            | (UInt32(array[3]) << 24)
    }
}
