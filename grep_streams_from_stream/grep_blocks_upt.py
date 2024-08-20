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
        #f, l = re.findall(r"\d+[_\d]*", key)
        blocks = re.findall(r"\d+[_\d]*", key)
        delimeter = re.findall(r"[-,]", key)
        if ',' in delimeter or len(blocks) == 1:
            d[key] = blocks
        else: #delimeter is '-'
            if len(blocks) > 2:
                print("WARNING: separate this line {} accroding to the rule of block file.\n".format(key))
            else:
                f,l = blocks
                if re.search(r"_",f) and re.search(r"_", l):
                    f_suf = re.sub(r"_",'', re.findall(r"_\d+",f)[0])
                    f_pref = re.sub(r"_",'', re.findall(r"\d+_",f)[0])
                    l_suf = re.sub(r"_",'', re.findall(r"_\d+",l)[0])
                    l_pref = re.sub(r"_",'', re.findall(r"\d+_",l)[0])

                    if f_pref != l_pref:
                        print("WARNING: this line {} could not be processed, because they have various prefix. Split these blocks into blocks with the same prefix!\n".format(key))
                    else:
                        r = np.arange(int(f_suf), int(l_suf) + 1)
                        rr = [f_pref+"_"+str(i) for i in r]
                        d[key] = rr
                elif re.search(r"_",f) and not re.search(r"_", l) or not re.search(r"_",f) and re.search(r"_", l):
                    print("WARNING: this line {} could not be processed because parts have different type of name! Split them.\n".format(key))
                else:
                    d[key] = [str(i) for i in np.arange(int(f), int(l) + 1)]
    
    return d


def parsing_stream(name_of_block):
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
                name_of_file = os.path.basename(os.path.dirname(line.split()[-1]))

                pattern_filename = re.search(r"[run]*\d+[_]*[\d]*", name_of_file).group()
                pattern_filename = re.search(r"\d+[_]*[\d]*", pattern_filename).group()
                
                if re.search(r'^0',pattern_filename):
                    pattern_filename = re.sub(r'^0','',pattern_filename)
                    
                if pattern_filename in blocks_dict[name_of_block]:
                    found_file = True
                    print(name_of_file)
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



if __name__ == "__main__":
    args = parse_cmdline_args()
    input_stream = args.i
    blocks = args.f

    blocks_dict = prepare_blocks(blocks)
    name_of_blocks = blocks_dict.keys()

    print(blocks_dict)

    with Pool(processes=10) as pool:
        pool.map(parsing_stream, name_of_blocks)