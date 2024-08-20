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
    parser.add_argument('fraction', type=float, help="Enter the value between 0 and 1")
    return parser.parse_args()



if __name__ == "__main__":
    args = parse_cmdline_args()
    
    path_from = os.path.abspath(args.path_from)
    fraction = args.fraction
    

    dic_stream = defaultdict(list)
    dic_list = defaultdict(list)

    dirs = os.listdir(path_from)
    d_runs = [os.path.join(path_from,di) for di in dirs if re.search(r"[run]*[\d]+[_\d]*", di) and os.path.isdir(os.path.join(path_from,di))]

    for di in d_runs:
        files_lst = glob.glob(os.path.join(di,"*.lst?*"))
        streams = glob.glob(os.path.join(di,"streams/*.stream?*"))



        if len(files_lst) == 0 or len(streams) == 0:
            print("Run {} has not been processed yet".format(di))
        else:
            
            for file_lst in files_lst:
                prefix, suffix = os.path.basename(file_lst).replace('split-events-','').split(".")
                suffix = re.search(r'\d+',suffix).group()
                key_name = prefix+'-'+suffix
                dic_list[os.path.join(path_from, key_name)] = file_lst
            
            for stream in streams:
                prefix, suffix = os.path.basename(stream).split(".")
                suffix = re.search(r'\d+',suffix).group()
                key_name = prefix+'-'+suffix
                dic_stream[os.path.join(path_from,key_name)] = stream

            mod_files_lst = dic_list.keys() #[os.path.basename(s).replace('split-events-','').split(".")[0] for s in files_lst]
            mod_streams = dic_stream.keys() #[os.path.basename(stream).split(".")[0] for stream in streams]
            
            k_inter = set(mod_files_lst) & set(mod_streams)
            for k in k_inter:
                
                lst = dic_list[k]
                #print("lst", lst)
                
                k_lst =  len([line.strip() for line in open(lst, 'r').readlines() if len(line)>0])
                stream =  dic_stream[k]
                #print("stream", stream)

                command = 'grep -ic "Image filename:" {}'.format(stream)
                process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
                k_stream = int(process.communicate()[0])

                if (k_stream/k_lst) < fraction:
                    print("For {} the fraction of processed files is {}".format(k, (k_stream/k_lst)))
                    pattern = r"{}".format(os.path.basename(k))
                    path = os.path.dirname(lst)
                    
                    
                    sh_call = [sh for sh in glob.glob(os.path.join(path,"*.sh")) if re.search(pattern, sh)][0]
                    print("SH for running is {}".format(sh_call))
                    command = "source {}".format(sh_call)
                    #call(shlex.split(command))
