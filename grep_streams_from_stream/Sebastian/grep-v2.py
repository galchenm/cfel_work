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

def getting_nxs_files(filename, h5path, event, name_of_block):
    file = h5.File(filename, 'r')
    nxs_file = file[h5path][event].split('//')[0].strip()
    file.close()
    return nxs_file == name_of_block

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
                found_file = False    
            elif reading_chunk:
                chunk += line
                if line.startswith('Image filename:'):
                    filename = line.split(':')[-1].strip()
                    
                elif line.startswith('Event:'):
                    event = line.split(':')[-1].strip().replace('//','')    
                    flag = getting_nxs_files(filename, h5path, int(event), name_of_block)
                    if flag:
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
            if len(line.strip()) > 0:
                name_of_blocks.append(line.strip())
    
    print(name_of_blocks)
    
    #parsing_stream_per_pattern(input_stream, name_of_blocks, h5path)
    
    #for name_of_block in name_of_blocks:
    #    parsing_stream_per_pattern(name_of_block)    
    
    with Pool(processes=len(name_of_blocks)) as pool:
        pool.map(parsing_stream_per_pattern, name_of_blocks)   
    
    print('FINISH')
    
