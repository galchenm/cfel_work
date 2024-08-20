#!/usr/bin/env python3
# coding: utf8

"""
python3 getting_patterns_with_high_Int.py [name_of_stream]

python3 getting_patterns_with_high_Int.py proc_r0095.stream 3046.56

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
    parser.add_argument('meanInt', type=float, help="Mean of Intensity")
    return parser.parse_args()

def parsing_for_indexed_patterns(stream_name, mInt):
    
    new_stream_name = 'indexed_' + stream_name
    nnew_stream_name = 'strong_indexed_' + stream_name


    out1 = open(new_stream_name, 'w')
    out2 = open(nnew_stream_name, 'w')

    with open(stream_name, 'r') as stream:
        reading_chunk = False
        reading_peaks = False
        mean_Int = None

        for line in stream:
            
            if line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                chunk = line

            elif line.startswith('Image filename:'):
                name_of_file = line.split()[-1] 
                chunk += line
                
            elif line.startswith('Event:'):
                serial_number = line.split('//')[-1]
                chunk += line     

            elif line.startswith('indexed_by ='): #none
                method_index = line.split()[-1] 
                chunk += line

            elif line.startswith('End of peak list'):
                reading_peaks = False
                
                chunk += line
                if numInt != 0:
                    mean_Int = round(sumInt/numInt, 2)

            elif line.startswith('  fs/px   ss/px (1/d)/nm^-1   Intensity  Panel'):
                reading_peaks = True
                sumInt = 0
                numInt = 0
                chunk += line

            elif reading_peaks:
                fs, ss, dump, intensity = [float(i) for i in line.split()[:4]]
                chunk += line
                sumInt += intensity
                numInt += 1

            elif line.strip() == '----- End chunk -----':
                reading_chunk = False
                chunk += line
                if 'none' not in method_index and mean_Int is not None:
                    if mean_Int > mInt:
                        out2.write(chunk)
                        print('{}\t{}\n'.format(name_of_file, serial_number))

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
    mean_Int = round(float(args.meanInt),2)

    indexed_outstream, strong_indexed_outstream = parsing_for_indexed_patterns(stream_name, mean_Int)


    