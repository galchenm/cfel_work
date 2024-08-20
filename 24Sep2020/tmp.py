#!/usr/bin/env python3
# coding: utf8

"""
DDC - detector centre determination

python3 gxparm_DDC.py <path>

python3 gxparm_DDC.py /gpfs/cfel/cxi/scratch/data/2019/PETRA-2019-Yefanov-Dec-P14/process/xdsA2/
"""

import os
import sys
import time
import numpy as np 
import subprocess

import re
import argparse
import h5py as h5


os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('path', type=str, help="The path of folder/s that contain/s GXPARM file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmdline_args()
    main_path = args.path

    print('''Main path = {}'''.format(main_path))

    #FILE_NAME1 = '-class0-sum'
    file_status = "status.txt"
    FILE_NAME1 = '-class1-sum'


    for path, dirs, all_files in os.walk(main_path):
        for file in all_files:
            if FILE_NAME1 in file:
                print("File is {}".format(os.path.join(path, file)))
                filename = os.path.join(path, file)
                H5file = h5.File(filename, 'r')
                data = H5file['/data/data'][:]
                print("Data shape is {}".format(data.shape))
                
                if file_status in all_files:
                    status = open(os.path.join(path, file_status), 'r')
                    lines = status.readlines()
                    for line in lines:
                        line = line.strip()
                        print("Line in status file is {}".format(line))
                        if line.startswith('Frames processed:'):
                            frames = int(line.split('Frames processed: ')[1])
                            print("Frames are {}".format(frames))
                        elif line.startswith('Number of hits: '):
                            hits = int(line.split('Number of hits: ')[1])
                            print("Hits are {}".format(hits))
                else:
                    print("WARNING! NO STATUS FILE. SKIP THIS folder\n")
                    frames = None
                    hits = None
                    continue

                if frames is not None and hits is not None:
                    newH5filename = os.path.join(path, 'av-' + file)
                    print("newH5filename is {}".format(newH5filename))
                    newH5file = h5.File(newH5filename, 'w')
                    #newH5file.create_dataset('/data/data', data=data/(frames - hits))
                    newH5file.create_dataset('/data/data', data=data/(hits))
                    newH5file.close()
                else:
                    pass

                H5file.close()