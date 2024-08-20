#!/usr/bin/env python3


import sys
import os
import h5py as h5
import numpy as np

os.nice(0)


if __name__ == "__main__":
    mask = sys.argv[1]
    path_to_data = sys.argv[2]
    num = int(sys.argv[3])
    f = h5.File(mask, 'r')
    M = np.array(f[path_to_data])
    dim = M.shape
    new_mask = '4D_mask_for_all_events.h5'

    M1 = np.array([np.reshape(M.ravel(),(dim[0]//512, 512, dim[1]))])
    
    with h5.File(new_mask, 'w') as f:
        d = f.create_dataset(path_to_data, (1,16,512,128), maxshape=(num,16,512,128), dtype=np.float32,chunks=(1,16,512,128), compression="gzip", compression_opts=4)
        d[0, :, :, :] = M1

        for i in range(num):
            d.resize((i+1,16,512,128))
            d[i, :, :,:] = M1
    


    print('Finish')