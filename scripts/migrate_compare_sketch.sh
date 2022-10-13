#!/bin/bash
set -eu

# Create working directories
rm -r /tmp/f2s_original /tmp/f2s_migrated
mkdir /tmp/f2s_original /tmp/f2s_migrated

# Make a copy of the original file
ORIGINAL=$1
MIGRATED=$(echo $ORIGINAL | sed s/$(basename $ORIGINAL .sketch).sketch/migrated.sketch/)
cp $ORIGINAL $MIGRATED

# Unzip original file
unzip -q $ORIGINAL -d /tmp/f2s_original

# Migrate .sketch
COMMAND="/Applications/Sketch.app/Contents/MacOS/sketchtool migrate $MIGRATED"

$SSH_COMMAND $COMMAND

# Unzip migrated file
unzip -q $MIGRATED -d /tmp/f2s_migrated

# Compare
for of in $(find /tmp/f2s_original -type f)
do
    filename=$(echo $of | sed sx/tmp/f2s_original/xx)
    echo ===== $filename =====
    if $(echo $of | grep -q json$)
    then
        diff -u <(jq -S .  /tmp/f2s_original/$filename) <(jq -S .  /tmp/f2s_migrated/$filename) && echo Identical || true
    else
        diff -u /tmp/f2s_original/$filename /tmp/f2s_migrated/$filename && echo Identical || true
    fi
done;
