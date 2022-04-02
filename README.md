# Dance Dance Revolution 5th Mix Solo
This is an UNOFFICIAL patch for the System 573/arcade version of Dance Dance Revolution 5th Mix.

The game contains left over code that supports 6 panel gameplay and a large number of songs have 6 panel charts left over from 4th Mix Plus. This project is an attempt to restore that functionality as well as make improvements to the UI to bring it closer to what a real 5th Mix Solo might have felt like.

All source code is included.


## KNOWN BUGS/ISSUES
- Edits are bugged in 6 panel mode (won't fix)
- Only one of the two sensors in each panel is read (won't fix)

## Instructions
Note: **YOU MUST PROVIDE YOUR OWN DATA!**

[Microsoft Visual Studio 2015 x86 Redistributable](https://www.microsoft.com/en-US/download/details.aspx?id=48145) is required for tools to work properly.

1. Extract the contents of your Dance Dance Revolution 5th Mix CD to the `data_source` folder. You should have a `DAT` folder, `GAME.DAT`, `CARD.DAT`, and `PSX.EXE` file in this folder.
2. Run `step1_extract.bat` (`step1_extract.sh` if you are on *nix) to generate the `data_raw` folder.
3. Run `step2_make.bat` or `step2_make_soloio.bat` (`step2_make.sh` or `step2_make_soloio.sh` if you are on *nix) to build the `ddr5thsolo.iso`/`ddr5thsolo_soloio.iso` files. If you are using a real Solo machine then use `step2_make_soloio.bat`. If you are using MAME or an otherwise non-Solo machine then use `step2_make.bat`.

Additionally, if you are building this for MAME, you must use `chdman` (included with MAME) to build the required CHD.
1. Generate CHD using `chdman.exe createcd -i ddr5thsolo.iso -o a27jaa02.chd -c none` (`-c none` is requested because the compression can throw timing off in MAME).
2. Overwrite `roms/ddr5m/a27jaa02.chd` in your MAME folder with the newly generated `a27jaa02.chd`.
3. Delete `nvram/ddr5m` in order to force reinstallation when you boot `ddr5m` next in MAME.
4. You must run MAME from the command line instead of through the normal MAME UI to bypass hash check errors

If you wish to extract the CD bin/cue from a CHD file, use `chdman.exe extractcd -i a27jaa02.chd -o a27jaa02.cue`.

## Additional Instructions (*NIX ONLY)
If you are building using *nix, you must compile the required Cython modules:
1. `cd tools/py`
2. `python3 -m pip install -r requirements.txt`
2. `python3 setup.py build_ext --inplace`


## Notes
- Dipswitch 1 can be toggled on/off to enable/disable autoplay (even on real hardware)
- There are various flags in [src/main.asm](https://github.com/987123879113/sys573mods/blob/main/ddr5thmix-solo-src/src/main.asm) that can be modified such as `FORCE_UNLOCK`, `SOLO_MODE`, `AUTOPLAY_ENABLED`, `AUTOPLAY_TIMING`, `DISABLE_ANNOUNCER`, `DISABLE_CHEERING`, and `SWAP_EXTRA_LIGHTS`.

## Thanks
- @WannyTiggah for the edited title screen and icon edits
- @SakamotoNeko13 for the edited 4PANEL/6PANEL graphics on the style select screen
- @dragonminded for testing with a real Solo cabinet as well as lights mapping, lights test menu and autoplay display on dip test menu
