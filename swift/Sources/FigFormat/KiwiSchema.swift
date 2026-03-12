import Foundation

public struct KiwiSchema: Equatable, Sendable {
    public struct Field: Equatable, Sendable {
        public var name: String
        public var typeID: Int32
        public var isArray: Bool
        public var valueID: UInt32

        public init(name: String, typeID: Int32, isArray: Bool, valueID: UInt32) {
            self.name = name
            self.typeID = typeID
            self.isArray = isArray
            self.valueID = valueID
        }
    }

    public enum Kind: UInt8, Equatable, Sendable {
        case enumeration = 0
        case `struct` = 1
        case message = 2
    }

    public struct TypeDef: Equatable, Sendable {
        public var name: String
        public var kind: Kind
        public var fieldsByValueID: [UInt32: Field]
        public var fieldsInSchemaOrder: [Field]

        public init(name: String, kind: Kind, fieldsByValueID: [UInt32: Field], fieldsInSchemaOrder: [Field]) {
            self.name = name
            self.kind = kind
            self.fieldsByValueID = fieldsByValueID
            self.fieldsInSchemaOrder = fieldsInSchemaOrder
        }
    }

    public var types: [TypeDef]

    public init(types: [TypeDef]) {
        self.types = types
    }

    public func type(named name: String) -> TypeDef? {
        types.first(where: { $0.name == name })
    }
}

public enum KiwiSchemaDecoder {
    public static func decode(data: Data) throws -> KiwiSchema {
        var reader = KiwiBinaryReader(data: data)
        let typeCount = try Int(reader.uint())
        var types: [KiwiSchema.TypeDef] = []
        types.reserveCapacity(typeCount)

        for _ in 0..<typeCount {
            let name = try reader.string()
            let kindRaw = try reader.byte()
            guard let kind = KiwiSchema.Kind(rawValue: kindRaw) else {
                throw KiwiDecoderError.unsupportedSchemaKind(kindRaw)
            }

            let fieldCount = try Int(reader.uint())
            var fieldsByID: [UInt32: KiwiSchema.Field] = [:]
            var ordered: [KiwiSchema.Field] = []
            ordered.reserveCapacity(fieldCount)

            for _ in 0..<fieldCount {
                let field = try decodeField(reader: &reader)
                fieldsByID[field.valueID] = field
                ordered.append(field)
            }

            types.append(.init(name: name, kind: kind, fieldsByValueID: fieldsByID, fieldsInSchemaOrder: ordered))
        }

        return KiwiSchema(types: types)
    }

    private static func decodeField(reader: inout KiwiBinaryReader) throws -> KiwiSchema.Field {
        .init(
            name: try reader.string(),
            typeID: try reader.int(),
            isArray: try reader.bool(),
            valueID: try reader.uint()
        )
    }
}
