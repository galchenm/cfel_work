#!/usr/bin/env python3
# coding: utf8

"""
python3 merge_stream.py /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/test_folder
"""

import os
import sys
import re
import argparse
from subprocess import call
from collections import defaultdict

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('path_to', type=str, help="The path where you will keep the result of data processing")
    parser.add_argument('key_word', type=str, help="The word that filename has")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmdline_args()
    path_to = args.path_to

    dic = defaultdict(list)

    for path, dirs, all_files in os.walk(path_to):
        for file in all_files:
            if 'stream' in file:
                num = re.search(r"r[un]*[\d]+[_\d]*", m).group()
                num = re.sub(r"[run]", '', num)

                #num = os.path.basename(file).split('_data')[0].split('.')[0]
                print("num is {}\n".format(num))
                #num = file.split('.')[0]
                #num = int(re.match(r'\d+', num).group())
                dic[num].append(os.path.join(path, file))
    

    for numRun in dic:
        command_line = "cat " + " ".join(dic[numRun]) + " >> {}.stream".format(os.path.join(path_to ,str(numRun)))
        os.system(command_line)
        

    



