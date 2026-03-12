import Foundation

public enum SketchJSONValue: Equatable, Sendable {
    case null
    case bool(Bool)
    case int(Int)
    case double(Double)
    case string(String)
    case array([SketchJSONValue])
    case object(SketchJSONObject)
}

public struct SketchJSONObject: Equatable, Sendable {
    public struct Field: Equatable, Sendable {
        public var key: String
        public var value: SketchJSONValue

        public init(key: String, value: SketchJSONValue) {
            self.key = key
            self.value = value
        }
    }

    public var fields: [Field]

    public init(fields: [Field]) {
        self.fields = fields
    }

    public init(_ pairs: [(String, SketchJSONValue?)]) {
        self.fields = pairs.compactMap { key, value in
            guard let value else { return nil }
            let outputKey = key.hasSuffix("_") ? String(key.dropLast()) : key
            return Field(key: outputKey, value: value)
        }
    }
}

public enum SketchJSONWriter {
    public static func serialize(_ value: SketchJSONValue) -> Data {
        var writer = _JSONUTF8Writer()
        writer.write(value)
        return Data(writer.bytes)
    }

    public static func serializeString(_ value: SketchJSONValue) -> String {
        String(decoding: serialize(value), as: UTF8.self)
    }
}

private struct _JSONUTF8Writer {
    var bytes: [UInt8] = []

    mutating func write(_ value: SketchJSONValue) {
        switch value {
        case .null:
            appendASCII("null")
        case .bool(let bool):
            appendASCII(bool ? "true" : "false")
        case .int(let int):
            appendASCII(String(int))
        case .double(let double):
            if double.isFinite {
                appendASCII(String(double))
            } else {
                appendASCII("null")
            }
        case .string(let string):
            writeJSONString(string)
        case .array(let array):
            bytes.append(UInt8(ascii: "["))
            for index in array.indices {
                if index > 0 { bytes.append(UInt8(ascii: ",")) }
                write(array[index])
            }
            bytes.append(UInt8(ascii: "]"))
        case .object(let object):
            bytes.append(UInt8(ascii: "{"))
            for index in object.fields.indices {
                if index > 0 { bytes.append(UInt8(ascii: ",")) }
                writeJSONString(object.fields[index].key)
                bytes.append(UInt8(ascii: ":"))
                write(object.fields[index].value)
            }
            bytes.append(UInt8(ascii: "}"))
        }
    }

    private mutating func appendASCII(_ string: String) {
        bytes.append(contentsOf: string.utf8)
    }

    private mutating func writeJSONString(_ string: String) {
        bytes.append(UInt8(ascii: "\""))
        for scalar in string.unicodeScalars {
            switch scalar.value {
            case 0x22: // "
                appendASCII("\\\"")
            case 0x5C: // \
                appendASCII("\\\\")
            case 0x08:
                appendASCII("\\b")
            case 0x0C:
                appendASCII("\\f")
            case 0x0A:
                appendASCII("\\n")
            case 0x0D:
                appendASCII("\\r")
            case 0x09:
                appendASCII("\\t")
            case 0x00...0x1F:
                appendASCII(String(format: "\\u%04X", scalar.value))
            default:
                bytes.append(contentsOf: String(scalar).utf8)
            }
        }
        bytes.append(UInt8(ascii: "\""))
    }
}
