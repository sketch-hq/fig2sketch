# .fig to Sketch converter

## Install

Use Python 3
```
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Convert .fig to .sketch

1. Run `python <path to .fig file> <path to store the .sketch file>`
2. Open the resulting .sketch file in Sketch

### Options

- Pass `--salt 12345678` to ensure a consistent conversion order
- Pass `--dump-fig-json example/figma.json` (which whichever path/name you like) to dump the generated JSON from the fig file

Example:

`python fig2sketch.py --salt 12345678 example/shapes_party.fig output/output.sketch --dump-fig-json example/figma.json`


## Documentation about .fig format
https://www.notion.so/sketch-hq/Figma-converter-d66dcb6c51f14baebf9b508141c095c2


## Identified issues
https://www.notion.so/sketch-hq/Figma2Sketch-converter-b72c65353fb4477fbacfbf9fd2a87606
