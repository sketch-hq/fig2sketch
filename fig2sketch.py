import argparse
import json
import logging
from zipfile import ZipFile
import ssl

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts a .fig document to .sketch')
    parser.add_argument('fig_file', type=argparse.FileType('rb'))
    parser.add_argument('sketch_file')
    parser.add_argument('--salt', type=str, help='salt used to generate ids, defaults to random')
    parser.add_argument('--force-convert-images', action='store_true',
                        help='try to convert corrupted images')
    parser.add_argument('-v', action='count', dest='verbosity',
                        help='return more details, can be repeated')
    parser.add_argument('--dump-fig-json', type=argparse.FileType('w'),
                        help='output a fig representation in json for debugging purposes')
    args = parser.parse_args()

    # Set log level
    level = logging.WARNING
    if args.verbosity:
        level = logging.INFO if args.verbosity == 1 else logging.DEBUG

    logging.basicConfig(level=level)

    # Import these after setting the log level
    import figformat.fig2json as fig2json
    import utils
    from converter import convert

    if args.salt:
        utils.id_salt = args.salt.encode('utf8')

    if args.force_convert_images:
        from PIL import ImageFile

        ImageFile.LOAD_TRUNCATED_IMAGES = True

    # Load SSL certificates in OSs where Python does not use system defaults
    if not ssl.create_default_context().get_ca_certs():
        import certifi
        import os
        os.environ['SSL_CERT_FILE'] = certifi.where()
        logging.debug("Loaded TLS certificates from certifi")
    else:
        logging.debug("Using system TLS certificates")

    # Import
    with ZipFile(args.sketch_file, 'w') as output:
        fig_json, id_map = fig2json.convert_fig(args.fig_file, output)

        if args.dump_fig_json:
            json.dump(fig_json, args.dump_fig_json, indent=2, ensure_ascii=False,
                      default=lambda x: x.tolist())

        convert.convert_json_to_sketch(fig_json, id_map, output)
