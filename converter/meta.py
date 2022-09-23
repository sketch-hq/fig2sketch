def convert(pages):
    return {
        'commit': '5af03e43d9c4d8bc0e1b21000ea30adc7abf8c31',
        'pagesAndArtboards': {
            page['do_objectID']: {
                'name': page['name'],
                'artboards': {
                    artboard['do_objectID']: {'name': artboard['name']}
                    for artboard in page['layers']
                }
            }
            for page in pages
        },
        'version': 134,
        'fonts': [
        ],
        'compatibilityVersion': 99,
        'app': 'com.bohemiancoding.sketch3',
        'autosaved': 0,
        'variant': 'NONAPPSTORE',
        'created': {
            'commit': '5af03e43d9c4d8bc0e1b21000ea30adc7abf8c31',
            'appVersion': '69.2',
            'build': 107504,
            'app': 'com.bohemiancoding.sketch3',
            'compatibilityVersion': 99,
            'version': 134,
            'variant': 'NONAPPSTORE'
        },
        'saveHistory': [
            'NONAPPSTORE.107504'
        ],
        'appVersion': '69.2',
        'build': 107504
    }
