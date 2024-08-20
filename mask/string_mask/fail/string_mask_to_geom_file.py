#!/usr/bin/env python3
import argparse
import os
import sys

"""
blablabla
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
    parser.add_argument('y_pixel', type=int, help="Number of y pixels from edges that is necessary to mask")

    return parser.parse_args()

if __name__ == "__main__":

    args = parse_cmdline_args()

    geom_file_name = args.geom_file
    x_pix = args.x_pixel
    y_pix = args.y_pixel


    d_pix = {'min_fs' : x_pix, 'min_ss' : y_pix, 'max_fs' : -x_pix, 'max_ss' : -y_pix}


    in_geom = open(geom_file_name, 'r+')  # from
    out_geom = open('agipd_2450_vds_v4_new.geom', 'w+')

    for line in in_geom:
        if line.startswith('p') and not(line.startswith(';')) and '/' in line: # p0a0/dim3 = fs
            s = line.split(' = ') # [p0a0/min_fs; 0]    [p0a0/dim3; fs]
            l = line.split('/') #   [p0a0; min_fs = 0]  [p0a0; dim3 = fs]
            s1 = s[0].split('/') #  [p0a0; min_fs]      [p0a0; dim3]
            
            out_geom.write(line)
            if len(s1) == 2 and s1[1] in ('min_ss', 'min_fs', 'max_ss', 'max_fs'):
                if len(s) == 2:
                    v = int(s[1]) + d_pix[s1[1]]
                    
                    out_geom.write('%s = %d\n'%('bad_'+s[0], v))
            elif len(s1) == 2 and s1[1] in ('dim1', 'dim2', 'dim3'):
                out_geom.write('%s\n'%('bad_' + line.strip()))
            else:
                out_geom.write(line)
        else:
            out_geom.write(line)

    in_geom.close()
    out_geom.close()