import appdirs
import os
import utils
import urllib.request
import urllib.parse
from fontTools.ttLib import TTFont
from sketchformat.document import FontReference, JsonFileReference
from zipfile import ZipFile

fonts_cache_dir = appdirs.user_cache_dir('Figma2Sketch', 'Sketch') + '/fonts'
os.makedirs(fonts_cache_dir, exist_ok=True)


def retrieve_webfont(family):
    WEB_FONT_BASE_URL = 'http://fonts.google.com/download?family='
    font_url = WEB_FONT_BASE_URL + urllib.parse.quote(family)
    font_file = f"{fonts_cache_dir}/{family}.zip"

    if not os.path.exists(font_file):
        urllib.request.urlretrieve(font_url, font_file)

    return ZipFile(font_file)


def get_webfont(family, subfamily):
    font_zip = retrieve_webfont(family)
    for fi in font_zip.infolist():
        if not fi.filename.endswith(('.ttf', '.otf')):
            continue

        font_file = font_zip.open(fi.filename, 'r')
        font_names = extract_names(font_file)
        if font_names['subfamily'] == subfamily:
            font_file.seek(0)
            return font_file, font_names['postscript']

    raise Exception(f'Could not find font {figma_font_name["postscript"]}')


def convert(name, output_zip):
    family, subfamily = name
    font_file, postscript = get_webfont(family, subfamily)
    data = font_file.read()
    sha = utils.generate_file_ref(data)
    path = f'fonts/{sha}'
    output_zip.open(path, 'w').write(data)

    return FontReference(
        do_objectID=utils.gen_object_id((0, 0), bytes.fromhex(sha)),
        fontData=JsonFileReference(
            _ref_class='MSFontData',
            _ref=path
        ),
        fontFamilyName=family,
        fontFileName=f'{family}-{subfamily}.ttf',
        postscriptNames=[postscript]
    )


def extract_names(font_file):
    font = TTFont(font_file)
    return {
        'family': font['name'].getBestFamilyName(),
        'subfamily': font['name'].getBestSubFamilyName(),
        'postscript': font['name'].getFirstDebugName((6,))
    }


def font_matches(figma, font_names):
    return figma['postscript'] == font_names['postscript'] or (
            figma['family'] == font_names['family'] and
            figma['style'] == font_names['subfamily'])
