import h5py as h5
import os
import sys
import numpy as np

#filename_gains = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/Cheetah-AGIPD08-subtracted-142_162-dark141_all.h5' #sys.argv[1]
#filename_data = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/upt-Cheetah-AGIPD08-subtracted-142_162-dark141_all.h5'
filename_data = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/new-Cheetah-AGIPD08-subtracted-143-dark141.h5' #Cheetah-AGIPD08-subtracted-142_162-dark141_all-corrected-screen.h5'

path_to_data = '/shadow/data' #sys.argv[2]
path_to_gains = '/shadow/gain' #sys.argv[3]


#path_to_data = '/comMode/data' #sys.argv[2]
#path_to_gains = '/comMode/gain' #sys.argv[3]

path_to_file = os.path.dirname(filename_data)
result_filename = filename_data.split('.')[0] + '-res-shadow-divide.h5'
dataHdf5 = '/data/data'

readFile = h5.File(filename_data, 'r')
data = readFile[path_to_data]

data_shape = data.shape
shape_data = data_shape[1:]
maxNum = data_shape[0]

#readFile_gains = h5.File(filename_gains, 'r')
#gains = readFile_gains[path_to_gains]

gains = readFile[path_to_gains]


writeFile = h5.File(result_filename, 'a')
init_shape = (1,) + shape_data
max_shape = (maxNum,) + shape_data
    
subtracted_data = writeFile.create_dataset(dataHdf5, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)

for cellId in range(0,maxNum):
    print(cellId)
    subtracted_data.resize((cellId+1,) + shape_data)
    subtracted_data[cellId, :,:] = np.multiply(data[cellId, :,:], gains[cellId, :,:])
    #subtracted_data[cellId, :,:] = np.divide(data[cellId, :,:], gains[cellId, :,:]) * 100

#readFile_gains.close()
readFile.close()
writeFile.close()