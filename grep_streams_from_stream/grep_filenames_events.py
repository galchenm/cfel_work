#!/usr/bin/env python3
# coding: utf8

"""
python3 grep_blocks.py -i [name of stream] -f [name of file with list of blocks]
"""


import os
import sys

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
    parser.add_argument('-f', type=str, help='File with blocks')
    return parser.parse_args()


def parsing_stream(name_of_blocks):
    global blocks
    global input_stream
    output = os.path.join(os.path.dirname(input_stream), os.path.basename(blocks).split('.')[0] + ".stream")
    out = open(output, 'w')
    
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
                    name_of_file = line.split(':')[-1].strip()
                        
                elif line.startswith('Event:'):
                        event = line.split(':')[-1].strip()
                        pattern_filename = name_of_file +' ' + event
                        chunk += line
                        print(pattern_filename in name_of_blocks)
                        if pattern_filename in name_of_blocks:
                            print(pattern_filename)
                            found_file = True
            else:
                out.write(line)

    out.close()






if __name__ == "__main__":
    args = parse_cmdline_args()
    input_stream = args.i
    blocks = args.f
    

    name_of_blocks = []
    with open(blocks, 'r') as file:
        for line in file:
            name_of_blocks.append(line.strip())
    print(name_of_blocks)
    parsing_stream(name_of_blocks)
    print('FINISH')
    
    

