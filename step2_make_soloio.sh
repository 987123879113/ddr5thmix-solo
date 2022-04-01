#!/bin/bash

set -e

mkdir -p build

cp -r data_source/* build
rm -f build/deleteme.txt

python3 tools/py/build_sys573_gamefs.py --input data_raw --input-modified-list data_modified/modified.json --base data_source --key DDR5 --output build --patch-dir data_modified

armips -definelabel SOLO_IO 1 src/main.asm

python3 tools/py/calc_checksum.py --input build/GAME.DAT build/CARD.DAT --output build

mkisofs -d -o ddr5thsolo_soloio.iso "build"
