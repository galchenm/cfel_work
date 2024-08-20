#!/usr/bin/env python3
# coding: utf8

"""

"""


import os
import sys

import argparse


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i','--i', type=str, help="Input stream file")
    parser.add_argument('-o','--o', type=str, help="Ouput stream file")
    parser.add_argument('-f','--f', type=str, help="Input file with list of streams file")
    return parser.parse_args()


def parsing_stream(input_stream, output_stream):
    out2 = open(output_stream, 'w')
    
    total_filenames = 0
    total_hits = 0

    with open(input_stream, 'r') as stream:
        reading_chunk = False
        reading_geometry = False
        found_hit = False

        for line in stream:
            if line.startswith('CrystFEL stream format'):
                chunk_geom = line
                reading_geometry = True
            elif line.strip() == '----- End geometry file -----':  #
                reading_geometry = False
                chunk_geom += line
                out2.write(chunk_geom)

            elif line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                chunk = line

            elif line.startswith('Image filename:'):
                chunk += line
                
            elif line.startswith('Event:'):
                serial_number = line.split('//')[-1]
                chunk += line     

            elif line.startswith('hit = 1'): #none
                found_hit = True 
                chunk += line


            elif line.strip() == '----- End chunk -----':
                reading_chunk = False
                chunk += line
                if found_hit:
                    out2.write(chunk)
                found_hit = False

            elif reading_chunk:
                chunk += line

            elif reading_geometry:
                chunk_geom += line
    out2.close()





if __name__ == "__main__":
    args = parse_cmdline_args()
    input_list_of_stream = args.f
    
    if input_list_of_stream is not None:
        path = os.path.dirname(input_list_of_stream)
        with open(input_list_of_stream, 'r') as f:
            for input_stream in f:
                if len(input_stream.strip()) != 0:
                    input_stream2 = os.path.basename(input_stream.strip())
                    list_with_hits = os.path.join(path, input_stream2.split('.')[0]+"_hits.lst")
                    print("Work with {}, output list with hits is {}\n".format(input_stream2, list_with_hits))
                    parsing_stream(input_stream.strip(), list_with_hits)
                else:
                    continue
    elif args.i is not None:
        parsing_stream(args.i, args.o)
