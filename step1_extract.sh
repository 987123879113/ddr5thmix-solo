#!/bin/bash

set -e

mkdir -p data_raw
python3 tools/py/dump_sys573_gamefs.py --input data_source --output data_raw --key DDR5 --type ddr --input-filenames tools/ddr5th_filenames.json
