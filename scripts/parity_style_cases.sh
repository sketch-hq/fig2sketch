#!/bin/bash

set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 3 ]; then
  echo "Usage: $0 <fixture.fig> [swift-cli-path] [oracle-cli-path]" >&2
  exit 64
fi

FIXTURE="$1"
SWIFT_BIN="${2:-./swift/.build/arm64-apple-macosx/debug/fig2sketch}"
ORACLE_BIN="${3:-${F2S_ORACLE_BIN:-}}"

if [ ! -f "$FIXTURE" ]; then
  echo "Fixture not found: $FIXTURE" >&2
  exit 66
fi

if [ ! -x "$SWIFT_BIN" ]; then
  ALT_SWIFT="./swift/.build/debug/fig2sketch"
  if [ -x "$ALT_SWIFT" ]; then
    SWIFT_BIN="$ALT_SWIFT"
  else
    echo "Swift CLI not found or not executable: $SWIFT_BIN" >&2
    exit 69
  fi
fi

if [ -z "$ORACLE_BIN" ]; then
  echo "Oracle CLI path is required (arg 3 or F2S_ORACLE_BIN)." >&2
  exit 69
fi

if [ ! -x "$ORACLE_BIN" ]; then
  echo "Oracle CLI not found or not executable: $ORACLE_BIN" >&2
  exit 69
fi

TMPDIR_F2S="$(mktemp -d "${TMPDIR:-/tmp}/f2s-style-parity.XXXXXX")"
trap 'rm -rf "$TMPDIR_F2S"' EXIT

ORACLE_SKETCH="$TMPDIR_F2S/oracle.sketch"
SWIFT_SKETCH="$TMPDIR_F2S/swift.sketch"
ORACLE_DUMP="$TMPDIR_F2S/oracle.dump.json"
SWIFT_DUMP="$TMPDIR_F2S/swift.dump.json"
ORACLE_STDERR="$TMPDIR_F2S/oracle.stderr"
SWIFT_STDERR="$TMPDIR_F2S/swift.stderr"
ORACLE_STDOUT="$TMPDIR_F2S/oracle.stdout"
SWIFT_STDOUT="$TMPDIR_F2S/swift.stdout"

echo "Running oracle CLI with --dump-fig-json..."
set +e
"$ORACLE_BIN" "$FIXTURE" "$ORACLE_SKETCH" --dump-fig-json "$ORACLE_DUMP" -v >"$ORACLE_STDOUT" 2>"$ORACLE_STDERR"
ORACLE_EXIT=$?
"$SWIFT_BIN" "$FIXTURE" "$SWIFT_SKETCH" --dump-fig-json "$SWIFT_DUMP" -v >"$SWIFT_STDOUT" 2>"$SWIFT_STDERR"
SWIFT_EXIT=$?
set -e

echo "Oracle exit: $ORACLE_EXIT"
echo "Swift exit:  $SWIFT_EXIT"

if [ ! -f "$ORACLE_DUMP" ] || [ ! -f "$SWIFT_DUMP" ]; then
  echo "Missing dump JSON from one or both CLIs." >&2
  exit 70
fi

python3 - "$ORACLE_DUMP" "$SWIFT_DUMP" "$ORACLE_STDERR" "$SWIFT_STDERR" <<'PY'
import json
import re
import sys
from pathlib import Path

oracle_dump, swift_dump, oracle_stderr, swift_stderr = map(Path, sys.argv[1:])

TARGET_KEYS = [
    "image_paints",
    "cropped_image_paints",
    "diamond_gradients",
    "progressive_blurs",
    "glass_effects",
    "paint_filters",
    "smooth_corners",
]

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def is_identity_transform(t):
    if not isinstance(t, dict):
        if isinstance(t, list) and len(t) >= 3:
            try:
                rows = [list(r) for r in t[:3]]
                if len(rows[0]) < 3 or len(rows[1]) < 3 or len(rows[2]) < 3:
                    return False
                target = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                for r, tr in zip(rows, target):
                    for a, b in zip(r[:3], tr):
                        if abs(float(a) - float(b)) >= 1e-9:
                            return False
                return True
            except Exception:
                return False
        return False
    vals = [t.get(k) for k in ("m00", "m01", "m02", "m10", "m11", "m12")]
    if any(v is None for v in vals):
        return False
    target = [1, 0, 0, 0, 1, 0]
    return all(abs(float(a) - float(b)) < 1e-9 for a, b in zip(vals, target))

def scan_features(dump_obj):
    counts = {k: 0 for k in TARGET_KEYS}
    examples = {k: [] for k in TARGET_KEYS}

    def visit(value, context_node=None):
        if isinstance(value, dict):
            node_like = value if ("type" in value and "name" in value) else context_node
            node_name = node_like.get("name") if isinstance(node_like, dict) else None
            node_type = node_like.get("type") if isinstance(node_like, dict) else None

            if (value.get("cornerSmoothing") or 0) > 0:
                counts["smooth_corners"] += 1
                if len(examples["smooth_corners"]) < 5:
                    examples["smooth_corners"].append({"type": node_type, "name": node_name, "cornerSmoothing": value.get("cornerSmoothing")})

            fills = value.get("fillPaints")
            strokes = value.get("strokePaints")
            if isinstance(fills, list) or isinstance(strokes, list):
                for paint in (fills or []) + (strokes or []):
                    if not isinstance(paint, dict):
                        continue
                    paint_type = paint.get("type")

                    if paint_type == "IMAGE":
                        counts["image_paints"] += 1
                        if "paintFilter" in paint:
                            counts["paint_filters"] += 1
                            if len(examples["paint_filters"]) < 5:
                                examples["paint_filters"].append({"type": node_type, "name": node_name})

                        if "transform" in paint and not is_identity_transform(paint.get("transform")):
                            counts["cropped_image_paints"] += 1
                            if len(examples["cropped_image_paints"]) < 5:
                                examples["cropped_image_paints"].append({
                                    "type": node_type,
                                    "name": node_name,
                                    "imageScaleMode": paint.get("imageScaleMode"),
                                    "transform": paint.get("transform"),
                                })

                    if paint_type == "GRADIENT_DIAMOND":
                        counts["diamond_gradients"] += 1
                        if len(examples["diamond_gradients"]) < 5:
                            examples["diamond_gradients"].append({"type": node_type, "name": node_name})

            effects = value.get("effects")
            if isinstance(effects, list):
                for effect in effects:
                    if not isinstance(effect, dict):
                        continue
                    effect_type = effect.get("type")
                    if effect_type in ("FOREGROUND_BLUR", "BACKGROUND_BLUR") and effect.get("blurOpType") == "PROGRESSIVE":
                        counts["progressive_blurs"] += 1
                        if len(examples["progressive_blurs"]) < 5:
                            examples["progressive_blurs"].append({"type": node_type, "name": node_name, "effectType": effect_type})
                    if effect_type == "GLASS":
                        counts["glass_effects"] += 1
                        if len(examples["glass_effects"]) < 5:
                            examples["glass_effects"].append({"type": node_type, "name": node_name})

            for child in value.values():
                visit(child, node_like)
        elif isinstance(value, list):
            for item in value:
                visit(item, context_node)

    visit(dump_obj)
    return counts, examples

def warning_codes(stderr_path: Path):
    text = stderr_path.read_text(encoding="utf-8", errors="replace")
    codes = [c for c in re.findall(r"\[([A-Z]{3}\d{3})\]", text) if c.startswith(("IMG", "STY"))]
    return sorted(set(codes))

oracle = load(oracle_dump)
swift = load(swift_dump)
oracle_counts, oracle_examples = scan_features(oracle)
swift_counts, swift_examples = scan_features(swift)
oracle_warning_codes = warning_codes(oracle_stderr)
swift_warning_codes = warning_codes(swift_stderr)

target_present = any(oracle_counts[k] > 0 for k in ("cropped_image_paints", "diamond_gradients", "progressive_blurs", "glass_effects"))
count_mismatches = {k: (oracle_counts[k], swift_counts[k]) for k in TARGET_KEYS if oracle_counts[k] != swift_counts[k]}

print("Style feature counts (oracle vs swift):")
for key in TARGET_KEYS:
    print(f"  {key}: {oracle_counts[key]} vs {swift_counts[key]}")

if count_mismatches:
    print("Count mismatches:")
    for key, pair in count_mismatches.items():
        print(f"  {key}: {pair[0]} vs {pair[1]}")
else:
    print("Count parity: OK")

print("Warning codes (oracle):", ",".join(oracle_warning_codes) or "(none)")
print("Warning codes (swift): ", ",".join(swift_warning_codes) or "(none)")

interesting = ("cropped_image_paints", "diamond_gradients", "progressive_blurs", "glass_effects")
if not target_present:
    print("Target style cases present: NO (fixture does not contain cropped-image / diamond / progressive / glass)")
else:
    print("Target style cases present: YES")
    for key in interesting:
        if oracle_examples[key]:
            print(f"  oracle examples for {key}:")
            for item in oracle_examples[key]:
                print("   ", item)

sys.exit(1 if count_mismatches else 0)
PY
