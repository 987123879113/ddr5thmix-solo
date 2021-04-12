if not exist build mkdir build

xcopy /Y /E /H /C data_source\* build
if exist build\deleteme.txt del build\deleteme.txt

tools\sys573tool.exe --mode build --input data_raw --input-modified-list data_modified\modified.json --base data_source --key DDR5 --output build --patch-dir data_modified
tools\thirdparty\armips.exe src\main.asm
tools\sys573tool.exe --mode checksum --input build\GAME.DAT build\CARD.DAT --output build
tools\thirdparty\mkisofs.exe -d -o ddr5thsolo.iso "build"

pause