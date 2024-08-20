#!/usr/bin/env python3
# coding: utf8

import os
import sys
import time
import numpy as np 
import subprocess

import sys
import re
from package_parsing_files_for_xds import processing
os.nice(0)


if __name__ == "__main__":
    print ('''Specify the folder from which to start searching for suitable files (enter the appropriate number): \n 1: Current directory \n2: Folder name in the current directory \n3: Full path''')
    variant = int(sys.argv[1])

    if variant == 1:
        main_path = os.getcwd()
        #res = float(sys.argv[2])
    elif variant == 2:
        main_path = os.getcwd()
        str_dir = sys.argv[2]
        main_path = main_path + r'/' + str_dir
        #res = float(sys.argv[3])
    elif variant == 3:
        main_path = str(sys.argv[2])
        #res = float(sys.argv[3])
    else: 
        exit()

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