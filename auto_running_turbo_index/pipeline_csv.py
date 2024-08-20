#!/usr/bin/env python3
# coding: utf8

"""
python3 pipeline_csv.py [path_from] [path_to] [data.csv] [[--t [time in seconds]]]
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

import pandas as pd
import glob


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
    parser.add_argument('data_base', type=str, help="Excel doc with all parameters for running turbo-index-uni")
    parser.add_argument('-time_delay','--t', type=float, help="Time in seconds that will be checked as the last modifications")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmdline_args()
    
    path_from = os.path.abspath(args.path_from)
    path_to = os.path.abspath(args.path_to)
    data_base = args.data_base
    time_delay = args.t

    if time_delay is None:
        time_delay = 120.0 #2 minutes

    folders_in_path_to = []

    dic_in_path_from = defaultdict(list)

    for path, dirs, all_files in os.walk(path_from):
        for di in dirs:
            if re.search(r"[run]*[\d]+", di) and (time.time() - os.stat(os.path.join(path, di)).st_mtime > time_delay):
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
    

    dic_runs_all = defaultdict(list)

    for current_run in folders_need_to_add:
        
        dir_from = os.path.join(path_from, dic_in_path_from[current_run])
        
        if os.path.exists(dir_from):
            
            data_files = os.listdir(dir_from)
            files_of_interest = [os.path.join(dir_from, filename) for filename in data_files if (".h5" in filename or ".cxi" in filename) and "data" in filename]
            
            if len(files_of_interest) > 0:

                new_dir = os.path.join(path_to, current_run)
                if not(os.path.exists(new_dir)):
                    
                    os.mkdir(new_dir)

                file_lst_name = os.path.join(new_dir, current_run +".lst")

                dic_runs_all[current_run] = os.path.abspath(file_lst_name)

                files_lst = open(file_lst_name, 'w+')
                for f in files_of_interest:
                    files_lst.write(f)
                    files_lst.write("\n")
                files_lst.close()
    
    os.chdir(path_to)
    
    df = pd.read_csv(data_base, sep=";", header=0)
    df = df.drop_duplicates() # delete duplicate rows
    

    df_run_with_geom = df[df['geom'].notnull()]
    df_runs_with_all = df_run_with_geom[df_run_with_geom['pdb'].notnull()]

    df_runs_with_all['run'] = df_runs_with_all['run'].map(lambda run: run.strip())

    runs = df_runs_with_all['run']

    

    if len(dic_runs_all.keys()) == 0:
        runs_from = folders_in_path_to
    else:
        runs_from = dic_runs_all.keys()

    

    for run in runs:
        current_run = run.strip()
        current_dir = os.path.join(path_to, current_run)
        
        if os.path.exists(current_dir):
            
            if not(os.path.exists(os.path.join(current_dir, "error"))):
                os.mkdir(os.path.join(current_dir, "error"))
            if not(os.path.exists(os.path.join(current_dir, "streams"))):
                os.mkdir(os.path.join(current_dir, "streams"))
            error_dir = os.path.join(current_dir, "error")
            streams_dir = os.path.join(current_dir, "streams")
            
            os.chdir(current_dir)
            files = glob.glob("*.lst")
            filename_lst = current_run+".lst"

            if len(glob.glob("status.txt")) == 0:

                if filename_lst in files:

                    if current_run in runs_from:
                        info = df_runs_with_all[df_runs_with_all['run'] == current_run]
                        geom = info['geom'].item()
                        pdb = info['pdb'].item()
                        command_line = "bash /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/turbo-index-uni {} {} {} {} {}".format(os.path.abspath(filename_lst), geom, streams_dir, error_dir, pdb)
                        

                        status_file = open(os.path.join(current_dir, "status.txt"), "w+")
                        status_file.write("FINISHED")
                        status_file.close()
                        
                        print("Run {}".format(command_line))
                        print('\n\n\n')
                        
                        call(shlex.split(command_line))
                    else:
                        print("WARNING: The run {} exists in CSV, but is not found between folders".format(current_run))
                else:
                    print("WARNING: There is no list of HDF5 files in {}".format(current_dir))
            else:
                print("The run {} has been already processed".format(current_run))

        else:
            print("WARNING: This run {} doesn't exist in {}".format(current_run, path_from))
    

