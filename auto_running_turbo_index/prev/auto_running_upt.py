#!/usr/bin/env python3
# coding: utf8

"""
python3 /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/auto_running_upt.py /asap3/petra3/gpfs/p11/2020/data/11009046/raw /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/tmp
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


    #folders_in_path_from = []
    folders_in_path_to = []

    dic_in_path_from = defaultdict(list)

    for path, dirs, all_files in os.walk(path_from):
        for di in dirs:
            if re.search(r"[run]*[\d]+", di):
                d_name = re.sub(r"[run]", '', di)
                dic_in_path_from[d_name]=di

                print("dir name is {}".format(d_name))
                print("dir is {}".format(di))
            #if "run" in di:
            #    folders_in_path_from.append(di)

    folders_in_path_from = dic_in_path_from.keys()

    print("folders_in_path_from is {}".format(folders_in_path_from))

    for path, dirs, all_files in os.walk(path_to):
        for file in all_files:
            #if 'lst' in file:
            #    folders_in_path_to.append('run'+file.split('.')[0])
            if re.search(r"lst", file):
                filename = re.search(r"[run]*[\d]+[_\d]*", file).group()
                if re.search(r"[run]*[\d]+", filename):
                    filename = re.sub(r"[run]", '', filename)
                    print("filename is {}".format(filename))
                    folders_in_path_to.append(filename)

    folders_need_to_add = list(set(folders_in_path_from) - set(folders_in_path_to))
    s_folders_need_to_add = "\t".join(folders_need_to_add)

    

    files_lst_all = []

    for current_run in folders_need_to_add:
        #current_run = di.split('run')[1]
        print("current_run is {}".format(current_run))
        new_dir = os.path.join(path_to, current_run)
        if not(os.path.exists(new_dir)):
            os.mkdir(new_dir)
        
        #current_run = re.search(r"[run]*[\d]+[_\d]*", file).group()
        #current_run = re.sub(r"[run]", '', current_run)

        file_lst_name = os.path.join(new_dir, current_run +".lst")
        
        files_lst_all.append(file_lst_name)

        dir_from = os.path.join(path_from, dic_in_path_from[current_run])
        
        if os.path.exists(dir_from):
            print("dir_from is {}".format(dir_from))
            data_files = os.listdir(dir_from)
            files_of_interest = [os.path.join(dir_from, filename) for filename in data_files if (".h5" in filename or ".cxi" in filename) and "data" in filename]
            
            if len(files_of_interest) > 0:
                files_lst = open(file_lst_name, 'w+')
                for f in files_of_interest:
                    files_lst.write(f)
                    files_lst.write("\n")
                files_lst.close()
    
    os.chdir(path_to)
    print("Current path is {}".format(os.getcwd()))

    files_lst_all.sort(reverse=True)
    print(files_lst_all)

    #for file in files_lst_all:
    #
    #    current_run = os.path.basename(file).split('run')[0].split('.')[0]
    #    print("current_run is {}\n".format(current_run))

    #    if num>=104 and num<=161 or num >=204 and num <=243:
    #        command_line = "bash /asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/galchenm/turbo-index-uni {} {}".format(file.strip(), lactamase)
    #    else:
    #        command_line = "bash /asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/galchenm/turbo-index-uni {} {}".format(file.strip(), lys)
    #    call(shlex.split(command_line))
