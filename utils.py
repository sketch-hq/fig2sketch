from genericpath import isdir
import uuid
from fontTools.ttLib import TTFont
import os
import fnmatch
import hashlib
import urllib.request
import urllib.parse
import shutil
from zipfile import ZipFile

figma_fonts = {}

def gen_object_id():
    return str(uuid.uuid4()).upper()


def make_point(x, y):
    return {
        '_class': 'curvePoint',
        'cornerRadius': 0,
        'curveFrom': '{0, 0}',
        'curveMode': 1,
        'curveTo': '{0, 0}',
        'hasCurveFrom': False,
        'hasCurveTo': False,
        'point': f'{{{x}, {y}}}'
    }



def record_figma_font(ffamily, fsfamily):
    if ffamily in figma_fonts:
        # figma_fonts[ffamily][fsfamily] = generate_font_ref(ffamily, fsfamily)
        figma_fonts[ffamily][fsfamily] = ""
    else:
        figma_fonts[ffamily]= {}

    return

def generate_font_ref(font_path):
    return hashlib.sha1(hashlib.sha1(open(font_path, 'rb').read()).digest()).hexdigest()

def global_fonts():
    return figma_fonts

def download_and_unzip_webfont(ffamily):
    WEB_FONT_BASE_URL = "http://fonts.google.com/download?family="
    font_url = "%s%s" % (WEB_FONT_BASE_URL, urllib.parse.quote(ffamily))
    temp_fonts_path = "output/temp-fonts"
    if not os.path.isdir(temp_fonts_path):
        os.mkdir(temp_fonts_path)
    with urllib.request.urlopen(font_url) as response, open(os.path.join(temp_fonts_path, "%s.zip" % ffamily), 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
        with ZipFile(os.path.join(temp_fonts_path, "%s.zip" % ffamily), 'r') as zipObj:
           zipObj.extractall(temp_fonts_path)    

def organize_sketch_fonts():
    temp_fonts_path = "output/temp-fonts"
    sketch_fonts_path = "output/fonts"
    if not figma_fonts:
        return
    if not os.path.isdir(sketch_fonts_path):
        os.mkdir(sketch_fonts_path)
    for root, dirnames, filenames in os.walk(temp_fonts_path):
        for filename in filenames:
            if fnmatch.fnmatch(filename, "*.ttf"):
                ffamily, fsfamily = get_font_family_from_file(os.path.join(root, filename))
                if ffamily in figma_fonts and fsfamily in figma_fonts[ffamily]:
                    figma_fonts[ffamily][fsfamily] = generate_font_ref(os.path.join(root, filename))
                    shutil.move(os.path.join(root, filename), os.path.join(sketch_fonts_path, figma_fonts[ffamily][fsfamily]))
    shutil.rmtree(temp_fonts_path)

def get_font_family_from_file(font_file):
    font = TTFont(font_file)
    return font['name'].getBestFamilyName(), font['name'].getBestSubFamilyName()


def add_points(point1, point2):
    return {'x': point1['x'] + point2['x'], 'y': point1['y'] + point2['y']}


def np_point_to_string(point):
    return f"{{{point[0]}, {point[1]}}}"


def point_to_string(point):
    return f"{{{point['x']}, {point['y']}}}"


# TODO: Call this function from every shape/image/etc
# TODO: Check if image masks work
def masking(figma):
    CLIPPING_MODE = {
        'ALPHA': 1,
        'OUTLINE': 0,  # TODO This works differently in Sketch vs Figma
        # Sketch masks only the fill and draws border normally and fill as background
        # Figma masks including the borders and ignores the stroke/fill properties
        # 'LUMINANCE': UNSUPPORTED
    }
    sketch = {
        'shouldBreakMaskChain': False
    }
    if figma.mask:
        sketch['hasClippingMask'] = True
        sketch['clippingMaskMode'] = CLIPPING_MODE[figma.maskType]
    else:
        sketch['hasClippingMask'] = False

    return sketch


def resizing_constraints(figma_item):
    # TODO: Figma is returning MIN so I assigned it to the defaults (TOP & LEFT respectively)
    v = {
        'MIN': 32,
        'BOTTOM': 8,
        'CENTER': 16,
        'TOP_BOTTOM': 40,
        'SCALE': 0,
    }
    h = {
        'MIN': 4,
        'RIGHT': 1,
        'CENTER': 2,
        'LEFT_RIGHT': 5,
        'SCALE': 0,
    }
    return h[figma_item['horizontalConstraint']] + v[figma_item['verticalConstraint']]


def get_style_table_override(figma_item):
    override_table = {0: {}}

    if 'styleOverrideTable' in figma_item:
        override_table.update({s['styleID']: s for s in figma_item['styleOverrideTable']})

    return override_table
