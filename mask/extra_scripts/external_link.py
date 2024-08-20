#!/usr/bin/env python3
#
# python3 mask_converter.py <mask_filename>.h5 path_to_data_mask <file.cxi> path_to_data_cxi

import os
import sys
import h5py as h5
import numpy as np
import subprocess
import re
import argparse


os.nice(0)

path_to_new_mask = 'mask_new/mask'


def parse_cmdline_args():
    parser = argparse.ArgumentParser(description='Parsing arguments from command line')
    parser.add_argument('file_cxi', type=str, help="Output file of cxi format")
    parser.add_argument('h5path', type=str, help="hdf5 path for the cxi file data")
    parser.add_argument('-f', '--flat',type=str, help="2D mask file")
    parser.add_argument('-mp', '--mask_h5path', type=str, help="path inside the h5file of the starting mask")
    parser.add_argument('-um','--union_mask',type=str, help="External union mask for each event")
    parser.add_argument('-up', '--union_h5path', type=str, help="path inside the h5file of the starting mask")

    return parser.parse_args()

if __name__ == "__main__":

    args = parse_cmdline_args()
    file_cxi = args.file_cxi
    path_to_data_cxi = args.h5path

    
    if args.flat is not None:
        if args.mask_h5path is not None:
            path_to_data_mask = args.mask_h5path
        else:
            path_to_data_mask = '/data/data'
        
        fm = h5.File(mask_file, 'r')
        M = np.array(fm[path_to_data_mask])
        fm.close()
        
        fnew_m = mask_file.split('.')[0]+"_soft.h5"
        fm = h5.File(fnew_m,'w')

        print('Starting reshaping mask from 2D to 4D and writing it to new mask {}\n'.format(fnew_m))
        M1 = np.array(np.reshape(M.ravel(),(dim[0]//512, 512, dim[1])))
        fm.create_dataset(path_to_data_mask, data = M1)
        fm.close()

    elif args.union_mask is not None:
        if args.union_h5path is not None:

            path_to_data_mask = args.union_h5path
        else:
            path_to_data_mask = '/data/data'
        fnew_m = args.union_mask
    else:
        print('Restart script with mask file and cxi file parameters\n')

    data_dim = subprocess.check_output(['/opt/hdf5/hdf5-1.10.5/bin/h5ls', str(os.path.join(os.getcwd(),file_cxi))+str(path_to_data_cxi)])
    data_dim = data_dim.strip().decode('utf-8').split('Dataset ')[1]
    num = int(re.sub(r'({|})','',data_dim).split(',')[0])


    #link = h5.ExternalLink(fnew_m, path_to_data_mask)
    #l = [link]*num

    with h5.File(file_cxi, 'a') as f:
        print('Starting adding new mask to cxi file as External Link\n')
        
        f[path_to_new_mask] = h5.ExternalLink(fnew_m, path_to_data_mask)
        #dt = h5.special_dtype(ref=h5.RegionReference)
        #str_type = h5.new_vlen(str)
        #str_type = h5.special_dtype(vlen=str)
        #dset = f.create_dataset(path_to_new_mask, (num,), dtype=str_type)
        
        #for i in range(num):
        #    dset[i] = link
        #    #f["mask_new"][str(i)] = h5.ExternalLink(files_list[i], path_to_data_mask)

        

    print('Finish')