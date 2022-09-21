#!/bin/bash

set -x

EXAMPLES_DIR="data/"
FIG_FILE=$1
if [[ ! -f ${FIG_FILE} ]]
then
  echo "File ${FIG_FILE} does not exist" && exit 1
fi

FIG_FILE_NAME=$(basename $FIG_FILE)
FIG_FILE_BASENAME=$(basename $FIG_FILE_NAME .fig)
FIG_FILE_DST_DIR="${EXAMPLES_DIR}${FIG_FILE_BASENAME}/"

[[ ! -d ${FIG_FILE_DST_DIR} ]] && mkdir -p ${FIG_FILE_DST_DIR}
mv $FIG_FILE ${FIG_FILE_DST_DIR}
unzip ${FIG_FILE_DST_DIR}${FIG_FILE_NAME} -d ${FIG_FILE_DST_DIR}
python figformat/decodefig.py ${FIG_FILE_DST_DIR}canvas.fig
mv segment* ${FIG_FILE_DST_DIR}
npx kiwi-schema --schema ${FIG_FILE_DST_DIR}segment0.data --text ${FIG_FILE_DST_DIR}schema.struct
npx kiwi-schema --schema ${FIG_FILE_DST_DIR}segment0.data --root-type Message --to-json ${FIG_FILE_DST_DIR}segment1.data
