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

## Convert a Figma JSON file to .sketch (via exporter plugin in Figma)

1. In Figma, select a file and use the "JSON Exporter" plugin (the red icon one) to export the **full document** in JSON. 
2. Run: `python convert.py example/exporter-plugin.json`
3. Get the resulting `output/output.sketch` file and open it in Sketch
