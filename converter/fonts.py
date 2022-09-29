from genericpath import isdir
from fontTools.ttLib import TTFont
import os
import fnmatch
import urllib.request
import urllib.parse
import shutil
from zipfile import ZipFile
import appdirs
import utils

figma_fonts = {}
fonts_cache_dir = appdirs.user_cache_dir("Figma2Sketch", "Sketch") + "/fonts"
os.makedirs(fonts_cache_dir, exist_ok=True)


def record_figma_font(ffamily, fsfamily):
    if ffamily in figma_fonts:
        # figma_fonts[ffamily][fsfamily] = generate_font_ref(ffamily, fsfamily)
        figma_fonts[ffamily][fsfamily] = ""
    else:
        figma_fonts[ffamily] = {}

    return


def global_fonts():
    return figma_fonts


def download_and_unzip_webfont(ffamily):
    WEB_FONT_BASE_URL = "http://fonts.google.com/download?family="
    font_url = WEB_FONT_BASE_URL + urllib.parse.quote(ffamily)
    font_file = f"{fonts_cache_dir}/{ffamily}.zip"

    if not os.path.exists(font_file):
        urllib.request.urlretrieve(font_url, font_file)
        ZipFile(font_file).extractall(os.path.join(fonts_cache_dir, ffamily))


def organize_sketch_fonts():
    sketch_fonts_path = "output/fonts"

    if not figma_fonts:
        return

    os.makedirs(sketch_fonts_path, exist_ok=True)

    for root, dirnames, filenames in os.walk(fonts_cache_dir):
        for filename in filenames:
            if fnmatch.fnmatch(filename, "*.ttf"):
                ffamily, fsfamily = get_font_family_from_file(os.path.join(root, filename))

                if ffamily in figma_fonts and fsfamily in figma_fonts[ffamily]:
                    file = open(os.path.join(root, filename), 'rb').read()
                    figma_fonts[ffamily][fsfamily] = utils.generate_file_ref(file)
                    fonts_path = os.path.join(sketch_fonts_path, figma_fonts[ffamily][fsfamily])
                    shutil.copyfile(os.path.join(root, filename), fonts_path)


def get_font_family_from_file(font_file):
    font = TTFont(font_file)
    return font['name'].getBestFamilyName(), font['name'].getBestSubFamilyName()
