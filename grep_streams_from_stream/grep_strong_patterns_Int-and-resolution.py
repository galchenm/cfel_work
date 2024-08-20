#!/usr/bin/env python3
# coding: utf8

"""

"""


import os
import sys

import re
import argparse
from collections import defaultdict
import numpy as np


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i', type=str, help="Input stream file")
    parser.add_argument('-t', type=float, help="Use this flag as a treshold for picking up strong patterns")
    parser.add_argument('-r','--r', type=float, help="Use this flag as a treshold for picking up strong patterns")
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


def sum_intensity_calculation_after_indexing(input_stream):
    data = defaultdict(dict)
    
    with open(input_stream, 'r') as file:
        in_list = 0
        
        for line in file:
            if line.startswith('----- Begin chunk -----'):
                continue
            if line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                continue
            if line.startswith('Event:'):
                event = line.strip().split('//')[-1]
                
                continue
            if line.find("Begin crystal") != -1:
                continue    

            if line.find("Reflections measured after indexing") != -1:
                if "{} //{}".format(name_of_file, event) in data:
                    in_list = 0
                    continue
                else:
                    in_list = 1
                    data["{} //{}".format(name_of_file, event)] = 0
                    continue
            if line.find("End of reflections") != -1:
                in_list = 0
            if in_list == 1:
                in_list = 2
                continue
            elif in_list != 2:
                continue

            # From here, we are definitely handling a reflection line

            # Add reflection to list
            columns = line.split()
            
            try:
                data["{} //{}".format(name_of_file, event)]+= float(columns[3])
            except:
                print("Error with line: "+line.rstrip("\r\n"))
      
    return data 

def parsing_stream(input_stream, d):

    out = open(input_stream.split('.')[0] + "-preselected-strong-patterns-according-to-intensity-after-indexing-and-resolution.stream", 'w')


    with open(input_stream, 'r') as stream:
        reading_chunk = False
        found_file = False
        proper_resolution = False
        for line in stream:

            if line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                chunk = line

            elif line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                chunk += line
            elif line.startswith('Event:'):
                event = line.split('//')[-1]
                if "{} //{}".format(name_of_file, event) in d:
                    found_file = True
                chunk += line
            elif line.startswith('diffraction_resolution_limit ='):
                chunk += line
                diffraction_resolution_limit = float(re.search(r'\d+.\d+ A',line.strip()).group().split(' ')[0])
                if diffraction_resolution_limit < avr_res:
                    proper_resolution = True
            elif line.strip() == '----- End chunk -----':
                
                chunk += line
                if found_file and proper_resolution:
                    out.write(chunk)

                found_file = False
                reading_chunk = False
                proper_resolution = False

            elif reading_chunk:
                chunk += line

            else:
                out.write(line)

    out.close()

    print('FINISH')


if __name__ == "__main__":
    args = parse_cmdline_args()
    input_stream = args.i

    treshold_int = args.t
    treshold_res = args.r
    
    data_input = sum_intensity_calculation_after_indexing(input_stream)
    sorted_elements_by_intensity = sorted(data_input.items(), key=lambda item: item[1], reverse=True)
    d = dict(sorted_elements_by_intensity[0:round(treshold_int*len(sorted_elements_by_intensity))])

    avr_res = average_resolution_calculation(input_stream)
    print(f"Average resolution for this stream is {avr_res} A")
    avr_res = avr_res if treshold_res is None else treshold_res
    
    parsing_stream(input_stream, d)
    
    print('FINISH')
    
    

