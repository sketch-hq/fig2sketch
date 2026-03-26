# fig2sketch

## Python
- Use `.venv` if present.
- Prefer `.venv/bin/python`, `.venv/bin/pytest`, `.venv/bin/mypy`.

## Files
- Edit `src/` and `tests/`; avoid generated outputs under `Build/`.
- Input/decode work lives in `src/figformat/`.
- Sketch schema/types live in `src/sketchformat/`; conversion logic lives in `src/converter/`.

## Conversion
- Prefer warn + continue over abort when degraded output is acceptable.
- Reuse existing warning codes; tests should assert codes, not log text.
- Keep in-place rewrite/retry flows; don’t bypass `Fig2SketchNodeChanged`.

## Fallbacks
- Keep the pure-Python Kiwi path; `fig_kiwi` is optional.
- Keep stdlib JSON path; `orjson` may be missing or unsuitable.

## Stability
- Use a fixed `--salt` when comparing generated output.
- Preserve `.sketch` layout and hashed asset refs unless a format change is intentional.

## Tests
- Converter changes should usually add or update narrow tests.
- Check `tests/integration/test_structure.py` when serialized output changes.
- In unit tests, avoid live font downloads by mocking `context.record_font` or the font retrieval path.
- For warning tests, mock `utils.log_conversion_warning`; assert codes and payloads.
