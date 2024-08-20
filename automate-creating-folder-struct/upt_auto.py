#!/usr/bin/env python3
# coding: utf8

"""
bla bla bla
"""
from multiprocessing import Pool, TimeoutError

import os
import sys
import time

from collections import defaultdict

import re
import argparse

from subprocess import call
import shlex


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
    parser.add_argument('file_extension', type=str, help="File extension of data files")
    parser.add_argument('-p', '--p', type=str, help="Pattern in data filenames")
    parser.add_argument('-s', '--s', type=str, help="Sample in data filenames")
    parser.add_argument('-to','--to', type=str, help="The path where you will keep the list of files")
    parser.add_argument('-e','--exclude', type=str, help="Exclude files with this pattern")
    return parser.parse_args()

def folder_to_list_of_files(data_files, new_dir):
    global pattern
    global sample
    global file_extension
    global path_to_lists_of_files
    global exclude
    files_of_interest = data_files
    
    if sample is None and pattern is not None:
        files_of_interest = [filename for filename in files_of_interest if (file_extension in filename and pattern in filename)]
    if sample is not None and pattern is not None:
        files_of_interest = [filename for filename in files_of_interest if (file_extension in filename and pattern in filename and sample in  filename)]
    if sample is not None and pattern is None:
        files_of_interest = [filename for filename in files_of_interest if (file_extension in filename and sample in  filename)]
    if sample is None and pattern is None:

        files_of_interest = [filename for filename in files_of_interest if (file_extension in filename)] 
    if exclude is not None:
        files_of_interest = [filename for filename in files_of_interest if (exclude not in filename)] 

    
    if len(files_of_interest) > 0:
        current_run = os.path.basename(new_dir)
        
        if path_to_lists_of_files is None:
            file_lst_name = os.path.join(new_dir, current_run +".lst")
        else:
            file_lst_name = os.path.join(path_to_lists_of_files, current_run +".lst")
        
        if os.path.exists(file_lst_name):
            os.remove(file_lst_name)
            
        files_lst = open(file_lst_name, 'w+')
        for f in files_of_interest:
            files_lst.write(f)
            files_lst.write("\n")
        files_lst.close()        
        
def create_struct(current_run):
    global dic_in_path_from

    dir_from = os.path.join(path_from, dic_in_path_from[current_run])
    print(100)
    
    if os.path.exists(dir_from):
        
        folders = [os.path.join(dir_from, folder) for folder in os.listdir(dir_from)]
        
        
        if all([os.path.isdir(folder) for folder in folders]):
            print(2)
            for folder in folders:
                data_files = [ os.path.join(folder, file) for file in os.listdir(folder)]
                
                new_dir = os.path.join(path_to, os.path.basename(os.path.dirname(folder))+"_"+os.path.basename(folder))
                print(new_dir)
                if not(os.path.exists(new_dir)):
                    print('Create new folder {}'.format(new_dir))
                    os.mkdir(new_dir)
                if not(os.path.exists(os.path.join(new_dir, "error"))):
                    os.mkdir(os.path.join(new_dir, "error"))
                if not(os.path.exists(os.path.join(new_dir, "streams"))):
                    os.mkdir(os.path.join(new_dir, "streams"))
                if not(os.path.exists(os.path.join(new_dir, "j_stream"))):
                    os.mkdir(os.path.join(new_dir, "j_stream"))
                    os.mkdir(os.path.join(new_dir, "j_stream/error"))    
                folder_to_list_of_files(data_files, new_dir)    
        else:
            print(1)
            new_dir = os.path.join(path_to, current_run)
            folder_to_list_of_files(folders, new_dir)
            if not(os.path.exists(new_dir)):
                print('Create new folder {}'.format(new_dir))
                os.mkdir(new_dir)
            if not(os.path.exists(os.path.join(new_dir, "error"))):
                os.mkdir(os.path.join(new_dir, "error"))
            if not(os.path.exists(os.path.join(new_dir, "streams"))):
                os.mkdir(os.path.join(new_dir, "streams"))
            if not(os.path.exists(os.path.join(new_dir, "j_stream"))):
                os.mkdir(os.path.join(new_dir, "j_stream"))
                os.mkdir(os.path.join(new_dir, "j_stream/error")) 
    

if __name__ == "__main__":
    args = parse_cmdline_args()
    path_from = args.path_from
    path_to = args.path_to
    file_extension = args.file_extension
    path_to_lists_of_files = args.to
    
    pattern = args.p
    sample = args.s
    exclude = args.exclude
    
    folders_in_path_to = []

    dic_in_path_from = defaultdict(list)

    for path, dirs, all_files in os.walk(path_from):
        for di in dirs:
            if re.search(r"[run]*[\d]+", di):
                d_name = di
                
                dic_in_path_from[d_name]=di

    folders_in_path_from = dic_in_path_from.keys()
    
    
    for path, dirs, all_files in os.walk(path_to):
        for file in all_files:
            if re.search(r"lst", file) and re.search(r"[run]*[\d]+[_\d]*", file):

                filename = re.search(r"[run]*[\d]+[_\d]*", file).group()
                if re.search(r"[run]*[\d]+", filename):
                    
                    folders_in_path_to.append(filename)

    folders_need_to_add = list(set(folders_in_path_from) - set(folders_in_path_to))
    
    
    
    for folder in folders_need_to_add:
        create_struct(folder)
    
    
    print('Finish')
