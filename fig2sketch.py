import os

import figformat.fig2json as fig2json
from converter import convert
import json
import shutil
import utils
import argparse


def clean_output():
    try:
        shutil.rmtree('output')
        os.mkdir('output')
    except:
        pass

    os.mkdir('output/pages')
    os.mkdir('output/images')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('fig_file', type=argparse.FileType('rb'))
    parser.add_argument('--salt', type=str, help='salt used to generate ids, defaults to random')
    args = parser.parse_args()

    if args.salt:
        utils.id_salt = args.salt.encode('utf8')

    clean_output()

    figma_json, id_map = fig2json.convert_fig(args.fig_file)

    try:
        os.remove('example/figma.json')
    except:
        pass

    json.dump(figma_json, open(f'example/figma.json', 'w'), indent=2, ensure_ascii=False, default=lambda x: x.tolist())

    convert.convert_json_to_sketch(figma_json, id_map)
