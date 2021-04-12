if not exist data_raw mkdir data_raw

tools\sys573tool.exe --mode dump --input data_source --output data_raw --key DDR5 --type ddr --input-filenames tools\ddr5th_filenames.json

pause
