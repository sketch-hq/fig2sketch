import json
import sys
import figformat.fig2json as fig2json

if __name__ == '__main__':
    print(json.dumps(fig2json.convert_fig(open(sys.argv[1], 'rb')), indent=2))
