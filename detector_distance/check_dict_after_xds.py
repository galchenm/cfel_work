#!/usr/bin/env python3
# coding: utf8

"""
python3 check_after_XDS.py <path>

python3 check_after_XDS.py /gpfs/cfel/cxi/scratch/data/2019/PETRA-2019-Yefanov-Dec-P14/process/xdsA2/
"""


import os
import sys
import time
import numpy as np 
import subprocess

import sys
import re
from package_parsing_files_for_xds import processing
import argparse


os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('path', type=str, help="The path of folder/s that contain/s GXPARM file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmdline_args()
    main_path = args.path

    print('''Main path = {}'''.format(main_path))

    # !!!!Specify the full name of the correct file of interest to us!!!!
    FILE_NAME1 = 'GXPARM.XDS'

    # Initialize an empty list, where later we add all the paths to our files
    all_paths = []

    for path, dirs, all_files in os.walk(main_path):
        for file in all_files:
            if file == FILE_NAME1:
                all_paths.append(path)

    for path in all_paths:
        if os.access(path, os.R_OK) == 'false':
            exit()

    processing(all_paths, FILE_NAME1)

    print('FINISH')