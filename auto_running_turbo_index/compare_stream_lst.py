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
    parser.add_argument('-p','--p', type=str, help='Path to the files with hits')
    
    return parser.parse_args()


def parsing_stream(input_stream, input_list):

    total_number_filenames = 0
    

    lst = open(input_list, 'r')
    lines = [line.strip() for line in lst.readlines()]
    
    total_records = len(lines)


    with open(input_stream, 'r') as stream:
        for line in stream:
            if line.startswith('Image filename:'):
                total_number_filenames += 1

    print("For {} the number of filename records is {}, and in list {} with hits is {}. The difference is {}".format(input_stream, total_number_filenames, input_list, total_records, (total_number_filenames - total_records)))

if __name__ == "__main__":
    args = parse_cmdline_args()
    input_list_of_stream = args.i
    path = args.p
    if path is None:
        path = os.path.dirname(input_list_of_stream)
    
    
    with open(input_list_of_stream, 'r') as f:
        for input_stream in f:

            input_stream2 = os.path.basename(input_stream.strip())
            input_list = os.path.join(path, input_stream2.split('.')[0]+"_indexed.lst")
            parsing_stream(input_stream.strip(), input_list)
