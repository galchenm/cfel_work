#!/usr/bin/env python3
# coding: utf8

"""
"""

import os
import sys
import time
import numpy as np 
from collections import defaultdict
import logging
import re
import argparse

import subprocess
from subprocess import call
import shlex

import glob
import shutil

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('path_from', type=str, help="The path of folder/s that contain/s files")
    parser.add_argument('-f','--f', type=str, help='File with blocks')
    parser.add_argument('-p','--p', type=str, help="Pattern in name")

    parser.add_argument('-suf','--suf', type=str, help="Suffix for stream filename")
    parser.add_argument('-pref','--pref', type=str, help="Prefix for stream filename")
    
    parser.add_argument('-o', '--o', type=str, help="The name of folder where you want to move prev results")
    parser.add_argument('-r', '--r', action='store_true', help="Use this flag if you want to rerun indexing")
    
    
    
    parser.add_argument('--s', default=False, action='store_true', help="Use this flag if you want to skip merging in case if joined streams is already created")
    parser.add_argument('--no-s', dest='s', action='store_false', help="Use this flag if you don not want to skip merging in case if joined streams is already created")
    parser.add_argument('-m', '--m', action='store_true' , help="Use this flag if you want to rerun merging manually. Be careful with prefix and suffix for new stream")
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

def creating_name_of_output_joined_stream(j_stream_dir, d_name, prefix, suffix):
    if len(prefix)>0 and len(suffix)>0:
        output = f'{os.path.join(j_stream_dir, prefix+"-"+str(d_name))}-{suffix}.stream'
    if len(prefix)>0 and len(suffix)==0:
        output = f'{os.path.join(j_stream_dir, prefix+"-"+str(d_name))}.stream'                        
    if len(prefix) == 0 and len(suffix)>0:
        output = f'{os.path.join(j_stream_dir, str(d_name))}-{suffix}.stream'
    if len(prefix) == 0 and len(suffix)==0:
        output = f'{os.path.join(j_stream_dir, str(d_name))}.stream'  
    return output

'''
def join_streams(streams_dir, j_stream_dir, d_name, prefix, suffix):
    logger = logging.getLogger('app')
    if os.path.exists(streams_dir):
        current_path = os.path.dirname(streams_dir)
        os.chdir(streams_dir)
        files = glob.glob("*.stream?*")
        if len(files) > 0:
            files = [os.path.abspath(file) for file in files]
            output = creating_name_of_output_joined_stream(j_stream_dir, d_name, prefix, suffix)                   
            
            command_line = "cat " + " ".join(files) + f' >> {output}'
            os.system(command_line)
            
            logger.info("Run the command line: {}".format(command_line))
            
        else:
            logger.info("There is no streams in {}".format(current_path))
    else:
        logger.info("There is something wrong with file struncture in {}".format(current_path))
'''

def join_streams(streams_dir, j_stream_dir, output_stream_name):
    logger = logging.getLogger('app')
    if os.path.exists(streams_dir):
        current_path = os.path.dirname(streams_dir)
        os.chdir(streams_dir)
        files = glob.glob("*.stream?*")
        if len(files) > 0:
            files = [os.path.abspath(file) for file in files]
                           
            
            command_line = "cat " + " ".join(files) + f' >> {output_stream_name}'
            os.system(command_line)
            
            command = f"python3 /gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_merge_streams/detector-shift {output_stream_name}"
            os.system(command)
            
            logger.info("Run the command line: {}".format(command_line))
            
        else:
            logger.info("There is no streams in {}".format(current_path))
    else:
        logger.info("There is something wrong with file structure in {}".format(current_path))


def merge_streams(current_path, rerun_manually, skip, prefix, suffix, output_path_for_prev_results):
    logger = logging.getLogger('app')
    
    if prefix is None:
        prefix = ''
    if suffix is None:
        suffix = ''    
    
    #print('skip ', skip)
    #print('rerun merging', rerun_manually)
    
    streams_dir = os.path.join(current_path, "streams")
    j_stream_dir = os.path.join(current_path, "j_stream")
    d_name = os.path.basename(current_path)
    
    if not(os.path.exists(j_stream_dir)):
        os.mkdir(j_stream_dir)
        
    output_stream_name = creating_name_of_output_joined_stream(j_stream_dir, d_name, prefix, suffix)
    
    if skip:
        if os.path.exists(output_stream_name): #skip it because joined stream with the same name exists
            print(f'You have already a joined stream with this name for {os.path.basename(current_path)}')
            logger.info(f'You have already a joined stream for {os.path.basename(current_path)}')
            return
        elif len(glob.glob(os.path.join(j_stream_dir, "*.stream"))) != 0: # if joined stream exists but with another name, you should move all results to another folder
            print(f'move existed one to prev_results subfolder in {os.path.join(j_stream_dir, output_path_for_prev_results)}')
            if not(os.path.exists(os.path.join(j_stream_dir, output_path_for_prev_results))):
                os.mkdir(os.path.join(j_stream_dir, output_path_for_prev_results))
            destination = os.path.join(j_stream_dir, output_path_for_prev_results)
            
            
            for f in glob.glob(os.path.join(j_stream_dir, "*.*")):
                shutil.move(f, destination)
            join_streams(streams_dir, j_stream_dir, output_stream_name)
            
        else: #here because you don't have a joined stream
            print(f'You do not have already a joined stream for {os.path.basename(current_path)}')
            join_streams(streams_dir, j_stream_dir, output_stream_name) #(streams_dir, j_stream_dir, d_name, prefix, suffix)
        
    elif not(skip) and rerun_manually:
        if os.path.exists(output_stream_name):
            print(f'You have already a joined stream with this name for {os.path.basename(current_path)}')
            cat = input(f'Type y if you want to cat a new stream for {os.path.basename(current_path)}, otherwise, enter n: ').lower()
            if cat == 'y':
                output_stream_name = input(f'Type a new name for joined stream (for instance, xg-thau-104.stream): ').lower()
                join_streams(streams_dir, j_stream_dir, output_stream_name)
        elif len(glob.glob(os.path.join(j_stream_dir, "*.stream"))) != 0:
            cat = input(f'Type y if you want to cat a new stream for {os.path.basename(current_path)}, otherwise, enter n: ').lower()
            if cat == 'y':
                if not(os.path.exists(os.path.join(j_stream_dir, output_path_for_prev_results))):
                    os.mkdir(os.path.join(j_stream_dir, output_path_for_prev_results))
                destination = os.path.join(j_stream_dir, output_path_for_prev_results)
                
                #for f in glob.glob(os.path.join(j_stream_dir, "*.stream")):
                for f in glob.glob(os.path.join(j_stream_dir, "*.*")):
                    shutil.move(f, destination)
                    
                join_streams(streams_dir, j_stream_dir, output_stream_name) #(streams_dir, j_stream_dir, d_name, prefix, suffix)
        else: #here because you don't have a joined stream
            join_streams(streams_dir, j_stream_dir, output_stream_name) #(streams_dir, j_stream_dir, d_name, prefix, suffix)
            
    else: # move all existed joined streams and results to another folder
        if len(glob.glob(os.path.join(j_stream_dir, "*.stream"))) != 0:
            print(f'You have already a joined stream for {os.path.basename(current_path)}')
            print(f'Move existed one to prev_results subfolder in {os.path.join(j_stream_dir, output_path_for_prev_results)}')
            if not(os.path.exists(os.path.join(j_stream_dir, output_path_for_prev_results))):
                os.mkdir(os.path.join(j_stream_dir, output_path_for_prev_results))
            destination = os.path.join(j_stream_dir, output_path_for_prev_results)
            
            #for f in glob.glob(os.path.join(j_stream_dir, "*.stream")):
            for f in glob.glob(os.path.join(j_stream_dir, "*.*")):
                shutil.move(f, destination)
                
            join_streams(streams_dir, j_stream_dir, output_stream_name) #(streams_dir, j_stream_dir, d_name, prefix, suffix)
        else: #here because you don't have a joined stream
            print(f'You do not have already a joined stream for {os.path.basename(current_path)}')
            join_streams(streams_dir, j_stream_dir, output_stream_name) #(streams_dir, j_stream_dir, d_name, prefix, suffix)




def compare_lists_with_streams(path_from, rerun, rerun_merge, skip, m_prefix, m_suffix, output_path_for_prev_results):
    logger = logging.getLogger('app')
    
    dic_stream = defaultdict(list)
    dic_list = defaultdict(list)
    
    files_lst = glob.glob(os.path.join(path_from,"*.lst?*"))
    streams = glob.glob(os.path.join(path_from,"streams/*.stream?*"))
    
    
    success = True

    if len(files_lst) == 0:# or len(streams) == 0:
        logger.info("Run {} has not been processed yet".format(path_from))
        success = False
    else:
        
        for file_lst in files_lst:
            filename = os.path.basename(file_lst).replace('split-events-EV-','').replace('split-events-','')

            suffix = re.search(r'.lst\d+', filename).group()
            prefix = filename.replace(suffix,'')

            suffix = re.search(r'\d+', suffix).group()

            key_name = prefix+'-'+suffix
            dic_list[os.path.join(path_from, key_name)] = file_lst
        
        for stream in streams:

            streamname = os.path.basename(stream)
            suffix = re.search(r'.stream\d+', streamname).group()
            prefix = streamname.replace(suffix,'')
            
            suffix = re.search(r'\d+', suffix).group()
            
            key_name = prefix+'-'+suffix
            dic_stream[os.path.join(path_from,key_name)] = stream

        mod_files_lst = dic_list.keys()
        mod_streams = dic_stream.keys()
        
        
        k_inter = set(mod_files_lst) & set(mod_streams)
        k_diff = set(mod_files_lst) - set(mod_streams) #there is no streams for some lst files
        
        if len(k_diff) != 0:
            for k in k_diff:
                logger.info("There is no streams for some {}".format(k))
                success = False
                
                if rerun:
                    os.chdir(os.path.dirname(k))
                    command = "sbatch {}".format(k+'.sh')
                    
                    os.system(command)
                
        for k in k_inter:
            
            lst = dic_list[k]

            k_lst =  len([line.strip() for line in open(lst, 'r').readlines() if len(line)>0])
            stream =  dic_stream[k]

            command = 'grep -ic "Image filename:" {}'.format(stream)
            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
            k_stream = int(process.communicate()[0])

            if k_lst != k_stream:
                logger.info("For {}: stream = {}, lst = {}".format(k, k_stream, k_lst))
                success = False
                if rerun:
                    
                    os.chdir(os.path.dirname(k))
                    command = "sbatch {}".format(k+'.sh')
                    
                    os.system(command)
    if success:
        print(f'All processed correctly in {os.path.basename(path_from)}')
        merge_streams(path_from, rerun_merge, skip, m_prefix, m_suffix, output_path_for_prev_results)
    else:
        print(f'Check log file. Not all processed correctly in {os.path.basename(path_from)}')
        
def process_path(path, pattern, rerun, rerun_merge, skip, prefix, suffix, output_path_for_prev_results):
    if pattern is not None and pattern in os.path.basename(path):
        compare_lists_with_streams(path, rerun, rerun_merge, skip, prefix, suffix, output_path_for_prev_results)
    elif pattern is None:
        compare_lists_with_streams(path, rerun, rerun_merge, skip, prefix, suffix, output_path_for_prev_results) 
        
def main():
    args = parse_cmdline_args()
    rerun = args.r
    pattern = args.p
    rerun_merge = args.m
    prefix = args.pref
    suffix = args.suf
    skip = args.s
    
    if args.o is not None:
        output_path_for_prev_results = args.o
    else:
        output_path_for_prev_results = 'prev_res'
    
    logger = logging.getLogger('app')
    logger.info("main")
    path_from = os.path.abspath(args.path_from)
    if args.f is None:
        if len(glob.glob(os.path.join(path_from, '*.lst*')))!=0:
            process_path(path_from, pattern, rerun, rerun_merge, skip, prefix, suffix, output_path_for_prev_results)
        else:
            for path, dirs, all_files in os.walk(path_from):
                if len(glob.glob(os.path.join(path, '*.lst*')))!=0 and path != path_from:
                    process_path(path, pattern, rerun, rerun_merge, skip, prefix, suffix, output_path_for_prev_results)                    
    else:
        with open(args.f,'r') as f:
            for d in f:
                d = d.strip()
                
                for path, dirs, all_files in os.walk(path_from):
                    if len(glob.glob(os.path.join(path, '*.lst*')))!=0 and path != path_from and d in os.path.basename(path):
                        process_path(path, pattern, rerun, rerun_merge, skip, prefix, suffix, output_path_for_prev_results)

setup_logger()
if __name__ == "__main__":
    main()     
