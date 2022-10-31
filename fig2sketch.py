import os

import figformat.fig2json as fig2json
import json
import shutil
import utils
import argparse
from converter import convert
from zipfile import ZipFile
import logging


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
    parser.add_argument('--force-convert-images', action='store_true', help='try to convert corrupted images')
    parser.add_argument('-v', action='count', dest='verbosity', help='return more details, can be repeated')
    args = parser.parse_args()

    if args.salt:
        utils.id_salt = args.salt.encode('utf8')

    if args.force_convert_images:
        from PIL import ImageFile
        ImageFile.LOAD_TRUNCATED_IMAGES = True

    # Set log level
    level = logging.WARNING
    if args.verbosity:
        level = logging.INFO if args.verbosity == 1 else logging.DEBUG

    logging.basicConfig(level=level)

    clean_output()
    output = ZipFile('output/output.sketch', 'w')

    figma_json, id_map = fig2json.convert_fig(args.fig_file, output)

    try:
        os.remove('example/figma.json')
    except:
        pass

    json.dump(figma_json, open(f'example/figma.json', 'w'), indent=2, ensure_ascii=False,
              default=lambda x: x.tolist())

    convert.convert_json_to_sketch(figma_json, id_map, output)
