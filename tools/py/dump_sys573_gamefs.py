import argparse
import ctypes
import json
import os
import string

from comp573 import decode_lz


def get_filename_hash(filename):
    filename_hash = 0

    for _, c in enumerate(filename):
        for i in range(6):
            filename_hash = ctypes.c_int(
                ((filename_hash >> 31) & 0x4c11db7) ^ ((filename_hash << 1) | ((ord(c) >> i) & 1))
            ).value

    return filename_hash & 0xffffffff


def decrypt_data_internal(data, key):
    def calculate_crc32(input):
        crc = -1

        for c in bytearray(input, encoding='ascii'):
            crc ^= c << 24

            for _ in range(8):
                if crc & 0x80000000:
                    crc = (crc << 1) ^ 0x4C11DB7
                else:
                    crc <<= 1

        return crc


    decryption_key = calculate_crc32(key)

    for i in range(len(data)):
        data[i] ^= (decryption_key >> 8) & 0xff # This 8 can be variable it seems, but it usually is 8?

    return data


def decrypt_data(data, input_key):
    def calculate_key(input_str):
        key = 0

        for cur in input_str.upper():
            if cur in string.ascii_uppercase:
                key -= 0x37

            elif cur in string.ascii_lowercase:
                key -= 0x57

            elif cur in string.digits:
                key -= 0x30

            key += ord(cur)

        return key & 0xff

    val = 0x41C64E6D
    key1 = (val * calculate_key(input_key)) & 0xffffffff
    counter = 0

    for idx, c in enumerate(data):
        val = ((key1 + counter) >> 5) ^ c
        data[idx] = val & 0xff
        counter += 0x3039

    return data


common_extensions = [
    'bin', 'exe', 'dat', 'rom', 'o'
]

mambo_common_extensions = [
    'bin.new', 'cmp', 'vas', 'olb', 'pup', 'cpr'
]

ddr_common_extensions = [
    'cmt', 'tim', 'cms', 'lmp', 'per', 'csq', 'ssq', 'cmm',
    'pos', 'ctx', 'lst', 'tmd', 'vab', 'sbs', 'can', 'anm',
    'lpe', 'mbk', 'lz', 'bs', 'txt', 'tan'
]

gfdm_common_extensions = [
    'pak', 'fcn', 'vas', 'sq2', 'sq3', 'gsq', 'dsq', 'bin', 'dat'
]

dmx_common_extensions = [
    'tex', 'lst', 'mdt', 'nmd', 'lmp', 'tng', 'bke', 'lz', 'seq'
]

common_extensions += mambo_common_extensions + ddr_common_extensions + gfdm_common_extensions + dmx_common_extensions

ddr_common_regions = [
    'span', 'ital', 'germ', 'fren', 'engl', 'japa', 'kore'
]

ddr_common_parts = [
    'cd', 'nm', 'in', 'ta', 'th', 'bk', 'fr', '25'
]


def generate_data_paths(hash_list={}):
    pccard_filenames = [
        "a.pak",
        "ascii_size16.bin",
        "ascii_size24.bin",
        "ascii_size8.bin",
        "course_info.bin",
        "d_cautio.dat",
        "d_cautio_aa.dat",
        "d_ending.dat",
        "d_res_ns.dat",
        "d_title.dat",
        "d_title_aa.dat",
        "data/all/inst.lst",
        "data/all/inst.tex",
        "data/all/inst.tmd",
        "data/all/texbind.bin",
        "data/area/area/cobk_25.cmt",
        "data/area/area/kicbk_25.cmt",
        "data/area/area/prac_25.cmt",
        "data/area/area/titl2_25.cmt",
        "data/area/area/title.cmt",
        "data/area/area/titls_25.cmt",
        "data/area/area_ua/cobk_25.cmt",
        "data/area/area_ua/kicbk_25.cmt",
        "data/area/area_ua/prac_25.cmt",
        "data/area/area_ua/titl2_25.cmt",
        "data/area/area_ua/title.cmt",
        "data/area/area_ua/titls_25.cmt",
        "data/area/area_ja/cobk_25.cmt",
        "data/area/area_ja/kicbk_25.cmt",
        "data/area/area_ja/prac_25.cmt",
        "data/area/area_ja/titl2_25.cmt",
        "data/area/area_ja/title.cmt",
        "data/area/area_ja/titls_25.cmt",
        "data/area/area_ea/cobk_25.cmt",
        "data/area/area_ea/kicbk_25.cmt",
        "data/area/area_ea/prac_25.cmt",
        "data/area/area_ea/titl2_25.cmt",
        "data/area/area_ea/title.cmt",
        "data/area/area_ea/titls_25.cmt",
        "data/area/area_ka/cobk_25.cmt",
        "data/area/area_ka/kicbk_25.cmt",
        "data/area/area_ka/prac_25.cmt",
        "data/area/area_ka/titl2_25.cmt",
        "data/area/area_ka/title.cmt",
        "data/area/area_ka/titls_25.cmt",
        "data/back/caut/cauta_25.cmt",
        "data/back/caut/caute_25.cmt",
        "data/back/caut/cautf_25.cmt",
        "data/back/caut/cautg_25.cmt",
        "data/back/caut/cauti_25.cmt",
        "data/back/caut/cautj_25.cmt",
        "data/back/caut/cautk_25.cmt",
        "data/back/caut/cauts_25.cmt",
        "data/back/demo/unist_25.cmt",
        "data/back/game/iron_25.cmt",
        "data/chara/chara.ctx",
        "data/chara/chara.lst",
        "data/chara/chara.pos",
        "data/chara/inst/inst.ctx",
        "data/chara/inst/inst.lst",
        "data/chara/inst/inst.pos",
        "data/chara/inst/inst.tmd",
        "data/chara/inst_d/inst_d.cmt",
        "data/chara/inst_d/inst_d.lst",
        "data/chara/inst_d/inst_d.pos",
        "data/chara/inst_d/inst_d.tmd",
        "data/chara/inst_s/inst_s.cmt",
        "data/chara/inst_s/inst_s.lst",
        "data/chara/inst_s/inst_s.pos",
        "data/chara/inst_s/inst_s.tmd",
        "data/course/onimode.bin",
        "data/course/onimode.ssq",
        "data/kanji/eames.cmp",
        "data/mcard/page0e.txt",
        "data/mcard/page0j.txt",
        "data/mcard/page0k.txt",
        "data/mcard/page1e.txt",
        "data/mcard/page1j.txt",
        "data/mcard/page1k.txt",
        "data/mcard/page2e.txt",
        "data/mcard/page2j.txt",
        "data/mcard/page2k.txt",
        "data/mcard/page0.txt",
        "data/mcard/page1.txt",
        "data/mcard/page2.txt",
        "data/mdb/aa_mdb.bin",
        "data/mdb/ea_mdb.bin",
        "data/mdb/ja_mdb.bin",
        "data/mdb/ka_mdb.bin",
        "data/mdb/ua_mdb.bin",
        "data/mdb/mdb.bin",
        "data/motion/inst/inst.cmm",
        "data/motion/prac/prac.cmm",
        "data/movie/titlemv.str",
        "data/mp3/enc/M81D7HHJ.DAT",
        "data/mp3/mp3_tab.bin",
        "data/spu/system.vas",
        "data/tex/rembind.bin",
        "data/tex/subbind.bin",
        "data/tim/allcd/alcda0.cmt",
        "data/tim/allcd/alcdu0.cmt",
        "data/tim/allcd/alcde0.cmt",
        "data/tim/allcd/alcdj0.cmt",
        "data/tim/allcd/alcdk0.cmt",
        "data/tim/wfont/wfont_w.bin",
        "data/vab/ddr3.lst",
        "data/vab/ddr3.vas",
        "data/vab/ddrusa.lst",
        "data/vab/ddrusa.vas",
        "dl/n1/pathtab.bin",
        "dl/pathtab.bin",
        "pathtab.bin",
        "g_id.dat",
        "got11hlf.bin",
        "got11j0b.bin",
        "got11j1b.bin",
        "group_list.bin",
        "ir_id.bin",
        "jp_title.bin",
        "kfont8.bin",
        "music_info.bin",
        "net_id.bin",
        "sd/data/close.vab",
        "sd/data/dj_chr1.vab",
        "sd/data/dj_chr2.vab",
        "sd/data/dj_chr3.vab",
        "sd/data/dj_chr4.vab",
        "sd/data/dj_chr5.vab",
        "sd/data/dj_clr1.vab",
        "sd/data/dj_clr2.vab",
        "sd/data/dj_clr3.vab",
        "sd/data/dj_clr4.vab",
        "sd/data/dj_fail1.vab",
        "sd/data/dj_fail2.vab",
        "sd/data/dj_fail3.vab",
        "sd/data/dj_fail4.vab",
        "sd/data/dj_fail5.vab",
        "sd/data/dj_slct1.vab",
        "sd/data/dj_slct2.vab",
        "sd/data/dj_slct3.vab",
        "sd/data/dj_slct4.vab",
        "sd/data/dj_slct5.vab",
        "sd/data/dj_slct6.vab",
        "sd/data/dj_slct7.vab",
        "sd/data/dj_st_c1.vab",
        "sd/data/dj_st_c2.vab",
        "sd/data/dj_st_c3.vab",
        "sd/data/dj_st_c4.vab",
        "sd/data/dj_st_c5.vab",
        "sd/data/end.vab",
        "sd/data/game1.vab",
        "sd/data/game2.vab",
        "sd/data/in_demo.vab",
        "sd/data/jochu.vab",
        "sd/data/monitor.vab",
        "sd/data/multi.vab",
        "sd/data/out_demo.vab",
        "sd/data/scale.vab",
        "soft/s573/overlay/bin/dbugtest.olb",
        "soft/s573/overlay/bin/fpga_mp3.olb",
        "soft/s573/overlay/bin/gtest.olb",
        "soft/s573/overlay/bin/play.olb",
        "system.vas",

        "cube0.bin",
        "cube1.bin",
        "mdb.bin",
        "courseboss.bin",
        "ircourse.bin",
        "course.bin",
        "fontdb.bin",
        "arrangement_data.bin",
        "object_2d_data.bin",
        "ja_mdb.bin",
        "marathoncourse.bin",
        "font08.bin",
        "font16.bin",
        "font24.bin",
        "font32.bin",
        "font04.bin",
        "dmx2.vas",
        "dmx.vas",

        "../flash/texdata/nentry.bin",
        "../flash/texdata/title.bin",
        "../flash/texdata/dlangsp.bin",
        "../flash/texdata/dlangit.bin",
        "../flash/texdata/dlangge.bin",
        "../flash/texdata/dlangfr.bin",
        "../flash/texdata/dlangen.bin",
        "../flash/texdata/dlangjp.bin",
        "../flash/texdata/select.bin",
        "../flash/texdata/riff.bin",
        "../flash/texdata/demopic.bin",
        "../flash/texdata/longla.bin",
        "../flash/texdata/longjet.bin",
        "../flash/texdata/longfire.bin",
        "../flash/texdata/nmedley.bin    ",
        "../flash/texdata/mmedley.bin",
        "../flash/texdata/pmedley.bin",
        "../flash/texdata/ddr.bin",
        "../flash/texdata/pdunk.bin",
        "../flash/texdata/eraser.bin",
        "../flash/texdata/spin.bin",
        "../flash/texdata/midnight.bin",
        "../flash/texdata/bump.bin",
        "../flash/texdata/break.bin",
        "../flash/texdata/help.bin",
        "../flash/texdata/onaway.bin",
        "../flash/texdata/boss.bin",
        "../flash/texdata/classic.bin",
        "../flash/texdata/cosmic.bin",
        "../flash/texdata/bossa.bin",
        "../flash/texdata/hand.bin",
        "../flash/texdata/cutie3.bin",
        "../flash/texdata/ppr.bin",
        "../flash/texdata/shadow.bin",
        "../flash/texdata/diana.bin",
        "../flash/texdata/jim.bin",
        "../flash/texdata/zeppeli.bin",
        "../flash/texdata/layla.bin",
        "../flash/texdata/moveover.bin",
        "../flash/texdata/still.bin",
        "../flash/texdata/deep.bin",
        "../flash/texdata/getit.bin",
        "../flash/texdata/highway.bin",
        "../flash/texdata/johnny.bin",
        "../flash/texdata/prim.bin",
        "../flash/texdata/car.bin",
        "../flash/texdata/eclipse.bin",
        "../flash/texdata/micky.bin",
        "../flash/texdata/evil.bin",
        "../flash/texdata/cutie2.bin",
        "../flash/texdata/hmetal2.bin",
        "../flash/texdata/king.bin",
        "../flash/texdata/punk2.bin",
        "../flash/texdata/flam.bin",
        "../flash/texdata/rockf.bin",
        "../flash/texdata/think.bin",
        "../flash/texdata/heaven.bin",
        "../flash/texdata/upower.bin",
        "../flash/texdata/night.bin",
        "../flash/texdata/skaska.bin",
        "../flash/texdata/joey.bin",
        "../flash/texdata/holiday.bin",
        "../flash/texdata/magic.bin",
        "../flash/texdata/advent.bin",
        "../flash/texdata/country.bin",
        "../flash/texdata/machine.bin",
        "../flash/texdata/ending.bin",
        "../flash/texdata/nrock.bin",
        "../flash/texdata/degirock.bin",
        "../flash/texdata/toydolls.bin",
        "../flash/texdata/fusion.bin",
        "../flash/texdata/mtown.bin",
        "../flash/texdata/vent.bin",
        "../flash/texdata/hmetal.bin",
        "../flash/texdata/jazz.bin",
        "../flash/texdata/funk.bin",
        "../flash/texdata/hrock.bin",
        "../flash/texdata/blues.bin",
        "../flash/texdata/common.bin",
        "../flash/model/demopic.tmd",
        "../flash/model/riff.tmd",
        "../flash/model/demo.tmd",
        "../flash/model/toydolls.tmd",
        "../flash/model/hmetal.tmd",
        "../flash/model/blues.tmd",
        "../flash/model/common.tmd",
        "../flash/tp/nentry.tpb",
        "../flash/tp/title.tpb",
        "../flash/tp/dlangsp.tpb",
        "../flash/tp/dlangit.tpb",
        "../flash/tp/dlangge.tpb",
        "../flash/tp/dlangfr.tpb",
        "../flash/tp/dlangen.tpb",
        "../flash/tp/dlangjp.tpb",
        "../flash/tp/demopic.tpb",
        "../flash/seq/p_riff3.bin",
        "../flash/seq/p_riff2.bin",
        "../flash/seq/p_riff1.bin",
        "../flash/seq/lr_z_2p2.bin",
        "../flash/seq/lr_z_2p1.bin",
        "../flash/seq/lr_z_1p1.bin",
        "../flash/seq/lr_x_2p2.bin",
        "../flash/seq/lr_x_2p1.bin",
        "../flash/seq/lr_x_1p1.bin",
        "../flash/seq/lr_n_2p2.bin",
        "../flash/seq/lr_n_2p1.bin",
        "../flash/seq/lr_n_1p2.bin",
        "../flash/seq/lr_n_1p1.bin",
        "../flash/seq/sp_z_2p2.bin",
        "../flash/seq/sp_z_2p1.bin",
        "../flash/seq/sp_z_1p1.bin",
        "../flash/seq/sp_x_2p2.bin",
        "../flash/seq/sp_x_2p1.bin",
        "../flash/seq/sp_x_1p1.bin",
        "../flash/seq/sp_n_2p2.bin",
        "../flash/seq/sp_n_2p1.bin",
        "../flash/seq/sp_n_1p2.bin",
        "../flash/seq/sp_n_1p1.bin",
        "../flash/seq/sp_x_bas.bin",
        "../flash/seq/sp_n_bas.bin",
        "../flash/seq/md_z_2p2.bin",
        "../flash/seq/md_z_2p1.bin",
        "../flash/seq/md_z_1p1.bin",
        "../flash/seq/md_x_2p2.bin",
        "../flash/seq/md_x_2p1.bin",
        "../flash/seq/md_x_1p1.bin",
        "../flash/seq/md_n_2p2.bin",
        "../flash/seq/md_n_2p1.bin",
        "../flash/seq/md_n_1p2.bin",
        "../flash/seq/md_n_1p1.bin",
        "../flash/seq/md_x_bas.bin",
        "../flash/seq/md_n_bas.bin",
        "../flash/seq/bp_z_2p2.bin",
        "../flash/seq/bp_z_2p1.bin",
        "../flash/seq/bp_z_1p1.bin",
        "../flash/seq/bp_x_2p2.bin",
        "../flash/seq/bp_x_2p1.bin",
        "../flash/seq/bp_x_1p1.bin",
        "../flash/seq/bp_n_2p2.bin",
        "../flash/seq/bp_n_2p1.bin",
        "../flash/seq/bp_n_1p2.bin",
        "../flash/seq/bp_n_1p1.bin",
        "../flash/seq/bp_x_bas.bin",
        "../flash/seq/bp_n_bas.bin",
        "../flash/seq/br_z_2p2.bin",
        "../flash/seq/br_z_2p1.bin",
        "../flash/seq/br_z_1p1.bin",
        "../flash/seq/br_x_2p2.bin",
        "../flash/seq/br_x_2p1.bin",
        "../flash/seq/br_x_1p1.bin",
        "../flash/seq/br_n_2p2.bin",
        "../flash/seq/br_n_2p1.bin",
        "../flash/seq/br_n_1p2.bin",
        "../flash/seq/br_n_1p1.bin",
        "../flash/seq/br_x_bas.bin",
        "../flash/seq/br_n_bas.bin",
        "../flash/seq/hp_z_2p2.bin",
        "../flash/seq/hp_z_2p1.bin",
        "../flash/seq/hp_z_1p1.bin",
        "../flash/seq/hp_x_2p2.bin",
        "../flash/seq/hp_x_2p1.bin",
        "../flash/seq/hp_x_1p1.bin",
        "../flash/seq/hp_n_2p2.bin",
        "../flash/seq/hp_n_2p1.bin",
        "../flash/seq/hp_n_1p2.bin",
        "../flash/seq/hp_n_1p1.bin",
        "../flash/seq/hp_x_bas.bin",
        "../flash/seq/hp_n_bas.bin",
        "../flash/seq/hp_z_bas.bin",
        "../flash/seq/oa_z_2p2.bin",
        "../flash/seq/oa_z_2p1.bin",
        "../flash/seq/oa_z_1p1.bin",
        "../flash/seq/oa_x_2p2.bin",
        "../flash/seq/oa_x_2p1.bin",
        "../flash/seq/oa_x_1p2.bin",
        "../flash/seq/oa_x_1p1.bin",
        "../flash/seq/oa_n_2p2.bin",
        "../flash/seq/oa_n_2p1.bin",
        "../flash/seq/oa_n_1p2.bin",
        "../flash/seq/oa_n_1p1.bin",
        "../flash/seq/oa_x_bas.bin",
        "../flash/seq/oa_n_bas.bin",
        "../flash/seq/lj_z_2p2.bin",
        "../flash/seq/lj_z_2p1.bin",
        "../flash/seq/lj_z_1p1.bin",
        "../flash/seq/lj_x_2p2.bin",
        "../flash/seq/lj_x_2p1.bin",
        "../flash/seq/lj_x_1p1.bin",
        "../flash/seq/lj_n_2p2.bin",
        "../flash/seq/lj_n_2p1.bin",
        "../flash/seq/lj_n_1p2.bin",
        "../flash/seq/lj_n_1p1.bin",
        "../flash/seq/bo_z_2p2.bin",
        "../flash/seq/bo_z_2p1.bin",
        "../flash/seq/bo_z_1p1.bin",
        "../flash/seq/bo_x_2p2.bin",
        "../flash/seq/bo_x_2p1.bin",
        "../flash/seq/bo_x_1p1.bin",
        "../flash/seq/bo_e_2p2.bin",
        "../flash/seq/bo_e_2p1.bin",
        "../flash/seq/bo_e_1p2.bin",
        "../flash/seq/bo_e_1p1.bin",
        "../flash/seq/bo_z_bas.bin",
        "../flash/seq/bo_x_bas.bin",
        "../flash/seq/bo_e_bas.bin",
        "../flash/seq/cl_z_2p2.bin",
        "../flash/seq/cl_z_2p1.bin",
        "../flash/seq/cl_z_1p1.bin",
        "../flash/seq/cl_x_2p2.bin",
        "../flash/seq/cl_x_2p1.bin",
        "../flash/seq/cl_x_1p1.bin",
        "../flash/seq/cl_n_2p2.bin",
        "../flash/seq/cl_n_2p1.bin",
        "../flash/seq/cl_n_1p2.bin",
        "../flash/seq/cl_n_1p1.bin",
        "../flash/seq/cl_x_bas.bin",
        "../flash/seq/cl_n_bas.bin",
        "../flash/seq/hu_z_2p2.bin",
        "../flash/seq/hu_z_2p1.bin",
        "../flash/seq/hu_z_1p1.bin",
        "../flash/seq/hu_x_2p2.bin",
        "../flash/seq/hu_x_2p1.bin",
        "../flash/seq/hu_x_1p1.bin",
        "../flash/seq/hu_n_2p2.bin",
        "../flash/seq/hu_n_2p1.bin",
        "../flash/seq/hu_n_1p2.bin",
        "../flash/seq/hu_n_1p1.bin",
        "../flash/seq/hu_z_bas.bin",
        "../flash/seq/hu_x_bas.bin",
        "../flash/seq/hu_n_bas.bin",
        "../flash/seq/gt_z_2p2.bin",
        "../flash/seq/gt_z_2p1.bin",
        "../flash/seq/gt_z_1p1.bin",
        "../flash/seq/gt_x_2p2.bin",
        "../flash/seq/gt_x_2p1.bin",
        "../flash/seq/gt_x_1p1.bin",
        "../flash/seq/gt_n_2p2.bin",
        "../flash/seq/gt_n_2p1.bin",
        "../flash/seq/gt_n_1p2.bin",
        "../flash/seq/gt_n_1p1.bin",
        "../flash/seq/gt_z_bas.bin",
        "../flash/seq/gt_x_bas.bin",
        "../flash/seq/gt_n_bas.bin",
        "../flash/seq/jo_z_2p2.bin",
        "../flash/seq/jo_z_2p1.bin",
        "../flash/seq/jo_z_1p1.bin",
        "../flash/seq/jo_x_2p2.bin",
        "../flash/seq/jo_x_2p1.bin",
        "../flash/seq/jo_x_1p1.bin",
        "../flash/seq/jo_n_2p2.bin",
        "../flash/seq/jo_n_2p1.bin",
        "../flash/seq/jo_n_1p2.bin",
        "../flash/seq/jo_n_1p1.bin",
        "../flash/seq/jo_x_bas.bin",
        "../flash/seq/jo_n_bas.bin",
        "../flash/seq/mv_z_2p2.bin",
        "../flash/seq/mv_z_2p1.bin",
        "../flash/seq/mv_z_1p1.bin",
        "../flash/seq/mv_x_2p2.bin",
        "../flash/seq/mv_x_2p1.bin",
        "../flash/seq/mv_x_1p1.bin",
        "../flash/seq/mv_n_2p2.bin",
        "../flash/seq/mv_n_2p1.bin",
        "../flash/seq/mv_n_1p2.bin",
        "../flash/seq/mv_n_1p1.bin",
        "../flash/seq/mv_x_bas.bin",
        "../flash/seq/mv_n_bas.bin",
        "../flash/seq/hi_z_2p2.bin",
        "../flash/seq/hi_z_2p1.bin",
        "../flash/seq/hi_z_1p1.bin",
        "../flash/seq/hi_x_2p2.bin",
        "../flash/seq/hi_x_2p1.bin",
        "../flash/seq/hi_x_1p1.bin",
        "../flash/seq/hi_n_2p2.bin",
        "../flash/seq/hi_n_2p1.bin",
        "../flash/seq/hi_n_1p2.bin",
        "../flash/seq/hi_n_1p1.bin",
        "../flash/seq/hi_x_bas.bin",
        "../flash/seq/hi_n_bas.bin",
        "../flash/seq/st_z_2p2.bin",
        "../flash/seq/st_z_2p1.bin",
        "../flash/seq/st_z_1p1.bin",
        "../flash/seq/st_x_2p2.bin",
        "../flash/seq/st_x_2p1.bin",
        "../flash/seq/st_x_1p1.bin",
        "../flash/seq/st_n_2p2.bin",
        "../flash/seq/st_n_2p1.bin",
        "../flash/seq/st_n_1p2.bin",
        "../flash/seq/st_n_1p1.bin",
        "../flash/seq/st_x_bas.bin",
        "../flash/seq/st_n_bas.bin",
        "../flash/seq/sm_x_2p2.bin",
        "../flash/seq/sm_x_2p1.bin",
        "../flash/seq/sm_x_1p1.bin",
        "../flash/seq/sm_n_2p2.bin",
        "../flash/seq/sm_n_2p1.bin",
        "../flash/seq/sm_n_1p2.bin",
        "../flash/seq/sm_n_1p1.bin",
        "../flash/seq/sm_x_bas.bin",
        "../flash/seq/sm_n_bas.bin",
        "../flash/seq/dd_z_2p2.bin",
        "../flash/seq/dd_z_2p1.bin",
        "../flash/seq/dd_z_1p1.bin",
        "../flash/seq/dd_x_2p2.bin",
        "../flash/seq/dd_x_2p1.bin",
        "../flash/seq/dd_x_1p1.bin",
        "../flash/seq/dd_e_2p2.bin",
        "../flash/seq/dd_e_2p1.bin",
        "../flash/seq/dd_e_1p2.bin",
        "../flash/seq/dd_e_1p1.bin",
        "../flash/seq/pd_z_2p2.bin",
        "../flash/seq/pd_z_2p1.bin",
        "../flash/seq/pd_z_1p1.bin",
        "../flash/seq/pd_x_2p2.bin",
        "../flash/seq/pd_x_2p1.bin",
        "../flash/seq/pd_x_1p1.bin",
        "../flash/seq/pd_e_2p2.bin",
        "../flash/seq/pd_e_2p1.bin",
        "../flash/seq/pd_e_1p2.bin",
        "../flash/seq/pd_e_1p1.bin",
        "../flash/seq/ee_z_2p2.bin",
        "../flash/seq/ee_z_2p1.bin",
        "../flash/seq/ee_z_1p1.bin",
        "../flash/seq/ee_x_2p2.bin",
        "../flash/seq/ee_x_2p1.bin",
        "../flash/seq/ee_x_1p1.bin",
        "../flash/seq/ee_e_2p2.bin",
        "../flash/seq/ee_e_2p1.bin",
        "../flash/seq/ee_e_1p2.bin",
        "../flash/seq/ee_e_1p1.bin",
        "../flash/seq/lf_z_2p2.bin",
        "../flash/seq/lf_z_2p1.bin",
        "../flash/seq/lf_z_1p1.bin",
        "../flash/seq/lf_x_2p2.bin",
        "../flash/seq/lf_x_2p1.bin",
        "../flash/seq/lf_x_1p1.bin",
        "../flash/seq/lf_n_2p2.bin",
        "../flash/seq/lf_n_2p1.bin",
        "../flash/seq/lf_n_1p2.bin",
        "../flash/seq/lf_n_1p1.bin",
        "../flash/seq/m3_z_2p2.bin",
        "../flash/seq/m3_z_2p1.bin",
        "../flash/seq/m3_z_1p1.bin",
        "../flash/seq/m3_x_2p2.bin",
        "../flash/seq/m3_x_2p1.bin",
        "../flash/seq/m3_x_1p1.bin",
        "../flash/seq/m3_n_2p2.bin",
        "../flash/seq/m3_n_2p1.bin",
        "../flash/seq/m3_n_1p2.bin",
        "../flash/seq/m3_n_1p1.bin",
        "../flash/seq/m2_z_2p2.bin",
        "../flash/seq/m2_z_2p1.bin",
        "../flash/seq/m2_z_1p1.bin",
        "../flash/seq/m2_x_2p2.bin",
        "../flash/seq/m2_x_2p1.bin",
        "../flash/seq/m2_x_1p1.bin",
        "../flash/seq/m2_n_2p2.bin",
        "../flash/seq/m2_n_2p1.bin",
        "../flash/seq/m2_n_1p2.bin",
        "../flash/seq/m2_n_1p1.bin",
        "../flash/seq/m1_z_2p2.bin",
        "../flash/seq/m1_z_2p1.bin",
        "../flash/seq/m1_z_1p1.bin",
        "../flash/seq/m1_x_2p2.bin",
        "../flash/seq/m1_x_2p1.bin",
        "../flash/seq/m1_x_1p1.bin",
        "../flash/seq/m1_n_2p2.bin",
        "../flash/seq/m1_n_2p1.bin",
        "../flash/seq/m1_n_1p2.bin",
        "../flash/seq/m1_n_1p1.bin",
        "../flash/seq/cs_z_2p2.bin",
        "../flash/seq/cs_z_2p1.bin",
        "../flash/seq/cs_z_1p1.bin",
        "../flash/seq/cs_x_2p2.bin",
        "../flash/seq/cs_x_2p1.bin",
        "../flash/seq/cs_x_1p1.bin",
        "../flash/seq/cs_e_2p2.bin",
        "../flash/seq/cs_e_2p1.bin",
        "../flash/seq/cs_e_1p1.bin",
        "../flash/seq/cs_n_2p2.bin",
        "../flash/seq/cs_n_2p1.bin",
        "../flash/seq/cs_n_1p2.bin",
        "../flash/seq/cs_n_1p1.bin",
        "../flash/seq/cs_x_bas.bin",
        "../flash/seq/cs_n_bas.bin",
        "../flash/seq/pp_z_2p2.bin",
        "../flash/seq/pp_z_2p1.bin",
        "../flash/seq/pp_z_1p1.bin",
        "../flash/seq/pp_x_2p2.bin",
        "../flash/seq/pp_x_2p1.bin",
        "../flash/seq/pp_x_1p1.bin",
        "../flash/seq/pp_e_2p2.bin",
        "../flash/seq/pp_e_2p1.bin",
        "../flash/seq/pp_e_1p1.bin",
        "../flash/seq/pp_n_2p2.bin",
        "../flash/seq/pp_n_2p1.bin",
        "../flash/seq/pp_n_1p2.bin",
        "../flash/seq/pp_n_1p1.bin",
        "../flash/seq/pp_x_bas.bin",
        "../flash/seq/pp_e_bas.bin",
        "../flash/seq/pp_n_bas.bin",
        "../flash/seq/pr_x_2p2.bin",
        "../flash/seq/pr_x_2p1.bin",
        "../flash/seq/pr_x_1p1.bin",
        "../flash/seq/pr_n_2p2.bin",
        "../flash/seq/pr_n_2p1.bin",
        "../flash/seq/pr_n_1p2.bin",
        "../flash/seq/pr_n_1p1.bin",
        "../flash/seq/pr_x_bas.bin",
        "../flash/seq/pr_n_bas.bin",
        "../flash/seq/bd_x_2p2.bin",
        "../flash/seq/bd_x_2p1.bin",
        "../flash/seq/bd_x_1p1.bin",
        "../flash/seq/bd_n_2p2.bin",
        "../flash/seq/bd_n_2p1.bin",
        "../flash/seq/bd_n_1p2.bin",
        "../flash/seq/bd_n_1p1.bin",
        "../flash/seq/bd_x_bas.bin",
        "../flash/seq/bd_n_bas.bin",
        "../flash/seq/bs_z_2p2.bin",
        "../flash/seq/bs_z_2p1.bin",
        "../flash/seq/bs_z_1p1.bin",
        "../flash/seq/bs_x_2p2.bin",
        "../flash/seq/bs_x_2p1.bin",
        "../flash/seq/bs_x_1p1.bin",
        "../flash/seq/bs_n_2p2.bin",
        "../flash/seq/bs_n_2p1.bin",
        "../flash/seq/bs_n_1p2.bin",
        "../flash/seq/bs_n_1p1.bin",
        "../flash/seq/bs_x_bas.bin",
        "../flash/seq/bs_n_bas.bin",
        "../flash/seq/sh_z_2p2.bin",
        "../flash/seq/sh_z_2p1.bin",
        "../flash/seq/sh_z_1p1.bin",
        "../flash/seq/sh_x_2p2.bin",
        "../flash/seq/sh_x_2p1.bin",
        "../flash/seq/sh_x_1p1.bin",
        "../flash/seq/sh_n_2p2.bin",
        "../flash/seq/sh_n_2p1.bin",
        "../flash/seq/sh_n_1p2.bin",
        "../flash/seq/sh_n_1p1.bin",
        "../flash/seq/sh_x_bas.bin",
        "../flash/seq/sh_n_bas.bin",
        "../flash/seq/uc_z_2p2.bin",
        "../flash/seq/uc_z_2p1.bin",
        "../flash/seq/uc_z_1p1.bin",
        "../flash/seq/uc_x_2p2.bin",
        "../flash/seq/uc_x_2p1.bin",
        "../flash/seq/uc_x_1p1.bin",
        "../flash/seq/uc_n_2p2.bin",
        "../flash/seq/uc_n_2p1.bin",
        "../flash/seq/uc_n_1p2.bin",
        "../flash/seq/uc_n_1p1.bin",
        "../flash/seq/lt_z_2p2.bin",
        "../flash/seq/lt_z_2p1.bin",
        "../flash/seq/lt_z_1p1.bin",
        "../flash/seq/lt_x_2p2.bin",
        "../flash/seq/lt_x_2p1.bin",
        "../flash/seq/lt_x_1p1.bin",
        "../flash/seq/lt_n_2p2.bin",
        "../flash/seq/lt_n_2p1.bin",
        "../flash/seq/lt_n_1p2.bin",
        "../flash/seq/lt_n_1p1.bin",
        "../flash/seq/ec_z_2p2.bin",
        "../flash/seq/ec_z_2p1.bin",
        "../flash/seq/ec_z_1p1.bin",
        "../flash/seq/ec_x_2p2.bin",
        "../flash/seq/ec_x_2p1.bin",
        "../flash/seq/ec_x_1p1.bin",
        "../flash/seq/ec_e_2p2.bin",
        "../flash/seq/ec_e_2p1.bin",
        "../flash/seq/ec_e_1p2.bin",
        "../flash/seq/ec_e_1p1.bin",
        "../flash/seq/ev_z_2p2.bin",
        "../flash/seq/ev_z_2p1.bin",
        "../flash/seq/ev_z_1p1.bin",
        "../flash/seq/ev_x_2p2.bin",
        "../flash/seq/ev_x_2p1.bin",
        "../flash/seq/ev_x_1p1.bin",
        "../flash/seq/ev_n_2p2.bin",
        "../flash/seq/ev_n_2p1.bin",
        "../flash/seq/ev_n_1p2.bin",
        "../flash/seq/ev_n_1p1.bin",
        "../flash/seq/mk_z_2p2.bin",
        "../flash/seq/mk_z_2p1.bin",
        "../flash/seq/mk_z_1p1.bin",
        "../flash/seq/mk_x_2p2.bin",
        "../flash/seq/mk_x_2p1.bin",
        "../flash/seq/mk_x_1p1.bin",
        "../flash/seq/mk_e_2p2.bin",
        "../flash/seq/mk_e_2p1.bin",
        "../flash/seq/mk_e_1p2.bin",
        "../flash/seq/mk_e_1p1.bin",
        "../flash/seq/c2_z_2p2.bin",
        "../flash/seq/c2_z_2p1.bin",
        "../flash/seq/c2_z_1p1.bin",
        "../flash/seq/c2_x_2p2.bin",
        "../flash/seq/c2_x_2p1.bin",
        "../flash/seq/c2_x_1p2.bin",
        "../flash/seq/c2_x_1p1.bin",
        "../flash/seq/c2_n_2p2.bin",
        "../flash/seq/c2_n_2p1.bin",
        "../flash/seq/c2_n_1p2.bin",
        "../flash/seq/c2_n_1p1.bin",
        "../flash/seq/c2_p_2p2.bin",
        "../flash/seq/c2_p_2p1.bin",
        "../flash/seq/c2_p_1p2.bin",
        "../flash/seq/c2_p_1p1.bin",
        "../flash/seq/mn_z_2p2.bin",
        "../flash/seq/mn_z_2p1.bin",
        "../flash/seq/mn_z_1p1.bin",
        "../flash/seq/mn_x_2p2.bin",
        "../flash/seq/mn_x_2p1.bin",
        "../flash/seq/mn_x_1p1.bin",
        "../flash/seq/mn_n_2p2.bin",
        "../flash/seq/mn_n_2p1.bin",
        "../flash/seq/mn_n_1p2.bin",
        "../flash/seq/mn_n_1p1.bin",
        "../flash/seq/kg_z_2p2.bin",
        "../flash/seq/kg_z_2p1.bin",
        "../flash/seq/kg_z_1p1.bin",
        "../flash/seq/kg_x_2p2.bin",
        "../flash/seq/kg_x_2p1.bin",
        "../flash/seq/kg_x_1p1.bin",
        "../flash/seq/kg_n_2p2.bin",
        "../flash/seq/kg_n_2p1.bin",
        "../flash/seq/kg_n_1p2.bin",
        "../flash/seq/kg_n_1p1.bin",
        "../flash/seq/sd_z_2p2.bin",
        "../flash/seq/sd_z_2p1.bin",
        "../flash/seq/sd_z_1p1.bin",
        "../flash/seq/sd_x_2p2.bin",
        "../flash/seq/sd_x_2p1.bin",
        "../flash/seq/sd_x_1p1.bin",
        "../flash/seq/sd_n_2p2.bin",
        "../flash/seq/sd_n_2p1.bin",
        "../flash/seq/sd_n_1p2.bin",
        "../flash/seq/sd_n_1p1.bin",
        "../flash/seq/sb_z_2p2.bin",
        "../flash/seq/sb_z_2p1.bin",
        "../flash/seq/sb_z_1p1.bin",
        "../flash/seq/sb_x_2p2.bin",
        "../flash/seq/sb_x_2p1.bin",
        "../flash/seq/sb_x_1p1.bin",
        "../flash/seq/sb_n_2p2.bin",
        "../flash/seq/sb_n_2p1.bin",
        "../flash/seq/sb_n_1p2.bin",
        "../flash/seq/sb_n_1p1.bin",
        "../flash/seq/rf_z_2p2.bin",
        "../flash/seq/rf_z_2p1.bin",
        "../flash/seq/rf_z_1p1.bin",
        "../flash/seq/rf_x_2p2.bin",
        "../flash/seq/rf_x_2p1.bin",
        "../flash/seq/rf_x_1p1.bin",
        "../flash/seq/rf_n_2p2.bin",
        "../flash/seq/rf_n_2p1.bin",
        "../flash/seq/rf_n_1p2.bin",
        "../flash/seq/rf_n_1p1.bin",
        "../flash/seq/th_z_2p2.bin",
        "../flash/seq/th_z_2p1.bin",
        "../flash/seq/th_z_1p1.bin",
        "../flash/seq/th_x_2p2.bin",
        "../flash/seq/th_x_2p1.bin",
        "../flash/seq/th_x_1p1.bin",
        "../flash/seq/th_n_2p2.bin",
        "../flash/seq/th_n_2p1.bin",
        "../flash/seq/th_n_1p2.bin",
        "../flash/seq/th_n_1p1.bin",
        "../flash/seq/jy_z_2p2.bin",
        "../flash/seq/jy_z_2p1.bin",
        "../flash/seq/jy_z_1p1.bin",
        "../flash/seq/jy_x_2p2.bin",
        "../flash/seq/jy_w_2p1.bin",
        "../flash/seq/jy_x_1p1.bin",
        "../flash/seq/jy_n_2p2.bin",
        "../flash/seq/jy_n_2p1.bin",
        "../flash/seq/jy_n_1p2.bin",
        "../flash/seq/jy_n_1p1.bin",
        "../flash/seq/sk_z_2p2.bin",
        "../flash/seq/sk_z_2p1.bin",
        "../flash/seq/sk_z_1p1.bin",
        "../flash/seq/sk_x_2p2.bin",
        "../flash/seq/sk_x_2p1.bin",
        "../flash/seq/sk_x_1p1.bin",
        "../flash/seq/sk_n_2p2.bin",
        "../flash/seq/sk_n_2p1.bin",
        "../flash/seq/sk_n_1p2.bin",
        "../flash/seq/sk_n_1p1.bin",
        "../flash/seq/hv_z_2p2.bin",
        "../flash/seq/hv_z_2p1.bin",
        "../flash/seq/hv_z_1p1.bin",
        "../flash/seq/hv_x_2p2.bin",
        "../flash/seq/hv_x_2p1.bin",
        "../flash/seq/hv_x_1p1.bin",
        "../flash/seq/hv_n_2p2.bin",
        "../flash/seq/hv_n_2p1.bin",
        "../flash/seq/hv_n_1p2.bin",
        "../flash/seq/hv_n_1p1.bin",
        "../flash/seq/pw_z_2p2.bin",
        "../flash/seq/pw_z_2p1.bin",
        "../flash/seq/pw_z_1p1.bin",
        "../flash/seq/pw_x_2p2.bin",
        "../flash/seq/pw_x_2p1.bin",
        "../flash/seq/pw_x_1p1.bin",
        "../flash/seq/pw_n_2p2.bin",
        "../flash/seq/pw_n_2p1.bin",
        "../flash/seq/pw_n_1p2.bin",
        "../flash/seq/pw_n_1p1.bin",
        "../flash/seq/ni_z_2p2.bin",
        "../flash/seq/ni_z_2p1.bin",
        "../flash/seq/ni_z_1p1.bin",
        "../flash/seq/ni_x_2p2.bin",
        "../flash/seq/ni_x_2p1.bin",
        "../flash/seq/ni_x_1p1.bin",
        "../flash/seq/ni_n_2p2.bin",
        "../flash/seq/ni_n_2p1.bin",
        "../flash/seq/ni_n_1p2.bin",
        "../flash/seq/ni_n_1p1.bin",
        "../flash/seq/hd_z_2p2.bin",
        "../flash/seq/hd_z_2p1.bin",
        "../flash/seq/hd_z_1p1.bin",
        "../flash/seq/hd_x_2p2.bin",
        "../flash/seq/hd_x_2p1.bin",
        "../flash/seq/hd_x_1p1.bin",
        "../flash/seq/hd_n_2p2.bin",
        "../flash/seq/hd_n_2p1.bin",
        "../flash/seq/hd_n_1p2.bin",
        "../flash/seq/hd_n_1p1.bin",
        "../flash/seq/mg_z_2p2.bin",
        "../flash/seq/mg_z_2p1.bin",
        "../flash/seq/mg_z_1p1.bin",
        "../flash/seq/mg_x_2p2.bin",
        "../flash/seq/mg_x_2p1.bin",
        "../flash/seq/mg_x_1p1.bin",
        "../flash/seq/mg_e_2p2.bin",
        "../flash/seq/mg_e_2p1.bin",
        "../flash/seq/mg_e_1p2.bin",
        "../flash/seq/mg_e_1p1.bin",
        "../flash/seq/mg_n_2p2.bin",
        "../flash/seq/mg_n_2p1.bin",
        "../flash/seq/mg_n_1p2.bin",
        "../flash/seq/mg_n_1p1.bin",
        "../flash/seq/adsx_2p2.bin",
        "../flash/seq/adsx_2p1.bin",
        "../flash/seq/adsx_1p1.bin",
        "../flash/seq/adse_2p2.bin",
        "../flash/seq/adse_2p1.bin",
        "../flash/seq/adse_1p2.bin",
        "../flash/seq/adse_1p1.bin",
        "../flash/seq/ad_z_2p2.bin",
        "../flash/seq/ad_z_2p1.bin",
        "../flash/seq/ad_z_1p1.bin",
        "../flash/seq/ad_x_2p2.bin",
        "../flash/seq/ad_x_2p1.bin",
        "../flash/seq/ad_x_1p1.bin",
        "../flash/seq/ad_e_2p2.bin",
        "../flash/seq/ad_e_2p1.bin",
        "../flash/seq/ad_e_1p2.bin",
        "../flash/seq/ad_e_1p1.bin",
        "../flash/seq/ad_n_2p2.bin",
        "../flash/seq/ad_n_2p1.bin",
        "../flash/seq/ad_n_1p2.bin",
        "../flash/seq/ad_n_1p1.bin",
        "../flash/seq/ctsx_2p2.bin",
        "../flash/seq/ctsx_2p1.bin",
        "../flash/seq/ctsx_1p1.bin",
        "../flash/seq/ctse_2p2.bin",
        "../flash/seq/ctse_2p1.bin",
        "../flash/seq/ctse_1p2.bin",
        "../flash/seq/ctse_1p1.bin",
        "../flash/seq/ct_z_2p2.bin",
        "../flash/seq/ct_z_2p1.bin",
        "../flash/seq/ct_w_1p1.bin",
        "../flash/seq/ct_x_2p2.bin",
        "../flash/seq/ct_x_2p1.bin",
        "../flash/seq/ct_x_1p1.bin",
        "../flash/seq/ct_e_2p2.bin",
        "../flash/seq/ct_e_2p1.bin",
        "../flash/seq/ct_e_1p2.bin",
        "../flash/seq/ct_e_1p1.bin",
        "../flash/seq/ct_n_2p2.bin",
        "../flash/seq/ct_n_2p1.bin",
        "../flash/seq/ct_n_1p2.bin",
        "../flash/seq/ct_n_1p1.bin",
        "../flash/seq/mm_z_2p2.bin",
        "../flash/seq/mm_z_2p1.bin",
        "../flash/seq/mm_z_1p1.bin",
        "../flash/seq/mm_x_2p2.bin",
        "../flash/seq/mm_x_2p1.bin",
        "../flash/seq/mm_x_1p1.bin",
        "../flash/seq/mm_n_2p2.bin",
        "../flash/seq/mm_n_2p1.bin",
        "../flash/seq/mm_n_1p2.bin",
        "../flash/seq/mm_n_1p1.bin",
        "../flash/seq/ed_z_2p2.bin",
        "../flash/seq/ed_z_2p1.bin",
        "../flash/seq/ed_z_1p1.bin",
        "../flash/seq/ed_x_2p2.bin",
        "../flash/seq/ed_x_2p1.bin",
        "../flash/seq/ed_x_1p1.bin",
        "../flash/seq/ed_n_2p2.bin",
        "../flash/seq/ed_n_2p1.bin",
        "../flash/seq/ed_n_1p2.bin",
        "../flash/seq/ed_n_1p1.bin",
        "../flash/seq/vt_z_2p2.bin",
        "../flash/seq/vt_z_2p1.bin",
        "../flash/seq/vt_z_1p1.bin",
        "../flash/seq/vt_x_2p2.bin",
        "../flash/seq/vt_x_2p1.bin",
        "../flash/seq/vt_x_1p1.bin",
        "../flash/seq/vt_w_2p2.bin",
        "../flash/seq/vt_n_2p1.bin",
        "../flash/seq/vt_n_1p2.bin",
        "../flash/seq/vt_n_1p1.bin",
        "../flash/seq/td_z_2p2.bin",
        "../flash/seq/td_z_2p1.bin",
        "../flash/seq/td_z_1p1.bin",
        "../flash/seq/td_x_2p2.bin",
        "../flash/seq/td_x_2p1.bin",
        "../flash/seq/td_x_1p1.bin",
        "../flash/seq/td_e_2p2.bin",
        "../flash/seq/td_e_2p1.bin",
        "../flash/seq/td_e_1p2.bin",
        "../flash/seq/td_e_1p1.bin",
        "../flash/seq/td_n_2p2.bin",
        "../flash/seq/td_n_2p1.bin",
        "../flash/seq/td_n_1p2.bin",
        "../flash/seq/td_n_1p1.bin",
        "../flash/seq/mt_z_2p2.bin",
        "../flash/seq/mt_z_2p1.bin",
        "../flash/seq/mt_z_1p1.bin",
        "../flash/seq/mt_x_2p2.bin",
        "../flash/seq/mt_x_2p1.bin",
        "../flash/seq/mt_x_1p1.bin",
        "../flash/seq/mt_n_2p2.bin",
        "../flash/seq/mt_n_2p1.bin",
        "../flash/seq/mt_n_1p2.bin",
        "../flash/seq/mt_n_1p1.bin",
        "../flash/seq/mt_p_2p2.bin",
        "../flash/seq/mt_p_2p1.bin",
        "../flash/seq/mt_p_1p2.bin",
        "../flash/seq/mt_p_1p1.bin",
        "../flash/seq/jz_z_2p2.bin",
        "../flash/seq/jz_z_2p1.bin",
        "../flash/seq/jz_z_1p1.bin",
        "../flash/seq/jz_x_2p2.bin",
        "../flash/seq/jz_x_2p1.bin",
        "../flash/seq/jz_x_1p1.bin",
        "../flash/seq/jz_e_2p2.bin",
        "../flash/seq/jz_e_2p1.bin",
        "../flash/seq/jz_e_1p2.bin",
        "../flash/seq/jz_e_1p1.bin",
        "../flash/seq/hr_z_2p2.bin",
        "../flash/seq/hr_z_2p1.bin",
        "../flash/seq/hr_z_1p1.bin",
        "../flash/seq/hr_x_2p2.bin",
        "../flash/seq/hr_x_2p1.bin",
        "../flash/seq/hr_x_1p1.bin",
        "../flash/seq/hr_e_2p2.bin",
        "../flash/seq/hr_e_2p1.bin",
        "../flash/seq/hr_e_1p2.bin",
        "../flash/seq/hr_e_1p1.bin",
        "../flash/seq/hm_z_2p2.bin",
        "../flash/seq/hm_z_2p1.bin",
        "../flash/seq/hm_z_1p1.bin",
        "../flash/seq/hm_x_2p2.bin",
        "../flash/seq/hm_x_2p1.bin",
        "../flash/seq/hm_x_1p1.bin",
        "../flash/seq/hm_e_2p2.bin",
        "../flash/seq/hm_e_2p1.bin",
        "../flash/seq/hm_e_1p2.bin",
        "../flash/seq/hm_e_1p1.bin",
        "../flash/seq/fs_z_2p2.bin",
        "../flash/seq/fs_w_2p1.bin",
        "../flash/seq/fs_z_1p1.bin",
        "../flash/seq/fs_x_2p2.bin",
        "../flash/seq/fs_x_2p1.bin",
        "../flash/seq/fs_x_1p1.bin",
        "../flash/seq/fs_e_2p2.bin",
        "../flash/seq/fs_e_2p1.bin",
        "../flash/seq/fs_e_1p2.bin",
        "../flash/seq/fs_e_1p1.bin",
        "../flash/seq/fk_z_2p2.bin",
        "../flash/seq/fk_z_2p1.bin",
        "../flash/seq/fk_z_1p1.bin",
        "../flash/seq/fk_x_2p2.bin",
        "../flash/seq/fk_x_2p1.bin",
        "../flash/seq/fk_x_1p1.bin",
        "../flash/seq/fk_n_2p2.bin",
        "../flash/seq/fk_n_2p1.bin",
        "../flash/seq/fk_n_1p2.bin",
        "../flash/seq/fk_n_1p1.bin",
        "../flash/seq/fr_z_2p2.bin",
        "../flash/seq/fr_z_2p1.bin",
        "../flash/seq/fr_z_1p1.bin",
        "../flash/seq/fr_x_2p2.bin",
        "../flash/seq/fr_x_2p1.bin",
        "../flash/seq/fr_x_1p1.bin",
        "../flash/seq/fr_n_2p2.bin",
        "../flash/seq/fr_n_2p1.bin",
        "../flash/seq/fr_n_1p2.bin",
        "../flash/seq/fr_n_1p1.bin",
        "../flash/seq/drsx_2p2.bin",
        "../flash/seq/drsx_2p1.bin",
        "../flash/seq/drsx_1p1.bin",
        "../flash/seq/drse_2p2.bin",
        "../flash/seq/drse_2p1.bin",
        "../flash/seq/drse_1p2.bin",
        "../flash/seq/drse_1p1.bin",
        "../flash/seq/dr_z_2p2.bin",
        "../flash/seq/dr_z_2p1.bin",
        "../flash/seq/dr_z_1p1.bin",
        "../flash/seq/dr_x_2p2.bin",
        "../flash/seq/dr_x_2p1.bin",
        "../flash/seq/dr_x_1p1.bin",
        "../flash/seq/dr_e_2p2.bin",
        "../flash/seq/dr_e_2p1.bin",
        "../flash/seq/dr_e_1p2.bin",
        "../flash/seq/dr_e_1p1.bin",
        "../flash/seq/dr_n_2p2.bin",
        "../flash/seq/dr_n_2p1.bin",
        "../flash/seq/dr_n_1p2.bin",
        "../flash/seq/dr_n_1p1.bin",
        "../flash/seq/bl_z_2p2.bin",
        "../flash/seq/bl_z_2p1.bin",
        "../flash/seq/bl_z_1p1.bin",
        "../flash/seq/bl_x_2p2.bin",
        "../flash/seq/bl_x_2p1.bin",
        "../flash/seq/bl_x_1p1.bin",
        "../flash/seq/bl_n_2p2.bin",
        "../flash/seq/bl_n_2p1.bin",
        "../flash/seq/bl_n_1p2.bin",
        "../flash/seq/bl_n_1p1.bin",
        "../flash/tp/longla.tpb",
        "../flash/tp/longjet.tpb",
        "../flash/tp/longfire.tpb",
        "../flash/tp/1169.tpb",
        "../flash/tp/mmedley.tpb",
        "../flash/tp/pmedley.tpb",
        "../flash/tp/ddr.tpb",
        "../flash/tp/pdunk.tpb",
        "../flash/tp/eraser.tpb",
        "../flash/tp/spin.tpb",
        "../flash/tp/midnight.tpb",
        "../flash/tp/bump.tpb",
        "../flash/tp/break.tpb",
        "../flash/tp/help.tpb",
        "../flash/tp/onaway.tpb",
        "../flash/tp/sakurai.tpb",
        "../flash/tp/classic.tpb",
        "../flash/tp/cosmic.tpb",
        "../flash/tp/bossa.tpb",
        "../flash/tp/hand.tpb",
        "../flash/tp/cutie3.tpb",
        "../flash/tp/ppr.tpb",
        "../flash/tp/shadow.tpb",
        "../flash/tp/diana.tpb",
        "../flash/tp/jim.tpb",
        "../flash/tp/zeppeli.tpb",
        "../flash/tp/layla.tpb",
        "../flash/tp/moveover.tpb",
        "../flash/tp/still.tpb",
        "../flash/tp/deep.tpb",
        "../flash/tp/getit.tpb",
        "../flash/tp/highway.tpb",
        "../flash/tp/johnny.tpb",
        "../flash/tp/prim.tpb",
        "../flash/tp/car.tpb",
        "../flash/tp/eclipse.tpb",
        "../flash/tp/micky.tpb",
        "../flash/tp/evil.tpb",
        "../flash/tp/cutie2.tpb",
        "../flash/tp/hmetal2.tpb",
        "../flash/tp/king.tpb",
        "../flash/tp/punk2.tpb",
        "../flash/tp/flamenco.tpb",
        "../flash/tp/rockf.tpb",
        "../flash/tp/think.tpb",
        "../flash/tp/heaven2.tpb",
        "../flash/tp/power.tpb",
        "../flash/tp/night.tpb",
        "../flash/tp/skaska.tpb",
        "../flash/tp/joey.tpb",
        "../flash/tp/holiday.tpb",
        "../flash/tp/magic.tpb",
        "../flash/tp/advent.tpb",
        "../flash/tp/country.tpb",
        "../flash/tp/machine.tpb",
        "../flash/tp/ending.tpb",
        "../flash/tp/ventures.tpb",
        "../flash/tp/riff.tpb",
        "../flash/tp/jazz.tpb",
        "../flash/tp/fusion.tpb",
        "../flash/tp/degirock.tpb",
        "../flash/tp/toydolls.tpb",
        "../flash/tp/nrock.tpb",
        "../flash/tp/hrock.tpb",
        "../flash/tp/funk.tpb",
        "../flash/tp/select.tpb",
        "../flash/tp/mtown.tpb",
        "../flash/tp/hmetal.tpb",
        "../flash/tp/demo.tpb",
        "../flash/tp/blues.tpb",
        "../flash/tp/common.tpb",
        "../flash/demodata/demo42.bin",
        "../flash/demodata/demo41.bin",
        "../flash/demodata/demo32.bin",
        "../flash/demodata/demo31.bin",
        "../flash/demodata/demo22.bin",
        "../flash/demodata/demo21.bin",
        "../flash/demodata/demo12.bin",
        "../flash/demodata/demo11.bin",
        "../flash/lamp/lalong1.bin",
        "../flash/lamp/jtln1.bin",
        "../flash/lamp/lfire1.bin",
        "../flash/lamp/nmedley1.bin",
        "../flash/lamp/mmedley1.bin",
        "../flash/lamp/pmedley1.bin",
        "../flash/lamp/love1.bin",
        "../flash/lamp/pdunk1.bin",
        "../flash/lamp/erase1.bin",
        "../flash/lamp/stop1.bin",
        "../flash/lamp/mid1.bin",
        "../flash/lamp/bump1.bin",
        "../flash/lamp/bout1.bin",
        "../flash/lamp/help1.bin",
        "../flash/lamp/onaway1.bin",
        "../flash/lamp/close1.bin",
        "../flash/lamp/cls1.bin",
        "../flash/lamp/ccg1.bin",
        "../flash/lamp/bs1.bin",
        "../flash/lamp/hand1.bin",
        "../flash/lamp/cutie31.bin",
        "../flash/lamp/ppr1.bin",
        "../flash/lamp/shadow1.bin",
        "../flash/lamp/harry1.bin",
        "../flash/lamp/move1.bin",
        "../flash/lamp/still1.bin",
        "../flash/lamp/smoke1.bin",
        "../flash/lamp/getit1.bin",
        "../flash/lamp/highway1.bin",
        "../flash/lamp/johney1.bin",
        "../flash/lamp/prim1.bin",
        "../flash/lamp/car1.bin",
        "../flash/lamp/eclipse1.bin",
        "../flash/lamp/micky1.bin",
        "../flash/lamp/evil1.bin",
        "../flash/lamp/cutie21.bin",
        "../flash/lamp/hmetal21.bin",
        "../flash/lamp/rock21.bin",
        "../flash/lamp/punk21.bin",
        "../flash/lamp/flam1.bin",
        "../flash/lamp/rockf1.bin",
        "../flash/lamp/think1.bin",
        "../flash/lamp/heaven1.bin",
        "../flash/lamp/power1.bin",
        "../flash/lamp/night1.bin",
        "../flash/lamp/skaska1.bin",
        "../flash/lamp/joey1.bin",
        "../flash/lamp/holiday1.bin",
        "../flash/lamp/magic1.bin",
        "../flash/lamp/adven1.bin",
        "../flash/lamp/country1.bin",
        "../flash/lamp/machine1.bin",
        "../flash/lamp/ending1.bin",
        "../flash/lamp/fire1.bin",
        "../flash/lamp/riffs3.bin",
        "../flash/lamp/rifft3.bin",
        "../flash/lamp/riffs2.bin",
        "../flash/lamp/rifft2.bin",
        "../flash/lamp/riffs1.bin",
        "../flash/lamp/rifft1.bin",
        "../flash/lamp/mdemo1.bin",
        "../flash/lamp/digi1.bin",
        "../flash/lamp/jazz21.bin",
        "../flash/lamp/hmetal1.bin",
        "../flash/lamp/hrock1.bin",
        "../flash/lamp/fusion1.bin",
        "../flash/lamp/vent1.bin",
        "../flash/lamp/funk1.bin",
        "../flash/lamp/blues1.bin",
        "../flash/lamp/tdoll1.bin",
        "../flash/lamp/mtown1.bin",
        "../flash/anime/rmgn0b.bin",
        "../flash/anime/rmgn0a.bin",
        "../flash/anime/rmbn1b.bin",
        "../flash/anime/rmbn1a.bin",
        "../flash/anime/rmnpic2b.bin",
        "../flash/anime/rmnpic2a.bin",
        "../flash/anime/rmnpic1b.bin",
        "../flash/anime/rmnpic1a.bin",
        "../flash/anime/rmnpic0b.bin",
        "../flash/anime/rmnpic0a.bin",
        "../flash/anime/rmwel0b.bin",
        "../flash/anime/rmwel0a.bin",
        "../flash/anime/rmvct1b.bin",
        "../flash/anime/rmvct1a.bin",
        "../flash/anime/rmvct0b.bin",
        "../flash/anime/rmvct0a.bin",
        "../flash/anime/rmpic1b.bin",
        "../flash/anime/rmpic1a.bin",
        "../flash/anime/rmpic0b.bin",
        "../flash/anime/rmpic0a.bin",
        "../flash/anime/rmok0b.bin",
        "../flash/anime/rmok0a.bin",
        "../flash/anime/rmnu2b.bin",
        "../flash/anime/rmnu2a.bin",
        "../flash/anime/rmnu1b.bin",
        "../flash/anime/rmnu1a.bin",
        "../flash/anime/rmnu0b.bin",
        "../flash/anime/rmnu0a.bin",
        "../flash/anime/rmbn0b.bin",
        "../flash/anime/rmbn0a.bin",
        "../flash/anime/rmbc0b.bin",
        "../flash/anime/rmbc0a.bin",
        "../flash/anime/rmbad0b1.bin",
        "../flash/anime/rmbad0a.bin",
        "../flash/anime/rt_sl0.bin",
        "../flash/anime/rt_pk0.bin",
        "../flash/anime/lt_sl0.bin",
        "../flash/anime/lt_pk0.bin",
        "../flash/anime/lov_1.bin",
        "../flash/anime/f_cam2.bin",
        "../flash/anime/f6.bin",
        "../flash/anime/ct_sl0.bin",
        "../flash/anime/ct_pk0.bin",
        "../flash/anime/hwall.bin",

        "../flash/stbl/stbl.bin",
        "../flash/tp/dlangsp.tpb",
        "../flash/tp/dlangit.tpb",
        "../flash/tp/dlangge.tpb",
        "../flash/tp/dlangfr.tpb",
        "../flash/tp/dlangen.tpb",
        "../flash/tp/dlangjp.tpb",
        "../flash/tp/demopic.tpb",
        "../flash/seq/p_riff3.bin",
        "../flash/seq/p_riff2.bin",
        "../flash/seq/p_riff1.bin",
        "../flash/seq/c2_z_2p2.bin",
        "../flash/seq/c2_z_2p1.bin",
        "../flash/seq/c2_z_1p1.bin",
        "../flash/seq/c2_x_2p2.bin",
        "../flash/seq/c2_x_2p1.bin",
        "../flash/seq/c2_x_1p2.bin",
        "../flash/seq/c2_x_1p1.bin",
        "../flash/seq/c2_n_2p2.bin",
        "../flash/seq/c2_n_2p1.bin",
        "../flash/seq/c2_n_1p2.bin",
        "../flash/seq/c2_n_1p1.bin",
        "../flash/seq/c2_p_2p2.bin",
        "../flash/seq/c2_p_2p1.bin",
        "../flash/seq/c2_p_1p2.bin",
        "../flash/seq/c2_p_1p1.bin",
        "../flash/seq/mn_z_2p2.bin",
        "../flash/seq/mn_z_2p1.bin",
        "../flash/seq/mn_z_1p1.bin",
        "../flash/seq/mn_x_2p2.bin",
        "../flash/seq/mn_x_2p1.bin",
        "../flash/seq/mn_x_1p1.bin",
        "../flash/seq/mn_n_2p2.bin",
        "../flash/seq/mn_n_2p1.bin",
        "../flash/seq/mn_n_1p2.bin",
        "../flash/seq/mn_n_1p1.bin",
        "../flash/seq/kg_z_2p2.bin",
        "../flash/seq/kg_z_2p1.bin",
        "../flash/seq/kg_z_1p1.bin",
        "../flash/seq/kg_x_2p2.bin",
        "../flash/seq/kg_x_2p1.bin",
        "../flash/seq/kg_x_1p1.bin",
        "../flash/seq/kg_n_2p2.bin",
        "../flash/seq/kg_n_2p1.bin",
        "../flash/seq/kg_n_1p2.bin",
        "../flash/seq/kg_n_1p1.bin",
        "../flash/seq/sd_z_2p2.bin",
        "../flash/seq/sd_z_2p1.bin",
        "../flash/seq/sd_z_1p1.bin",
        "../flash/seq/sd_x_2p2.bin",
        "../flash/seq/sd_x_2p1.bin",
        "../flash/seq/sd_x_1p1.bin",
        "../flash/seq/sd_n_2p2.bin",
        "../flash/seq/sd_n_2p1.bin",
        "../flash/seq/sd_n_1p2.bin",
        "../flash/seq/sd_n_1p1.bin",
        "../flash/seq/sb_z_2p2.bin",
        "../flash/seq/sb_z_2p1.bin",
        "../flash/seq/sb_z_1p1.bin",
        "../flash/seq/sb_x_2p2.bin",
        "../flash/seq/sb_x_2p1.bin",
        "../flash/seq/sb_x_1p1.bin",
        "../flash/seq/sb_n_2p2.bin",
        "../flash/seq/sb_n_2p1.bin",
        "../flash/seq/sb_n_1p2.bin",
        "../flash/seq/sb_n_1p1.bin",
        "../flash/seq/rf_z_2p2.bin",
        "../flash/seq/rf_z_2p1.bin",
        "../flash/seq/rf_z_1p1.bin",
        "../flash/seq/rf_x_2p2.bin",
        "../flash/seq/rf_x_2p1.bin",
        "../flash/seq/rf_x_1p1.bin",
        "../flash/seq/rf_n_2p2.bin",
        "../flash/seq/rf_n_2p1.bin",
        "../flash/seq/rf_n_1p2.bin",
        "../flash/seq/rf_n_1p1.bin",
        "../flash/seq/th_z_2p2.bin",
        "../flash/seq/th_z_2p1.bin",
        "../flash/seq/th_z_1p1.bin",
        "../flash/seq/th_x_2p2.bin",
        "../flash/seq/th_x_2p1.bin",
        "../flash/seq/th_x_1p1.bin",
        "../flash/seq/th_n_2p2.bin",
        "../flash/seq/th_n_2p1.bin",
        "../flash/seq/th_n_1p2.bin",
        "../flash/seq/th_n_1p1.bin",
        "../flash/seq/jy_z_2p2.bin",
        "../flash/seq/jy_z_2p1.bin",
        "../flash/seq/jy_z_1p1.bin",
        "../flash/seq/jy_x_2p2.bin",
        "../flash/seq/jy_w_2p1.bin",
        "../flash/seq/jy_x_1p1.bin",
        "../flash/seq/jy_n_2p2.bin",
        "../flash/seq/jy_n_2p1.bin",
        "../flash/seq/jy_n_1p2.bin",
        "../flash/seq/jy_n_1p1.bin",
        "../flash/seq/sk_z_2p2.bin",
        "../flash/seq/sk_z_2p1.bin",
        "../flash/seq/sk_z_1p1.bin",
        "../flash/seq/sk_x_2p2.bin",
        "../flash/seq/sk_x_2p1.bin",
        "../flash/seq/sk_x_1p1.bin",
        "../flash/seq/sk_n_2p2.bin",
        "../flash/seq/sk_n_2p1.bin",
        "../flash/seq/sk_n_1p2.bin",
        "../flash/seq/sk_n_1p1.bin",
        "../flash/seq/hv_z_2p2.bin",
        "../flash/seq/hv_z_2p1.bin",
        "../flash/seq/hv_z_1p1.bin",
        "../flash/seq/hv_x_2p2.bin",
        "../flash/seq/hv_x_2p1.bin",
        "../flash/seq/hv_x_1p1.bin",
        "../flash/seq/hv_n_2p2.bin",
        "../flash/seq/hv_n_2p1.bin",
        "../flash/seq/hv_n_1p2.bin",
        "../flash/seq/hv_n_1p1.bin",
        "../flash/seq/pw_z_2p2.bin",
        "../flash/seq/pw_z_2p1.bin",
        "../flash/seq/pw_z_1p1.bin",
        "../flash/seq/pw_x_2p2.bin",
        "../flash/seq/pw_x_2p1.bin",
        "../flash/seq/pw_x_1p1.bin",
        "../flash/seq/pw_n_2p2.bin",
        "../flash/seq/pw_n_2p1.bin",
        "../flash/seq/pw_n_1p2.bin",
        "../flash/seq/pw_n_1p1.bin",
        "../flash/seq/ni_z_2p2.bin",
        "../flash/seq/ni_z_2p1.bin",
        "../flash/seq/ni_z_1p1.bin",
        "../flash/seq/ni_x_2p2.bin",
        "../flash/seq/ni_x_2p1.bin",
        "../flash/seq/ni_x_1p1.bin",
        "../flash/seq/ni_n_2p2.bin",
        "../flash/seq/ni_n_2p1.bin",
        "../flash/seq/ni_n_1p2.bin",
        "../flash/seq/ni_n_1p1.bin",
        "../flash/seq/hd_z_2p2.bin",
        "../flash/seq/hd_z_2p1.bin",
        "../flash/seq/hd_z_1p1.bin",
        "../flash/seq/hd_x_2p2.bin",
        "../flash/seq/hd_x_2p1.bin",
        "../flash/seq/hd_x_1p1.bin",
        "../flash/seq/hd_n_2p2.bin",
        "../flash/seq/hd_n_2p1.bin",
        "../flash/seq/hd_n_1p2.bin",
        "../flash/seq/hd_n_1p1.bin",
        "../flash/seq/mg_z_2p2.bin",
        "../flash/seq/mg_z_2p1.bin",
        "../flash/seq/mg_z_1p1.bin",
        "../flash/seq/mg_x_2p2.bin",
        "../flash/seq/mg_x_2p1.bin",
        "../flash/seq/mg_x_1p1.bin",
        "../flash/seq/mg_e_2p2.bin",
        "../flash/seq/mg_e_2p1.bin",
        "../flash/seq/mg_e_1p2.bin",
        "../flash/seq/mg_e_1p1.bin",
        "../flash/seq/mg_n_2p2.bin",
        "../flash/seq/mg_n_2p1.bin",
        "../flash/seq/mg_n_1p2.bin",
        "../flash/seq/mg_n_1p1.bin",
        "../flash/seq/ad_z_2p2.bin",
        "../flash/seq/ad_z_2p1.bin",
        "../flash/seq/ad_z_1p1.bin",
        "../flash/seq/ad_x_2p2.bin",
        "../flash/seq/ad_x_2p1.bin",
        "../flash/seq/ad_x_1p1.bin",
        "../flash/seq/ad_e_2p2.bin",
        "../flash/seq/ad_e_2p1.bin",
        "../flash/seq/ad_e_1p2.bin",
        "../flash/seq/ad_e_1p1.bin",
        "../flash/seq/ad_n_2p2.bin",
        "../flash/seq/ad_n_2p1.bin",
        "../flash/seq/ad_n_1p2.bin",
        "../flash/seq/ad_n_1p1.bin",
        "../flash/seq/ct_z_2p2.bin",
        "../flash/seq/ct_z_2p1.bin",
        "../flash/seq/ct_w_1p1.bin",
        "../flash/seq/ct_x_2p2.bin",
        "../flash/seq/ct_x_2p1.bin",
        "../flash/seq/ct_x_1p1.bin",
        "../flash/seq/ct_e_2p2.bin",
        "../flash/seq/ct_e_2p1.bin",
        "../flash/seq/ct_e_1p2.bin",
        "../flash/seq/ct_e_1p1.bin",
        "../flash/seq/ct_n_2p2.bin",
        "../flash/seq/ct_n_2p1.bin",
        "../flash/seq/ct_n_1p2.bin",
        "../flash/seq/ct_n_1p1.bin",
        "../flash/seq/mm_z_2p2.bin",
        "../flash/seq/mm_z_2p1.bin",
        "../flash/seq/mm_z_1p1.bin",
        "../flash/seq/mm_x_2p2.bin",
        "../flash/seq/mm_x_2p1.bin",
        "../flash/seq/mm_x_1p1.bin",
        "../flash/seq/mm_n_2p2.bin",
        "../flash/seq/mm_n_2p1.bin",
        "../flash/seq/mm_n_1p2.bin",
        "../flash/seq/mm_n_1p1.bin",
        "../flash/seq/ed_z_2p2.bin",
        "../flash/seq/ed_z_2p1.bin",
        "../flash/seq/ed_z_1p1.bin",
        "../flash/seq/ed_x_2p2.bin",
        "../flash/seq/ed_x_2p1.bin",
        "../flash/seq/ed_x_1p1.bin",
        "../flash/seq/ed_n_2p2.bin",
        "../flash/seq/ed_n_2p1.bin",
        "../flash/seq/ed_n_1p2.bin",
        "../flash/seq/ed_n_1p1.bin",
        "../flash/seq/vt_z_2p2.bin",
        "../flash/seq/vt_z_2p1.bin",
        "../flash/seq/vt_z_1p1.bin",
        "../flash/seq/vt_x_2p2.bin",
        "../flash/seq/vt_x_2p1.bin",
        "../flash/seq/vt_x_1p1.bin",
        "../flash/seq/vt_w_2p2.bin",
        "../flash/seq/vt_n_2p1.bin",
        "../flash/seq/vt_n_1p2.bin",
        "../flash/seq/vt_n_1p1.bin",
        "../flash/seq/td_z_2p2.bin",
        "../flash/seq/td_z_2p1.bin",
        "../flash/seq/td_z_1p1.bin",
        "../flash/seq/td_x_2p2.bin",
        "../flash/seq/td_x_2p1.bin",
        "../flash/seq/td_x_1p1.bin",
        "../flash/seq/td_e_2p2.bin",
        "../flash/seq/td_e_2p1.bin",
        "../flash/seq/td_e_1p2.bin",
        "../flash/seq/td_e_1p1.bin",
        "../flash/seq/td_n_2p2.bin",
        "../flash/seq/td_n_2p1.bin",
        "../flash/seq/td_n_1p2.bin",
        "../flash/seq/td_n_1p1.bin",
        "../flash/seq/mt_z_2p2.bin",
        "../flash/seq/mt_z_2p1.bin",
        "../flash/seq/mt_z_1p1.bin",
        "../flash/seq/mt_x_2p2.bin",
        "../flash/seq/mt_x_2p1.bin",
        "../flash/seq/mt_x_1p1.bin",
        "../flash/seq/mt_n_2p2.bin",
        "../flash/seq/mt_n_2p1.bin",
        "../flash/seq/mt_n_1p2.bin",
        "../flash/seq/mt_n_1p1.bin",
        "../flash/seq/jz_z_2p2.bin",
        "../flash/seq/jz_z_2p1.bin",
        "../flash/seq/jz_z_1p1.bin",
        "../flash/seq/jz_x_2p2.bin",
        "../flash/seq/jz_x_2p1.bin",
        "../flash/seq/jz_x_1p1.bin",
        "../flash/seq/jz_e_2p2.bin",
        "../flash/seq/jz_e_2p1.bin",
        "../flash/seq/jz_e_1p2.bin",
        "../flash/seq/jz_e_1p1.bin",
        "../flash/seq/hr_z_2p2.bin",
        "../flash/seq/hr_z_2p1.bin",
        "../flash/seq/hr_z_1p1.bin",
        "../flash/seq/hr_x_2p2.bin",
        "../flash/seq/hr_x_2p1.bin",
        "../flash/seq/hr_x_1p1.bin",
        "../flash/seq/hr_e_2p2.bin",
        "../flash/seq/hr_e_2p1.bin",
        "../flash/seq/hr_e_1p2.bin",
        "../flash/seq/hr_e_1p1.bin",
        "../flash/seq/hm_z_2p2.bin",
        "../flash/seq/hm_z_2p1.bin",
        "../flash/seq/hm_z_1p1.bin",
        "../flash/seq/hm_x_2p2.bin",
        "../flash/seq/hm_x_2p1.bin",
        "../flash/seq/hm_x_1p1.bin",
        "../flash/seq/hm_e_2p2.bin",
        "../flash/seq/hm_e_2p1.bin",
        "../flash/seq/hm_e_1p2.bin",
        "../flash/seq/hm_e_1p1.bin",
        "../flash/seq/fs_z_2p2.bin",
        "../flash/seq/fs_w_2p1.bin",
        "../flash/seq/fs_z_1p1.bin",
        "../flash/seq/fs_x_2p2.bin",
        "../flash/seq/fs_x_2p1.bin",
        "../flash/seq/fs_x_1p1.bin",
        "../flash/seq/fs_e_2p2.bin",
        "../flash/seq/fs_e_2p1.bin",
        "../flash/seq/fs_e_1p2.bin",
        "../flash/seq/fs_e_1p1.bin",
        "../flash/seq/fk_z_2p2.bin",
        "../flash/seq/fk_z_2p1.bin",
        "../flash/seq/fk_z_1p1.bin",
        "../flash/seq/fk_x_2p2.bin",
        "../flash/seq/fk_x_2p1.bin",
        "../flash/seq/fk_x_1p1.bin",
        "../flash/seq/fk_n_2p2.bin",
        "../flash/seq/fk_n_2p1.bin",
        "../flash/seq/fk_n_1p2.bin",
        "../flash/seq/fk_n_1p1.bin",
        "../flash/seq/fr_z_2p2.bin",
        "../flash/seq/fr_z_2p1.bin",
        "../flash/seq/fr_z_1p1.bin",
        "../flash/seq/fr_x_2p2.bin",
        "../flash/seq/fr_x_2p1.bin",
        "../flash/seq/fr_x_1p1.bin",
        "../flash/seq/fr_n_2p2.bin",
        "../flash/seq/fr_n_2p1.bin",
        "../flash/seq/fr_n_1p2.bin",
        "../flash/seq/fr_n_1p1.bin",
        "../flash/seq/dr_z_2p2.bin",
        "../flash/seq/dr_z_2p1.bin",
        "../flash/seq/dr_z_1p1.bin",
        "../flash/seq/dr_x_2p2.bin",
        "../flash/seq/dr_x_2p1.bin",
        "../flash/seq/dr_x_1p1.bin",
        "../flash/seq/dr_e_2p2.bin",
        "../flash/seq/dr_e_2p1.bin",
        "../flash/seq/dr_e_1p2.bin",
        "../flash/seq/dr_e_1p1.bin",
        "../flash/seq/dr_n_2p2.bin",
        "../flash/seq/dr_n_2p1.bin",
        "../flash/seq/dr_n_1p2.bin",
        "../flash/seq/dr_n_1p1.bin",
        "../flash/seq/bl_z_2p2.bin",
        "../flash/seq/bl_z_2p1.bin",
        "../flash/seq/bl_z_1p1.bin",
        "../flash/seq/bl_x_2p2.bin",
        "../flash/seq/bl_x_2p1.bin",
        "../flash/seq/bl_x_1p1.bin",
        "../flash/seq/bl_n_2p2.bin",
        "../flash/seq/bl_n_2p1.bin",
        "../flash/seq/bl_n_1p2.bin",
        "../flash/seq/bl_n_1p1.bin",
        "../flash/tp/cutie2.tpb",
        "../flash/tp/hmetal2.tpb",
        "../flash/tp/king.tpb",
        "../flash/tp/punk2.tpb",
        "../flash/tp/flamenco.tpb",
        "../flash/tp/rockf.tpb",
        "../flash/tp/think.tpb",
        "../flash/tp/heaven2.tpb",
        "../flash/tp/power.tpb",
        "../flash/tp/night.tpb",
        "../flash/tp/skaska.tpb",
        "../flash/tp/joey.tpb",
        "../flash/tp/holiday.tpb",
        "../flash/tp/magic.tpb",
        "../flash/tp/advent.tpb",
        "../flash/tp/country.tpb",
        "../flash/tp/machine.tpb",
        "../flash/tp/ending.tpb",
        "../flash/tp/ventures.tpb",
        "../flash/tp/riff.tpb",
        "../flash/tp/jazz.tpb",
        "../flash/tp/fusion.tpb",
        "../flash/tp/degirock.tpb",
        "../flash/tp/toydolls.tpb",
        "../flash/tp/nrock.tpb",
        "../flash/tp/hrock.tpb",
        "../flash/tp/funk.tpb",
        "../flash/tp/select.tpb",
        "../flash/tp/mtown.tpb",
        "../flash/tp/hmetal.tpb",
        "../flash/tp/demo.tpb",
        "../flash/tp/blues.tpb",
        "../flash/tp/common.tpb",
        "../flash/demodata/demo42.bin",
        "../flash/demodata/demo41.bin",
        "../flash/demodata/demo32.bin",
        "../flash/demodata/demo31.bin",
        "../flash/demodata/demo22.bin",
        "../flash/demodata/demo21.bin",
        "../flash/demodata/demo12.bin",
        "../flash/demodata/demo11.bin",
        "../flash/lamp/cutie21.bin",
        "../flash/lamp/hmetal21.bin",
        "../flash/lamp/rock21.bin",
        "../flash/lamp/punk21.bin",
        "../flash/lamp/flam1.bin",
        "../flash/lamp/rockf1.bin",
        "../flash/lamp/think1.bin",
        "../flash/lamp/heaven1.bin",
        "../flash/lamp/power1.bin",
        "../flash/lamp/night1.bin",
        "../flash/lamp/skaska1.bin",
        "../flash/lamp/joey1.bin",
        "../flash/lamp/holiday1.bin",
        "../flash/lamp/magic1.bin",
        "../flash/lamp/adven1.bin",
        "../flash/lamp/country1.bin",
        "../flash/lamp/machine1.bin",
        "../flash/lamp/ending1.bin",
        "../flash/lamp/fire1.bin",
        "../flash/lamp/riffs3.bin",
        "../flash/lamp/rifft3.bin",
        "../flash/lamp/riffs2.bin",
        "../flash/lamp/rifft2.bin",
        "../flash/lamp/riffs1.bin",
        "../flash/lamp/rifft1.bin",
        "../flash/lamp/mdemo1.bin",
        "../flash/lamp/digi1.bin",
        "../flash/lamp/jazz21.bin",
        "../flash/lamp/hmetal1.bin",
        "../flash/lamp/hrock1.bin",
        "../flash/lamp/fusion1.bin",
        "../flash/lamp/vent1.bin",
        "../flash/lamp/funk1.bin",
        "../flash/lamp/blues1.bin",
        "../flash/lamp/tdoll1.bin",
        "../flash/lamp/mtown1.bin",
        "../flash/anime/rmgn0b.bin",
        "../flash/anime/rmgn0a.bin",
        "../flash/anime/rmbn1b.bin",
        "../flash/anime/rmbn1a.bin",
        "../flash/anime/rmnpic2b.bin",
        "../flash/anime/rmnpic2a.bin",
        "../flash/anime/rmnpic1b.bin",
        "../flash/anime/rmnpic1a.bin",
        "../flash/anime/rmnpic0b.bin",
        "../flash/anime/rmnpic0a.bin",
        "../flash/anime/rmwel0b.bin",
        "../flash/anime/rmwel0a.bin",
        "../flash/anime/rmvct1b.bin",
        "../flash/anime/rmvct1a.bin",
        "../flash/anime/rmvct0b.bin",
        "../flash/anime/rmvct0a.bin",
        "../flash/anime/rmpic1b.bin",
        "../flash/anime/rmpic1a.bin",
        "../flash/anime/rmpic0b.bin",
        "../flash/anime/rmpic0a.bin",
        "../flash/anime/rmok0b.bin",
        "../flash/anime/rmok0a.bin",
        "../flash/anime/rmnu2b.bin",
        "../flash/anime/rmnu2a.bin",
        "../flash/anime/rmnu1b.bin",
        "../flash/anime/rmnu1a.bin",
        "../flash/anime/rmnu0b.bin",
        "../flash/anime/rmnu0a.bin",
        "../flash/anime/rmbn0b.bin",
        "../flash/anime/rmbn0a.bin",
        "../flash/anime/rmbc0b.bin",
        "../flash/anime/rmbc0a.bin",
        "../flash/anime/rmbad0b1.bin",
        "../flash/anime/rmbad0a.bin",
        "../flash/anime/rt_sl0.bin",
        "../flash/anime/rt_pk0.bin",
        "../flash/anime/lt_sl0.bin",
        "../flash/anime/lt_pk0.bin",
        "../flash/anime/lov_1.bin",
        "../flash/anime/f_cam2.bin",
        "../flash/anime/f6.bin",
        "../flash/anime/ct_sl0.bin",
        "../flash/anime/ct_pk0.bin",
        "../flash/anime/hwall.bin",
        "../flash/VAB/p_riff.vab",
        "../flash/VAB/pra.vab",
        "../flash/VAB/mns.vab",
        "../flash/VAB/sand.vab",
        "../flash/VAB/rf.vab",
        "../flash/VAB/king.vab",
        "../flash/VAB/ssboy.vab",
        "../flash/VAB/thinkgf.vab",
        "../flash/VAB/skagf.vab",
        "../flash/VAB/joey.vab",
        "../flash/VAB/heavengt.vab",
        "../flash/VAB/power2.vab",
        "../flash/VAB/night.vab",
        "../flash/VAB/magic.vab",
        "../flash/VAB/holiday.vab",
        "../flash/VAB/adventur.vab",
        "../flash/VAB/machine.vab",
        "../flash/VAB/country.vab",
        "../flash/VAB/lstuff.vab",
        "../flash/VAB/fire.vab",
        "../flash/VAB/happy.vab",
        "../flash/VAB/hyp.vab",
        "../flash/VAB/qt_pie.vab",
        "../flash/VAB/jcat.vab",
        "../flash/VAB/dmart.vab",
        "../flash/VAB/ride.vab",
        "../flash/VAB/shake.vab",
        "../flash/VAB/els.vab",
        "../flash/VAB/cool.vab",
        "../flash/VAB/cblue.vab",
        "../flash/VAB/rf_pie.vab",
        "../flash/VAB/scale.vab",
        "../flash/VAB/s_cheer.vab",
        "../flash/VAB/s_select.vab",
        "../flash/VAB/v_over.vab",
        "../flash/VAB/v_select.vab",
        "../flash/VAB/v_result.vab",
        "../flash/VAB/v_entry.vab",
        "../flash/VAB/v_game.vab",
        "../flash/VAB/v_riff.vab",
        "../flash/VAB/v_topic.vab",
        "../flash/VAB/v_howto.vab",
        "../flash/VAB/v_tittle.vab",
        "../flash/VAB/riff.vab",
        "../flash/VAB/close.vab",
        "../flash/VAB/coin.vab",
        "../flash/texdata/dlangsp.bin",
        "../flash/texdata/dlangit.bin",
        "../flash/texdata/dlangge.bin",
        "../flash/texdata/dlangfr.bin",
        "../flash/texdata/dlangen.bin",
        "../flash/texdata/dlangjp.bin",
        "../flash/texdata/select.bin",
        "../flash/texdata/riff.bin",
        "../flash/texdata/demopic.bin",
        "../flash/texdata/cutie2.bin",
        "../flash/texdata/hmetal2.bin",
        "../flash/texdata/king.bin",
        "../flash/texdata/punk2.bin",
        "../flash/texdata/flam.bin",
        "../flash/texdata/rockf.bin",
        "../flash/texdata/think.bin",
        "../flash/texdata/heaven.bin",
        "../flash/texdata/upower.bin",
        "../flash/texdata/night.bin",
        "../flash/texdata/skaska.bin",
        "../flash/texdata/joey.bin",
        "../flash/texdata/holiday.bin",
        "../flash/texdata/magic.bin",
        "../flash/texdata/advent.bin",
        "../flash/texdata/country.bin",
        "../flash/texdata/machine.bin",
        "../flash/texdata/ending.bin",
        "../flash/texdata/nrock.bin",
        "../flash/texdata/degirock.bin",
        "../flash/texdata/toydolls.bin",
        "../flash/texdata/fusion.bin",
        "../flash/texdata/mtown.bin",
        "../flash/texdata/vent.bin",
        "../flash/texdata/hmetal.bin",
        "../flash/texdata/jazz.bin",
        "../flash/texdata/funk.bin",
        "../flash/texdata/hrock.bin",
        "../flash/texdata/blues.bin",
        "../flash/texdata/common.bin",
        "../flash/model/demopic.tmd",
        "../flash/model/select.tmd",
        "../flash/model/riff.tmd",
        "../flash/model/demo.tmd",
        "../flash/model/toydolls.tmd",
        "../flash/model/hmetal.tmd",
        "../flash/model/blues.tmd",
        "../flash/model/common.tmd",
        "../flash/movie/dance.str",
        "../flash/checksum/chksum.dat",

        "../model/demopic.tmd",
        "../model/select.tmd",
        "../model/riff.tmd",
        "../model/demo.tmd",
        "../model/toydolls.tmd",
        "../model/hmetal.tmd",
        "../model/blues.tmd",
        "../model/common.tmd",
        "../texdata/dlangsp.bin",
        "../texdata/dlangit.bin",
        "../texdata/dlangge.bin",
        "../texdata/dlangfr.bin",
        "../texdata/dlangen.bin",
        "../texdata/dlangjp.bin",
        "../texdata/demopic.bin",
        "../texdata/select.bin",
        "../texdata/riff.bin",
        "../texdata/demo.bin",
        "../texdata/ending.bin",
        "../texdata/nrock.bin",
        "../texdata/degirock.bin",
        "../texdata/toydolls.bin",
        "../texdata/fusion.bin",
        "../texdata/mtown.bin",
        "../texdata/vent.bin",
        "../texdata/hmetal.bin",
        "../texdata/jazz.bin",
        "../texdata/funk.bin",
        "../texdata/hrock.bin",
        "../texdata/blues.bin",
        "../texdata/common.bin",
        "../tp/dlangsp.tpb",
        "../tp/dlangit.tpb",
        "../tp/dlangge.tpb",
        "../tp/dlangfr.tpb",
        "../tp/dlangen.tpb",
        "../tp/dlangjp.tpb",
        "../tp/demopic.tpb",
        "../seq/ed_e_2p2.bin",
        "../seq/ed_e_2p1.bin",
        "../seq/ed_e_1p.bin",
        "../seq/mt_riff3.bin",
        "../seq/mt_riff2.bin",
        "../seq/mt_riff1.bin",
        "../seq/vt_n_2p2.bin",
        "../seq/vt_n_2p1.bin",
        "../seq/vt_n_1p.bin",
        "../seq/td_e_2p2.bin",
        "../seq/td_e_2p1.bin",
        "../seq/td_e_1p.bin",
        "../seq/td_n_2p2.bin",
        "../seq/td_n_2p1.bin",
        "../seq/td_n_1p.bin",
        "../seq/mt_n_2p2.bin",
        "../seq/mt_n_2p1.bin",
        "../seq/mt_n_1p.bin",
        "../seq/mt_p_2p2.bin",
        "../seq/mt_p_2p1.bin",
        "../seq/mt_p_1p.bin",
        "../seq/jz_n_2p2.bin",
        "../seq/jz_n_2p1.bin",
        "../seq/jz_n_1p.bin",
        "../seq/hr_e_2p2.bin",
        "../seq/hr_e_2p1.bin",
        "../seq/hr_e_1p.bin",
        "../seq/hm_e_2p2.bin",
        "../seq/hm_e_2p1.bin",
        "../seq/hm_e_1p.bin",
        "../seq/fs_e_2p2.bin",
        "../seq/fs_e_2p1.bin",
        "../seq/fs_e_1p.bin",
        "../seq/fk_n_2p2.bin",
        "../seq/fk_n_2p1.bin",
        "../seq/fk_n_1p.bin",
        "../seq/fr_n_2p2.bin",
        "../seq/fr_n_2p1.bin",
        "../seq/fr_n_1p.bin",
        "../seq/dr_e_2p2.bin",
        "../seq/dr_e_2p1.bin",
        "../seq/dr_e_1p.bin",
        "../seq/dr_n_2p2.bin",
        "../seq/dr_n_2p1.bin",
        "../seq/dr_n_1p.bin",
        "../seq/bl_n_2p2.bin",
        "../seq/bl_n_2p1.bin",
        "../seq/bl_n_1p.bin",
        "../tp/ending.tpb",
        "../tp/ventures.tpb",
        "../tp/riff.tpb",
        "../tp/jazz.tpb",
        "../tp/fusion.tpb",
        "../tp/degirock.tpb",
        "../tp/toydolls.tpb",
        "../tp/nrock.tpb",
        "../tp/hrock.tpb",
        "../tp/funk.tpb",
        "../tp/select.tpb",
        "../tp/mtown.tpb",
        "../tp/hmetal.tpb",
        "../tp/demo.tpb",
        "../tp/blues.tpb",
        "../tp/common.tpb",
        "../demodata/demo42.bin",
        "../demodata/demo41.bin",
        "../demodata/demo32.bin",
        "../demodata/demo31.bin",
        "../demodata/demo22.bin",
        "../demodata/demo21.bin",
        "../demodata/demo12.bin",
        "../demodata/demo11.bin",
        "../lamp/ending1.bin",
        "../lamp/fire1.bin",
        "../lamp/riffs3.bin",
        "../lamp/rifft3.bin",
        "../lamp/riffs2.bin",
        "../lamp/rifft2.bin",
        "../lamp/riffs1.bin",
        "../lamp/rifft1.bin",
        "../lamp/mdemo1.bin",
        "../lamp/digi1.bin",
        "../lamp/jazz1.bin",
        "../lamp/hmetal1.bin",
        "../lamp/hrock1.bin",
        "../lamp/fusion1.bin",
        "../lamp/vent1.bin",
        "../lamp/funk1.bin",
        "../lamp/blues1.bin",
        "../lamp/tdoll1.bin",
        "../lamp/mtown1.bin",
        "../anime/rmgn0b.bin",
        "../anime/rmgn0a.bin",
        "../anime/rmbn1b.bin",
        "../anime/rmbn1a.bin",
        "../anime/rmnpic2b.bin",
        "../anime/rmnpic2a.bin",
        "../anime/rmnpic1b.bin",
        "../anime/rmnpic1a.bin",
        "../anime/rmnpic0b.bin",
        "../anime/rmnpic0a.bin",
        "../anime/rmwel0b.bin",
        "../anime/rmwel0a.bin",
        "../anime/rmvct1b.bin",
        "../anime/rmvct1a.bin",
        "../anime/rmvct0b.bin",
        "../anime/rmvct0a.bin",
        "../anime/rmpic1b.bin",
        "../anime/rmpic1a.bin",
        "../anime/rmpic0b.bin",
        "../anime/rmpic0a.bin",
        "../anime/rmok0b.bin",
        "../anime/rmok0a.bin",
        "../anime/rmnu2b.bin",
        "../anime/rmnu2a.bin",
        "../anime/rmnu1b.bin",
        "../anime/rmnu1a.bin",
        "../anime/rmnu0b.bin",
        "../anime/rmnu0a.bin",
        "../anime/rmbn0b.bin",
        "../anime/rmbn0a.bin",
        "../anime/rmbc0b.bin",
        "../anime/rmbc0a.bin",
        "../anime/rmbad0b.bin",
        "../anime/rmbad0a.bin",
        "../anime/rt_sl0.bin",
        "../anime/rt_pk0.bin",
        "../anime/lt_sl0.bin",
        "../anime/lt_pk0.bin",
        "../anime/lov_1.bin",
        "../anime/f_cam2.bin",
        "../anime/f6.bin",
        "../anime/ct_sl0.bin",
        "../anime/ct_pk0.bin",
        "../anime/hwall.bin",
        "../movie/dance.str",
        "../sd/TOYVAB/rf_pie.vab",
        "../sd/TOYVAB/scale.vab",
        "../sd/TOYVAB/s_cheer.vab",
        "../sd/TOYVAB/s_select.vab",
        "../sd/TOYVAB/v_over.vab",
        "../sd/TOYVAB/v_select.vab",
        "../sd/TOYVAB/v_result.vab",
        "../sd/TOYVAB/v_entry.vab",
        "../sd/TOYVAB/v_game.vab",
        "../sd/TOYVAB/v_riff.vab",
        "../sd/TOYVAB/v_topic.vab",
        "../sd/TOYVAB/v_howto.vab",
        "../sd/TOYVAB/v_tittle.vab",
        "../sd/TOYVAB/ending.vab",
        "../sd/TOYVAB/FIRE2.vab",
        "../sd/TOYVAB/FIRE1.vab",
        "../sd/TOYVAB/nm2vab.vab",
        "../sd/TOYVAB/nm1vab.vab",
        "../sd/TOYVAB/6_TOY.vab",
        "../sd/TOYVAB/qt_pie.vab",
        "../sd/TOYVAB/chopper.vab",
        "../sd/TOYVAB/5_VENT.vab",
        "../sd/TOYVAB/jazz.vab",
        "../sd/TOYVAB/4_HM1_1.vab",
        "../sd/TOYVAB/3_FNK1_S.vab",
        "../sd/TOYVAB/3_FNK1_1.vab",
        "../sd/TOYVAB/2_HR_H.vab",
        "../sd/TOYVAB/2_HR_M.vab",
        "../sd/TOYVAB/2_HR_K.vab",
        "../sd/TOYVAB/1_BLS1_1.vab",
        "../sd/TOYVAB/riff.vab",
        "../sd/TOYVAB/close.vab",
        "../sd/TOYVAB/coin.vab",
        "../checksum/chksum.dat",

        "../flash/model/demopic.tmd",
        "../flash/model/riff.tmd",
        "../flash/model/demo.tmd",
        "../flash/model/toydolls.tmd",
        "../flash/model/hmetal.tmd",
        "../flash/model/blues.tmd",
        "../flash/model/common.tmd",
        "../flash/texdata/dlangsp.bin",
        "../flash/texdata/dlangit.bin",
        "../flash/texdata/dlangge.bin",
        "../flash/texdata/dlangfr.bin",
        "../flash/texdata/dlangen.bin",
        "../flash/texdata/dlangjp.bin",
        "../flash/texdata/select.bin",
        "../flash/texdata/riff.bin",
        "../flash/texdata/demopic.bin",
        "../flash/texdata/eclipse.bin",
        "../flash/texdata/micky.bin",
        "../flash/texdata/evil.bin",
        "../flash/texdata/cutie2.bin",
        "../flash/texdata/hmetal2.bin",
        "../flash/texdata/king.bin",
        "../flash/texdata/punk2.bin",
        "../flash/texdata/flam.bin",
        "../flash/texdata/rockf.bin",
        "../flash/texdata/think.bin",
        "../flash/texdata/heaven.bin",
        "../flash/texdata/upower.bin",
        "../flash/texdata/night.bin",
        "../flash/texdata/skaska.bin",
        "../flash/texdata/joey.bin",
        "../flash/texdata/holiday.bin",
        "../flash/texdata/magic.bin",
        "../flash/texdata/advent.bin",
        "../flash/texdata/country.bin",
        "../flash/texdata/machine.bin",
        "../flash/texdata/ending.bin",
        "../flash/texdata/nrock.bin",
        "../flash/texdata/degirock.bin",
        "../flash/texdata/toydolls.bin",
        "../flash/texdata/fusion.bin",
        "../flash/texdata/mtown.bin",
        "../flash/texdata/vent.bin",
        "../flash/texdata/hmetal.bin",
        "../flash/texdata/jazz.bin",
        "../flash/texdata/funk.bin",
        "../flash/texdata/hrock.bin",
        "../flash/texdata/blues.bin",
        "../flash/texdata/common.bin",
        "../flash/stbl/stbl.bin",
        "../flash/tp/dlangsp.tpb",
        "../flash/tp/dlangit.tpb",
        "../flash/tp/dlangge.tpb",
        "../flash/tp/dlangfr.tpb",
        "../flash/tp/dlangen.tpb",
        "../flash/tp/dlangjp.tpb",
        "../flash/tp/demopic.tpb",
        "../flash/seq/p_riff3.bin",
        "../flash/seq/p_riff2.bin",
        "../flash/seq/p_riff1.bin",
        "../flash/seq/ec_z_2p2.bin",
        "../flash/seq/ec_z_2p1.bin",
        "../flash/seq/ec_z_1p1.bin",
        "../flash/seq/ec_x_2p2.bin",
        "../flash/seq/ec_x_2p1.bin",
        "../flash/seq/ec_x_1p1.bin",
        "../flash/seq/ec_e_2p2.bin",
        "../flash/seq/ec_e_2p1.bin",
        "../flash/seq/ec_e_1p2.bin",
        "../flash/seq/ec_e_1p1.bin",
        "../flash/seq/ev_z_2p2.bin",
        "../flash/seq/ev_z_2p1.bin",
        "../flash/seq/ev_z_1p1.bin",
        "../flash/seq/ev_x_2p2.bin",
        "../flash/seq/ev_x_2p1.bin",
        "../flash/seq/ev_x_1p1.bin",
        "../flash/seq/ev_n_2p2.bin",
        "../flash/seq/ev_n_2p1.bin",
        "../flash/seq/ev_n_1p2.bin",
        "../flash/seq/ev_n_1p1.bin",
        "../flash/seq/mk_z_2p2.bin",
        "../flash/seq/mk_z_2p1.bin",
        "../flash/seq/mk_z_1p1.bin",
        "../flash/seq/mk_x_2p2.bin",
        "../flash/seq/mk_x_2p1.bin",
        "../flash/seq/mk_x_1p1.bin",
        "../flash/seq/mk_e_2p2.bin",
        "../flash/seq/mk_e_2p1.bin",
        "../flash/seq/mk_e_1p2.bin",
        "../flash/seq/mk_e_1p1.bin",
        "../flash/seq/c2_z_2p2.bin",
        "../flash/seq/c2_z_2p1.bin",
        "../flash/seq/c2_z_1p1.bin",
        "../flash/seq/c2_x_2p2.bin",
        "../flash/seq/c2_x_2p1.bin",
        "../flash/seq/c2_x_1p2.bin",
        "../flash/seq/c2_x_1p1.bin",
        "../flash/seq/c2_n_2p2.bin",
        "../flash/seq/c2_n_2p1.bin",
        "../flash/seq/c2_n_1p2.bin",
        "../flash/seq/c2_n_1p1.bin",
        "../flash/seq/c2_p_2p2.bin",
        "../flash/seq/c2_p_2p1.bin",
        "../flash/seq/c2_p_1p2.bin",
        "../flash/seq/c2_p_1p1.bin",
        "../flash/seq/mn_z_2p2.bin",
        "../flash/seq/mn_z_2p1.bin",
        "../flash/seq/mn_z_1p1.bin",
        "../flash/seq/mn_x_2p2.bin",
        "../flash/seq/mn_x_2p1.bin",
        "../flash/seq/mn_x_1p1.bin",
        "../flash/seq/mn_n_2p2.bin",
        "../flash/seq/mn_n_2p1.bin",
        "../flash/seq/mn_n_1p2.bin",
        "../flash/seq/mn_n_1p1.bin",
        "../flash/seq/kg_z_2p2.bin",
        "../flash/seq/kg_z_2p1.bin",
        "../flash/seq/kg_z_1p1.bin",
        "../flash/seq/kg_x_2p2.bin",
        "../flash/seq/kg_x_2p1.bin",
        "../flash/seq/kg_x_1p1.bin",
        "../flash/seq/kg_n_2p2.bin",
        "../flash/seq/kg_n_2p1.bin",
        "../flash/seq/kg_n_1p2.bin",
        "../flash/seq/kg_n_1p1.bin",
        "../flash/seq/sd_z_2p2.bin",
        "../flash/seq/sd_z_2p1.bin",
        "../flash/seq/sd_z_1p1.bin",
        "../flash/seq/sd_x_2p2.bin",
        "../flash/seq/sd_x_2p1.bin",
        "../flash/seq/sd_x_1p1.bin",
        "../flash/seq/sd_n_2p2.bin",
        "../flash/seq/sd_n_2p1.bin",
        "../flash/seq/sd_n_1p2.bin",
        "../flash/seq/sd_n_1p1.bin",
        "../flash/seq/sb_z_2p2.bin",
        "../flash/seq/sb_z_2p1.bin",
        "../flash/seq/sb_z_1p1.bin",
        "../flash/seq/sb_x_2p2.bin",
        "../flash/seq/sb_x_2p1.bin",
        "../flash/seq/sb_x_1p1.bin",
        "../flash/seq/sb_n_2p2.bin",
        "../flash/seq/sb_n_2p1.bin",
        "../flash/seq/sb_n_1p2.bin",
        "../flash/seq/sb_n_1p1.bin",
        "../flash/seq/rf_z_2p2.bin",
        "../flash/seq/rf_z_2p1.bin",
        "../flash/seq/rf_z_1p1.bin",
        "../flash/seq/rf_x_2p2.bin",
        "../flash/seq/rf_x_2p1.bin",
        "../flash/seq/rf_x_1p1.bin",
        "../flash/seq/rf_n_2p2.bin",
        "../flash/seq/rf_n_2p1.bin",
        "../flash/seq/rf_n_1p2.bin",
        "../flash/seq/rf_n_1p1.bin",
        "../flash/seq/th_z_2p2.bin",
        "../flash/seq/th_z_2p1.bin",
        "../flash/seq/th_z_1p1.bin",
        "../flash/seq/th_x_2p2.bin",
        "../flash/seq/th_x_2p1.bin",
        "../flash/seq/th_x_1p1.bin",
        "../flash/seq/th_n_2p2.bin",
        "../flash/seq/th_n_2p1.bin",
        "../flash/seq/th_n_1p2.bin",
        "../flash/seq/th_n_1p1.bin",
        "../flash/seq/jy_z_2p2.bin",
        "../flash/seq/jy_z_2p1.bin",
        "../flash/seq/jy_z_1p1.bin",
        "../flash/seq/jy_x_2p2.bin",
        "../flash/seq/jy_w_2p1.bin",
        "../flash/seq/jy_x_1p1.bin",
        "../flash/seq/jy_n_2p2.bin",
        "../flash/seq/jy_n_2p1.bin",
        "../flash/seq/jy_n_1p2.bin",
        "../flash/seq/jy_n_1p1.bin",
        "../flash/seq/sk_z_2p2.bin",
        "../flash/seq/sk_z_2p1.bin",
        "../flash/seq/sk_z_1p1.bin",
        "../flash/seq/sk_x_2p2.bin",
        "../flash/seq/sk_x_2p1.bin",
        "../flash/seq/sk_x_1p1.bin",
        "../flash/seq/sk_n_2p2.bin",
        "../flash/seq/sk_n_2p1.bin",
        "../flash/seq/sk_n_1p2.bin",
        "../flash/seq/sk_n_1p1.bin",
        "../flash/seq/hv_z_2p2.bin",
        "../flash/seq/hv_z_2p1.bin",
        "../flash/seq/hv_z_1p1.bin",
        "../flash/seq/hv_x_2p2.bin",
        "../flash/seq/hv_x_2p1.bin",
        "../flash/seq/hv_x_1p1.bin",
        "../flash/seq/hv_n_2p2.bin",
        "../flash/seq/hv_n_2p1.bin",
        "../flash/seq/hv_n_1p2.bin",
        "../flash/seq/hv_n_1p1.bin",
        "../flash/seq/pw_z_2p2.bin",
        "../flash/seq/pw_z_2p1.bin",
        "../flash/seq/pw_z_1p1.bin",
        "../flash/seq/pw_x_2p2.bin",
        "../flash/seq/pw_x_2p1.bin",
        "../flash/seq/pw_x_1p1.bin",
        "../flash/seq/pw_n_2p2.bin",
        "../flash/seq/pw_n_2p1.bin",
        "../flash/seq/pw_n_1p2.bin",
        "../flash/seq/pw_n_1p1.bin",
        "../flash/seq/ni_z_2p2.bin",
        "../flash/seq/ni_z_2p1.bin",
        "../flash/seq/ni_z_1p1.bin",
        "../flash/seq/ni_x_2p2.bin",
        "../flash/seq/ni_x_2p1.bin",
        "../flash/seq/ni_x_1p1.bin",
        "../flash/seq/ni_n_2p2.bin",
        "../flash/seq/ni_n_2p1.bin",
        "../flash/seq/ni_n_1p2.bin",
        "../flash/seq/ni_n_1p1.bin",
        "../flash/seq/hd_z_2p2.bin",
        "../flash/seq/hd_z_2p1.bin",
        "../flash/seq/hd_z_1p1.bin",
        "../flash/seq/hd_x_2p2.bin",
        "../flash/seq/hd_x_2p1.bin",
        "../flash/seq/hd_x_1p1.bin",
        "../flash/seq/hd_n_2p2.bin",
        "../flash/seq/hd_n_2p1.bin",
        "../flash/seq/hd_n_1p2.bin",
        "../flash/seq/hd_n_1p1.bin",
        "../flash/seq/mg_z_2p2.bin",
        "../flash/seq/mg_z_2p1.bin",
        "../flash/seq/mg_z_1p1.bin",
        "../flash/seq/mg_x_2p2.bin",
        "../flash/seq/mg_x_2p1.bin",
        "../flash/seq/mg_x_1p1.bin",
        "../flash/seq/mg_e_2p2.bin",
        "../flash/seq/mg_e_2p1.bin",
        "../flash/seq/mg_e_1p2.bin",
        "../flash/seq/mg_e_1p1.bin",
        "../flash/seq/mg_n_2p2.bin",
        "../flash/seq/mg_n_2p1.bin",
        "../flash/seq/mg_n_1p2.bin",
        "../flash/seq/mg_n_1p1.bin",
        "../flash/seq/ad_z_2p2.bin",
        "../flash/seq/ad_z_2p1.bin",
        "../flash/seq/ad_z_1p1.bin",
        "../flash/seq/ad_x_2p2.bin",
        "../flash/seq/ad_x_2p1.bin",
        "../flash/seq/ad_x_1p1.bin",
        "../flash/seq/ad_e_2p2.bin",
        "../flash/seq/ad_e_2p1.bin",
        "../flash/seq/ad_e_1p2.bin",
        "../flash/seq/ad_e_1p1.bin",
        "../flash/seq/ad_n_2p2.bin",
        "../flash/seq/ad_n_2p1.bin",
        "../flash/seq/ad_n_1p2.bin",
        "../flash/seq/ad_n_1p1.bin",
        "../flash/seq/ct_z_2p2.bin",
        "../flash/seq/ct_z_2p1.bin",
        "../flash/seq/ct_w_1p1.bin",
        "../flash/seq/ct_x_2p2.bin",
        "../flash/seq/ct_x_2p1.bin",
        "../flash/seq/ct_x_1p1.bin",
        "../flash/seq/ct_e_2p2.bin",
        "../flash/seq/ct_e_2p1.bin",
        "../flash/seq/ct_e_1p2.bin",
        "../flash/seq/ct_e_1p1.bin",
        "../flash/seq/ct_n_2p2.bin",
        "../flash/seq/ct_n_2p1.bin",
        "../flash/seq/ct_n_1p2.bin",
        "../flash/seq/ct_n_1p1.bin",
        "../flash/seq/mm_z_2p2.bin",
        "../flash/seq/mm_z_2p1.bin",
        "../flash/seq/mm_z_1p1.bin",
        "../flash/seq/mm_x_2p2.bin",
        "../flash/seq/mm_x_2p1.bin",
        "../flash/seq/mm_x_1p1.bin",
        "../flash/seq/mm_n_2p2.bin",
        "../flash/seq/mm_n_2p1.bin",
        "../flash/seq/mm_n_1p2.bin",
        "../flash/seq/mm_n_1p1.bin",
        "../flash/seq/ed_z_2p2.bin",
        "../flash/seq/ed_z_2p1.bin",
        "../flash/seq/ed_z_1p1.bin",
        "../flash/seq/ed_x_2p2.bin",
        "../flash/seq/ed_x_2p1.bin",
        "../flash/seq/ed_x_1p1.bin",
        "../flash/seq/ed_n_2p2.bin",
        "../flash/seq/ed_n_2p1.bin",
        "../flash/seq/ed_n_1p2.bin",
        "../flash/seq/ed_n_1p1.bin",
        "../flash/seq/vt_z_2p2.bin",
        "../flash/seq/vt_z_2p1.bin",
        "../flash/seq/vt_z_1p1.bin",
        "../flash/seq/vt_x_2p2.bin",
        "../flash/seq/vt_x_2p1.bin",
        "../flash/seq/vt_x_1p1.bin",
        "../flash/seq/vt_w_2p2.bin",
        "../flash/seq/vt_n_2p1.bin",
        "../flash/seq/vt_n_1p2.bin",
        "../flash/seq/vt_n_1p1.bin",
        "../flash/seq/td_z_2p2.bin",
        "../flash/seq/td_z_2p1.bin",
        "../flash/seq/td_z_1p1.bin",
        "../flash/seq/td_x_2p2.bin",
        "../flash/seq/td_x_2p1.bin",
        "../flash/seq/td_x_1p1.bin",
        "../flash/seq/td_e_2p2.bin",
        "../flash/seq/td_e_2p1.bin",
        "../flash/seq/td_e_1p2.bin",
        "../flash/seq/td_e_1p1.bin",
        "../flash/seq/td_n_2p2.bin",
        "../flash/seq/td_n_2p1.bin",
        "../flash/seq/td_n_1p2.bin",
        "../flash/seq/td_n_1p1.bin",
        "../flash/seq/mt_z_2p2.bin",
        "../flash/seq/mt_z_2p1.bin",
        "../flash/seq/mt_z_1p1.bin",
        "../flash/seq/mt_x_2p2.bin",
        "../flash/seq/mt_x_2p1.bin",
        "../flash/seq/mt_x_1p1.bin",
        "../flash/seq/mt_n_2p2.bin",
        "../flash/seq/mt_n_2p1.bin",
        "../flash/seq/mt_n_1p2.bin",
        "../flash/seq/mt_n_1p1.bin",
        "../flash/seq/jz_z_2p2.bin",
        "../flash/seq/jz_z_2p1.bin",
        "../flash/seq/jz_z_1p1.bin",
        "../flash/seq/jz_x_2p2.bin",
        "../flash/seq/jz_x_2p1.bin",
        "../flash/seq/jz_x_1p1.bin",
        "../flash/seq/jz_e_2p2.bin",
        "../flash/seq/jz_e_2p1.bin",
        "../flash/seq/jz_e_1p2.bin",
        "../flash/seq/jz_e_1p1.bin",
        "../flash/seq/hr_z_2p2.bin",
        "../flash/seq/hr_z_2p1.bin",
        "../flash/seq/hr_z_1p1.bin",
        "../flash/seq/hr_x_2p2.bin",
        "../flash/seq/hr_x_2p1.bin",
        "../flash/seq/hr_x_1p1.bin",
        "../flash/seq/hr_e_2p2.bin",
        "../flash/seq/hr_e_2p1.bin",
        "../flash/seq/hr_e_1p2.bin",
        "../flash/seq/hr_e_1p1.bin",
        "../flash/seq/hm_z_2p2.bin",
        "../flash/seq/hm_z_2p1.bin",
        "../flash/seq/hm_z_1p1.bin",
        "../flash/seq/hm_x_2p2.bin",
        "../flash/seq/hm_x_2p1.bin",
        "../flash/seq/hm_x_1p1.bin",
        "../flash/seq/hm_e_2p2.bin",
        "../flash/seq/hm_e_2p1.bin",
        "../flash/seq/hm_e_1p2.bin",
        "../flash/seq/hm_e_1p1.bin",
        "../flash/seq/fs_z_2p2.bin",
        "../flash/seq/fs_w_2p1.bin",
        "../flash/seq/fs_z_1p1.bin",
        "../flash/seq/fs_x_2p2.bin",
        "../flash/seq/fs_x_2p1.bin",
        "../flash/seq/fs_x_1p1.bin",
        "../flash/seq/fs_e_2p2.bin",
        "../flash/seq/fs_e_2p1.bin",
        "../flash/seq/fs_e_1p2.bin",
        "../flash/seq/fs_e_1p1.bin",
        "../flash/seq/fk_z_2p2.bin",
        "../flash/seq/fk_z_2p1.bin",
        "../flash/seq/fk_z_1p1.bin",
        "../flash/seq/fk_x_2p2.bin",
        "../flash/seq/fk_x_2p1.bin",
        "../flash/seq/fk_x_1p1.bin",
        "../flash/seq/fk_n_2p2.bin",
        "../flash/seq/fk_n_2p1.bin",
        "../flash/seq/fk_n_1p2.bin",
        "../flash/seq/fk_n_1p1.bin",
        "../flash/seq/fr_z_2p2.bin",
        "../flash/seq/fr_z_2p1.bin",
        "../flash/seq/fr_z_1p1.bin",
        "../flash/seq/fr_x_2p2.bin",
        "../flash/seq/fr_x_2p1.bin",
        "../flash/seq/fr_x_1p1.bin",
        "../flash/seq/fr_n_2p2.bin",
        "../flash/seq/fr_n_2p1.bin",
        "../flash/seq/fr_n_1p2.bin",
        "../flash/seq/fr_n_1p1.bin",
        "../flash/seq/dr_z_2p2.bin",
        "../flash/seq/dr_z_2p1.bin",
        "../flash/seq/dr_z_1p1.bin",
        "../flash/seq/dr_x_2p2.bin",
        "../flash/seq/dr_x_2p1.bin",
        "../flash/seq/dr_x_1p1.bin",
        "../flash/seq/dr_e_2p2.bin",
        "../flash/seq/dr_e_2p1.bin",
        "../flash/seq/dr_e_1p2.bin",
        "../flash/seq/dr_e_1p1.bin",
        "../flash/seq/dr_n_2p2.bin",
        "../flash/seq/dr_n_2p1.bin",
        "../flash/seq/dr_n_1p2.bin",
        "../flash/seq/dr_n_1p1.bin",
        "../flash/seq/bl_z_2p2.bin",
        "../flash/seq/bl_z_2p1.bin",
        "../flash/seq/bl_z_1p1.bin",
        "../flash/seq/bl_x_2p2.bin",
        "../flash/seq/bl_x_2p1.bin",
        "../flash/seq/bl_x_1p1.bin",
        "../flash/seq/bl_n_2p2.bin",
        "../flash/seq/bl_n_2p1.bin",
        "../flash/seq/bl_n_1p2.bin",
        "../flash/seq/bl_n_1p1.bin",
        "../flash/tp/eclipse.tpb",
        "../flash/tp/micky.tpb",
        "../flash/tp/evil.tpb",
        "../flash/tp/cutie2.tpb",
        "../flash/tp/hmetal2.tpb",
        "../flash/tp/king.tpb",
        "../flash/tp/punk2.tpb",
        "../flash/tp/flamenco.tpb",
        "../flash/tp/rockf.tpb",
        "../flash/tp/think.tpb",
        "../flash/tp/heaven2.tpb",
        "../flash/tp/power.tpb",
        "../flash/tp/night.tpb",
        "../flash/tp/skaska.tpb",
        "../flash/tp/joey.tpb",
        "../flash/tp/holiday.tpb",
        "../flash/tp/magic.tpb",
        "../flash/tp/advent.tpb",
        "../flash/tp/country.tpb",
        "../flash/tp/machine.tpb",
        "../flash/tp/ending.tpb",
        "../flash/tp/ventures.tpb",
        "../flash/tp/riff.tpb",
        "../flash/tp/jazz.tpb",
        "../flash/tp/fusion.tpb",
        "../flash/tp/degirock.tpb",
        "../flash/tp/toydolls.tpb",
        "../flash/tp/nrock.tpb",
        "../flash/tp/hrock.tpb",
        "../flash/tp/funk.tpb",
        "../flash/tp/select.tpb",
        "../flash/tp/mtown.tpb",
        "../flash/tp/hmetal.tpb",
        "../flash/tp/demo.tpb",
        "../flash/tp/blues.tpb",
        "../flash/tp/common.tpb",
        "../flash/demodata/demo42.bin",
        "../flash/demodata/demo41.bin",
        "../flash/demodata/demo32.bin",
        "../flash/demodata/demo31.bin",
        "../flash/demodata/demo22.bin",
        "../flash/demodata/demo21.bin",
        "../flash/demodata/demo12.bin",
        "../flash/demodata/demo11.bin",
        "../flash/lamp/eclipse1.bin",
        "../flash/lamp/micky1.bin",
        "../flash/lamp/evil1.bin",
        "../flash/lamp/cutie21.bin",
        "../flash/lamp/hmetal21.bin",
        "../flash/lamp/rock21.bin",
        "../flash/lamp/punk21.bin",
        "../flash/lamp/flam1.bin",
        "../flash/lamp/rockf1.bin",
        "../flash/lamp/think1.bin",
        "../flash/lamp/heaven1.bin",
        "../flash/lamp/power1.bin",
        "../flash/lamp/night1.bin",
        "../flash/lamp/skaska1.bin",
        "../flash/lamp/joey1.bin",
        "../flash/lamp/holiday1.bin",
        "../flash/lamp/magic1.bin",
        "../flash/lamp/adven1.bin",
        "../flash/lamp/country1.bin",
        "../flash/lamp/machine1.bin",
        "../flash/lamp/ending1.bin",
        "../flash/lamp/fire1.bin",
        "../flash/lamp/riffs3.bin",
        "../flash/lamp/rifft3.bin",
        "../flash/lamp/riffs2.bin",
        "../flash/lamp/rifft2.bin",
        "../flash/lamp/riffs1.bin",
        "../flash/lamp/rifft1.bin",
        "../flash/lamp/mdemo1.bin",
        "../flash/lamp/digi1.bin",
        "../flash/lamp/jazz21.bin",
        "../flash/lamp/hmetal1.bin",
        "../flash/lamp/hrock1.bin",
        "../flash/lamp/fusion1.bin",
        "../flash/lamp/vent1.bin",
        "../flash/lamp/funk1.bin",
        "../flash/lamp/blues1.bin",
        "../flash/lamp/tdoll1.bin",
        "../flash/lamp/mtown1.bin",
        "../flash/anime/rmgn0b.bin",
        "../flash/anime/rmgn0a.bin",
        "../flash/anime/rmbn1b.bin",
        "../flash/anime/rmbn1a.bin",
        "../flash/anime/rmnpic2b.bin",
        "../flash/anime/rmnpic2a.bin",
        "../flash/anime/rmnpic1b.bin",
        "../flash/anime/rmnpic1a.bin",
        "../flash/anime/rmnpic0b.bin",
        "../flash/anime/rmnpic0a.bin",
        "../flash/anime/rmwel0b.bin",
        "../flash/anime/rmwel0a.bin",
        "../flash/anime/rmvct1b.bin",
        "../flash/anime/rmvct1a.bin",
        "../flash/anime/rmvct0b.bin",
        "../flash/anime/rmvct0a.bin",
        "../flash/anime/rmpic1b.bin",
        "../flash/anime/rmpic1a.bin",
        "../flash/anime/rmpic0b.bin",
        "../flash/anime/rmpic0a.bin",
        "../flash/anime/rmok0b.bin",
        "../flash/anime/rmok0a.bin",
        "../flash/anime/rmnu2b.bin",
        "../flash/anime/rmnu2a.bin",
        "../flash/anime/rmnu1b.bin",
        "../flash/anime/rmnu1a.bin",
        "../flash/anime/rmnu0b.bin",
        "../flash/anime/rmnu0a.bin",
        "../flash/anime/rmbn0b.bin",
        "../flash/anime/rmbn0a.bin",
        "../flash/anime/rmbc0b.bin",
        "../flash/anime/rmbc0a.bin",
        "../flash/anime/rmbad0b1.bin",
        "../flash/anime/rmbad0a.bin",
        "../flash/anime/rt_sl0.bin",
        "../flash/anime/rt_pk0.bin",
        "../flash/anime/lt_sl0.bin",
        "../flash/anime/lt_pk0.bin",
        "../flash/anime/lov_1.bin",
        "../flash/anime/f_cam2.bin",
        "../flash/anime/f6.bin",
        "../flash/anime/ct_sl0.bin",
        "../flash/anime/ct_pk0.bin",
        "../flash/anime/hwall.bin",
        "../flash/VAB/m02f.vab",
        "../flash/VAB/m01f.vab",
        "../flash/VAB/ecl2.vab",
        "../flash/VAB/p_riff.vab",
        "../flash/VAB/pra.vab",
        "../flash/VAB/mns.vab",
        "../flash/VAB/sand.vab",
        "../flash/VAB/rf.vab",
        "../flash/VAB/king.vab",
        "../flash/VAB/ssboy.vab",
        "../flash/VAB/thinkgf.vab",
        "../flash/VAB/skagf.vab",
        "../flash/VAB/joey.vab",
        "../flash/VAB/heavengt.vab",
        "../flash/VAB/power2.vab",
        "../flash/VAB/night.vab",
        "../flash/VAB/magic.vab",
        "../flash/VAB/holiday.vab",
        "../flash/VAB/adventur.vab",
        "../flash/VAB/machine.vab",
        "../flash/VAB/country.vab",
        "../flash/VAB/lstuff.vab",
        "../flash/VAB/fire.vab",
        "../flash/VAB/happy.vab",
        "../flash/VAB/hyp.vab",
        "../flash/VAB/qt_pie.vab",
        "../flash/VAB/jcat.vab",
        "../flash/VAB/dmart.vab",
        "../flash/VAB/ride.vab",
        "../flash/VAB/shake.vab",
        "../flash/VAB/els.vab",
        "../flash/VAB/cool.vab",
        "../flash/VAB/cblue.vab",
        "../flash/VAB/rf_pie.vab",
        "../flash/VAB/scale.vab",
        "../flash/VAB/s_cheer.vab",
        "../flash/VAB/s_select.vab",
        "../flash/VAB/v_over.vab",
        "../flash/VAB/v_select.vab",
        "../flash/VAB/v_result.vab",
        "../flash/VAB/v_entry.vab",
        "../flash/VAB/v_game.vab",
        "../flash/VAB/v_riff.vab",
        "../flash/VAB/v_topic.vab",
        "../flash/VAB/v_howto.vab",
        "../flash/VAB/v_tittle.vab",
        "../flash/VAB/riff.vab",
        "../flash/VAB/close.vab",
        "../flash/VAB/coin.vab",
        "../flash/data/chksum.dat",

        # DMX
        "io_rr.tmd",
        "io_pp.tmd",
        "io_rb.tmd",
        "io_pb.tmd",
        "io_rp.tmd",
        "io_laser_r.tmd",
        "io_laser_b.tmd",
        "man0.mdt",
        "para.mdt",
        "yumi.mdt",
        "gren.mdt",
        "pa_all.mdt",
        "grabfile.tim",
        "cube0.tmd",
        "cube1.tmd",
    ]

    for i in range(0, 100):
        pccard_filenames.append("data/back/game/chr/%08d_25.cmt" % i)

    common_filenames = [
        'checksum', 'psx', 'main', 'config', 'fpga_mp3', 'boot', 'aout'
    ]

    common_paths = [
        '', 'boot', 's573', 'data', 'data/fpga', 'soft', 'soft/s573', 'boot/s573', 'boot/soft/s573'
    ]

    toplevel_paths = [
        '', '../flash', 'flash', '/flash', '../'
    ]

    ddr_movie_filenames = [
        'cddana', 'scrob_25', 'scrbk_16', 're2424', 'acxx28', 'ccsaca', 'ccrgca', 'ccltaa',
        'ccitaa', 'ccheaa', 'ccdrga', 'ccddra', 'cccuba', 'ccclma', 'ccclca', 'title',
        'hwrlja', 'hwfroa', 'hwnora', 'hwhaja',
        'jutrah', 'jutrag', 'jutraf', 'jutrae', 'jutrad', 'jutrac', 'jutrab', 'jutraa', 'justri', 'justrh', 'justrg',
        'justrf', 'justre', 'justrd', 'justrc', 'justrb', 'justra', 'juspka', 'juspib', 'juspia', 'jusech', 'jusecg',
        'jusecf', 'jusece', 'jusecd', 'jusecc', 'jusecb', 'juseca', 'jurbab', 'jurbaa', 'junycb', 'junyca', 'juhrta',
        'juhrda', 'juhpla', 'juhmsa', 'juhmra', 'juhmma', 'juhmfa', 'juhgra', 'juhbga', 'jufdcb', 'jufdca', 'jszxca',
        'jsytra', 'jsxrpa', 'jswwwa', 'jswsxa', 'jsuioa', 'jstusa', 'jstrea', 'jstasa', 'jssssa', 'jssiba', 'jsrewa',
        'jsprza', 'jspora', 'jspaua', 'jskera', 'jskeba', 'jsjkla', 'jshjka', 'jsghja', 'jsgfda', 'jsfufa', 'jsfdsa',
        'jsewqa', 'jsenea', 'jseeee', 'jsdsaa', 'jsdima', 'jsddda', 'jsdaba', 'jsdaaa', 'jsccca', 'jsbeba', 'jsbbba',
        'jsaaaa', 'jrwird', 'jrwira', 'jruzuc', 'jruzub', 'jruzua', 'jrtryt', 'jrsupb', 'jrsupa', 'jrsumb', 'jrsuma',
        'jrssma', 'jrsmra', 'jrskya', 'jrsawa', 'jrlina', 'jrjazd', 'jrjazc', 'jrjazb', 'jrjaza', 'jrgnma', 'jrfsea',
        'jrdria', 'jrcusa', 'jrcupa', 'jrcrba', 'jrcndd', 'jrcndb', 'jrcnda', 'jrcmab', 'jrcmaa', 'jrcarb', 'jrbapa',
        'jmswrp', 'jmpaxt', 'jmparu', 'jmpahb', 'jmpaha', 'jmpabf', 'jmpaab', 'jmpaaa', 'jmlobb', 'jmloba', 'jmline',
        'jmkatb', 'jmkata', 'jmglow', 'jmflcb', 'jmflca', 'jmfilm', 'jmfcub', 'jmfcua', 'jmefil', 'jmcufb', 'jmcufa',
        'jmcubs', 'jmcubk', 'jfwrdd', 'jfwrdc', 'jfwrdb', 'jfwrda', 'jfwirc', 'jfwira', 'jfttma', 'jftrnd', 'jftrnb',
        'jftrna', 'jfsana', 'jfpiwa', 'jfpara', 'jfmjba', 'jfmecb', 'jfmeca', 'jflngb', 'jflnga', 'jflita', 'jfldac',
        'jfkoac', 'jfkkzb', 'jfinaa', 'jfhtaa', 'jffrga', 'jfctmb', 'jfctma', 'jfclib', 'jfclia', 'jfbfud', 'jfbfuc',
        'jfbfub', 'jfbfua', 'jewawa', 'jetopb', 'jetopa', 'jetono', 'jethdc', 'jethdb', 'jethda', 'jetcla', 'jestra',
        'jesnwb', 'jesnwa', 'jerain', 'jepusb', 'jepusa', 'jepmpa', 'jepina', 'jenmma', 'jeninf', 'jeninc', 'jenina',
        'jekara', 'jejete', 'jeifee', 'jeifec', 'jeifeb', 'jehnaa', 'jehgla', 'jehall', 'jegara', 'jegaku', 'jeflgb',
        'jeelea', 'jeearo', 'jedjtb', 'jedjta', 'jecupa', 'jecara', 'jeblea', 'jebkha'
    ]

    ddr_movie_paths = [
        'common', 'howto'
    ]

    ddr_anime_base_filenames = [
        'mfjc', 'mfjb', 'mfja', 'mljc', 'mljb', 'mlja', 'mrsc', 'mrsb',
        'mrsa', 'mfsc', 'mfsb', 'mfsa', 'mbsc', 'mbsb', 'mbsa', 'mlsc',
        'mlsb', 'mlsa', 'mnor'
    ]

    ddr_anime_filenames = []
    for x in ddr_anime_base_filenames:
        for i in range(0, 10):
            ddr_anime_filenames.append("%s%d" % (x, i))

    ddr_motion_filenames = [
        "abc", "abcd", "abcde", "abcdef", "abcdefg", "capoera1", "cdef", "defg",
        "defgh", "dummy", "ef", "efg", "efghi", "efghijk", "fgh", "fghi",
        "fghijk", "fghijklm", "ghi", "ghijk", "ghijklm", "hijk", "hijklm", "hiphop1",
        "hiphop2", "hopping1", "ijklm", "ijkln", "jazz1", "jazz2", "klm", "lock1",
        "mhouse1", "n31", "normal", "sino_", "soul1", "soul2", "thouse2", "thouse3",
        "wave1", "wave2", "y11", "y31",
    ]

    mambo_puppet_filenames = [
        "uhiy", "lhiy", "cygp", "cygl", "gunm", "geng", "genr", "genb",
        "brow", "sung", "spym", "uhir", "lhir", "sabo", "cong", "samr",
        "samg", "samy", "yase", "debu", "ygir", "rgir", "furc", "furb",
        "fura"
    ]

    for ext in gfdm_common_extensions:
        for x in range(0, 1000):
            pccard_filenames.append("spu%03dgf.%s" % (x, ext))
            pccard_filenames.append("spu%03ddm.%s" % (x, ext))
            pccard_filenames.append("bg%03d.%s" % (x, ext))

            for x1 in range(0, 10):
                for x2 in range(0, 10):
                    pccard_filenames.append("g%03d%01d%01d.%s" % (x, x1, x2, ext))
                    pccard_filenames.append("d%03d%01d%01d.%s" % (x, x1, x2, ext))

    for ext in common_extensions:
        for i in range(0, 100):
            pccard_filenames.append("data/texture/banner/banner%02d.%s" % (i, ext))

        for filename in common_filenames:
            for path2 in toplevel_paths:
                for path in common_paths:
                    pccard_filenames.append("/".join([x for x in [path2, path, "%s.%s" % (filename, ext)] if x]))

        for part in ddr_common_parts:
            for filename in ["x"] + ["cos%02d" % x for x in range(0, 100)] + ["non%02d" % x for x in range(0, 100)]:
                pccard_filenames.append("data/course/%s_%s.%s" % (filename, part, ext))

        for region in ddr_common_regions:
            pccard_filenames.append("data/mcard/%s/pages.%s" % (region, ext))
            pccard_filenames.append("data/mcard/%s/pagel.%s" % (region, ext))

            for i in range(0, 10):
                pccard_filenames.append("data/mcard/%s/page%d.%s" % (region, i, ext))

            pccard_filenames.append("data/mcard/%s/titl2_25.%s" % (region, ext))
            pccard_filenames.append("data/mcard/%s/title.%s" % (region, ext))
            pccard_filenames.append("data/mcard/%s/titls_25.%s" % (region, ext))
            pccard_filenames.append("data/mcard/%s/unist_25.%s" % (region, ext))

        for filename in ddr_movie_filenames + ddr_motion_filenames + ddr_anime_filenames:
            pccard_filenames.append("data/anime/%s/%s.%s" % (filename, filename, ext))

        for motion in ddr_movie_filenames + ddr_motion_filenames + ddr_anime_filenames:
            pccard_filenames.append("data/motion/%s/%s.%s" % (motion, motion, ext))

        for movie_path in ddr_movie_paths:
            for filename in ddr_movie_filenames + ddr_motion_filenames + ddr_anime_filenames:
                pccard_filenames.append("data/movie/%s/%s.%s" % (movie_path, filename, ext))

        for filename in mambo_puppet_filenames:
            pccard_filenames.append("data/puppet/%s.%s" % (filename, ext))

        for x in range(0, 100):
            pccard_filenames.append("data/motion/motion%d.%s" % (x, ext))

        for filename in pccard_filenames:
            hash_list[get_filename_hash(filename)] = filename

        pccard_filenames = []

    return hash_list


def generate_ddr_song_paths(input_songlist=[], hash_list={}):
    # This is not a complete songlist. It only exists to help find songs that may not be in the game's music database
    # but are still hidden in the filesystem, which should be a rare case.
    ddr_base_songlist = [
        "have",    "that",    "kung",    "smok",    "boom",    "badg",    "lets",    "boys",
        "butt",    "puty",    "bril",    "puty2",   "bril2",   "make",    "make2",   "myfi",
        "stri",    "dubi",    "litt",    "stom",    "hero",    "getu",    "ifyo",    "ibel",
        "star",    "trip",    "para",    "sptr",    "para2",   "elri",    "tubt",    "love",
        "parh",    "ajam",    "clea",    "luvm",    "this",    "thin",    "keep",    "imth",
        "nove",    "nove2",   "inth",    "race",    "jamj",    "begi",    "doyo",    "over",
        "five",    "gamb",    "bein",    "emot",    "sogr",    "sala",    "mix",     "drlo",
        "gmdd",    "melt",    "divi",    "perf",    "rthr",    "dunk",    "deep",    "skaa",
        "spec",    "prin",    "cele",    "grad",    "luvt",    "youm",    "been",    "floj",
        "ther",    "pats",    "quee",    "into",    "inyo",    "geno",    "gent",    "ckee",
        "mach",    "cpar",    "rugg",    "cbri",    "nazo",    "sogr2",   "twen2",   "over2",
        "dunk2",   "rthr2",   "skaa2",   "spec2",   "deep2",   "grad2",   "upan",    "xana",
        "upsi",    "iton",    "soma",    "doit",    "oper",    "volf",    "rock",    "foll",
        "hbut",    "ohni",    "cans",    "mrwo",    "etup",    "hboo",    "damd",    "holi",
        "capt",    "turn",    "flas",    "wond",    "afro",    "endo",    "dyna",    "dead",
        "lase",    "sile",    "rebi",    "dluv",    "djam",    "dgra",    "dgen",    "cpar2",
        "cpar3",   "afte",    "cuti",    "theb",    "virt",    "amcs",    "theg",    "gimm",
        "bumb",    "kher",    "drop",    "stop",    "wild",    "letb",    "sprs",    "hyst",
        "pevo",    "walk",    "pink",    "musi",    "kick",    "only",    "eaty",    "adre",
        "oose",    "seve",    "shak",    "neve",    "youn",    "gotc",    "hhav",    "heat",
        "shoo",    "onet",    "nigh",    "hboy",    "sain",    "ninz",    "baby",    "clim",
        "burn",    "gher",    "naha",    "bfor",    "agai",    "hypn",    "summ",    "hify",
        "hdam",    "hher",    "talk",    "lead",    "teng",    "olic",    "eran",    "lety",
        "your",    "onts",    "getm",    "vide",    "groo",    "midn",    "orio",    "shar",
        "nana",    "kyhi",    "cafe",    "cong",    "nite",    "sexy",    "cats",    "sync",
        "onda",    "dome",    "lupi",    "rhyt",    "them",    "alla",    "ldyn",    "feal",
        "stil",    "ecst",    "abso",    "brok",    "dxyy",    "mrtt",    "tequ",    "iwas",
        "hotl",    "elec",    "peta",    "roma",    "twis",    "ones",    "lbfo",    "beto",
        "ponp",    "mats",    "reme",    "estm",    "noli",    "myge",    "cube",    "abys",
        "sana",    "moon",    "ever",    "movi",    "righ",    "trib",    "oops",    "dive",
        "gain",    "pafr",    "radi",    "inse",    "lcan",    "miam",    "samb",    "dont",
        "leth",    "wayn",    "ialv",    "toge",    "gtof",    "gtup",    "mama",    "frky",
        "lmac",    "club",    "stru",    "fore",    "aliv",    "skyh",    "oflo",    "tipi",
        "idon",    "dril",    "kiss",    "drea",    "lett",    "roov",    "heal",    "look",
        "itri",    "onth",    "styl",    "nori",    "cent",    "lovi",    "ordi",    "ghos",
        "some",    "fant",    "witc",    "oyou",    "ollo",    "offu",    "mira",    "twil",
        "cowg",    "tele",    "just",    "imin",    "etsg",    "byeb",    "then",    "wwwb",
        "maxx",    "true",    "mysw",    "frec",    "sode",    "fire",    "yozo",    "exot",
        "cand",    "ruee",    "kind",    "soin",    "long",    "maxi",    "youl",    "waka",
        "abyl",    "drte",    "esti",    "inam",    "amin",    "swee",    "snow",    "refl",
        "sofa",    "drif",    "itsr",    "stay",    "secr",    "ittl",    "rain",    "unli",
        "toth",    "tsug",    "roll",    "opti",    "noth",    "anta",    "ifee",    "andy",
        "spin",    "tran",    "atus",    "than",    "thew",    "kaku",    "afro3",   "star3",
        "bril3",   "bfor3",   "drop3",   "dyna3",   "hyst3",   "mats3",   "sexy3",   "sprs3",
        "stil3",   "wild3",   "burn3",   "tsug3",   "ecst3",   "sile3",   "nite3",   "gher3",
        "summ3",   "stro",    "didi",    "cari",    "thev",    "tryt",    "iwan",    "cott",
        "thet",    "wast",    "aaro",    "fivs",    "like",    "team",    "what",    "with",
        "anyw",    "memo",    "cras",    "yeby",    "tell",    "vani",    "tomp",    "itr2",
        "jamm",    "logi",    "loo2",    "blas",    "peac",    "imfo",    "shin",    "bom2",
        "ddyn",    "morn",    "ylea",    "dark",    "ilik",    "sand",    "mcut",    "brou",
        "keon",    "mode",    "tomo",    "suns",    "surv",    "laco",    "wewi",    "irre",
        "cart",    "spee",    "issk",    "suga",    "lamo",    "imgo",    "stin",    "thel",
        "game",    "jane",    "mobo",    "belo",    "ledl",    "radu",    "vvvv",    "aaaa",
        "wear",    "idoi",    "colo",    "tayy",    "meal",    "wite",    "froz",    "mess",
        "feel",    "daik",    "maho",    "hold",    "jetw",    "wedd",    "surv3",   "bagg",
        "lege",    "aois",    "mike",    "yncc",    "stoi",    "tars",    "ichi",    "gene",
        "xeno",    "saku",    "rose",    "heav",    "hype",    "laba",    "ddre",    "ripm",
        "airr",    "thef",    "tear",    "seno",    "acro",    "rand",    "funk",    "tryl",
        "itr3",    "loo3",    "kind3",   "frve",    "satn",    "myfa",    "yogo",    "dsmo",
        "badt",    "dsco",    "cant",    "addi",    "itta",    "iwou",    "sigh",    "lcat",
        "lcat2",   "urbo",    "oste",    "frea",    "whey",    "alit",    "stea",    "mize",
        "inee",    "cmon",    "days",    "grin",    "stal",    "getd",    "take",    "teen",
        "wann",    "stup",    "scor",    "ofec",    "allt",    "dcal",    "aven",    "foca",
        "juar",    "stbe",    "bain",    "illi",    "visi",    "dizy",    "vity",    "msic",
        "getb",    "wont",    "deux",    "maxp",    "wan2",    "canb",    "inee2",   "simp",
        "ving",    "ride",    "come",    "parb",    "fory",    "enjo",    "west",    "loco",
        "onem",    "plan",    "ofsu",    "hump",    "mick",    "free",    "stas",    "kids",
        "viva",    "ente",    "sunl",    "rela",    "ine3",    "move",    "rapp",    "shur",
        "ymca",    "supe",    "nout",    "prom",    "inda",    "beli",    "biza",    "ladi",
        "call",    "volt",    "gott",    "fami",    "lyou",    "wait",    "virg",    "rage",
        "chih",    "jama",    "good",    "okok",    "come2",   "eart",    "abs2",    "anly",
        "babx",    "bail",    "bald",    "batt",    "bt4u",    "eyes",    "fdub",    "geti",
        "gorg",    "inff",    "infi",    "ins2",    "kee2",    "kybm",    "madb",    "matj",
        "mean",    "mgs2",    "mind",    "nems",    "oute",    "put3",    "quic",    "san2",
        "swon",    "whas",    "diam",    "smap",    "odor",    "gaku",    "hone",    "kise",
        "tuff",    "chai",    "dizz",    "girl",    "mixe",    "thes",    "yous",    "kunc",
        "lady",    "oody",    "frid",    "hipt",    "midd",    "dipi",    "shou",    "geni",
        "wonn",    "asth",    "bloc",    "busy",    "mich",    "mymy",    "ilen",    "pres",
        "worl",    "opsi",    "iwsu",    "spsp",    "pump",    "fnkm",    "wona",    "craz",
        "myma",    "lose",    "polo",    "oran",    "diff",    "mari",    "tmrr",    "sedu",
        "insi",    "inje",    "pass",    "youg",    "nine",    "ridl",    "mine",    "gtwo",
        "zero",    "rout",    "luvu",    "vjar",    "rten",    "lovd",    "catc",    "voya",
        "flyt",    "hitn",    "mids",    "toej",    "monk",    "istn",    "redr",    "bais",
        "cuca",    "gyru",    "jamd",    "tenr",    "imem",    "itoy",    "remx",    "popn",
        "banz",    "brin",    "hipe",    "letd",    "stck",    "vola",    "choo",    "skrb",
        "inje2",   "doll",    "ifut",    "evrd",    "aaaa2",   "rzon",    "hpan",    "xeph",
        "hima",    "drab",    "curu",    "muge",    "nizi",    "gekk",    "kono",    "mooo",
        "thir",    "dand",    "kage",    "tika",    "unde",    "time",    "rara",    "braz",
        "taur",    "tier",    "sksk",    "okor",    "murm",    "flya",    "inno",    "myon",
        "flow",    "rbow",    "bala",    "gate",    "fold",    "long2",   "mgir",    "alov",
        "sigh2",   "daba",    "toxi",    "waww",    "laba2LA", "jerk",    "fasc",    "lare",
        "punc",    "eace",    "gold",    "glor",    "dayd",    "mond",    "cach",    "driv",
        "qmas",    "stop2",   "dyna2",   "surr",    "sedu2",   "hunt",    "daca",    "give",
        "does",    "chao",    "bred",    "colo2",   "lab3",    "illm",    "fjus",    "tlov",
        "btea",    "wowo",    "dvis",    "hana",    "flow2",   "fasc2",   "comc",    "fain",
        "meag",    "flya2",   "soul",    "gate2",   "moos",    "flow3",   "felw",    "silv",
        "trim",    "fnky",    "leff",    "shiv",    "ikno",    "sinc",    "such",    "theo",
        "onew",    "runi",    "dare",    "trno",    "doyw",    "city",    "bttw",    "sorr",
        "yoex",    "mams",    "chec",    "whyr",    "soss",    "danc",    "galv",    "numb",
        "gett",    "brkf",    "blab",    "prnc",    "sosi",    "temp",    "dscc",    "robo",
        "beau",    "btea2",   "biol",    "hood",    "godi",    "rome",    "rhrn",    "brui",
        "soni",    "onme",    "said",    "jacq",    "heyb",    "step",    "luft",    "cloc",
        "fina",    "gonn",    "hots",    "karm",    "byou",    "risa",    "sign",    "ysme",
        "fara",    "lips",    "conm",    "alie",    "fied",    "mitr",    "mala",    "rasp",
        "bloo",    "agir",    "mber",    "lefr",    "subu",    "unbe",    "prol",    "hook",
        "ofth",    "reas",    "fast",    "ange",    "csto",    "lste",    "unwr",    "dazz",
        "fway",    "alwa",    "infe",    "tlel",    "buty",    "away",    "caug",    "gyps",
        "flik",    "memi",    "unap",    "bmon",    "stim",    "tltl",    "lshi",    "bdow",
        "spar",    "cufo",    "acol",    "conf",    "leti",    "will",    "lits",    "touc",
        "ifly",    "wwlt",    "hand",    "ngon",    "higo",    "tbea",    "bins",    "mwit",
        "trea",    "samu",    "ucha",    "tigh",    "ryou",    "tobe",    "onmy",    "andt",
        "sudd",    "toky",    "orig",    "aint",    "ngoo",    "smac",    "btol",    "firr",
        "unre",    "stah",    "skan",    "hesa",    "cbac",    "sayg",    "feva",    "arou",
        "twom",    "vate",    "venu",    "blin",    "athi",    "wind",    "uber",    "arra",
        "dori",    "unti",    "trix",    "vemb",    "eter",    "dofl",    "volc",    "eday",
        "plut",    "sunr",    "pard",    "swit",    "alth",    "bbbu",    "favo",    "nomo",
        "trus",    "plur",    "lamd",    "votu",    "jupi",    "sunj",    "uran",    "mars",
        "whyn",    "shad",    "gili",    "pose",    "bris",    "amch",    "dtwf",    "dyns",
        "bfov",    "deag",    "sune",    "satu",    "tloc",    "pluf",    "bfos",    "doub",
        "smil",    "puzz",    "leav",    "timh",    "saga",    "cara",    "ontb",    "feee",
        "ghet",    "mcry",    "trac",    "waiu",    "drem",    "disn",    "fotl",    "bibb",
        "ball",    "tiki",    "circ",    "cohm",    "wish",    "spoo",    "hawa",    "heme",
        "bout",    "cmix",    "apir",    "cany",    "chim",    "evry",    "ijus",    "ltle",
        "bare",    "zadd",    "cmar",    "wabe",    "youc",    "stet",    "itsa",    "supc",
        "devi",    "haku",    "flig",    "tick",    "tajh",    "sabe",    "lovy",    "iyhr",
        "staa",    "reac",    "want",    "noma",    "crcs",    "trbu",    "here",    "wine",
        "lift",    "flou",    "taka",    "boyd",    "pute",    "myde",    "umbr",    "caom",
        "niru",    "oclo",    "allg",    "mawo",    "reda",    "feto",    "slac",    "blac",
        "cahe",    "toot",    "wasu",    "ican",    "iran",    "wego",    "youi",    "evda",
        "dane",    "thom",    "stre",    "hetr",    "mmla",    "djgo",    "icei",    "duck",
        "mcmi",    "almy",    "heit",    "happ",    "ucan",    "play",    "dace",    "slip",
        "hora",    "bust",    "dyou",    "obse",    "bigg",    "bene",    "tare",    "sare",
        "slre",    "dacr",    "jube",    "esce",    "sett",    "soyo",    "suhe",    "unit",
        "open",    "mylo",    "opee",    "soun",    "butt2",   "boys2",   "thli",    "ttlg",
        "clos",    "orig2",   "kyou",    "dmin",    "weve",    "synt",    "dubi2",   "getu2",
        "hero2",   "reup",    "weco",    "insp",    "onbo",    "trig",    "danf",    "weca",
        "raci",    "dese",    "sidr",    "thlo",    "habi",    "osak1",   "osak2",   "osak3",
        "xmix1",   "xmix2",   "xmix3",   "xmix4",   "xmix5",   "rint",    "turk",    "jung",
        "blue",    "zerr",    "purp",    "brea",    "sust",    "crgo",    "bigt",    "reso",
        "trav",    "hous",    "ours",    "crim",    "blra",    "chan",    "koko",    "parx",
        "trxs",    "parx2",   "sptx",    "rebx",    "afrx",    "pevx",    "clix",    "petx",
        "feax",    "canx",    "xmax",    "unlx",    "kakx",    "legx",    "ddrx",    "xpar",
        "geis",    "tric",    "seka",    "suki",    "tabi",    "cspa",    "cssp",    "inlo",
        "sttb",    "pori",    "less",    "geis2",   "eoti",    "tone",    "bewi",    "orig3",
        "ropp1",   "prds",    "ille",    "hott1",   "hott2",   "sabe2",   "sidr2",   "dyna4",
        "newg",    "nows",    "taki",    "dist",    "detr",    "drdr",    "imco",    "priv",
        "teme",    "frez",    "haun",    "wick",    "sosp",    "thei",    "jena",    "sacr",
        "wwcm",    "vila",    "clsr",    "iceb",    "daft",    "canu",    "rist",    "pock",
        "nver",    "hung",    "boog",    "gtim",    "vood",    "fego",    "sout",    "twau",
        "curr",    "tame",    "iair",    "ahla",    "down",    "spac",    "rnow",    "ensi",
        "bbay",    "shie",    "lvag",    "bona",    "pork",    "mypr",    "onst",    "laca",
        "ikny",    "inty",    "imag",    "nost",    "hien",    "grav",    "hest",    "tasf",
        "inzo",    "ttim",    "eine",    "kimp",    "shlo",    "dokn",    "lget",    "juda",
        "when",    "abri",    "bene2",   "yyou",    "drec",    "thni",    "geba",    "theh",
        "goda",    "sowa",    "elrt",    "ceye",    "aper",    "youa",    "seul",    "lali",
        "unen",    "letg",    "larc",    "prai",    "clju",    "crco",    "ropp",    "smoo",
        "seco",    "poss",    "huch",    "fifi",    "dada",    "allm",    "cgpr",    "whro",
        "skyi",    "shei",    "tako",    "onra",    "ifyo2",   "ezdo",    "beyo",    "sasu",
        "ropp1",   "ropp2",   "ropp3",   "ropp4",   "aftr",    "delt",    "dirt",    "dumm",
        "oarf",    "sak2",    "thr8",    "yoan",    "rezo",    "zeta",    "anti",    "batf_c",
        "capt2",   "dada2",   "damd2",   "droo",    "etny",    "goru",    "goup_c",  "hide",
        "ifut_c",  "vane",    "tens",    "sueu",    "sudr",    "shwo",    "shng",    "sday",
        "pose2",   "pier",    "nizi_c",  "newd",    "momo",    "melo_c",  "meii",    "maxl_c",
        "lvng_c",  "issk2",   "ifyo3",   "melo",    "maxl",    "lvng",    "goup",    "batf",
        "valk",    "titi",    "evti",    "pier",    "imso",    "toet",    "alst",    "amal",
        "angl",    "bere",    "cbtm",    "chro",    "cone",    "dids",    "dorm",    "dree",
        "feve",    "futu",    "fwer",    "geba",    "haun",    "hbfo",    "hevy",    "hien1",
        "hien2",   "hien3",   "hrtb",    "illf",    "ioio",    "lanj",    "litp",    "meme",
        "merm",    "mesg",    "mprd",    "neph",    "newb",    "nyev1",   "nyev2",   "nyev3",
        "pavo",    "priv",    "prog",    "rebo",    "rthm",    "ryor",    "seul",    "shiz",
        "sigs",    "snow2",   "sson",    "stra",    "sumi",    "tenj",    "toho",    "toky1",
        "toky2",   "toky3",   "trbe",    "trvo",    "twin",    "ublv",    "urlv",    "cosh",
        "koen",    "rens",    "snpr",    "revo",    "gofo",    "keyc",    "puda",    "trxa",
        "brak",    "paks",    "acwo",    "airh",    "anot",    "arms",    "bedr",    "brig",
        "burs",    "cctr",    "chew",    "chil",    "chin",    "ckpp",    "dail",    "deba",
        "dimo",    "dind",    "disp",    "doth",    "elem",    "elys",    "empa",    "engr",
        "fndw",    "furi",    "fuuf",    "gaia",    "hevy2",   "hosh",    "hyen",    "iman",
        "ixix",    "jojo",    "joke",    "kara",    "kike",    "koih",    "lanj2",   "lond",
        "magn",    "maji",    "mawa",    "meum",    "miga",    "mmme",    "mobu",    "mura",
        "nagi",    "nblw",    "negr",    "niji",    "okom",    "oren",    "oron",    "ostt",
        "pran",    "prte",    "puni",    "raki",    "revn",    "rint2",   "rola",    "rryu",
        "scho",    "seit",    "sola",    "sota",    "soth",    "sous",    "span",    "sque",
        "stel",    "sthe",    "stoa",    "stul",    "suca",    "sumf",    "swra",    "synf",
        "todo",    "tpch",    "trbl",    "tuke",    "twog",    "umum",    "vega",    "wifa",
        "wisi",    "wwve",    "yaco",    "yaky",    "yama",    "zutt",    "adul",    "akhu",
        "aozo",    "asai",    "atoz",    "awak",    "awao",    "ayak",    "bada",    "baku",
        "bamb",    "basb",    "bbme",    "bibi",    "boku",    "ccch",    "chea",    "choc",
        "cive",    "cleo",    "cody",    "czgt",    "dete",    "dkdk",    "doca",    "dong",
        "dopa",    "edmj",    "egoi",    "eltr",    "endr",    "esed",    "fiel",    "fksb",
        "foto",    "ftsy",    "fuji",    "geki",    "gens",    "gogo",    "hakt",    "hbfo2",
        "hlat",    "hlye",    "hnmr",    "home",    "idol",    "intb",    "joma",    "kaiy",
        "kawa",    "kira",    "kuro",    "llcu",    "luck",    "maam",    "mayu",    "miku",
        "mine2",   "miso",    "mrps",    "myco",    "myhr",    "nage",    "nekn",    "niko",
        "noil",    "onna",    "orrs",    "osen",    "oslv",    "otom",    "ovtp",    "papi",
        "peit",    "pooc",    "poss2",   "pran2",   "ptay",    "rair",    "raku",    "rema",
        "rusy",    "sabl",    "sakm",    "sans",    "scar",    "sedm",    "setu",    "shik",
        "ssca",    "ssst",    "stfa",    "stfa2",   "strb",    "strg",    "sumd",    "syak",
        "syun",    "tenk",    "tiho",    "tnaw",    "totu",    "tsub",    "wada",    "wech",
        "beat",    "tota",
    ]

    songlist = ddr_base_songlist if not input_songlist else input_songlist

    for song_id in songlist:
        for ext in common_extensions:
            for part in ddr_common_parts:
                filename = "data/mdb/%s/%s_%s.%s" % (song_id, song_id, part, ext)
                hash_list[get_filename_hash(filename)] = filename

            filename = "data/mdb/%s/all.%s" % (song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            filename = "data/mdb/%s/%s.%s" % (song_id, song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            filename = "data/ja/music/%s/%s.%s" % (song_id, song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            filename = "ja/music/%s/%s.%s" % (song_id, song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            filename = "music/%s/%s.%s" % (song_id, song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            filename = "%s/%s.%s" % (song_id, song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            filename = "%s.%s" % (song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            filename = "mus_%s.%s" % (song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            filename = "mus_%s/mus_%s.%s" % (song_id, song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            filename = "%s_rec.%s" % (song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            filename = "rec/%s_rec.%s" % (song_id, ext)
            hash_list[get_filename_hash(filename)] = filename

            for a in 'sdab':
                for b in 'sdab':
                    filename = "%s_%c%c.%s" % (song_id, a, b, ext)
                    hash_list[get_filename_hash(filename)] = filename

    return hash_list


# Functions used to parse DDR data
def parse_rembind_filenames(data, hash_list={}):
    entries = len(data) // 0x30

    for i in range(entries):
        filename_len = 0

        while filename_len + 0x10 < 0x30 and data[i*0x30+0x10+filename_len] != 0:
            filename_len += 1

        orig_filename = data[i*0x30+0x10:i*0x30+0x10+filename_len].decode('ascii').strip('\0')

        for ext in common_extensions:
            filename = "data/%s.%s" % (orig_filename, ext)
            hash_list[get_filename_hash(filename)] = filename

            for region in ddr_common_regions:
                for region2 in ddr_common_regions:
                    if region2 == region:
                        continue

                    needle = "%s/" % region

                    if needle not in orig_filename:
                        continue

                    filename = "data/%s.%s" % (orig_filename, ext)
                    filename = filename.replace(needle, "%s/" % region2)
                    hash_list[get_filename_hash(filename)] = filename

    return hash_list


# Functions used to parse GFDM data
def parse_group_list_filenames(data, hash_list={}):
    for i in range(len(data) // 0x30):
        filename_len = 0

        while filename_len < 0x30 and data[i*0x30+filename_len] != 0:
            filename_len += 1

        filename = data[i*0x30:i*0x30+filename_len].decode('ascii').strip('\0')

        for ext in common_extensions:
            path = "%s.%s" % (filename, ext)
            hash_list[get_filename_hash(path)] = path

        filename = os.path.splitext(filename)[0]
        for ext in common_extensions:
            path = "%s.%s" % (filename, ext)
            hash_list[get_filename_hash(path)] = path

    return hash_list


# Functions used to parse Dancemaniax data
def parse_group_list_filenames_dmx(data, hash_list={}):
    entry_size = 0x20
    cnt = int.from_bytes(data[:4], byteorder="little")
    for i in range(cnt):
        filename_len = 0

        while filename_len < entry_size and data[i*entry_size+filename_len] != 0:
            filename_len += 1

        filename = data[i*entry_size:i*entry_size+filename_len].decode('ascii').strip('\0')

        hash_list[get_filename_hash(filename)] = filename

        for ext in common_extensions:
            path = "%s.%s" % (filename, ext)
            hash_list[get_filename_hash(path)] = path

        filename = os.path.splitext(filename)[0]
        for ext in common_extensions:
            path = "%s.%s" % (filename, ext)
            hash_list[get_filename_hash(path)] = path

    data = data[0x10+0x20*cnt:]
    entry_size = 0x30
    for i in range(len(data) // entry_size):
        filename_len = 0

        while filename_len < entry_size and data[i*entry_size+filename_len] != 0:
            filename_len += 1

        filename = data[i*entry_size:i*entry_size+filename_len].decode('ascii').strip('\0')
        hash_list[get_filename_hash(filename)] = filename

        for ext in common_extensions:
            path = "%s.%s" % (filename, ext)
            hash_list[get_filename_hash(path)] = path

        filename = os.path.splitext(filename)[0]
        for ext in common_extensions:
            path = "%s.%s" % (filename, ext)
            hash_list[get_filename_hash(path)] = path

    return hash_list


# Common readers
def parse_mdb_filenames(data, entry_size, hash_list={}):
    songlist = []

    try:
        for i in range(len(data) // entry_size):
            if data[i*entry_size] == 0:
                break

            songlist.append(data[i*entry_size:i*entry_size+6].decode('ascii').strip('\0').strip())
    except:
        pass

    return generate_ddr_song_paths(songlist, hash_list)


# File table readers
def read_file_table_ddr(filename, table_offset):
    files = []

    with open(filename, "rb") as infile:
        infile.seek(table_offset, 0)

        while True:
            filename_hash = int.from_bytes(infile.read(4), byteorder="little")
            offset = int.from_bytes(infile.read(2), byteorder="little")
            flag_loc = int.from_bytes(infile.read(2), byteorder="little")
            flag_comp = int.from_bytes(infile.read(1), byteorder="little")
            flag_enc = int.from_bytes(infile.read(1), byteorder="little")
            unk = int.from_bytes(infile.read(2), byteorder="little")
            filesize = int.from_bytes(infile.read(4), byteorder="little")

            if filename_hash == 0xffffffff and offset == 0xffff:
                break

            if filename_hash == 0 and offset == 0 and filesize == 0:
                break

            files.append({
                'idx': len(files),
                'filename_hash': filename_hash,
                'offset': offset * 0x800,
                'filesize': filesize,
                'flag_loc': flag_loc,
                'flag_comp': flag_comp,
                'flag_enc': flag_enc,
                'unk': unk,
            })

    return files


def read_file_table_gfdm(filename, table_offset, forced_secondary=False):
    files = []

    with open(filename, "rb") as infile:
        infile.seek(table_offset, 0)

        while True:
            filename_hash = int.from_bytes(infile.read(4), byteorder="little")
            offset = int.from_bytes(infile.read(4), byteorder="little")
            filesize = int.from_bytes(infile.read(4), byteorder="little")
            flag = int.from_bytes(infile.read(4), byteorder="little")

            if filesize == 0:
                continue

            if filename_hash == 0xffffffff and offset == 0xffffffff:
                break

            files.append({
                'idx': len(files),
                'filename_hash': filename_hash,
                'offset': offset,
                'filesize': filesize,
                'flag_loc': 0 if not forced_secondary else 1,
                'flag_comp': 0,
                'flag_enc': 0,
                'unk': 0,
                '_flag': flag,
            })

    return files


def read_file_table_gfdm2(filename, table_offset, forced_secondary=False):
    files = []

    with open(filename, "rb") as infile:
        infile.seek(table_offset, 0)

        while True:
            filename_hash = int.from_bytes(infile.read(4), byteorder="little")
            offset = int.from_bytes(infile.read(4), byteorder="little")
            flag = int.from_bytes(infile.read(4), byteorder="little")
            filesize = int.from_bytes(infile.read(4), byteorder="little")

            if filename_hash in [0, 0xffffffff] and offset in [0, 0xffffffff]:
                break

            if filesize == 0:
                continue

            files.append({
                'idx': len(files),
                'filename_hash': filename_hash,
                'offset': (offset << 11) & 0x3fffff if offset >= 0x8000 else offset * 0x800,
                'filesize': filesize,
                'flag_loc': 1 if offset >= 0x8000 or forced_secondary else 0,
                'flag_comp': 1,
                'flag_enc': 0,
                'unk': 0,
                '_flag': flag,
            })

    return files


def get_file_data(input_folder, fileinfo, enckey=None):
    game_filename = None
    card_filename = None

    game_path = os.path.join(input_folder, "GAME.DAT")
    game2_path = os.path.join(input_folder, "GQ883JA.DAT")
    game3_path = os.path.join(input_folder, "GQ886JA.DAT")
    game4_path = os.path.join(input_folder, "GE929JA.DAT")

    if os.path.exists(game_path):
        game_filename = game_path

    if os.path.exists(game2_path):
        game_filename = game2_path

    if os.path.exists(game3_path):
        game_filename = game3_path

    if os.path.exists(game4_path):
        game_filename = game4_path

    pccard_path = os.path.join(input_folder, "PCCARD.DAT")
    pccard1_path = os.path.join(input_folder, "PCCARD1.DAT")
    card_path = os.path.join(input_folder, "CARD.DAT")
    card1_path = os.path.join(input_folder, "CARD1.DAT")
    card2_path = os.path.join(input_folder, "GQ883CAR.DAT")
    card3_path = os.path.join(input_folder, "GE929CAR.DAT")

    if os.path.exists(pccard_path):
        card_filename = pccard_path

    if os.path.exists(pccard1_path):
        card_filename = pccard1_path

    elif os.path.exists(card_path):
        card_filename = card_path

    elif os.path.exists(card1_path):
        card_filename = card1_path

    elif os.path.exists(card2_path):
        card_filename = card2_path

    elif os.path.exists(card3_path):
        card_filename = card3_path

    game = open(game_filename, "rb") if game_filename else None
    card = open(card_filename, "rb") if card_filename else None

    data = None
    if fileinfo['flag_loc'] == 1:
        if card:
            card.seek(fileinfo['offset'])
            data = bytearray(card.read(fileinfo['filesize']))

    else:
        if game:
            game.seek(fileinfo['offset'])
            data = bytearray(game.read(fileinfo['filesize']))

    if data and fileinfo['flag_enc'] != 0 and enckey:
        data = decrypt_data(data, enckey)

    if data and fileinfo['flag_comp'] == 1:
        try:
            data = decode_lz(data, len(data))

        except IndexError:
            pass

    return bytearray(data)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', help='Input folder', default=None, required=True)
    parser.add_argument('--output', help='Output folder', default="output")
    parser.add_argument('--key', help='Encryption key', choices=['EXTREME', 'EURO2', 'MAX2', 'DDR5', 'MAMBO'])
    parser.add_argument('--type', help='Game Type', choices=['ddr', 'gfdm-old', 'gfdm-old2', 'gfdm-old3', 'gfdm-old4', 'gfdm-old5', 'gfdm', 'mambo', 'dmx'])
    parser.add_argument('--no-metadata', help='Do not save metadata file', default=False, action='store_true')
    parser.add_argument('--bruteforce-ddr', help='Bruteforce DDR songs using an internal database (SLOW!)',
                        default=False, action='store_true')
    parser.add_argument('--input-filenames', help='Input filename lookup JSON', default=None)

    args, _ = parser.parse_known_args()

    if args.output and not os.path.exists(args.output):
        os.makedirs(args.output)

    parse_internal_filenames = True

    hash_list = {}
    if args.input_filenames is not None:
        parse_internal_filenames = False
        for filename in json.load(open(args.input_filenames, "r")):
            hash_list[get_filename_hash(filename)] = filename

    else:
        hash_list = generate_data_paths()

        if args.bruteforce_ddr:
            hash_list = generate_ddr_song_paths(hash_list=hash_list)

    files = []
    if args.type in ["ddr", "mambo"]:
        files = read_file_table_ddr(os.path.join(args.input, "GAME.DAT"), 0xFE4000)

    elif args.type == "gfdm-old":
        files = read_file_table_gfdm(os.path.join(args.input, "GAME.DAT"), 0x180000)

        if os.path.exists("PCCARD1.DAT"):
            files += read_file_table_gfdm(os.path.join(args.input, "PCCARD1.DAT"), 0, True)

    elif args.type == "gfdm":
        files = read_file_table_gfdm(os.path.join(args.input, "GAME.DAT"), 0x198000)

        if os.path.exists("PCCARD1.DAT"):
            files += read_file_table_gfdm(os.path.join(args.input, "PCCARD1.DAT"), 0, True)

    elif args.type == "dmx":
        files = read_file_table_gfdm(os.path.join(args.input, "GAME.DAT"), 0xFF0000)

    elif args.type == "gfdm-old2":
        files = read_file_table_gfdm2(os.path.join(args.input, "GAME.DAT"), 0xFE4000)

        if os.path.exists("PCCARD1.DAT"):
            files += read_file_table_gfdm2(os.path.join(args.input, "PCCARD1.DAT"), 0, True)

    elif args.type == "gfdm-old3":
        files = read_file_table_gfdm2(os.path.join(args.input, "GQ883JA.DAT"), 0x178000)

    elif args.type == "gfdm-old4":
        files = read_file_table_gfdm2(os.path.join(args.input, "GQ886JA.DAT"), 0x100000)

    elif args.type == "gfdm-old5":
        files = read_file_table_gfdm2(os.path.join(args.input, "GE929JA.DAT"), 0x1b8000)

    else:
        print("Unknown format!")
        exit(1)

    for idx, fileinfo in enumerate(files):
        if fileinfo['filename_hash'] == 0x45fda52a or (fileinfo['filename_hash'] in hash_list and hash_list[fileinfo['filename_hash']].endswith("config.dat")): # Just try to decrypt any config.dat
            try:
                config = decrypt_data_internal(get_file_data(args.input, fileinfo, args.key), "/s573/config.dat")
                open(os.path.join(args.output, "_config.txt"), "wb").write(config)

                config = config.decode('shift-jis')

                print("Configuration file decrypted:")
                print(config)

                for l in config.split('\n'):
                    if l.startswith("conversion "):
                        # Dumb way of doing this but I'm lazy
                        for path in l[len("conversion "):].split(':'):
                            if path.startswith('/'):
                                path = path[1:]

                            hash_list[get_filename_hash(path)] = path

            except:
                pass

        if parse_internal_filenames and fileinfo['filename_hash'] in hash_list:
            if args.type in ["ddr", "mambo"]:
                if hash_list[fileinfo['filename_hash']] in ["data/tex/rembind.bin", "data/all/texbind.bin"]:
                    hash_list = parse_rembind_filenames(get_file_data(args.input, fileinfo, args.key), hash_list)

            if args.type == "ddr":
                if hash_list[fileinfo['filename_hash']] == "data/mdb/mdb.bin":
                    hash_list = parse_mdb_filenames(get_file_data(args.input, fileinfo, args.key), 0x2c, hash_list)
                    hash_list = parse_mdb_filenames(get_file_data(args.input, fileinfo, args.key), 0x30, hash_list)
                    hash_list = parse_mdb_filenames(get_file_data(args.input, fileinfo, args.key), 0x64, hash_list)
                    hash_list = parse_mdb_filenames(get_file_data(args.input, fileinfo, args.key), 0x6c, hash_list)
                    hash_list = parse_mdb_filenames(get_file_data(args.input, fileinfo, args.key), 0x80, hash_list)

                elif hash_list[fileinfo['filename_hash']] in ["data/mdb/ja_mdb.bin", "data/mdb/ka_mdb.bin",
                                                              "data/mdb/aa_mdb.bin", "data/mdb/ea_mdb.bin",
                                                              "data/mdb/ua_mdb.bin"]:
                    hash_list = parse_mdb_filenames(get_file_data(args.input, fileinfo, args.key), 0x38, hash_list)

            elif args.type == "mambo":
                if hash_list[fileinfo['filename_hash']] == "data/mdb/mdb.bin":
                    hash_list = parse_mdb_filenames(get_file_data(args.input, fileinfo, args.key), 0x2c, hash_list)

            elif args.type in ["gfdm", "gfdm-old"]:
                if hash_list[fileinfo['filename_hash']] == "group_list.bin":
                    hash_list = parse_group_list_filenames(get_file_data(args.input, fileinfo, args.key), hash_list)

            elif args.type == "dmx":
                if hash_list[fileinfo['filename_hash']] == "ja_mdb.bin":
                    hash_list = parse_mdb_filenames(get_file_data(args.input, fileinfo, args.key)[0x10:], 0x24, hash_list)
                    hash_list = parse_mdb_filenames(get_file_data(args.input, fileinfo, args.key), 0x38, hash_list)

                elif hash_list[fileinfo['filename_hash']] == "arrangement_data.bin":
                    hash_list = parse_group_list_filenames_dmx(get_file_data(args.input, fileinfo, args.key), hash_list)

    game_filename = None
    card_filename = None

    game_path = os.path.join(args.input, "GAME.DAT")
    game2_path = os.path.join(args.input, "GQ883JA.DAT")
    game3_path = os.path.join(args.input, "GQ886JA.DAT")
    game4_path = os.path.join(args.input, "GE929JA.DAT")

    if os.path.exists(game_path):
        game_filename = game_path

    if os.path.exists(game2_path):
        game_filename = game2_path

    if os.path.exists(game3_path):
        game_filename = game3_path

    if os.path.exists(game4_path):
        game_filename = game4_path

    pccard_path = os.path.join(args.input, "PCCARD.DAT")
    pccard1_path = os.path.join(args.input, "PCCARD1.DAT")
    card_path = os.path.join(args.input, "CARD.DAT")
    card1_path = os.path.join(args.input, "CARD1.DAT")
    card2_path = os.path.join(args.input, "GQ883CAR.DAT")
    card3_path = os.path.join(args.input, "GE929CAR.DAT")

    if os.path.exists(pccard_path):
        card_filename = pccard_path

    if os.path.exists(pccard1_path):
        card_filename = pccard1_path

    elif os.path.exists(card_path):
        card_filename = card_path

    elif os.path.exists(card1_path):
        card_filename = card1_path

    elif os.path.exists(card2_path):
        card_filename = card2_path

    elif os.path.exists(card3_path):
        card_filename = card3_path

    used_regions = {}

    if game_filename:
        used_regions[0] = {
            0: {
                'filename': game_filename,
                'data': [0] * os.path.getsize(game_filename),
            },
        }

    if card_filename:
        used_regions[1] = {
            'filename': card_filename,
            'data': [0] * os.path.getsize(card_filename),
        }

    for idx, fileinfo in enumerate(files):
        output_filename = "_output_%08x.bin" % (fileinfo['filename_hash'])

        if fileinfo['filename_hash'] in hash_list:
            output_filename = hash_list[fileinfo['filename_hash']]

            if output_filename.startswith("/"):
                output_filename = "_" + output_filename[1:]

            while output_filename.startswith("../"):
                output_filename = output_filename[3:]

        else:
            print("Unknown hash %08x" % fileinfo['filename_hash'], output_filename)

        files[idx]['filename'] = output_filename

        output_filename = os.path.join(args.output, output_filename)

        # Mark region as used
        region_size = fileinfo['offset'] + fileinfo['filesize']

        # if (region_size % 0x800) != 0:
        #     region_size += 0x800 - (region_size % 0x800)

        # used_regions[fileinfo['flag_loc']]['data'][fileinfo['offset']:region_size] = [1] * (region_size - fileinfo['offset'])

        if os.path.exists(output_filename):
            continue

        filepath = os.path.dirname(output_filename)
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        print(fileinfo)
        print("Extracting", output_filename)
        with open(output_filename, "wb") as outfile:
            data = get_file_data(args.input, fileinfo, args.key)

            if output_filename.endswith(".lz"):
                data = decode_lz(data, len(data))

            outfile.write(data)

    if not args.no_metadata:
        json.dump({'files': files}, open(os.path.join(args.output, "_metadata.json"), "w"), indent=4)


    # unreferenced_path = os.path.join(args.output, "#unreferenced")
    # for k in used_regions:
    #     data = bytearray(open(os.path.join(args.input, used_regions[k]['filename']), "rb").read())

    #     # Find and dump unreferenced regions with data in them
    #     start = 0
    #     while start < len(used_regions[k]['data']):
    #         if used_regions[k]['data'][start] == 0:
    #             end = start

    #             while end < len(used_regions[k]['data']) and used_regions[k]['data'][end] == 0:
    #                 end += 1

    #             if len([x for x in data[start:end] if x != 0]) > 0 and len([x for x in data[start:end] if x != 0xff]) > 0:
    #                 if not os.path.exists(unreferenced_path):
    #                     os.makedirs(unreferenced_path)

    #                 print("Found unreferenced data @ %08x - %08x" % (start, end))

    #                 open(os.path.join(unreferenced_path, "%d_%08x.bin" % (k, start)), "wb").write(data[start:end])

    #             start = end + 1

    #         else:
    #             start += 1


if __name__ == "__main__":
    main()
