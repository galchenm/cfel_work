#!/usr/bin/env python3
#
# python3 mask_converter.py <mask_filename>.h5 /path_to_data

import sys
import os
import h5py as h5
import numpy as np

os.nice(0)


if __name__ == "__main__":
    mask = sys.argv[1]
    path_to_data = sys.argv[2]
    f = h5.File(mask, 'r')
    M = np.array(f[path_to_data])
    dim = M.shape
    
    new_mask = mask.split('.')[0]+'_test.h5'

    if len(dim) == 2:
        num = 27270
        #M1 = np.array([np.reshape(M.ravel(),(dim[0]//512, 512, dim[1])) for i in range(num)], dtype=np.int8)
        M1 = np.array([np.reshape(M.ravel(),(dim[0]//512, 512, dim[1]))], dtype=np.int8)
        print(M1.shape)
    else:
        M1 = np.array([np.reshape(i.ravel(),(i.shape[0]//512,512,i.shape[1])) for i in M])
        num = M1.shape[0]

    with h5.File(new_mask, 'w') as f:
        d = f.create_dataset(path_to_data, (1,16,512,128), maxshape=(num,16,512,128), dtype=np.float32,chunks=(1,16,512,128), compression="gzip", compression_opts=4)
        d[0, :, :, :] = M1

        for i in range(num):
            print(i)
            d.resize((i+1,16,512,128))
            d[i, :, :,:] = M1 if len(dim) == 2 else M1[i]
    


    print('Finish')