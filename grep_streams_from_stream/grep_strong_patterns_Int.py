#!/usr/bin/env python3
# coding: utf8

"""

"""


import os
import sys

import argparse
from collections import defaultdict

import matplotlib.pyplot as plt


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i', type=str, help="Input stream file")
    parser.add_argument('-t', type=float, help="Use this flag as a percentage of number of strong patterns")
    return parser.parse_args()


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
    name_of_output_streamfile = input_stream.split('.')[0] + "-preselected-strong-patterns-according-to-intensity-after-indexing.stream"
    out = open(name_of_output_streamfile, 'w')

    
    with open(input_stream, 'r') as stream:
        reading_chunk = False
        found_file = False

        for line in stream:

            if line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                chunk = line

            elif line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                chunk += line
            elif line.startswith('Event:'):
                chunk += line
                event = line.strip().split('//')[-1]
                if "{} //{}".format(name_of_file, event) in d:
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
    return name_of_output_streamfile
    
def plotHistogram(p, o):
    """
    p and o are iterables with the values you want to
    plot the histogram of
    """
    print(len(p), len(o))
    plt.hist([p, o], alpha=0.8, label=['all patterns', 'strong patterns'])
    plt.show()

if __name__ == "__main__":
    args = parse_cmdline_args()
    input_stream = args.i

    treshold = args.t
    
    data_input = sum_intensity_calculation_after_indexing(input_stream)
    sorted_elements_by_intensity = sorted(data_input.items(), key=lambda item: item[1], reverse=True)
    d = dict(sorted_elements_by_intensity[0:round(treshold*len(sorted_elements_by_intensity))])
    
    
    name_of_output_streamfile = parsing_stream(input_stream, d)
    
    data_output = sum_intensity_calculation_after_indexing(name_of_output_streamfile)
    plotHistogram(list(data_input.values()), list(data_output.values()))
    print('FINISH')
    
