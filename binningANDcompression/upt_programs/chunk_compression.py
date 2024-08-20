import os
import sys
import numpy as np
import h5py as h5

bad_mask = 0
file_cxi = sys.argv[1] #

mask = h5.File('/gpfs/cfel/cxi/scratch/user/yefanov/data/experiments/nk/210216_processing/mask_agipd_edges.h5', 'r')['/data/data']


path_to_data_cxi = "/entry_1/instrument_1/detector_1/data"

path_to_data = "/entry_1/instrument_1/detector_1/dataChunkAuto"
chunksShape = (1,128,128)

with h5.File(file_cxi, 'a') as f:
    data = f[path_to_data_cxi]
    shape_data = data.shape[1:]
    num = data.shape[0]
    initShape = (1,) + shape_data
    maxShape = (num,) + shape_data
    d = f.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32,chunks=True, compression="gzip", compression_opts=6)
    d[0,] = np.where(mask == 0, 0, data[0,])
    
    for i in range(num):
        d.resize((i+1,) + shape_data)
        d[i,] = np.where(mask == 0, 0, data[i,])