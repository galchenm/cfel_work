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

def prepare_blocks(blocks):
    d = defaultdict(list)
    file = open(blocks, 'r')
    for line in file:
        key = line.strip()
        f, l = re.findall(r"\d+[_\d]*", key)
        if re.search(r"_",f) and re.search(r"_", l):
            f_suf = re.sub(r"_",'', re.findall(r"_\d+",f)[0])
            f_pref = re.sub(r"_",'', re.findall(r"\d+_",f)[0])
            l_suf = re.sub(r"_",'', re.findall(r"_\d+",l)[0])
            l_pref = re.sub(r"_",'', re.findall(r"\d+_",l)[0])

            if f_pref != l_pref:
                print("WARNING: split these blockw into blocks with the same prefix!\n")
            else:
                r = np.arange(int(f_suf), int(l_suf) + 1)
                rr = [f_pref+"_"+str(i) for i in r]
                d[key] = rr
        else:
            d[key] = [str(i) for i in np.arange(int(f), int(l) + 1)]

    return d


def parsing_stream_old(name_of_block):
    global blocks_dict
    global input_stream

    print("name_of_block is {}".format(name_of_block))

    out = open(name_of_block + ".stream", 'w')


    with open(input_stream, 'r') as stream:
        reading_chunk = False
        found_file = False

        for line in stream:

            if line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                chunk = line

            elif line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                print("name_of_file is ", name_of_file)
                pattern_filename = re.search(r"[run]+\d+[_\d]*", name_of_file).group()
                pattern_filename = re.search(r"\d+[_\d]*", pattern_filename).group()
                print("pattern_filename", pattern_filename)
                if pattern_filename in blocks_dict[name_of_block]:
                    found_file = True
                chunk += line

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

    print('FINISH')



def parsing_stream(name_of_block):
    global blocks_dict
    global input_stream

    print("name_of_block is {}".format(name_of_block))

    out = open(name_of_block + ".stream", 'w')


    with open(input_stream, 'r') as stream:
        reading_chunk = False
        found_file = False
        reading_geometry = False
        found_pattern = False


        for line in stream:
            if line.startswith('CrystFEL stream format 2.3'):
                chunk_geom = line
                reading_geometry = True
            elif 'indexamajig' in line:
                pattern = line.split(' -i ')[1].split(' -o ')[0]
                pattern = pattern.replace("split-",'').replace("events-",'')
                pattern = re.sub(r".\d+[\.h5]*[\.cxi]*\.lst\d+",'', pattern)
                pattern = re.sub(r"[a-zA-Z]+",'', pattern)
                
                if len(re.findall(r"\d+", pattern)) == 1:
                    pattern = re.findall(r"\d+", pattern)[0]
                else:
                    pattern = re.search(r"\d+_\d+",pattern).group()
                print("pattern is ", pattern)

                if not re.search(r"\d+_\d+",pattern) and re.search(r"\d+_\d+", blocks_dict[name_of_block][0]):
                    r_search = [ re.sub(r"_",'', re.findall(r"_\d+", i )[0]) for i in blocks_dict[name_of_block]]
                else:
                    r_search = blocks_dict[name_of_block]

                if pattern in r_search:
                    found_pattern = True
                chunk_geom += line

            elif line.strip() == '----- End unit cell -----':  # ----- End geometry file -----
                reading_geometry = False
                chunk_geom += line
                if found_pattern:
                    out.write(chunk_geom)
                found_pattern = False

            elif line.strip() == '----- Begin chunk -----':
                reading_chunk = True
                chunk = line

            elif line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                print("name_of_file is ", name_of_file)
                pattern_filename = re.search(r"[run]+\d+[_\d]*", name_of_file).group()
                pattern_filename = re.search(r"\d+[_\d]*", pattern_filename).group()
                print("pattern_filename", pattern_filename)
                if pattern_filename in blocks_dict[name_of_block]:
                    found_file = True
                    if len(chunk_geom):
                        out.write(chunk_geom)
                chunk += line

            elif line.strip() == '----- End chunk -----':
                
                chunk += line
                if found_file:
                    out.write(chunk)

                found_file = False
                reading_chunk = False

            elif reading_chunk:
                chunk += line

            elif reading_geometry:
                chunk_geom += line

    out.close()

    print('FINISH')

if __name__ == "__main__":
    args = parse_cmdline_args()
    input_stream = args.i
    blocks = args.f

    blocks_dict = prepare_blocks(blocks)
    name_of_blocks = blocks_dict.keys()

    print(blocks_dict)

    with Pool(processes=10) as pool:
        pool.map(parsing_stream_old, name_of_blocks)



    
