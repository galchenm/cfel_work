#!/usr/bin/env python3
# coding: utf8

"""


python3 region_parsing.py -i all_runs.stream -o p8snr6.stream -f r0096

Input: stream file with all patterns
Ouput: stream file with indexed patterns
"""


import os
import sys
import h5py as h5
import subprocess
import re
import argparse
from collections import defaultdict
import pandas as pd


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i', type=str, help="Input stream file")
    parser.add_argument('-o', type=str, help='Output stream file')
    parser.add_argument('-x0', type=float, help='x0')
    parser.add_argument('-y0', type=float, help='y0')
    parser.add_argument('-r', type=float, help='r')
    return parser.parse_args()


def parsing_stream(input_stream, output_stream, x0, y0, r):
    out = open(output_stream, 'w')

    with open(input_stream, 'r') as stream:
        reading_chunk = False
        x = None
        y = None
        
        


        for line in stream:

            if line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                found_pattern = False
                chunk = line

            elif line.strip() == '----- End chunk -----':
                reading_chunk = False
                chunk += line
                if found_pattern:
                    out.write(chunk)
                
            elif reading_chunk:
                chunk += line
                if line.startswith("predict_refine/det_shift "):
                    print(re.findall(r"[-]*[\d.]+\d+",line))
                    print("Line is {}".format(line))
                    x, y = re.findall(r"[-]*[\d.]+\d+",line)
                    x = float(x)
                    y = float(y)

                    

                    print("x = {}, y = {}".format(x,y))

                    if (x-x0)**2+(y-y0)**2 <= r**2:
                        found_pattern = True
            else:
                out.write(line)

    out.close()
    
    print('FINISH')



if __name__ == "__main__":
    args = parse_cmdline_args()
    input_stream = args.i
    output_stream = args.o
    x0 = args.x0
    y0 = args.y0
    r = args.r

    parsing_stream(input_stream, output_stream, x0, y0, r)
