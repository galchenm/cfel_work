#!/usr/bin/env python3
# coding: utf8

"""
python3 resolution_script.py <path>

Input: path
Output: path_to_folder_contains_LP_file resolution
"""

import os
import sys
import time
import numpy as np 
import subprocess
import argparse
import sys
import re

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('path', type=str, help="The path to folders that contain *.LP file")
    parser.add_argument('-prefix','--pref',type=str, help="Specification of path")
    parser.add_argument('-treshold','--tr',type=float, help="Specification of path")
    return parser.parse_args()



def get_patterns(lines):
    resolution = 0
    index1 = None
    index2 = None
    for line in lines:
        
        if line.startswith(' RESOLUTION RANGE  I/Sigma  Chi^2  R-FACTOR  R-FACTOR  NUMBER ACCEPTED REJECTED\n'):
            index1 = lines.index(line)
        if line.startswith('   --------------------------------------------------------------------------\n'):
            index2 = lines.index(line)
            break
    
    if index1 is None or index2 is None:
        return -200000
    else:
        i_start = index1+3
        l = re.sub(r"\s+", "**", lines[i_start].strip('\n')).split('**')[1:]

        res1, I1 = float(l[0]), float(l[2])
        p_res1, p_I1 = 0., 0.

        while I1 >= 1. and i_start < index2:
            if I1 == 1.:
                return res1

            p_res1, p_I1 = res1, I1
            i_start += 1
            l = re.sub(r"\s+", "**", lines[i_start].strip('\n')).split('**')[1:]
            try:
                res1, I1 = float(l[0]), float(l[2])
            except ValueError:
                return p_res1
        
        k = round((I1 - p_I1)/(res1 - p_res1),3)
        b = round((res1*p_I1-p_res1*I1)/(res1-p_res1),3)
        try:
            resolution = round((1-b)/k,3)
        except ZeroDivisionError:
            return -1000

    return resolution

if __name__ == "__main__":
    args = parse_cmdline_args()
    main_path = args.path
    FILE_NAME = 'CORRECT.LP'

    if args.tr is not None:
        treshold = args.tr
        files_list = open('files.lst', 'w')
    else:
        treshold = False

    if args.pref is not None:
        prefix = args.pref
        for path, dirs, all_files in os.walk(main_path):
            
            if FILE_NAME in all_files and prefix in path:
                with open(os.path.join(path,FILE_NAME), 'r') as stream:
                    lines = stream.readlines()
                    patterns_data = get_patterns(lines)
                    if patterns_data < 0:
                        print('With CORRECT.LP file in {} is something wrong'.format(path))
                        pass
                    else:
                        print(path, patterns_data, sep='    ')
                        if treshold and patterns_data < treshold:
                            files_list.write(path)
                            files_list.write('\n')
    else:
        for path, dirs, all_files in os.walk(main_path):
            if FILE_NAME in all_files:
                
                with open(os.path.join(path,FILE_NAME), 'r') as stream:
                    lines = stream.readlines()
                    patterns_data = get_patterns(lines)
                    if patterns_data < 0:
                        print('With CORRECT.LP file in {} is something wrong'.format(path))
                        pass
                    else:
                        print(path, patterns_data, sep='    ')
                        if treshold and patterns_data < treshold:
                            files_list.write(path)
                            files_list.write('\n')

    if treshold:
        files_list.close()
