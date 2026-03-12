#!/bin/bash

set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 <fixture.fig> [swift-cli-path]" >&2
  exit 64
fi

FIXTURE="$1"
SWIFT_BIN="${2:-./swift/.build/debug/fig2sketch}"

if [ ! -f "$FIXTURE" ]; then
  echo "Fixture not found: $FIXTURE" >&2
  exit 66
fi

if [ ! -x "$SWIFT_BIN" ]; then
  echo "Swift CLI not found or not executable: $SWIFT_BIN" >&2
  echo "Build it first: (cd swift && swift build)" >&2
  exit 69
fi

TMPDIR_F2S="$(mktemp -d "${TMPDIR:-/tmp}/f2s-parity.XXXXXX")"
trap 'rm -rf "$TMPDIR_F2S"' EXIT

PY_OUT="$TMPDIR_F2S/python.sketch"
SW_OUT="$TMPDIR_F2S/swift.sketch"

echo "Running Python oracle..."
python3 ./src/fig2sketch.py "$FIXTURE" "$PY_OUT"

echo "Running Swift CLI..."
"$SWIFT_BIN" "$FIXTURE" "$SW_OUT"

echo "Comparing outputs..."
./scripts/compare_sketch.sh "$PY_OUT" "$SW_OUT"

echo "Parity comparison completed (see diff output above if any)."
