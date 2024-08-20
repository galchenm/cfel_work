#!/usr/bin/env python3
# coding: utf8

"""
python3 pick_up_indexed_patterns.py [name_of_stream]

python3 pick_up_indexed_patterns.py proc_r0095.stream

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
    parser.add_argument('stream', type=str, help="Input stream file")
    return parser.parse_args()

def parsing_for_indexed_patterns(stream_name):
    
    new_stream_name = 'indexed_' + stream_name
    nnew_stream_name = 'strong_indexed_' + stream_name


    out1 = open(new_stream_name, 'w')
    out2 = open(nnew_stream_name, 'w')

    with open(stream_name, 'r') as stream:
        reading_chunk = False

        for line in stream:
            
            if line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                chunk = line    

            elif line.startswith('indexed_by ='): #none
                method_index = line.split()[-1] 
                chunk += line

            elif line.startswith('num_peaks ='):
                # num_peaks = 35
                num_peaks = int(line.split()[-1])
                chunk += line

            elif line.strip() == '----- End chunk -----':
                reading_chunk = False
                chunk += line
                if 'none' not in method_index:
                    if num_peaks > 50:
                        out2.write(chunk)

                    out1.write(chunk)


            elif reading_chunk:
                chunk += line

            else:
                out1.write(line)
                out2.write(line)

    out1.close()
    out2.close()

    return new_stream_name, nnew_stream_name

if __name__ == "__main__":
    args = parse_cmdline_args()
    stream_name = args.stream

    indexed_outstream, strong_indexed_outstream = parsing_for_indexed_patterns(stream_name)


    