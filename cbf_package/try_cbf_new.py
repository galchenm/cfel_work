# coding: utf8

import numpy as np
import fabio
import h5py as h5
import sys

file_name = "files.lst"

max_size = 0
min_shape = None
data_shape = None
with open(file_name,'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        
        if min_shape is None:
            print('Find min shape')
            data =  fabio.open(line)
            min_shape = (1,) + (data.data.shape[-2], data.data.shape[-1],)
            data_shape = (data.data.shape[-2], data.data.shape[-1],)
        max_size+=1
        print('still in loop...')

max_shape = (max_size,) + data_shape

print(min_shape, max_shape)

imageNumber = 0

with h5.File('fdip_background_new.h5', 'w') as h5w, open(file_name,'r') as f:
    lines = f.readlines()
    print('Create dataset')
    d = h5w.create_dataset("/data/data", min_shape, maxshape=max_shape, dtype=np.float32,chunks=min_shape, compression="gzip", compression_opts=4)
    for line in lines:
        print('Push data into hdf5 file')
        line = line.strip()
        data = fabio.open(line)
        d.resize((imageNumber+1,) + data_shape)
        d[imageNumber,] = np.array(data.data)
        print('Finished with image number {}'.format(imageNumber))
        imageNumber+=1
