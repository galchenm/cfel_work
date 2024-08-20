#!/usr/bin/env python3
# coding: utf8

"""
"""

import os
import sys
import time
import numpy as np 
from collections import defaultdict

import re
import argparse
from multiprocessing import Pool, TimeoutError
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

def stream_list_func(path_from):
    dic_stream = defaultdict(list)
    dic_list = defaultdict(list)

    files_lst = glob.glob(os.path.join(path_from,"*.lst?*"))
    streams = glob.glob(os.path.join(path_from,"streams/*.stream?*"))

    if len(files_lst) == 0 or len(streams) == 0:
        print("Run {} has not been processed yet".format(path_from))
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

        mod_files_lst = dic_list.keys()
        mod_streams = dic_stream.keys()
        
        k_inter = set(mod_files_lst) & set(mod_streams)
        
        k_diff = set(mod_files_lst) - set(mod_streams) #there is no streams for some lst files
        
        if len(k_diff) != 0:
            for k in k_diff:
                os.chdir(os.path.dirname(k))
                
                command = "sbatch {}".format(k+'.sh')
                print('there is no streams for some lst files')
                print(command)
                #call(shlex.split(command))
                os.system(command)
        
        for k in k_inter:
            os.chdir(os.path.dirname(k))
            #print(os.getcwd())
            
            lst = dic_list[k]

            #k_lst =  len([line.strip() for line in open(lst, 'r').readlines() if len(line)>0])
            command_lst = 'wc -l {}'.format(lst)
            process_lst = subprocess.Popen(shlex.split(command_lst), stdout=subprocess.PIPE)
            k_lst =  int(process_lst.communicate()[0].decode('utf-8').split()[0])
            
            stream =  dic_stream[k]

            command = 'grep -ic "Image filename:" {}'.format(stream)
            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
            k_stream = int(process.communicate()[0])

            
            
            if k_stream != k_lst:
                sh_call = "{}.sh".format(k)
                print("For {}: stream = {}, lst = {}".format(k, k_stream, k_lst))
                
                print("SH for running is {}".format(sh_call))
                command = "sbatch {}".format(sh_call)
                
                #call(shlex.split(command))
                os.system(command)

if __name__ == "__main__":
    args = parse_cmdline_args()
    
    input_path = os.path.abspath(args.path_from)

    folders = []

    for path, dirs, all_files in os.walk(input_path):
        lst = glob.glob(os.path.join(path, '*.lst?*'))
        if len(lst) != 0:
            folders.append(path)
    

    with Pool(processes=20) as pool:
        pool.map(stream_list_func, folders)

    
