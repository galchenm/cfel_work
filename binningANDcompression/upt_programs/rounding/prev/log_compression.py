import os
import sys
import numpy as np
import h5py as h5


def round_precision(n,precision):
   return ((n+precision//2)//precision)*precision
   
   
def round_log(n):
   return np.sign(n)*(np.sqrt(2)**(np.round(np.log2(n*n+1),0))).astype(np.int)
   


file_cxi = sys.argv[1]
path_to_data_cxi = sys.argv[2]
path_to_data = sys.argv[3]

with h5.File(file_cxi, 'a') as f:
    data = f[path_to_data_cxi]
    shape_data = data.shape[1:]
    num = data.shape[0]
    initShape = (1,) + shape_data
    maxShape = (num,) + shape_data
    d = f.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
    
    d[0,] = (round_log(data[0,])).astype(np.int32)
    
    for i in range(num):
        d.resize((i+1,) + shape_data)
        d[i,] = (round_log(data[i,])).astype(np.int32)