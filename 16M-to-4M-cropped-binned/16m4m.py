#!/usr/bin/env python3

"""
Geometry converter from 16M to 4M crooped or binned format and vice versa for Eiger16M
python3 16m4m.py <mode> -i <in_geom> -o <out_name> -m <mask> -mh5 <path to data in mask>
Ex., path to data = /entry_1/instrument_1/detector_1/data
"""

import sys
import os
from datetime import date
import argparse
import re

os.nice(0)



class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    
    parser.add_argument('-i', type=str, help="Input geometry file")
    parser.add_argument('-o', type=str, help="Output geometry file")
    parser.add_argument("--g4M_c", default=False, action="store" , help="Use this flag if you want to create 4M cropped geometry")
    parser.add_argument("--g4M_b", default=False, action="store" , help="Use this flag if you want to create 4M binend geometry")
    parser.add_argument('-mask', '--mask', type=str, help="Mask")
    parser.add_argument('-mh5', '--mh5', type=str, help="The hdf5 path to data in mask")
    return parser.parse_args()

if __name__ == "__main__":
    print('It is a geometry converter\n')
    args = parse_cmdline_args()

    mask = None
    path_in_mask = None
    
    in_geom_file_name = args.i
    out_geom_file_name = args.o
    cropped_new = {"min_ss": 0, "min_fs":0, "max_ss":2161, "max_fs":2067}
    
    cropped_old = {"min_ss": 0, "min_fs":0, "max_ss":0, "max_fs":0}

    if args.mask is not None:
        mask = args.mask

    if args.mh5 is not None:
        path_in_mask = args.mh5

    ss_fs = ["min_ss","min_fs","max_ss", "max_fs"]
    corner = ["corner_x", "corner_y"]
    shift = {"corner_x":0, "corner_y":0}
    shift_fot_corner = {"corner_x": "max_fs", "corner_y": "max_ss"}

    in_geom = open(in_geom_file_name, 'r')  # from
    out_geom = open(out_geom_file_name, 'w') # to
    
    today = date.today()
    out_geom.write('; This geometry file {} was made from {}, {}\n'.format(out_geom_file_name, in_geom_file_name,today.strftime("%d-%b-%Y")))

    if args.g4M_c:
        out_geom2 = open(os.path.join(os.path.dirname(out_geom_file_name),"minus_shift_" + os.path.basename(out_geom_file_name)), 'w')
        for line in in_geom:
            if not line.startswith(";") and line.startswith("mask_file ="):
                if mask is not None:
                    newline = "mask_file = {}\n".format(mask)
                    out_geom.write(newline)
                    
                else:
                    out_geom.write("; " + line)
                    
                    print("WARNING: provide geometry file with mask file!\n")

            elif not line.startswith(';') and line.startswith("mask = "):
                if mask is not None:
                    newline = "mask = {}\n".format(path_in_mask)
                    out_geom.write(newline)
                    
                else:
                    out_geom.write("; "+line)
                    
                    print("WARNING: provide geometry file with path to mask\n")
            else:
                st = line.split(' = ')
                s = st[0].split('/')
                if len(s) == 2 and s[1] in ss_fs and not line.startswith(";"):
                    newline = s[0] + "/"+s[1] + " = {}\n".format(cropped_new[s[1]])
                    cropped_old[s[1]] = float(re.search(r'[-\d.]*\d+', st[1]).group())
                    out_geom.write(newline)
                    
                elif len(s) == 2 and s[1] in corner and not line.startswith(";"):
                    
                    shift[s[1]] = (cropped_old[shift_fot_corner[s[1]]] - cropped_new[shift_fot_corner[s[1]]]) // 2.0
                    
                    corner_value = float(re.search(r'[-\d.]*\d+', st[1]).group())
                    
                    newline = s[0] + "/"+s[1] + " = {}\n".format(corner_value + shift[s[1]])
                    
                    out_geom.write(newline)
                    
                else:
                    out_geom.write(line)
                    
        print("Finished!\n")

    if args.g4M_b:
        for line in in_geom:
            if not line.startswith(";") and line.startswith("res = "):
                res = float(re.search(r'\d+[.\d]*', line).group())
                newline = "res = {}\n".format(res/2)
                out_geom.write(newline)
            elif not line.startswith(";") and line.startswith("mask_file ="):
                if mask is not None:
                    newline = "mask_file = {}\n".format(mask)
                    out_geom.write(newline)
                    
                else:
                    out_geom.write("; " + line)
                    print("WARNING: provide geometry file with mask file!\n")

            elif not line.startswith(';') and line.startswith("mask = "):
                if mask is not None:
                    newline = "mask = {}\n".format(path_in_mask)
                    out_geom.write(newline)
                    
                else:
                    out_geom.write("; "+line)
                    print("WARNING: provide geometry file with path to mask\n")
            else:
                st = line.split(' = ')
                s = st[0].split('/')
                if len(s) == 2 and s[1] in ss_fs and not line.startswith(";"):
                    value = (int(re.search(r'[-\d.]*\d+', st[1]).group()))//2 # +1 
                    newline = st[0] + " = {}\n".format(value)
                    out_geom.write(newline)
                    
                elif len(s) == 2 and s[1] in corner and not line.startswith(";"):
                    
                    corner_value = float(re.search(r'[-\d.]*\d+', st[1]).group())
                    newline = st[0] + " = {}\n".format(int(corner_value/2))
                    out_geom.write(newline)
                    
                else:
                    out_geom.write(line)
        print("Finished!\n")
        


