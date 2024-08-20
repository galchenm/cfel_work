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

path_to_new_mask = 'mask_new/mask'

if __name__ == "__main__":
    mask_file = sys.argv[1]
    path_to_data_mask = sys.argv[2]

    fm = h5.File(mask_file, 'r')
    M = np.array(fm[path_to_data_mask])
    dim = M.shape
    fm.close()
    
    print('Finished reading data from mask. Its dimension is equal to {}\n'.format(dim))

    file_cxi = sys.argv[3]
    path_to_data_cxi = sys.argv[4]
    
    print('Starting reshaping mask from 2D to 4D\n')
    if len(dim) == 2:
        print('We have one mask with 2D array\n')
        M1 = np.array([np.reshape(M.ravel(),(dim[0]//512, 512, dim[1]))])
        print('Just check that output dimension is 4D = {}\n'.format(M1.shape))
    else:
        #M1 = np.array([np.reshape(i.ravel(),(i.shape[0]//512,512,i.shape[1])) for i in M])
        #num = M1.shape[0]
        pass

    data_dim = subprocess.check_output(['/opt/hdf5/hdf5-1.10.5/bin/h5ls', str(os.path.join(os.getcwd(),file_cxi))+str(path_to_data_cxi)])
    data_dim = data_dim.strip().decode('utf-8').split('Dataset ')[1]
    num = int(re.sub(r'({|})','',data_dim).split(',')[0])

    with h5.File(file_cxi, 'a') as f:
        print('Starting adding new mask to cxi file\n')

        d = f.create_dataset(path_to_new_mask, (1,16,512,128), maxshape=(num,16,512,128), dtype=np.float32,chunks=(1,16,512,128), compression="gzip", compression_opts=4)
        d[0, :, :, :] = M1

        for i in range(num):
            d.resize((i+1,16,512,128))
            d[i, :, :,:] = M1 if len(dim) == 2 else M1[i]
    


    print('Finish')