#!/usr/bin/env python3
# coding: utf8

"""
python3 merge_stream.py /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/test_folder
"""
from multiprocessing import Pool, TimeoutError
import os
import sys
import re
import argparse
from subprocess import call
from collections import defaultdict
import glob
import logging
import shutil

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('path_to', type=str, help="The path where you will keep the result of data processing")
    parser.add_argument('-p','--p', type=str, help="Pattern in name")
    parser.add_argument('-f','--f', type=str, help='File with blocks')
    parser.add_argument('-suf','--suf', type=str, help="Suffix for stream filename")
    parser.add_argument('-pref','--pref', type=str, help="Prefix for stream filename")
    parser.add_argument('-r', '--r', default=False, action="store" , help="Use this flag if you want to rerun indexing")
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



def merge_streams(current_path, rerun, prefix, suffix):
    
    logger = logging.getLogger('app')
    
    streams_dir = os.path.join(current_path, "streams")
    j_stream_dir = os.path.join(current_path, "j_stream")
    d_name = os.path.basename(current_path)
    
    if not(os.path.exists(j_stream_dir)):
        os.mkdir(j_stream_dir)
    
    if len(glob.glob(os.path.join(j_stream_dir, "*.stream"))) != 0 and not(rerun):
        cat = input(f'Type y if you want to cat new stream for {os.path.basename(current_path)}, otherwise, enter n: ').lower()
        if cat == 'y':
            #if not(os.path.exists(os.path.join(j_stream_dir, 'prev'))):
            #    os.mkdir(os.path.join(j_stream_dir, 'prev'))
            #destination = os.path.join(j_stream_dir, 'prev')
            
            #for f in glob.glob(os.path.join(j_stream_dir, "*.stream")):
            #    shutil.move(f, destination)
            
            if os.path.exists(streams_dir):
                os.chdir(streams_dir)
                files = glob.glob("*.stream?*")
                if len(files) > 0:
                    files = [os.path.abspath(file) for file in files]
                    
                    command_line = "cat " + " ".join(files) + f' >> {os.path.join(j_stream_dir, prefix+"-"+str(d_name))}-{suffix}.stream'
                    os.system(command_line)
                    
                    logger.info("Run the command line: {}".format(command_line))
                else:
                    logger.info("There is no streams in {}".format(current_path))
    elif os.path.exists(streams_dir) or rerun:
        os.chdir(streams_dir)
        files = glob.glob("*.stream?*")
        if len(files) > 0:
            files = [os.path.abspath(file) for file in files]
            
            command_line = "cat " + " ".join(files) + f' >> {os.path.join(j_stream_dir, prefix+"-"+str(d_name))}-{suffix}.stream'
            os.system(command_line)
            
            logger.info("Run the command line: {}".format(command_line))
        else:
            logger.info("There is no streams in {}".format(current_path))
        
            
    else:
        logger.info("There is no streams folder in {}".format(current_path))




def main():
    args = parse_cmdline_args()
    path_to = args.path_to
    pattern = args.p
    rerun = args.r
    prefix = args.pref
    suffix = args.suf
    logger = logging.getLogger('app')
    logger.info("main")
    folders = []
    #logger = logging.getLogger('app')
    #f_handler = logging.FileHandler(os.path.join(path_to, 'file.log'))
    
    #f_format = logging.Formatter('%(levelname)s - %(message)s')
    #f_handler.setFormatter(f_format)
    #logger.addHandler(f_handler)
    
    if args.f is None:
        for path, dirs, all_files in os.walk(path_to):
            for di in dirs:
                if re.search(r"[run]*[\d]+[_]*[\d]*", di):
                    d_name = re.sub(r"run", '', di)
                    
                    current_path = os.path.join(path, d_name)
                    if pattern is not None and pattern in di:
                        folders.append(current_path)
                    elif pattern is None:
                        folders.append(current_path)
    else:
        with open(args.f,'r') as f:
            for d in f:
                d = d.strip()
                
                for path, dirs, all_files in os.walk(path_to):
                    for di in dirs:
                        '''
                        if re.search(r"[run]*[\d]+[_]*[\d]*", di):
                            d_name = re.sub(r"run", '', di)
                            #print(d_name)
                            if d in d_name or d == d_name:
                        '''
                        if d == di:
                            current_path = os.path.join(path, di)
                            if pattern is not None and pattern in di:
                                folders.append(current_path)
                            elif pattern is None:
                                folders.append(current_path)
                            
                
    print(folders)
    
    for folder in folders:
        merge_streams(folder, rerun, prefix, suffix)
    
    #with Pool(processes=20) as pool:
    #    pool.map(merge_streams, folders)

setup_logger()
if __name__ == "__main__":
    main() 