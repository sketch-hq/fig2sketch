import os

import figformat.fig2json as fig2json
from converter import convert
import sys
import json
import shutil


def clean_output():
    try:
        shutil.rmtree('output')
        os.mkdir('output')
    except:
        pass

    os.mkdir('output/pages')
    os.mkdir('output/images')


if __name__ == '__main__':
    clean_output()

    figma_json = fig2json.convert_fig(open(sys.argv[1], 'rb'))

    try:
        os.remove('example/figma.json')
    except:
        pass

    json.dump(figma_json, open(f'example/figma.json', 'w'), indent=2)

    convert.convert_json_to_sketch(figma_json)
