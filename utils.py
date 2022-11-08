import uuid
import hashlib
import random
import struct
from typing import BinaryIO, List, Dict
import logging

id_salt = random.randbytes(16)

issued_warnings: Dict[tuple[int, int], list[str]] = {}

def gen_object_id(figma_id: List[int], suffix: bytes=b'') -> str:
    # Generate UUIDs by hashing the figma ID with a salt
    salted_id = id_salt + struct.pack('<' + 'I' * len(figma_id), *figma_id) + suffix
    uuid_bytes = bytearray(hashlib.shake_128(salted_id).digest(16))

    # Override bits to match UUIDv4
    uuid_bytes[6] = (uuid_bytes[6] & 0x0f) | 0x40
    uuid_bytes[8] = (uuid_bytes[8] & 0x3f) | 0x80

    return str(uuid.UUID(bytes=bytes(uuid_bytes))).upper()

def generate_file_ref(data):
    return hashlib.sha1(hashlib.sha1(data).digest()).hexdigest()


def get_style_table_override(figma_item):
    override_table = {0: {}}

    if 'styleOverrideTable' in figma_item:
        override_table.update({s['styleID']: s for s in figma_item['styleOverrideTable']})

    return override_table

def log_conversion_warning(warning_code: str, figma_node: dict):
    WARNING_MESSAGES = {
        "TXT001": f"is missing the glyphs property. If the text has unicode characters, it may not convert the format properly",
        "TXT002": f"has multiple text fill colors. Only the first one will be converted",
        "TXT003": f"has a non-solid text color (gradient or image) which is not supported by Sketch",
        "TXT004": f"contains a 'TITLE' transformation. Sketch does not support this text transformation, so no transformation is applied",

        "SHP001": f"contains a line with at least one 'Reversed triangle' end. This type of marker does not exist in Sketch. It has been converted to a 'Line' type marker",

        "STY001": f"contains a layer blur and a background blur. Only one will be converted",

        "SYM001": f"references an invalid symbol. It will be converted to an empty placeholder group",
    }

    if not figma_node['guid'] in issued_warnings:
        issued_warnings[figma_node['guid']] = [warning_code]
    elif not warning_code in issued_warnings[figma_node['guid']]:
        issued_warnings[figma_node['guid']].append(warning_code)
    else: 
        return
    logging.warning(f"[{warning_code}] Figma {figma_node['type']} '{figma_node['name']}' {WARNING_MESSAGES[warning_code]}")
