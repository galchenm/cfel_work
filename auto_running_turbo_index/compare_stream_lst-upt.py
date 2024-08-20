#!/usr/bin/env python3
# coding: utf8

"""
python3 /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/pipeline_csv.py /asap3/petra3/gpfs/p11/2020/data/11009046/raw/ /asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/galchenm/processed/ /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/data.csv
"""

import os
import sys
import time
import numpy as np 
from collections import defaultdict

import re
import argparse

import subprocess
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
    return parser.parse_args()



if __name__ == "__main__":
    args = parse_cmdline_args()
    
    path_from = os.path.abspath(args.path_from)
    #di = os.path.abspath(args.path_from)
    
    

    dic_stream = defaultdict(list)
    dic_list = defaultdict(list)

    #dirs = os.listdir(path_from)
    #d_runs = [os.path.join(path_from,di) for di in dirs if re.search(r"[run]*[\d]+[_\d]*", di) and os.path.isdir(os.path.join(path_from,di))]
    #print(d_runs)

    #for di in d_runs:
    files_lst = glob.glob(os.path.join(path_from,"*.lst?*"))
    streams = glob.glob(os.path.join(path_from,"streams/*.stream?*"))



    if len(files_lst) == 0 or len(streams) == 0:
        print("Run {} has not been processed yet".format(path_from))
    else:
        
        for s in files_lst:
            dic_list[os.path.join(path_from, os.path.basename(s).replace('split-events-','').split(".")[0])] = s
        
        for stream in streams:
            dic_stream[os.path.join(path_from,os.path.basename(stream).split(".")[0])] = stream

        mod_files_lst = dic_list.keys() #[os.path.basename(s).replace('split-events-','').split(".")[0] for s in files_lst]
        mod_streams = dic_stream.keys() #[os.path.basename(stream).split(".")[0] for stream in streams]
        
        k_inter = set(mod_files_lst) & set(mod_streams)
        for k in k_inter:
            
            lst = dic_list[k]

            k_lst =  len([line.strip() for line in open(lst, 'r').readlines() if len(line)>0])
            stream =  dic_stream[k]

            command = 'grep -ic "Image filename:" {}'.format(stream)
            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
            k_stream = int(process.communicate()[0])

            print("For {}: stream = {}, lst = {}".format(k, k_stream, k_lst))
