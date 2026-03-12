import FigFormat
import Foundation

enum FigDumpJSONWriter {
    static func write(decoded: DecodedCanvasFig, to url: URL) throws {
        let object: [String: Any] = [
            "version": decoded.version,
            "isSchemaZstd": decoded.isSchemaZstd,
            "isDataZstd": decoded.isDataZstd,
            "root": makeJSONObject(from: decoded.rootMessage),
        ]
        let data = try JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
        try data.write(to: url)
    }

    private static func makeJSONObject(from value: KiwiValue) -> Any {
        switch value {
        case .bool(let v):
            return v
        case .byte(let v):
            return Int(v)
        case .int(let v):
            return Int(v)
        case .uint(let v):
            return Int(v)
        case .float(let v):
            return v
        case .string(let v):
            return v
        case .int64(let v):
            return v >= Int64(Int.min) && v <= Int64(Int.max) ? Int(v) : String(v)
        case .uint64(let v):
            return v <= UInt64(Int.max) ? Int(v) : String(v)
        case .array(let values):
            return values.map(makeJSONObject)
        case .object(let object):
            var out: [String: Any] = [:]
            out.reserveCapacity(object.count)
            for (key, value) in object {
                out[key] = makeJSONObject(from: value)
            }
            return out
        }
    }
}
