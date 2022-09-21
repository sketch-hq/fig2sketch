import codecs

# Decoder for kiwi files (incomplete, only implemented what's needed for schema decoding)
class KiwiReader:
    def __init__(self, reader):
        self._reader = reader

    def byte(self):
        return self._reader.read(1)[0]

    def uint(self):
        uint = 0
        shift = 0
        for shift in range(0, 36, 7):
            b = self.byte()
            uint |= (b & 127) << shift
            if b < 128:
                break

        return uint

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

# Load a kiwi-schema
TYPES = ['bool', 'byte', 'int', 'uint', 'float', 'string'];
KINDS = ['ENUM', 'STRUCT', 'MESSAGE'];

kw = KiwiReader(open("segment0.data", "rb"))

types = []
for _ in range(kw.uint()):
    name = kw.string()
    kind = kw.byte()

    fields = []
    for _ in range(kw.uint()):
        fname = kw.string()
        ftype = kw.int()
        farray = kw.byte() > 0
        fvalue = kw.uint()

        fields.append({
            "name": fname,
            "type": ftype,
            "array": farray,
            "value": fvalue
        })

    types.append({
        "name": name,
        "kind": kind,
        "fields": fields
    })

# Print the schema in the same format as kiwi-schema to verify quickly with diff
for t in types:
    print(f"{KINDS[t['kind']].lower()} {t['name']} {{")
    for f in t["fields"]:
        typename = types[f["type"]]["name"] if f["type"] >= 0 else TYPES[~f["type"]]

        if t['kind'] == 2:
            print(f"  {typename}{'[]' if f['array'] else ''} {f['name']} = {f['value']};")
        elif t['kind'] == 1:
            print(f"  {typename}{'[]' if f['array'] else ''} {f['name']};")
        else:
            print(f"  {f['name']} = {f['value']};")

    print("}\n")
