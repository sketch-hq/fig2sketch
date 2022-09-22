import figformat.fig2json as fig2json
import sys

if __name__ == '__main__':
    fig2json.convert_fig(open(sys.argv[1], 'rb'))
