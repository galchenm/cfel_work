#!/usr/bin/env python3
# coding: utf8

"""

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
    return parser.parse_args()


def processing(all_paths):
    
    global FILE_NAME
    
    logger = logging.getLogger('app')
    for path in all_paths:
        if os.path.exists(os.path.join(path,FILE_NAME)):
            with open(os.path.join(path,FILE_NAME), 'r') as fileflow1:
                readFlag = False
                find_anisotropic = False
                for line in fileflow1:
                    
                    if "Unit cell parameters" in line:
                           
                        a,b,c,alpha,beta, gamma = line.split('Unit cell parameters')[1].split()
                        readFlag = True
                        resolutionFlag = False
                        
                        
                    elif readFlag:
                    
                        if "High resolution limit" in line:
                            
                            resolution = line.split('   High resolution limit')[1].split()[-1]
                            resolutionFlag = True
                            
                        elif '  CC(1/2)' in line:
                            readFlag = False
                            CChalf = line.split('  CC(1/2)')[1].split()[-1]
                            
                            if resolutionFlag:
                                #print(f'{path:<100}{resolution:^10}{CChalf:^10}{a:^10}{b:^10}{c:^10}{alpha:^10}{beta:^10}{gamma:^10}')
                                resolutionFlag = False
                                logger.info(f'{path:<100}{resolution:^10}{CChalf:^10}{a:^10}{b:^10}{c:^10}{alpha:^10}{beta:^10}{gamma:^10}')
                                break
                    else:
                        pass
                
        else:
            print('In current path {} file with name {} does not exist'.format(path, FILE_NAME))
        

    return 0

if __name__ == "__main__":
    args = parse_cmdline_args()
    
    
    level = logging.INFO
    logger = logging.getLogger('app')
    logger.setLevel(level)
    log_file = 'file-autoproc.log'
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    f_handler = logging.FileHandler(os.path.join(os.getcwd(), log_file))
    logger.addHandler(f_handler)
    logger.info(f'{"path":<100}{"resolution":^10}{"CChalf":^10}{"a":^10}{"b":^10}{"c":^10}{"alpha":^10}{"beta":^10}{"gamma":^10}')
    print("Log file is {}".format(os.path.join(os.getcwd(), log_file)))

    # !!!!Specify the full name of the correct file of interest to us!!!!
    FILE_NAME = 'staraniso_alldata-unique.table1'

    if args.path is not None:
        main_path = args.path
        
        # Initialize an empty list, where later we add all the paths to our files
        all_paths = []
        for path, dirs, all_files in os.walk(main_path):
            for file in all_files:
                if file == FILE_NAME:
                    all_paths.append(path)
                    print(path)
    elif args.f is not None:
        all_paths = [os.path.dirname(line.strip()) for line in open(args.f, 'r').readlines() if len(line.strip()) > 0]
        
    
    for path in all_paths:
        if os.access(path, os.R_OK) == 'false':
            exit()
    processing(all_paths)
    
    print('FINISH')