import codecs
from collections import OrderedDict
import ctypes


class KiwiReader:
    def __init__(self, reader):
        self._reader = reader

    def byte(self):
        return self._reader.read(1)[0]

    def bool(self):
        return self.byte() > 0

    def uint(self):
        uint = 0
        shift = 0
        for shift in range(0, 36, 7):
            b = self.byte()
            uint |= (b & 127) << shift
            if b < 128:
                break

        return uint

    def float(self):
        b = self.byte()
        if b == 0:
            return 0.0

        bits = b | self.byte() << 8 | self.byte() << 16 | self.byte() << 24
        bits = (bits << 23) | (bits >> 9)

        return ctypes.c_float.from_buffer(ctypes.c_uint32(bits)).value

    def int(self):
        v = self.uint()
        return ~(v >> 1) if v & 1 else v >> 1

    def string(self):
        string = ''
        decoder = codecs.lookup('utf8').incrementaldecoder()
        while not (string and string[-1] == '\x00'):
            ch = ''
            while not ch:
                ch = decoder.decode(self._reader.read(1))
            string += ch

        return string[:-1]


class KiwiSchema:
    def __init__(self, reader):
        kw = KiwiReader(reader)

        self.types = []
        for _ in range(kw.uint()):
            name = kw.string()
            kind = kw.byte()

            fields = OrderedDict()
            for _ in range(kw.uint()):
                field = KiwiSchema._decode_field(kw)

                fields[field["value"]] = field

            self.types.append({
                "name": name,
                "kind": kind,
                "fields": fields
            })

    def _decode_field(kw):
        return {
            "name": kw.string(),
            "type": kw.int(),
            "array": kw.bool(),
            "value": kw.uint()
        }


class KiwiDecoder:
    TYPES = ['bool', 'byte', 'int', 'uint', 'float', 'string'];
    KINDS = ['ENUM', 'STRUCT', 'MESSAGE'];

    def __init__(self, schema):
        self.schema = schema

    def decode(self, reader, root):
        kw = KiwiReader(reader)
        root_type = [t for t in self.schema.types if t["name"] == root][0]
        return self._decodeMessage(kw, root_type)

    def _decodeMessage(self, kw, type):
        obj = {}
        while (fid := kw.uint()) != 0:
            field = type["fields"][fid]
            ftype = field["type"]

            obj[field["name"]] = self._decodeType(kw, ftype, field["array"])

        return obj

    def _decodeStruct(self, kw, type):
        return {f["name"]: self._decodeType(kw, f["type"], f["array"]) for f in
                type["fields"].values()}

    def _decodeEnum(self, kw, type):
        value = kw.uint()
        return type["fields"][value]["name"]

    def _decodeType(self, kw, type_id, array):
        if array:
            return [self._decodeType(kw, type_id, False) for i in range(kw.uint())]

        if type_id < 0:
            primitive = self.TYPES[~type_id]
            return kw.__getattribute__(primitive)()
        else:
            type = self.schema.types[type_id]
            match type["kind"]:
                case 0:
                    return self._decodeEnum(kw, type)
                case 1:
                    return self._decodeStruct(kw, type)
                case 2:
                    return self._decodeMessage(kw, type)
                case other:
                    raise "Unknown"
