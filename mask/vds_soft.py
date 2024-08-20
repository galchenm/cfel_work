#!/usr/bin/env python3

"""
This Python script converts slab mask to 3D format ans use VDS features.
Example of usage: 
python3 vds_soft.py r0014_detectors_virt.cxi /entry_1/instrument_1/detector_1 -f mask_mar.h5 -mp /data/data


Command line 1: 
./vds_soft.py <file_cxi> <hdf5 path for the cxi file data> [[-f <slab mask>] [-mp <hdf5 path to slab mask data>]]


Command line 2: 
./vds_soft.py <file_cxi> <hdf5 path for the cxi file data> [[-um <external mask for each event>] [-up <hdf5 path to mask data>]]

Using flags [-f, -mp] excludes usage of [-um, -up] and vice versa.


[[-f <2D mask file>] [-mp <hdf5 path to slab mask data>]]: 
convert input slab mask into 3D format, add this mask into initial cxi file and 
create virtual dataset in cxi file to recorded mask for all runs.


[[-um <External mask for each event>] [-up <hdf5 path to mask data>]]: 
create external link to this mask in cxi file


Warning: external link can work only if the size of mask dataset satisfies number of runs in cxi file.
"""


import os
import sys
import h5py as h5
import numpy as np
import subprocess
import re
import argparse


os.nice(0)

path_to_new_mask = 'mask_new/mask'


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('file_cxi', type=str, help="Output file of cxi format")
    parser.add_argument('h5path', type=str, help="hdf5 path for the cxi file data")
    parser.add_argument('-f', '--flat',type=str, help="2D mask file")
    parser.add_argument('-mp', '--mask_h5path', type=str, help="hdf5 path to slab mask data")
    parser.add_argument('-um','--union_mask',type=str, help="External union mask for each event")
    parser.add_argument('-up', '--union_h5path', type=str, help="hdf5 path to mask data")

    return parser.parse_args()

if __name__ == "__main__":

    args = parse_cmdline_args()
    file_cxi = args.file_cxi
    path_to_data_cxi = args.h5path

    data_dim = subprocess.check_output(['/opt/hdf5/hdf5-1.10.5/bin/h5ls', str(os.path.join(os.getcwd(),file_cxi))+str(path_to_data_cxi)])
    data_dim = data_dim.strip().decode('utf-8').split('Dataset ')[1]
    num = int(re.sub(r'({|})','',data_dim).split(',')[0])

    
    if args.flat is not None:
        if args.mask_h5path is not None:
            path_to_data_mask = args.mask_h5path
        else:
            path_to_data_mask = '/data/data'
        
        mask_file = args.flat
        fm = h5.File(mask_file, 'r')
        M = np.array(fm[path_to_data_mask])
        dim = M.shape
        fm.close()
        
        print('Starting reshaping mask from 2D to 4D\n')
        
        M1 = np.array(np.reshape(M.ravel(),(dim[0]//512, 512, dim[1])))

        print('Adding 3D mask to cxi file\n')

        fm = h5.File(file_cxi,'a')
        fm.create_dataset('mask_data/data', data=M1)
        fm.close()

        print('Creating layout\n')

        layout = h5.VirtualLayout(shape=(num,M1.shape[0],M1.shape[1],M1.shape[2]))
        vsource = h5.VirtualSource(file_cxi, 'mask_data/data', shape=(M1.shape[0],M1.shape[1],M1.shape[2],))
        vvsource =[vsource for i in range(num)]
        
        for n in range(num):
            layout[n] = vvsource[n]

        with h5.File(file_cxi, 'a') as f:
            print('Starting adding new mask to cxi file\n')
            f.create_virtual_dataset(path_to_new_mask, layout)

        print('Finish')

    elif args.union_mask is not None:
        if args.union_h5path is not None:

            path_to_data_mask = args.union_h5path
        else:
            path_to_data_mask = '/data/data'
        fnew_m = args.union_mask


        with h5.File(file_cxi, 'a') as f:
            print('Starting adding new mask to cxi file as External Link\n')       
            f[path_to_new_mask] = h5.ExternalLink(fnew_m, path_to_data_mask)

        print('Finish')
    else:
        print('Restart script with mask file and cxi file parameters\n')



