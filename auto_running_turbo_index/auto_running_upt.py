#!/usr/bin/env python3
# coding: utf8

"""
bla bla bla
"""

import os
import sys
import time
import numpy as np 
from collections import defaultdict

import re
import argparse

from subprocess import call
import shlex


os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('path_from', type=str, help="The path of folder/s that contain/s files")
    parser.add_argument('path_to', type=str, help="The path where you will keep the result of data processing")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmdline_args()
    path_from = args.path_from
    path_to = args.path_to

    lactamase = "/asap3/petra3/gpfs/p11/2020/data/11009046/processed/indexing/6gth.pdb"
    lys = "/asap3/petra3/gpfs/p11/2020/data/11009046/processed/indexing/lysozyme.cell"
    geometry = "/asap3/petra3/gpfs/p11/2020/data/11009046/processed/indexing/eiger16M-P11_200mm_sh1.geom"

    folders_in_path_to = []

    dic_in_path_from = defaultdict(list)

    for path, dirs, all_files in os.walk(path_from):
        for di in dirs:
            if re.search(r"[run]*[\d]+", di):
                d_name = re.sub(r"[run]", '', di)
                dic_in_path_from[d_name]=di

    folders_in_path_from = dic_in_path_from.keys()

    for path, dirs, all_files in os.walk(path_to):
        for file in all_files:
            if re.search(r"lst", file):
                filename = re.search(r"[run]*[\d]+[_\d]*", file).group()
                if re.search(r"[run]*[\d]+", filename):
                    filename = re.sub(r"[run]", '', filename)
                    folders_in_path_to.append(filename)

    folders_need_to_add = list(set(folders_in_path_from) - set(folders_in_path_to))
    s_folders_need_to_add = "\t".join(folders_need_to_add)

    files_lst_all = []

    for current_run in folders_need_to_add:
        
        dir_from = os.path.join(path_from, dic_in_path_from[current_run])
        
        if os.path.exists(dir_from):
            
            data_files = os.listdir(dir_from)
            files_of_interest = [os.path.join(dir_from, filename) for filename in data_files if (".h5" in filename or ".cxi" in filename) and "data" in filename]
            
            if len(files_of_interest) > 0:

                new_dir = os.path.join(path_to, current_run)
                if not(os.path.exists(new_dir)):
                    print('Create new folder {}'.format(new_dir))
                    os.mkdir(new_dir)

                file_lst_name = os.path.join(new_dir, current_run +".lst")
                
                files_lst_all.append(os.path.abspath(file_lst_name))

                files_lst = open(file_lst_name, 'w+')
                for f in files_of_interest:
                    files_lst.write(f)
                    files_lst.write("\n")
                files_lst.close()
    
    os.chdir(path_to)
    print("Current path is {}".format(os.getcwd())) 

    files_lst_all.sort(reverse=True)
    print(files_lst_all)

    for file in files_lst_all:
        current_dir = os.path.dirname(file)
        print(current_dir)
        if not(os.path.exists(os.path.join(current_dir, "error"))):
            os.mkdir(os.path.join(current_dir, "error"))
        if not(os.path.exists(os.path.join(current_dir, "streams"))):
            os.mkdir(os.path.join(current_dir, "streams"))
        error_dir = os.path.join(current_dir, "error")
        streams_dir = os.path.join(current_dir, "streams")
        