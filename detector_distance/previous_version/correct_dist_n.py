#!/usr/bin/env python3
# coding: utf8

import os
import sys
import time
import numpy as np 
import subprocess

import sys
import re
from package_parsing_files_for_xds import processing, get_initial_patterns_from_INP

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
    # FILE_NAME1 = 'XPARM.XDS'
    FILE_NAME2 = 'XDS.INP'

    # Initialize an empty list, where later we add all the paths to our files
    all_paths = []
    
    for path, dirs, all_files in os.walk(main_path):
        for file in all_files:
            if file == FILE_NAME2: #FILE_NAME
                all_paths.append(path)

    for path in all_paths:
        if os.access(path, os.R_OK) == 'false':
            exit()

    d1 = get_initial_patterns_from_INP(all_paths)
    
    print("START EXECUTE XDS")

    new_all_paths = []
    for path in all_paths:
        os.chdir(path)

        os.rename(os.path.join(path,FILE_NAME2),os.path.join(path,'old'+FILE_NAME2))
        with open(os.path.join(path,'old'+FILE_NAME2),'r') as f1, open(os.path.join(path,FILE_NAME2),'a+') as f2:
            lines = f1.readlines()
            for line in lines:
                if 'REFINE' in line and not(line.startswith('!')):
                    tmpline = line.split('=')
                    line = tmpline[0]+'='+'BEAM '+ tmpline[1]
                f2.write(line)

        os.remove(os.path.join(path,'old'+FILE_NAME2))
        print('SBATCH PROCESS\n')
        job_file = os.path.join(path,"%s.job" % path.split("/")[-1])
        with open(job_file, 'w+') as fh:
            fh.writelines("#!/bin/sh\n")
            fh.writelines("#SBATCH --job=%s.job\n" % path.split("/")[-1])
            fh.writelines("#SBATCH --partition=upex\n")
            fh.writelines("#SBATCH --time=12:00:00\n")
            fh.writelines("#SBATCH --nodes=1\n")
            fh.writelines("#SBATCH --nice=100\n")
            fh.writelines("#SBATCH --mem=500000\n")
            fh.writelines("#SBATCH --output=%s.out\n" % path.split("/")[-1])
            fh.writelines("#SBATCH --error=%s.err\n" % path.split("/")[-1])
            fh.writelines("source /etc/profile.d/modules.sh\n")
            fh.writelines("module load xray\n")
            fh.writelines("xds_par\n")
        os.system("sbatch %s" % job_file)

    print('FINISH')