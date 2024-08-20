#!/usr/bin/env python3
#
# python3 mask_converter.py <mask_filename>.h5 path_to_data_mask <file.cxi> path_to_data_cxi

import os
import sys
import h5py as h5
import numpy as np
import subprocess
import re

os.nice(0)

path_to_new_mask = '/mask_new/mask'

if __name__ == "__main__":
    mask_file = sys.argv[1]
    path_to_data_mask = sys.argv[2]

    fm = h5.File(mask_file, 'r')
    M = np.array(fm[path_to_data_mask])
    dim = M.shape
    fm.close()

    print('Finished reading data from mask. Its dimension is equal to {}\n'.format(dim))

    file_cxi = sys.argv[3]
    
    print('Starting reshaping mask from 2D to 3D\n')
    
    print('We have one mask with 2D array\n')
    M1 = np.array(np.reshape(M.ravel(),(dim[0]//512, 512, dim[1])))
    print('Just check that output dimension is 3D = {}\n'.format(M1.shape))
    new_mask_file = '3D_from_slab_'+mask_file
    fm = h5.File(new_mask_file,'a')
    fm.create_dataset(path_to_data_mask, data = M1)
    fm.close()


    with h5.File(file_cxi, 'a') as f:
        print('Starting adding new mask to cxi file\n')
        #f[path_to_new_mask] = h5.SoftLink('mask_data/data')
        f[path_to_new_mask] = h5.ExternalLink(new_mask_file, path_to_data_mask)

    print('Finish')