import sys
import json

import figformat.decodefig as decodefig

if __name__ == '__main__':
    print(json.dumps(decodefig.decode(open(sys.argv[1], 'rb'))))
