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
from datetime import datetime

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i', type=str, help="Input stream file")
    parser.add_argument('-t', '--t', type=float, help="Use this flag as a treshold for picking up strong patterns")
    return parser.parse_args()


def average_resolution_calculation(input_stream):
    f = open(input_stream, 'r')
    stream = f.read()
    f.close()
    
    def f(x): 
        return round(10/float(x),2)
        
    p = re.compile("diffraction_resolution_limit = ([\+\-\d\.]*)")
    resolutions = list(map(f, p.findall(stream)))
    
    return round(np.mean(resolutions))
    
def parsing_stream(input_stream, avr_res):
    print(f'We are going to pick up patterns with resolution better than {avr_res}')
    output = input_stream.split('.')[0] + "-preselected-strong-patterns-according-to-avr-resolution.stream"
    if os.path.exists(output):
        dateTimeObj = datetime.now()
        timestampStr = dateTimeObj.strftime("%d-%b-%Y-%H-%M-%S") + ".stream"
        output = output.split('.')[0] +'-'+ timestampStr 
    
    out = open(output, 'w')
    with open(input_stream, 'r') as stream:
        reading_chunk = False
        found_file = False

        for line in stream:

            if line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                chunk = line

            elif line.startswith('diffraction_resolution_limit ='):
                chunk += line
                diffraction_resolution_limit = float(re.search(r'\d+.\d+ A',line.strip()).group().split(' ')[0])
                if diffraction_resolution_limit < avr_res:
                    found_file = True

            elif line.strip() == '----- End chunk -----':
                
                chunk += line
                if found_file:
                    out.write(chunk)

                found_file = False
                reading_chunk = False

            elif reading_chunk:
                chunk += line

            else:
                out.write(line)

    out.close()


if __name__ == "__main__":
    args = parse_cmdline_args()
    input_stream = args.i
    treshold = args.t
    avr_res = average_resolution_calculation(input_stream)
    print(f"Average resolution for this stream is {avr_res} A")
    
    

    parsing_stream(input_stream, avr_res if treshold is None else treshold)
    
    print('FINISH')
    
    

