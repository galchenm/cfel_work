#!/usr/bin/env python3
# coding: utf8

"""
python3 parallel_check_v2.py [path from] [fraction]


Ex.,
python3 parallel_check_v2.py  /asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/galchenm/processed/blocks 0.9
"""

from multiprocessing import Pool, TimeoutError
import time

import os
import sys


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


def sh_call(di):
    files_lst = glob.glob(os.path.join(di,"*.lst?*"))
    streams = glob.glob(os.path.join(di,"streams/*.stream?*"))

    #print(files_lst)
    #print(streams)
    
    if len(files_lst) == 0:
        print("WARNING: there are no lists in {}. It has not been processed yet\n\n".format(di))
    elif len(streams) == 0: # len(files_lst!=0)
        
        for s in files_lst:
            suffix = re.search(r"\d+", os.path.basename(s).replace('split-events-','').replace('EV-','').split(".")[1]).group()
            sh_call = os.path.join(os.path.dirname(s), os.path.basename(s).replace('split-events-','').replace('EV-','').split(".")[0]) +"-{}".format(suffix) +".sh"
            command = "sbatch {}".format(sh_call)
            print("Command", command)
            call(shlex.split(command))
            
    else:
        print('here')
        for s in files_lst:
            
            num = re.search(r'[\d]+',os.path.basename(s).replace('split-events-','').replace('EV-','').split(".")[1]).group()
            name_lst = os.path.join(path_from,os.path.basename(s).replace('split-events-','').replace('EV-','').split(".")[0]) + "-" + str(num)
            dic_list[name_lst] = s
        
        for stream in streams:
            
            num = re.search(r'[\d]+',os.path.basename(stream).split(".")[1]).group()
            name_stream = os.path.join(path_from,os.path.basename(stream).split(".")[0]) + "-" + str(num)
            dic_stream[name_stream] = stream

        mod_files_lst = dic_list.keys()
        mod_streams = dic_stream.keys()
        
        
        k_inter = set(mod_files_lst) & set(mod_streams)
        
        
        k_diff = set(mod_files_lst) - set(mod_streams) #there is no streams for some lst files
        
        if len(k_diff) != 0:
            for k in k_diff:
                command = "sbatch {}".format(k+'.sh')
                print(command)
        
        for k in k_inter:
            
            lst = dic_list[k]
            
            
            k_lst =  len([line.strip() for line in open(lst, 'r').readlines() if len(line)>0])
            stream =  dic_stream[k]
            

            command = 'grep -ic "Image filename:" {}'.format(stream)
            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
            k_stream = int(process.communicate()[0])
            

            if (k_stream/k_lst) <= fraction:
                print("For {} the fraction of processed files is {}".format(k, (k_stream/k_lst)))
                pattern = r"{}".format(os.path.basename(k))
                path = os.path.dirname(lst)
                
                sh_call = "{}.sh".format(k)
                #sh_call = [sh for sh in glob.glob(os.path.join(path,"*.sh")) if re.search(pattern, sh)][0]
                print("SH for running is {}\n\n".format(sh_call))
                command = "sbatch {}".format(sh_call)
                
                call(shlex.split(command))
        

if __name__ == "__main__":
    args = parse_cmdline_args()
    
    path_from = os.path.abspath(args.path_from)
    fraction = args.fraction
    

    dic_stream = defaultdict(list)
    dic_list = defaultdict(list)

    #dirs = os.listdir(path_from)
    #d_runs = [os.path.join(path_from,di) for di in dirs if re.search(r"[run]*[\d]+[_\d]*", di) and os.path.isdir(os.path.join(path_from,di))]
    d_runs = [path_from]
    
    sh_call(path_from)