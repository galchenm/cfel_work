#!/usr/bin/env python3

"""
python3 add_mask_for_event.py <file_cxi> <maskH5> <slab mask> [-m, <mask_h5path>]

if -m is skipped, h5path to data in slab mask is /data/data

python3 add_mask_for_event.py r0014_detectors_virt.cxi /entry_1/instrument_1/detector_1/mask mask_lyso.h5
"""


import os
import sys
import h5py as h5
import numpy as np
import subprocess
import re
import argparse


os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('file_cxi', type=str, help="Output file of cxi format")
    parser.add_argument('maskH5', type=str, help="hdf5 path for the cxi file mask")
    parser.add_argument('slab',type=str, help="2D mask file")
    parser.add_argument('-m', '--mask_h5path', type=str, help="hdf5 path to slab mask data")

    return parser.parse_args()

def converting_slab_to_3D(mask_file, path_to_mask):

    print('Starting reshaping mask from 2D to 3D\n')

    f = h5.File(mask_file, 'r')
    slab_mask = np.array(f[path_to_mask])
    dim = slab_mask.shape
    f.close()
    
    mask_3D = np.array(np.reshape(slab_mask.ravel(),(dim[0]//512, 512, dim[1])))
    
    print('Finish reshaping\n')

    return mask_3D

def inversion_mask(mask_data):
    print('Inversion of static mask\n')
    inv_mask_data = np.ones_like(mask_data) - mask_data
    return inv_mask_data

def copy_cxi(cxi):
    h5r = h5.File(cxi, 'r')
    cxi = cxi.split('/')[-1] #get the file name
    file_cxi_copy = cxi.split('.')[0] + '_copy_upt_lyso.cxi'
    file_cxi_copy = os.path.join(os.getcwd(),file_cxi_copy)
    
    with h5.File(file_cxi_copy, 'w') as h5w:
        for obj in h5r.keys():        
            h5r.copy(obj, h5w)       
    
    h5r.close()
    return file_cxi_copy

if __name__ == "__main__":
    
    args = parse_cmdline_args()

    file_cxi = args.file_cxi
    mask_cxi = args.maskH5
    slab = args.slab
    mask_slab = "/data/data"

    if args.mask_h5path is not None:
        mask_slab = args.mask_h5path

    #Converting slab mask into 3D
    mask_3D = converting_slab_to_3D(slab, mask_slab)
    
    #Inversion of mask
    mask_3D_inv = inversion_mask(mask_3D) # 1 - bad, 0 - good
    num_events = subprocess.check_output(['/opt/hdf5/hdf5-1.10.6/bin/h5ls', str(file_cxi)+str(mask_cxi)])
    num_events = num_events.strip().decode('utf-8').split('Dataset ')[1]
    num = int(re.sub(r'({|})', '', num_events).split(',')[0]) # Number of events
    print('NUM = {}'.format(num))
    
    #Make o copy of initial cxi file
    
    
    file_cxi_copy = copy_cxi(file_cxi)
    h5r = h5.File(file_cxi, 'r')
    path_to_new_mask = mask_cxi + '_new'
    print('Path to new mask is {}'.format(path_to_new_mask))
    
    with h5.File(file_cxi_copy, 'a') as h5w:
        d = h5w.create_dataset(path_to_new_mask, (1,16,512,128), maxshape=(num,16,512,128), dtype=np.float32,chunks=(1,16,512,128), compression="gzip", compression_opts=4)
        mask = h5r[mask_cxi]
        for i in range(num):
            d.resize((i+1,16,512,128))
            slice_arr = mask[i,:,:,:]
            slice_arr = np.array(slice_arr)
            index_bad = np.where(slice_arr > 0)
            
            slice_arr_upt = np.zeros_like(slice_arr) # creating binary mask of event: 1 - bad, 0 - good
            slice_arr_upt[index_bad] = 1

            tmp = np.bitwise_or(slice_arr_upt, mask_3D_inv)
            tmp[index_bad] = slice_arr[index_bad] # add real value of bad pixels
            d[i, :, :, :] = tmp


    h5r.close()





