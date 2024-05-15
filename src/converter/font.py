import appdirs
import os
import urllib.request
import urllib.parse
import json
import logging
from converter import utils
from fontTools.ttLib import TTFont
from sketchformat.document import FontReference, JsonFileReference
from typing import IO, Tuple
from zipfile import ZipFile

fonts_cache_dir = appdirs.user_cache_dir("Fig2Sketch", "Sketch") + "/fonts"
os.makedirs(fonts_cache_dir, exist_ok=True)


class FontNotFoundError(Exception):
    pass


def retrieve_webfont_family(family):
    WEB_FONT_LIST_URL = "https://fonts.google.com/download/list?family="
    list_url = WEB_FONT_LIST_URL + urllib.parse.quote(family)
    list_response = urllib.request.urlopen(list_url)
    return json.loads(bytearray(list_response.read())[5:])


def get_webfont(family, subfamily):
    family_list = retrieve_webfont_family(family)

    for fi in family_list["manifest"]["fileRefs"]:
        filename = fi["filename"].replace("static/", "")
        if not filename.endswith((".ttf", ".otf")):
            continue
        if family.lower() in filename.lower() and subfamily.lower() in filename.lower():
            font_file_path = f"{fonts_cache_dir}/{filename}"
            if not os.path.exists(font_file_path):
                urllib.request.urlretrieve(fi["url"], font_file_path)

            font_file = open(font_file_path, "rb")
            font_names = extract_names(font_file)

            return font_file, font_names["postscript"]

    raise FontNotFoundError(f"Could not find font {family} {subfamily}")


def convert(
    name: Tuple[str, str], font_file: IO[bytes], postscript: str, output_zip: ZipFile
) -> FontReference:
    family, subfamily = name
    data = font_file.read()
    sha = utils.generate_file_ref(data)
    path = f"fonts/{sha}"
    output_zip.open(path, "w").write(data)

    return FontReference(
        do_objectID=utils.gen_object_id((0, 0), bytes.fromhex(sha)),
        fontData=JsonFileReference(_ref_class="MSFontData", _ref=path),
        fontFamilyName=family,
        fontFileName=f"{family}-{subfamily}.ttf",
        postscriptNames=[postscript],
    )


def extract_names(font_file):
    font = TTFont(font_file)
    return {
        "family": font["name"].getBestFamilyName(),
        "subfamily": font["name"].getBestSubFamilyName(),
        "postscript": font["name"].getFirstDebugName((6,)),
    }


def font_matches(fig, font_names):
    return fig["postscript"] == font_names["postscript"] or (
        fig["family"] == font_names["family"] and fig["style"] == font_names["subfamily"]
    )
