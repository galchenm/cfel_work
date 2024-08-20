#!/usr/bin/env python3
# coding: utf8

"""
DDC - detector centre determination

python3 gxparm_DDC.py <path>

python3 gxparm_DDC.py /gpfs/cfel/cxi/scratch/data/2019/PETRA-2019-Yefanov-Dec-P14/process/xdsA2/
"""

import os
import sys

import numpy as np 
import glob

import re
import argparse
import logging

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-path','--path', type=str, help="The path of folder/s that contain/s GXPARM file")
    parser.add_argument('-f','--f', type=str, help="File with path to folders of interest")
    parser.add_argument('-tr','--tr',type=float, help="Treshold for resolution")
    return parser.parse_args()

def get_resolution(CORRECTLP):
    resolution = 0
    index1 = None
    index2 = None
    
    with open(CORRECTLP, 'r') as stream:
        lines = stream.readlines()
        for line in lines:
            
            if line.startswith(' RESOLUTION RANGE  I/Sigma  Chi^2  R-FACTOR  R-FACTOR  NUMBER ACCEPTED REJECTED\n'):
                index1 = lines.index(line)
            if line.startswith('   --------------------------------------------------------------------------\n'):
                index2 = lines.index(line)
                break
        
        if index1 is None or index2 is None:
            return -200000
        else:
            i_start = index1+3
            l = re.sub(r"\s+", "**", lines[i_start].strip('\n')).split('**')[1:]

            res1, I1 = float(l[0]), float(l[2])
            p_res1, p_I1 = 0., 0.

            while I1 >= 1. and i_start < index2:
                if I1 == 1.:
                    return res1

                p_res1, p_I1 = res1, I1
                i_start += 1
                l = re.sub(r"\s+", "**", lines[i_start].strip('\n')).split('**')[1:]
                try:
                    res1, I1 = float(l[0]), float(l[2])
                except ValueError:
                    return p_res1
            
            k = round((I1 - p_I1)/(res1 - p_res1),3)
            b = round((res1*p_I1-p_res1*I1)/(res1-p_res1),3)
            try:
                resolution = round((1-b)/k,3)
            except ZeroDivisionError:
                return -1000

    return resolution



def processing(all_paths, treshold):
    
    global FILE_NAME1
    global FILE_NAME
    
    logger = logging.getLogger('app')
    processed_files = 0
    for path in all_paths:
        if os.path.exists(os.path.join(path,FILE_NAME)):
        
            resolution = get_resolution(os.path.join(path,FILE_NAME))
            if resolution < 0:
                print('With CORRECT.LP file in {} is something wrong'.format(path))
                pass
            else:
                if treshold:
                    if resolution < treshold:
                        if os.path.exists(os.path.join(path,FILE_NAME1)):
                            
                            with open(os.path.join(path,FILE_NAME1), 'r') as fileflow1:
                                
                                line = fileflow1.readline()
                                line = fileflow1.readline()
                                line = fileflow1.readline()
                                
                                space_group, a,b,c, alpha,beta,gamma = fileflow1.readline().split() # UC
                                logger.info(f'{path:<100}{resolution:^10}{a:^10}{b:^10}{c:^10}{alpha:^10}{beta:^10}{gamma:^10}')
                        else:
                            print('In current path {} file with name {} does not exist'.format(path, FILE_NAME1))
                            
                else:
                        if os.path.exists(os.path.join(path,FILE_NAME1)):
                            
                            with open(os.path.join(path,FILE_NAME1), 'r') as fileflow1:
                                
                                line = fileflow1.readline()
                                line = fileflow1.readline()
                                line = fileflow1.readline()

                                
                                space_group, a,b,c, alpha,beta,gamma = fileflow1.readline().split() # UC
                                logger.info(f'{path:<100}{resolution:^10}{a:^10}{b:^10}{c:^10}{alpha:^10}{beta:^10}{gamma:^10}')
                        else:
                            print('In current path {} file with name {} does not exist'.format(path, FILE_NAME1))
                
        else:
            print('In current path {} file with name {} does not exist'.format(path, FILE_NAME))
        

    return 0

if __name__ == "__main__":
    args = parse_cmdline_args()
    
    treshold = args.tr
    
    level = logging.INFO
    logger = logging.getLogger('app')
    logger.setLevel(level)
    log_file = 'file.log'
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    f_handler = logging.FileHandler(os.path.join(os.getcwd(), 'file.log'))
    logger.addHandler(f_handler)
    logger.info(f'{"path":<100}{"resolution":^10}{"a":^10}{"b":^10}{"c":^10}{"alpha":^10}{"beta":^10}{"gamma":^10}')
    print("Log file is {}".format(os.path.join(os.getcwd(), 'file.log')))

    # !!!!Specify the full name of the correct file of interest to us!!!!
    FILE_NAME1 = 'GXPARM.XDS'
    FILE_NAME = 'CORRECT.LP'

    
    
    if args.path is not None:
        main_path = args.path
        
        # Initialize an empty list, where later we add all the paths to our files
        all_paths = []
        for path, dirs, all_files in os.walk(main_path):
            for file in all_files:
                if file == FILE_NAME1:
                    all_paths.append(path)
                    print(path)
    elif args.f is not None:
        all_paths = [os.path.dirname(line.strip()) for line in open(args.f, 'r').readlines() if len(line.strip()) > 0]
        
    #print(all_paths)
    
    for path in all_paths:
        if os.access(path, os.R_OK) == 'false':
            exit()
    processing(all_paths, treshold)
    
    print('FINISH')