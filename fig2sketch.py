import os

import figformat.fig2json as fig2json
from converter import convert
import sys
import json

if __name__ == '__main__':
    figma_json = fig2json.convert_fig(open(sys.argv[1], 'rb'))

    try:
        os.remove('example/figma.json')
    except:
        pass

    json.dump(figma_json, open(f'example/figma.json', 'w'), indent=2)

    convert.convert_json_to_sketch(figma_json)
