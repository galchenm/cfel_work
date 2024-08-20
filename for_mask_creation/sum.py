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
    parser.add_argument('-i','--i', type=str, help="Path with files")
    parser.add_argument('-o','--o', type=str, help="The name of file for making mask")
    parser.add_argument('-s','--s', type=str, help="Single file")
    parser.add_argument('-n','--n', type=int, help="Num of patterns for the sum")
    parser.add_argument('-h5p', type=str, help="hdf5 path for the cxi file data")

    return parser.parse_args()


if __name__ == "__main__":
    
    args = parse_cmdline_args()
    
    path_cxi = args.h5p
    correct = True
    
    if args.s is not None:
        file = h5.File(args.s, 'r')
        data = file[path_cxi]
        if args.n is not None:
            Sum_Int = np.sum(data[0:args.n,],axis=0)
        else:
            Sum_Int = np.sum(data[:,],axis=0)        
    elif args.i is not None:
        files = glob.glob(os.path.join(args.i,'*cxi'))
        if len(files) == 0:
            files = glob.glob(os.path.join(args.i,'*data*.h5'))
            #files = glob.glob(os.path.join(args.i,'*.h5'))
            if len(files) == 0:
                print(f'Check {args.i} - something went wrong. Carefully check format and filenames')
                correct = False
            else:
                if args.n is not None:
                    Sum_Int = 0
                    N = args.n
                    num = 0
                    for ffile in files:
                        file = h5.File(ffile, 'r')
                        data = file[path_cxi]
                        if num >= N:
                            break
                        Sum_Int += np.sum(data[:,],axis=0)
                        num += data.shape[0]
                else:        
                    Sum_Int = 0
                    for file in files:
                        file = h5.File(ffile, 'r')
                        data = file[path_cxi]
                        Sum_Int += np.sum(data[:,],axis=0)
    else:
        print('You have to provide with anything for making mask!')
        correct = False
    
    if correct:
        if args.o is not None:
            output_filename = args.o
        else:
            output_filename = 'forMask-v1.h5'
        f = h5.File(output_filename, 'w')
        f.create_dataset('/data/data', data=np.array([Sum_Int]))
        f.close()
