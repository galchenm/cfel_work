#!/usr/bin/env python3
# coding: utf8

"""
python3 auto_running.py /asap3/petra3/gpfs/p11/2020/data/11009046/raw /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/test_folder
"""

import os
import sys
import time
import numpy as np 


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


    print('''Main path = {}'''.format(path_from))

    folders_in_path_from = []
    folders_in_path_to = []

    min_run_number = None
    max_run_number = None


    for path, dirs, all_files in os.walk(path_from):
        for di in dirs:
            if "run" in di:
                folders_in_path_from.append(di)
    print("folders_in_path_from is \n {}".format(folders_in_path_from))

    for path, dirs, all_files in os.walk(path_to):
        for file in all_files:
            if 'lst' in file:
                folders_in_path_to.append('run'+file.split('.')[0])

    print("folders_in_path_to is \n {}".format(folders_in_path_to))

    folders_need_to_add = list(set(folders_in_path_from) - set(folders_in_path_to))
    s_folders_need_to_add = "\t".join(folders_need_to_add)

    print("s_folders_need_to_add \n {}".format(s_folders_need_to_add))

    runs_number = [int(n) for n in re.findall(r'\d+', s_folders_need_to_add)[0]]

    min_run_number = min(runs_number)
    max_run_number = max(runs_number)
    print("min_run_number = {}, max_run_number = {}\n".format(min_run_number, max_run_number))

    files_lst_all = []

    for di in folders_need_to_add:
        current_run_number = re.findall(r'\d+', di)[0]
        file_lst_name = os.path.join(path_to, current_run_number +".lst")

        print("file_lst_name {}\n".format(file_lst_name))
        files_lst_all.append(file_lst_name)

        files_lst = open(file_lst_name, 'w+')

        dir_from = os.path.join(path_from, di)
        data_files = os.listdir(dir_from)
        files_of_interest = [os.path.join(dir_from, filename) for filename in data_files if ".h5" in filename and "data" in filename]
        #l_files_of_interest = "\n".join(files_of_interest)
        for f in files_of_interest:
            files_lst.write(f)
            files_lst.write("\n")
        files_lst.close()
    
    os.chdir(path_to)
    print("Current path is {}".format(os.getcwd()))

    files_lst_all = files_lst_all[::-1]

    for file in files_lst_all:
        num = int(re.findall(r'\d+',os.path.basename(file))[0])

        if num>=104 and num<=161 or num >=204 and num <=243:
            command_line = "bash /asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/galchenm/turbo-index-uni {} {}".format(file.strip(), lactamase)
        else:
            command_line = "bash /asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/galchenm/turbo-index-uni {} {}".format(file.strip(), lys)
        call(shlex.split(command_line))
