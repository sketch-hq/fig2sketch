import utils
from . import fonts

def convert(pages):
    for ffamily in fonts.figma_fonts.keys():
        fonts.download_and_unzip_webfont(ffamily)
    fonts.organize_sketch_fonts()

    font_references = []
    for ffamily, ffamily_dict in fonts.figma_fonts.items():
        for fsfamily, font_hash in ffamily_dict.items():
            font_references.append(
                {
                    '_class': 'fontReference',
                    'do_objectID': utils.gen_object_id(),
                    'fontData': {
                        "_class": 'MSJSONFileReference',
                        '_ref_class': 'MSFontData',
                        '_ref': 'fonts/%s' % font_hash
                    },
                    'fontFamilyName': ffamily,
                    'fontFileName': '%s-%s.ttf' % (ffamily, fsfamily),
                    'options': 1,
                    'postscriptNames': [
                        '%s-%s' % (ffamily, fsfamily)
                    ]
                })

    print(fonts.figma_fonts)
    return {
        '_class': 'document',
        'do_objectID': utils.gen_object_id(),
        'assets': {
            '_class': 'assetCollection',
            'do_objectID': utils.gen_object_id(),
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
        'colorSpace': 0,
        'currentPageIndex': 0,
        'foreignLayerStyles': [],
        'foreignSymbols': [],
        'foreignTextStyles': [],
        'foreignSwatches': [],
        'layerStyles': {
            '_class': 'sharedStyleContainer',
            'do_objectID': utils.gen_object_id(),
            'objects': []
        },
        'layerSymbols': {
            '_class': 'symbolContainer',
            'do_objectID': utils.gen_object_id(),
            'objects': []
        },
        'layerTextStyles': {
            '_class': 'sharedTextStyleContainer',
            'do_objectID': utils.gen_object_id(),
            'objects': []
        },
        'sharedSwatches': {
            '_class': 'swatchContainer',
            'do_objectID': utils.gen_object_id(),
            'objects': []
        },
        'fontReferences': font_references,
        'documentState': {
            '_class': 'documentState'
        },
        'pages': [
            {
                '_class': 'MSJSONFileReference',
                '_ref_class': 'MSImmutablePage',
                '_ref': f"pages/{page['do_objectID']}"
            } for page in pages
        ]
    }
