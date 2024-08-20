#!/usr/bin/env python3
import argparse
import os
import sys

"""
python3 string_mask_for_Cheetah_geom.py agipd_2450_v4.geom
"""

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass


def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('geom_file', type=str, help="Input geometry file")
    parser.add_argument('x_pixel', type=int, help="Number of x pixels from edges that is necessary to mask")
    parser.add_argument('-y','--y_pixel', type=int, help="Number of y pixels from edges that is necessary to mask")

    return parser.parse_args()

def bcopy_file(file):
    prefix, suffix = file.split('.')
    file_copy = prefix + '_copy.' + suffix
    h5r = open(file,'rb')
    f2 = open(file_copy,'wb')
    lines = h5r.readlines()

    for line in lines:
        f2.write(line)

    h5r.close()
    f2.close()

    return file_copy

if __name__ == "__main__":

    args = parse_cmdline_args()

    geom_file_name = args.geom_file
    x_pix = args.x_pixel

    if args.y_pixel is None:
        y_pix = x_pix #ss
    else:
        y_pix = args.y_pixel

    d_pix = {'min_fs' : x_pix, 'min_ss' : y_pix, 'max_fs' : -x_pix, 'max_ss' : -y_pix}

    new_geom_file_name = bcopy_file(geom_file_name)
    in_geom = open(geom_file_name, 'r+')  # from

    out_geom = open(new_geom_file_name, 'a+')
    min_ss = None
    min_fs = None
    max_ss = None
    max_fs = None
    num_panel = None
    sub_panel = None

    for line in in_geom:


        if line.startswith('p') and not(line.startswith(';')) and '/' in line: # p0a0/dim3 = fs
            s = line.split(' = ') # [p0a0/min_fs; 0]    [p0a0/dim3; fs]
            l = line.split('/') #   [p0a0; min_fs = 0]  [p0a0; dim3 = fs]
            s1 = s[0].split('/') #  [p0a0; min_fs]      [p0a0; dim3]

            num_panel, sub_panel = s1[0].split('a')
            if len(s1) == 2 and 'min_ss' in s1[1]:
                if len(s) == 2:
                    min_ss = int(s[1])

            if len(s1) == 2 and 'min_fs' in s1[1]:
                if len(s) == 2:
                    min_fs = int(s[1])

            if len(s1) == 2 and 'max_ss' in s1[1]:
                if len(s) == 2:
                    max_ss = int(s[1])

            if len(s1) == 2 and 'max_fs' in s1[1]:
                if len(s) == 2:
                    max_fs = int(s[1])


            if min_ss is not None and min_fs is not None and max_ss is not None and max_fs is not None and num_panel is not None and sub_panel is not None:
                #print(num_panel, sub_panel, max_fs, max_ss, min_ss, min_fs)
                chunk = '''\nbad_{}v1{}/min_fs = {}\nbad_{}v1{}/min_ss = {}\nbad_{}v1{}/max_fs = {}\nbad_{}v1{}/max_ss = {}\n\nbad_{}h1{}/min_fs = {}\nbad_{}h1{}/min_ss = {}\nbad_{}h1{}/max_fs = {}\nbad_{}h1{}/max_ss = {}\n\nbad_{}v2{}/min_fs = {}\nbad_{}v2{}/min_ss = {}\nbad_{}v2{}/max_fs = {}\nbad_{}v2{}/max_ss = {}\n\nbad_{}h2{}/min_fs = {}\nbad_{}h2{}/min_ss = {}\nbad_{}h2{}/max_fs = {}\nbad_{}h2{}/max_ss = {}\n'''.format(num_panel, sub_panel, min_fs, num_panel, sub_panel, min_ss, num_panel, sub_panel, max_fs, num_panel, sub_panel, min_ss + d_pix['min_ss'],
                    num_panel, sub_panel, min_fs, num_panel, sub_panel, min_ss, num_panel, sub_panel, min_fs + d_pix['min_fs'], num_panel, sub_panel, max_ss,
                    num_panel, sub_panel, min_fs, num_panel, sub_panel, max_ss + d_pix['max_ss'], num_panel, sub_panel, max_fs, num_panel, sub_panel, max_ss,
                    num_panel, sub_panel, max_fs + d_pix['max_fs'], num_panel, sub_panel, min_ss, num_panel, sub_panel, max_fs, num_panel, sub_panel, max_ss)
                
                #print(chunk)
                out_geom.write(chunk)
                min_ss = None
                min_fs = None
                max_ss = None
                max_fs = None
                num_panel = None
                sub_panel = None



    in_geom.close()
    out_geom.close()