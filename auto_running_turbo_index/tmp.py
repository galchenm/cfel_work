#!/usr/bin/env python3
# coding: utf8

"""
bla bla bla
"""

import os
import sys
import time
import pandas as pd

import argparse

from subprocess import call
import shlex

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
    parser.add_argument('data_base', type=str, help="Excel doc with all parameters for running turbo-index-uni")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmdline_args()
    path_from = os.path.abspath(args.path_from)
    data_base = args.data_base

    df = pd.read_csv(data_base, sep=";", header=0)
    df = df.drop_duplicates() # delete duplicate rows
    

    run_with_geom = df[df['geom'].notnull()]
    runs_with_all = run_with_geom[run_with_geom['pdb'].notnull()]

    runs = runs_with_all['run']
    for run in runs:
        current_run = run.strip()
        current_dir = os.path.join(path_from, current_run)
        
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

            

            if filename_lst in files:

                info = runs_with_all[runs_with_all['run'] == run]
                geom = info['geom'].item()
                pdb = info['pdb'].item()
                command_line = "bash /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/turbo-index-uni {} {} {} {} {}".format(os.path.abspath(filename_lst), geom, streams_dir, error_dir, pdb)
                #print(command_line)
                #print('\n\n')

                call(shlex.split(command_line))
            else:
                print("WARNING: There is no list of HDF5 files in {}".format(current_dir))

        else:
            print("WARNING: This run {} doesn't exist in {}".format(current_run, path_from))



        