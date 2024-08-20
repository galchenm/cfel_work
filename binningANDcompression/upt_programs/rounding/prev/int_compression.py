import os
import sys
import numpy as np
import h5py as h5


file_cxi = sys.argv[1]
path_to_data_cxi = sys.argv[2]
path_to_data = sys.argv[3]
N = int(sys.argv[4])


with h5.File(file_cxi, 'a') as f:
    data = f[path_to_data_cxi]
    shape_data = data.shape[1:]
    num = data.shape[0]
    initShape = (1,) + shape_data
    maxShape = (num,) + shape_data
    d = f.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
    
    d[0,] = np.where(data[0,] < 32000, data[0,], 32000) #(np.round(data[0,]/N,0)*N).astype(np.int32)
    
    for i in range(num):
        d.resize((i+1,) + shape_data)
        d[i,] =  np.where(data[i,] < 32000, data[i,], 32000) #(np.round(data[i,]/N,0)*N).astype(np.int32)