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
import glob

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('path_to', type=str, help="The path where you will keep the result of data processing")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmdline_args()
    path_to = args.path_to

    dic = defaultdict(list)

    for path, dirs, all_files in os.walk(path_to):
        for di in dirs:
            if re.search(r"[run]*[\d]+[_\d]*", di):
                d_name = re.sub(r"[run]", '', di)
                
                current_path = os.path.join(path, d_name)
                
                streams_dir = os.path.join(current_path, "streams")
                if os.path.exists(streams_dir):
                    os.chdir(streams_dir)
                    files = glob.glob("*.stream*")
                    if len(files) > 0:
                        files = [os.path.abspath(file) for file in files]
                        dic[d_name] = files
                else:
                    print("WARNING: There is no streams folder in {}".format(current_path))
    
    for numRun in dic:
        current_path = os.path.join(path_to, numRun)
        j_stream_dir = os.path.join(current_path, "j_stream")

        print("j_stream_dir: ", j_stream_dir)

        if not(os.path.exists(j_stream_dir)):
            os.mkdir(j_stream_dir)

        command_line = "cat " + " ".join(dic[numRun]) + " >> {}.stream".format(os.path.join(j_stream_dir, str(numRun)))
        
        os.system(command_line)
        

    



