#!/bin/sh
set -eu

cd figformat/fig_kiwi

# Build and install
maturin develop --release
