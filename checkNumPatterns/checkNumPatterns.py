#!/usr/bin/env python
# coding: utf8

"""
"""

import os
import sys
import h5py as h5
import numpy as np
import argparse
import glob

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i', type=str, help="Path with files")
    parser.add_argument('-h5p', type=str, help="hdf5 path for the cxi file data")

    return parser.parse_args()


if __name__ == "__main__":
    
    args = parse_cmdline_args()
    
    path_cxi = args.h5p
    
    d = {}
    for path, dirs, all_files in os.walk(args.i):
        #print(path)
        if path != args.i:
            files = glob.glob(os.path.join(path,'*cxi'))
            if len(files) == 0:
                files = glob.glob(os.path.join(path,'*data*.h5'))
                if len(files) == 0:
                    print(f'Check {path} - something went wrong')
                else:
                    for ffile in files:
                        block = os.path.basename(os.path.dirname(ffile))
                        #print(block)
                        file = h5.File(ffile, 'r')
                        data = file[path_cxi]
                        d[block] = d.get(block, 0) + data.shape[0]
                 
    for block in d:
       print(f'{block} - {d[block]}')
    