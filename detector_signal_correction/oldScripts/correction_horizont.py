import numpy as np
import h5py as h5
import os
import sys

filename = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/Cheetah-AGIPD08-subtracted-142_162-dark141_all.h5'
f = h5.File(filename, 'r')
dataHdf5 = '/data/data'
data = f[dataHdf5]
cellIds, maxFS, maxSS = data.shape
print(cellIds, maxFS, maxSS)
shape_data = (maxFS, maxSS)

new_filename = os.path.join(os.path.dirname(filename),'upt-'+os.path.basename(filename))
writeFile = h5.File(new_filename, 'a')

init_shape = (1,) + shape_data
max_shape = (cellIds,) + shape_data

subtracted_data = writeFile.create_dataset(dataHdf5, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=6)

for cellId in range(0,cellIds):
    
    subtracted_data.resize((cellId+1,) + shape_data)
    mean_upp = np.median(data[cellId,66:91,0:64])
    mean_down = np.median(data[cellId,66:91,64:128])
    print(cellId, mean_down)
    subtracted_data[cellId,:,0:64] = data[cellId,:,0:64] - mean_upp
    subtracted_data[cellId,:,64:128] = data[cellId,:,64:128] - mean_down

f.close()
writeFile.close()
print('FINISH1')