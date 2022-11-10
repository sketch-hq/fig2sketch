#!/bin/sh
set -eu

patch=$PWD/$(dirname $0)/orjson.patch

# Check dependencies
#if ! command -v maturin &> /dev/null
#then
#    echo 'Installing maturin'
#    brew install maturin
#fi

# Download orjson
if [ ! -d /tmp/orjson ]
then
    git clone https://github.com/ijl/orjson.git /tmp/orjson
fi

cd /tmp/orjson

# Patch orjson with Sketch specifics
git checkout 3.8.1
git reset --hard
patch -p1 < $patch

# Build
maturin build --release --strip

# Install
pip3 install target/wheels/*.whl --force-reinstall
