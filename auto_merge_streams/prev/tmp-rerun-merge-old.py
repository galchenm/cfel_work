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
    
    #parser.add_argument('-m', '--m', type=bool, default=False, action="store" , help="Use this flag if you want to rerun merging. Be careful with prefix and suffix for new stream")
    #parser.add_argument('-r', '--r', type=bool, default=False, action="store" , help="Use this flag if you want to rerun indexing")
    #parser.add_argument('-s', '--s', type=bool, default=False, action="store" , help="Use this flag if you want to skip merging in case if joined streams is alreadz created")

    parser.add_argument('-m', '--m', action='store_true' , help="Use this flag if you want to rerun merging. Be careful with prefix and suffix for new stream")
    parser.add_argument('-r', '--r', action='store_true', help="Use this flag if you want to rerun indexing")
    parser.add_argument('-s', '--s', action='store_true', help="Use this flag if you want to skip merging in case if joined streams is alreadz created")
    
    return parser.parse_args()


def merge_streams(current_path, rerun, prefix, suffix):
    if prefix is None:
        prefix = ''
    if suffix is None:
        suffix = ''    
    
    streams_dir = os.path.join(current_path, "streams")
    j_stream_dir = os.path.join(current_path, "j_stream")
    d_name = os.path.basename(current_path)
    print(current_path)
    print(d_name)
    
    if not(os.path.exists(j_stream_dir)):
        os.mkdir(j_stream_dir)
    
    if len(glob.glob(os.path.join(j_stream_dir, "*.stream"))) != 0 and not(rerun):
        cat = input(f'Type y if you want to cat new stream for {os.path.basename(current_path)}, otherwise, enter n: ').lowercase()
        if cat == 'y':
            if not(os.path.exists(os.path.join(j_stream_dir, 'prev'))):
                os.mkdir(os.path.join(j_stream_dir, 'prev'))
            destination = os.path.join(j_stream_dir, 'prev')
            
            for f in glob.glob(os.path.join(j_stream_dir, "*.stream")):
                shutil.move(f, destination)
            
            if os.path.exists(streams_dir):
                os.chdir(streams_dir)
                files = glob.glob("*.stream?*")
                if len(files) > 0:
                    files = [os.path.abspath(file) for file in files]
                    
                    if len(prefix)>0 and len(suffix)>0:
                        output = f'{os.path.join(j_stream_dir, prefix+"-"+str(d_name))}-{suffix}.stream'
                    if len(prefix)>0 and len(suffix)==0:
                        output = f'{os.path.join(j_stream_dir, prefix+"-"+str(d_name))}.stream'                        
                    if len(prefix) == 0 and len(suffix)>0:
                        output = f'{os.path.join(j_stream_dir, str(d_name))}-{suffix}.stream'
                    if len(prefix) == 0 and len(suffix)==0:
                        output = f'{os.path.join(j_stream_dir, str(d_name))}.stream'                    
                    
                    command_line = "cat " + " ".join(files) + f' >> {output}'
                    os.system(command_line)
                    
                    print("Run the command line: {}".format(command_line))
                    print(f'{os.path.join(j_stream_dir, prefix+"-"+str(d_name))}-{suffix}.stream')
                else:
                    print("There is no streams in {}".format(current_path))
    elif os.path.exists(streams_dir) or rerun:
        os.chdir(streams_dir)
        files = glob.glob("*.stream?*")
        if len(files) > 0:
            files = [os.path.abspath(file) for file in files]
            
            if len(prefix)>0 and len(suffix)>0:
                output = f'{os.path.join(j_stream_dir, prefix+"-"+str(d_name))}-{suffix}.stream'
            if len(prefix)>0 and len(suffix)==0:
                output = f'{os.path.join(j_stream_dir, prefix+"-"+str(d_name))}.stream'                        
            if len(prefix) == 0 and len(suffix)>0:
                output = f'{os.path.join(j_stream_dir, str(d_name))}-{suffix}.stream'
            if len(prefix) == 0 and len(suffix)==0:
                output = f'{os.path.join(j_stream_dir, str(d_name))}.stream'                    
            
            command_line = "cat " + " ".join(files) + f' >> {output}'
            os.system(command_line)
            
            print("Run the command line: {}".format(command_line))
            
        else:
            print("There is no streams in {}".format(current_path))
        
    else:
        print("There is no streams folder in {}".format(current_path))


#def compare_lists_with_streams(path_from, rerun, pattern, rerun_merge, m_prefix, m_suffix):
def compare_lists_with_streams(path_from, rerun, rerun_merge, m_prefix, m_suffix):
    print('Rerun ', rerun) # type(rerun) = bool
    dic_stream = defaultdict(list)
    dic_list = defaultdict(list)
    
    files_lst = glob.glob(os.path.join(path_from,"*.lst?*"))
    streams = glob.glob(os.path.join(path_from,"streams/*.stream?*"))
    
    success = True

    if len(files_lst) == 0 or len(streams) == 0:
        print("Run {} has not been processed yet".format(path_from))
        success = False
    else:
        
        for file_lst in files_lst:
            filename = os.path.basename(file_lst).replace('split-events-','')

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
                print("There is no streams for some {}".format(k))
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
                print("For {}: stream = {}, lst = {}".format(k, k_stream, k_lst))
                success = False
                if rerun:
                    os.chdir(os.path.dirname(k))
                    command = "sbatch {}".format(k+'.sh')
                    os.system(command)
    if success:
        print(f'All processed correctly in {os.path.basename(path_from)}')
        merge_streams(path_from, rerun_merge, m_prefix, m_suffix)
        
def process_path(path, pattern, rerun, rerun_merge, skip, prefix, suffix):
    if pattern is not None and pattern in os.path.basename(path):
        compare_lists_with_streams(path, rerun, rerun_merge, prefix, suffix)
    elif pattern is None:
        compare_lists_with_streams(path, rerun, rerun_merge, prefix, suffix) 
                        
if __name__ == "__main__":
    args = parse_cmdline_args()
    rerun = args.r
    pattern = args.p
    rerun_merge = args.m
    prefix = args.pref
    suffix = args.suf
    skip = args.s
    
    path_from = os.path.abspath(args.path_from)
    if args.f is None:
        if len(glob.glob(os.path.join(path_from, '*.lst*')))!=0:
            if pattern is not None and pattern in os.path.basename(path_from):
                compare_lists_with_streams(path_from, rerun, rerun_merge, prefix, suffix)
            elif pattern is None:
                compare_lists_with_streams(path_from, rerun, rerun_merge, prefix, suffix)            
        else:
            for path, dirs, all_files in os.walk(path_from):
                
                if len(glob.glob(os.path.join(path, '*.lst*')))!=0 and path != path_from:
                    
                    if pattern is not None and pattern in os.path.basename(path):
                        compare_lists_with_streams(path, rerun, rerun_merge, prefix, suffix)
                    elif pattern is None:
                        compare_lists_with_streams(path, rerun, rerun_merge, prefix, suffix)                    
    else:
        with open(args.f,'r') as f:
            for d in f:
                d = d.strip()
                for path, dirs, all_files in os.walk(path_from):
                    
                    if len(glob.glob(os.path.join(path, '*.lst*')))!=0 and path != path_from and d in os.path.basename(path):
                        if pattern is not None and pattern in os.path.basename(path):
                            compare_lists_with_streams(path, rerun, rerun_merge, prefix, suffix)
                        elif pattern is None:
                            compare_lists_with_streams(path, rerun, rerun_merge, prefix, suffix)

    