#!/usr/bin/env python3

"""
Geometry converter from Cheetah to proc format and vice versa
python3 modification.py <mode> <in_geom> <out_geom> <path to data>

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
    parser.add_argument('const', type=int, help="Constant that would be add to ss")
    parser.add_argument('input_geom', type=str, help="Input geometry file")
    parser.add_argument('output_geom', type=str, help="Output geometry file")
    
    return parser.parse_args()

if __name__ == "__main__":
    print('It is a geometry converter\n')
    args = parse_cmdline_args()

    
    n = args.const # mode of the converter
    in_geom_file_name = args.input_geom
    out_geom_file_name = args.output_geom
    
    with open(in_geom_file_name, 'r') as in_geom, open(out_geom_file_name, 'w') as out_geom:
        for line in in_geom:
            
            s = line.split(' = ')[0].split('/')
            print(s)
            if len(s) == 2 and s[1] in ('min_ss', 'max_ss'):
                s = line.split(' = ')
                print(s)
                if len(s) == 2:
                    v = int(s[1]) + n
                    if v > 5631:
                        v -= 5632
                    print(v)
                    out_geom.write('%s = %d\n'%(s[0], v))              
            else:
                print(line)
                out_geom.write(line)