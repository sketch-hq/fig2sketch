import Foundation

public enum KiwiValue: Equatable, Sendable {
    case bool(Bool)
    case byte(UInt8)
    case int(Int32)
    case uint(UInt32)
    case float(Double)
    case string(String)
    case int64(Int64)
    case uint64(UInt64)
    case array([KiwiValue])
    case object([String: KiwiValue])
}

public extension KiwiValue {
    var objectValue: [String: KiwiValue]? {
        if case .object(let value) = self { return value }
        return nil
    }

    var arrayValue: [KiwiValue]? {
        if case .array(let value) = self { return value }
        return nil
    }

    var uintValue: UInt32? {
        if case .uint(let value) = self { return value }
        return nil
    }

    var floatValue: Double? {
        if case .float(let value) = self { return value }
        return nil
    }

    var stringValue: String? {
        if case .string(let value) = self { return value }
        return nil
    }
}
