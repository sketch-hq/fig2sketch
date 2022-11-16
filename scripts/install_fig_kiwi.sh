#!/bin/sh
set -eu

cd figformat/fig_kiwi

# Build and install
maturin build --release --strip
pip3 install target/wheels/*.whl --force-reinstall
