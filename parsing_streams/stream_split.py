#!/usr/bin/env python3
# coding: utf8

"""
python3 stream_split.py [name_of_stream]

python3 stream_split.py -i all_runs.stream -o p8snr6.stream -f r0096

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
    parser.add_argument('-f', type=str, help='File name which patters we want to get')
    return parser.parse_args()


def parsing_stream(input_stream, output_stream, pattern_filename):
    out = open(output_stream, 'w')
    output_stream2 = output_stream.split('.')[0] + '_indexed.stream'
    out2 = open(output_stream2, 'w')

    with open(input_stream, 'r') as stream:
        reading_chunk = False
        found_file = False
        reading_geometry = False
        found_pattern = False


        for line in stream:
            if line.startswith('CrystFEL stream format 2.3'):
                chunk_geom = line
                reading_geometry = True
            elif 'indexamajig' in line:
                if pattern_filename in line:
                    found_pattern = True
                chunk_geom += line

            elif line.strip() == '----- End unit cell -----':  # ----- End geometry file -----
                reading_geometry = False
                chunk_geom += line
                if found_pattern:
                    out.write(chunk_geom)
                    out2.write(chunk_geom)
                found_pattern = False

            elif line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                chunk = line

            elif line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                if pattern_filename in name_of_file:
                    found_file = True
                chunk += line
                
            elif line.startswith('Event:'):
                serial_number = line.split('//')[-1]
                chunk += line     

            elif line.startswith('indexed_by ='): #none
                method_index = line.split()[-1] 
                chunk += line


            elif line.strip() == '----- End chunk -----':
                reading_chunk = False
                chunk += line
                if found_file:
                    out.write(chunk)
                    print('{}\t{}\n'.format(name_of_file, serial_number))

                    if 'none' not in method_index:
                        out2.write(chunk)
                found_file = False

            elif reading_chunk:
                chunk += line

            elif reading_geometry:
                chunk_geom += line

    out.close()
    out2.close()
    print('FINISH')



if __name__ == "__main__":
    args = parse_cmdline_args()
    input_stream = args.i
    output_stream = args.o
    pattern_filename = args.f

    parsing_stream(input_stream, output_stream, pattern_filename)


    