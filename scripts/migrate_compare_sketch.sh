#!/bin/bash
set -e

# Make a copy of the original file
ORIGINAL=$1
MIGRATED=$(echo $ORIGINAL | sed s/$(basename $ORIGINAL .sketch).sketch/migrated.sketch/)
cp $ORIGINAL $MIGRATED

# Migrate .sketch
COMMAND="/Applications/Sketch.app/Contents/MacOS/sketchtool migrate $MIGRATED"

$SSH_COMMAND $COMMAND

$(dirname $0)/compare_sketch.sh $ORIGINAL $MIGRATED
