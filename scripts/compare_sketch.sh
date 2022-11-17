#!/bin/bash

set -eu

# Create working directories
rm -rf /tmp/f2s_original /tmp/f2s_changed
mkdir /tmp/f2s_original /tmp/f2s_changed

# Unzip original file
unzip -q "$1" -d /tmp/f2s_original

# Unzip changed file
unzip -q $2 -d /tmp/f2s_changed

# Compare
for of in $(find /tmp/f2s_original -type f)
do
    filename=$(echo $of | sed sx/tmp/f2s_original/xx)
    echo ===== $filename =====
    if $(echo $of | grep -q json$)
    then
        # Round floats to compare
        JQ_FILTER='(.. | select(type == "number" )) |= (. * 1000000000 | round | . / 1000000000)'

        # Skip properties encoding floats as strings
        for key in from to point curveFrom curveTo glyphBounds
        do
            JQ_FILTER+="| (.. | .$key?) |= empty"
        done

        jq -S "$JQ_FILTER" /tmp/f2s_original/$filename > /tmp/f2s_original/$filename.compare
        jq -S "$JQ_FILTER" /tmp/f2s_changed/$filename > /tmp/f2s_changed/$filename.compare
        diff -u /tmp/f2s_original/$filename.compare /tmp/f2s_changed/$filename.compare && echo Identical || true
    else
        diff -u /tmp/f2s_original/$filename /tmp/f2s_changed/$filename && echo Identical || true
    fi
done
