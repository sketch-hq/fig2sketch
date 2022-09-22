# Figma to Sketch converter

## Documentation about Figma format
https://www.notion.so/sketch-hq/Figma-converter-d66dcb6c51f14baebf9b508141c095c2

## Install

Use Python 3
```
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Convert .fig to .sketch directly

1. Run `python fig2sketch.py example/shapes_party.fig `
2. Open the resulting `output/output.sketch` in Sketch

## Convert a .fig to .sketch step by step
1. Run `python figformat/fig2json.py example/shapes_party.fig > example/figma.json`
2. Run: `python convert.py example/figma.json`
3. Open the resulting `output/output.sketch` in Sketch

## Other conversions

### Decode .fig via KiwiDecoder

This decodes the .fig file and generates a JSON file without any fix. **The resulting JSON can't be used directly in the converter.**

```
python decode_fig.py example/shapes_party.fig > example/figma.json
```
