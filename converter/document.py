import utils
from . import font
from .context import context


def convert(pages, output_zip):
    return {
        '_class': 'document',
        'do_objectID': utils.gen_object_id((0, 0), b'document'),
        'assets': {
            '_class': 'assetCollection',
            'do_objectID': utils.gen_object_id((0, 0), b'assetCollection'),
            'imageCollection': {
                '_class': 'imageCollection',
                'images': {}
            },
            'colorAssets': [],
            'gradientAssets': [],
            'images': [],
            'colors': [],
            'gradients': [],
            'exportPresets': []
        },
        'colorSpace': 1,
        'currentPageIndex': 0,
        'foreignLayerStyles': [],
        'foreignSymbols': [],
        'foreignTextStyles': [],
        'foreignSwatches': [],
        'layerStyles': {
            '_class': 'sharedStyleContainer',
            'do_objectID': utils.gen_object_id((0, 0), b'sharedStyleContainer'),
            'objects': []
        },
        'layerSymbols': {
            '_class': 'symbolContainer',
            'do_objectID': utils.gen_object_id((0, 0), b'symbolContainer'),
            'objects': []
        },
        'layerTextStyles': {
            '_class': 'sharedTextStyleContainer',
            'do_objectID': utils.gen_object_id((0, 0), b'sharedTextStyleContainer'),
            'objects': []
        },
        'perDocumentLibraries': [],
        'sharedSwatches': {
            '_class': 'swatchContainer',
            'do_objectID': utils.gen_object_id((0, 0), b'swatchContainer'),
            'objects': [component for component in context.sketch_components() if
                        component['_class'] == 'swatch']
        },
        'fontReferences': sorted(
            [font.convert(name, font_file, postscript, output_zip) for name, (font_file, postscript) in context.used_fonts().items() if font_file],
            key=lambda x: x.do_objectID
        ),
        'documentState': {
            '_class': 'documentState'
        },
        'pages': [
            {
                '_class': 'MSJSONFileReference',
                '_ref_class': 'MSImmutablePage',
                '_ref': f"pages/{page.do_objectID}"
            } for page in pages
        ]
    }
