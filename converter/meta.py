def convert(pages):
    return {
        'commit': '1899e24f63af087a9dd3c66f73b492b72c27c2c8',
        'pagesAndArtboards': {
            page['do_objectID']: {
                'name': page['name'],
                'artboards': {
                    artboard['do_objectID']: {'name': artboard['name']}
                    for artboard in page['layers']
                    if artboard['_class'] in ['artboard', 'symbolMaster']
                }
            }
            for page in pages
        },
        'version': 144,
        'compatibilityVersion': 99,
        'coeditCompatibilityVersion': 143,
        'app': 'com.bohemiancoding.sketch3',
        'autosaved': 0,
        'variant': 'NONAPPSTORE',
        'created': {
            'commit': '1899e24f63af087a9dd3c66f73b492b72c27c2c8',
            'appVersion': '93',
            'build': 155335,
            'app': 'com.bohemiancoding.sketch3',
            'compatibilityVersion': 99,
            'coeditCompatibilityVersion': 143,
            'version': 144,
            'variant': 'NONAPPSTORE'
        },
        'saveHistory': [
            'NONAPPSTORE.155335'
        ],
        'appVersion': '93',
        'build': 155335
    }
