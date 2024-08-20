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
import concurrent.futures
import subprocess
import shlex
import logging
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


def setup_logger():
   level = logging.INFO
   logger = logging.getLogger("app")
   logger.setLevel(level)
   log_file = 'file.log'
   formatter = logging.Formatter('%(levelname)s - %(message)s')
   ch = logging.FileHandler(log_file)
   
   ch.setLevel(level)
   ch.setFormatter(formatter)
   logger.addHandler(ch)
   logger.info("Setup logger in PID {}".format(os.getpid()))

def stream_list_func(path_from):
    logger = logging.getLogger('app')
    
    dic_stream = defaultdict(list)
    dic_list = defaultdict(list)

    files_lst = glob.glob(os.path.join(path_from,"*.lst?*"))
    streams = glob.glob(os.path.join(path_from,"streams/*.stream?*"))

    if len(files_lst) == 0 or len(streams) == 0:
        logger.info("Run {} has not been processed yet".format(path_from))
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
                os.system(command)
                logger.info("There is no streams for some {}".format(k))
                
        
        for k in k_inter:
            os.chdir(os.path.dirname(k))
            
            lst = dic_list[k]

            
            command_lst = 'wc -l {}'.format(lst)
            process_lst = subprocess.Popen(shlex.split(command_lst), stdout=subprocess.PIPE)
            k_lst =  int(process_lst.communicate()[0].decode('utf-8').split()[0])
            
            stream =  dic_stream[k]

            command = 'grep -ic "Image filename:" {}'.format(stream)
            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
            k_stream = int(process.communicate()[0])
            
            if k_stream != k_lst:
                sh_call = "{}.sh".format(k)
                
                logger.info("For {}: stream = {}, lst = {}".format(k, k_stream, k_lst))
                logger.info("SH for running is {}".format(sh_call))
                
                command = "sbatch {}".format(sh_call)
                os.system(command)
    return f'Finished {path_from}'

def main():
    args = parse_cmdline_args()
    
    input_path = os.path.abspath(args.path_from)

    folders = []
    
    logger = logging.getLogger('app')
    logger.info("main")
    
    for path, dirs, all_files in os.walk(input_path):
        lst = glob.glob(os.path.join(path, '*.lst?*'))
        if len(lst) != 0:
            folders.append(path)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [ executor.submit(stream_list_func, folder) for folder in folders]
        
        for f in concurrent.futures.as_completed(results):
            print(f.result())
    

setup_logger()

if __name__ == "__main__":
    main()  
