import Foundation

public enum KiwiDecoderError: Error, Equatable {
    case unsupportedSchemaKind(UInt8)
    case rootTypeNotFound(String)
    case invalidTypeID(Int32)
    case invalidPrimitiveType(Int)
    case unknownFieldID(UInt32, typeName: String)
    case invalidEnumCase(UInt32, typeName: String)
    case unsupportedZstdSegment
    case invalidCanvasFig
    case unsupportedCanvasFigVersion(Int)
    case malformedRootMessage
    case malformedNodeChange(Int)
    case noRootNode
    case missingParent(UInt32)
}

public struct KiwiDecoder {
    public typealias TypeConverter = @Sendable (KiwiValue) -> KiwiValue

    public var schema: KiwiSchema
    public var typeConverters: [String: TypeConverter]

    public init(schema: KiwiSchema, typeConverters: [String: TypeConverter] = [:]) {
        self.schema = schema
        self.typeConverters = typeConverters
    }

    public func decode(data: Data, rootTypeName: String) throws -> KiwiValue {
        guard let rootType = schema.type(named: rootTypeName) else {
            throw KiwiDecoderError.rootTypeNotFound(rootTypeName)
        }
        var reader = KiwiBinaryReader(data: data)
        return try decodeMessage(reader: &reader, type: rootType)
    }

    private func decodeMessage(reader: inout KiwiBinaryReader, type: KiwiSchema.TypeDef) throws -> KiwiValue {
        var object: [String: KiwiValue] = [:]
        while true {
            let fieldID = try reader.uint()
            if fieldID == 0 { break }
            guard let field = type.fieldsByValueID[fieldID] else {
                throw KiwiDecoderError.unknownFieldID(fieldID, typeName: type.name)
            }
            object[field.name] = try decodeType(reader: &reader, typeID: field.typeID, isArray: field.isArray)
        }
        return .object(object)
    }

    private func decodeStruct(reader: inout KiwiBinaryReader, type: KiwiSchema.TypeDef) throws -> KiwiValue {
        var object: [String: KiwiValue] = [:]
        for field in type.fieldsInSchemaOrder {
            object[field.name] = try decodeType(reader: &reader, typeID: field.typeID, isArray: field.isArray)
        }
        return .object(object)
    }

    private func decodeEnum(reader: inout KiwiBinaryReader, type: KiwiSchema.TypeDef) throws -> KiwiValue {
        let value = try reader.uint()
        guard let field = type.fieldsByValueID[value] else {
            throw KiwiDecoderError.invalidEnumCase(value, typeName: type.name)
        }
        return .string(field.name)
    }

    private func decodeType(reader: inout KiwiBinaryReader, typeID: Int32, isArray: Bool) throws -> KiwiValue {
        let decoded: KiwiValue
        if isArray {
            let count = try Int(reader.uint())
            var values: [KiwiValue] = []
            values.reserveCapacity(count)
            for _ in 0..<count {
                values.append(try decodeType(reader: &reader, typeID: typeID, isArray: false))
            }
            decoded = .array(values)
        } else if typeID < 0 {
            decoded = try decodePrimitive(reader: &reader, typeID: typeID)
        } else {
            let index = Int(typeID)
            guard schema.types.indices.contains(index) else {
                throw KiwiDecoderError.invalidTypeID(typeID)
            }
            let type = schema.types[index]
            switch type.kind {
            case .enumeration:
                decoded = try decodeEnum(reader: &reader, type: type)
            case .struct:
                decoded = try decodeStruct(reader: &reader, type: type)
            case .message:
                decoded = try decodeMessage(reader: &reader, type: type)
            }
        }

        if !isArray, typeID >= 0 {
            let type = schema.types[Int(typeID)]
            if let converter = typeConverters[type.name] {
                return converter(decoded)
            }
        }
        return decoded
    }

    private func decodePrimitive(reader: inout KiwiBinaryReader, typeID: Int32) throws -> KiwiValue {
        let primitiveIndex = Int(~typeID)
        switch primitiveIndex {
        case 0:
            return .bool(try reader.bool())
        case 1:
            return .byte(try reader.byte())
        case 2:
            return .int(try reader.int())
        case 3:
            return .uint(try reader.uint())
        case 4:
            return .float(Double(try reader.float()))
        case 5:
            return .string(try reader.string())
        case 6:
            return .int64(try reader.int64())
        case 7:
            return .uint64(try reader.uint64())
        default:
            throw KiwiDecoderError.invalidPrimitiveType(primitiveIndex)
        }
    }
}
