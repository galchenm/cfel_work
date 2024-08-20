#!/usr/bin/env python3
# coding: utf8

"""
python3 grep_stream.py [name_of_stream]

python3 grep_stream.py -i all_runs.stream -o p8snr6.stream -f r0096

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
    #parser.add_argument('-o', type=str, help='Output stream file')
    #parser.add_argument('-thres', type=str, help='Threshold')
    return parser.parse_args()


def parsing_stream(input_stream, output_stream):
    out = open(output_stream, 'w')
    

    '''
    Image filename: /asap3/petra3/gpfs/p11/2020/data/11009046/raw/run87/87_data_000003.h5
    Event: //607
    Image serial number: 608
    hit = 1
    indexed_by = mosflm-latt-nocell
    n_indexing_tries = 6
    photon_energy_eV = 12000.000000
    beam_divergence = 0.00e+00 rad
    beam_bandwidth = 1.00e-08 (fraction)
    average_camera_length = 0.288000 m
    num_peaks = 31
    peak_resolution = 2.462998 nm^-1 or 4.060093 A
    '''
    total_filenames = 0
    total_hits = 0

    with open(input_stream, 'r') as stream:
        reading_chunk = False
        found_pattern = False

        for line in stream:
            
            if line.strip() == '----- Begin chunk -----':
                reading_chunk = True

            elif line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                total_filenames += 1
                found_pattern = True

            elif line.startswith('Event:'):
                event = line.split('//')[-1]
                
            elif line.startswith('hit ='):
                hit = int(line.split(' = ')[-1])

            elif line.startswith('indexed_by ='): #none
                method_index = line.split()[-1] 
                
            elif line.startswith('num_peaks ='):
                num_peaks = int(line.split(" = ")[-1])

            elif line.strip() == '----- End chunk -----':
                reading_chunk = False
                #if found_pattern and 'none' not in method_index and hit == 1:
                if found_pattern and hit == 1:
                    
                    total_hits += hit
                    

                    new_line = "{} //{}".format(name_of_file, event)
                    out.write(new_line)

                found_pattern = False

            elif reading_chunk:
                pass

            else:
                pass
    print("Total hits = {}, total records = {} for {}".format(total_hits, total_filenames, input_stream))
    out.close()

    if total_hits == 0:
        print("Number of hits is zero. Delete {}".format(output_stream))
        os.remove(output_stream)




if __name__ == "__main__":
    args = parse_cmdline_args()
    input_list_of_stream = args.i
    #output_stream = args.o
    #threshold = args.tres
    path = os.path.dirname(input_list_of_stream)

    with open(input_list_of_stream, 'r') as f:
        for input_stream in f:
            
            input_stream2 = os.path.basename(input_stream.strip())
            print("Work with {}".format(input_stream2))
            output_stream = os.path.join(path, input_stream2.split('.')[0]+"_hits.lst")
            print("output_stream is {}".format(output_stream))
            parsing_stream(input_stream.strip(), output_stream)
