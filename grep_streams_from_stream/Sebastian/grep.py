#!/usr/bin/env python3
# coding: utf8

"""
python3 grep_blocks.py -i [name of stream] -f [name of file with list of blocks]
"""


import os
import sys
import h5py as h5
import re
import argparse
from collections import defaultdict
import numpy as np

from multiprocessing import Pool, TimeoutError


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i', type=str, help="Input stream file")
    parser.add_argument('--h5p', type=str, default='/entry/data/event_id', help="HDF5 path in hdf5 file for event_id")
    parser.add_argument('-f', type=str, help='File with files of interest')
    return parser.parse_args()

def getting_nxs_files(filename, h5path):
    file = h5.File(filename, 'r')
    nxs_with_events = file[h5path]
    nxs_files = set(list(map(lambda x: x.split('//')[0].strip(), nxs_with_events)))
    file.close()
    return nxs_files

def parsing_stream_per_pattern(name_of_block):
    global blocks
    global input_stream
    global h5path
    
    output_name = os.path.join(os.path.dirname(input_stream), os.path.basename(name_of_block).split('.')[0] + ".stream")
    
    out = open(output_name, 'w')
    
    with open(input_stream, 'r') as stream:
        reading_chunk = False
        
        for line in stream:
            if line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                found_file = False
                chunk = line

            elif line.strip() == '----- End chunk -----':
                reading_chunk = False
                chunk += line
                if found_file:
                    out.write(chunk)
                    
            elif reading_chunk:
                chunk += line
                if line.startswith('Image filename:'):
                    filename = line.split(':')[-1].strip()
                    nxs_files = getting_nxs_files(filename, h5path)
                    #print(nxs_files, name_of_block in nxs_files)
                    if name_of_block in nxs_files:
                        found_file = True       
            else:
                out.write(line)
                #print(69, line)
                

    out.close()



if __name__ == "__main__":
    args = parse_cmdline_args()
    input_stream = args.i
    h5path = args.h5p
    blocks = args.f
    

    name_of_blocks = []
    with open(blocks, 'r') as file:
        for line in file:
            if len(line) > 0:
                name_of_blocks.append(line.strip())
    
    print(name_of_blocks)
    
    #for name_of_block in name_of_blocks:
    #    parsing_stream_per_pattern(name_of_block)    
    
    with Pool(processes=len(name_of_blocks)) as pool:
        pool.map(parsing_stream_per_pattern, name_of_blocks)    
    
    print('FINISH')
    
