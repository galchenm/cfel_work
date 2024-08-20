import h5py as h5
import os
import sys
import numpy as np


filename_gain = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/Cheetah-AGIPD08-subtracted-142_162-dark141_all-corrected-screen-v2.h5'
path_to_gains = '/gain/data'

#filename_data = '/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/hdf5/r0107-cry60a_snr5_dark95/S00000/EuXFEL-r0107-c00.cxi' #'/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/hdf5/r0143-cry60a_snr5_dark95/r0108-detector0-class1-sum.h5'

pathCELLId='/instrument/cellID'
p='/entry_1/instrument_1/detector_1/detector_corrected/data'

#template1 = '/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/hdf5/r0107-cry60a_snr5_dark95/S000{}/EuXFEL-r0107-c00.cxi'
#template2 = '/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/hdf5/r0107-cry60a_snr5_dark95/S000{}/EuXFEL-r0107-c01.cxi'
template1 = '/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/hdf5/r0143-cry8_snr5_dark141/S000{}/EuXFEL-r0143-c00.cxi'
template2 = '/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/hdf5/r0143-cry8_snr5_dark141/S000{}/EuXFEL-r0143-c01.cxi'

files = [template1.format( '0'+str(i) if len(str(i)) < 2 else str(i)) for i in range(29)] 
files += [template2.format( '0'+str(i) if len(str(i)) < 2 else str(i)) for i in range(29)]

files = [file for file in files if os.path.isfile(file)]

print(files)

readFile = h5.File(filename_gain, 'r')
gains = readFile[path_to_gains]
shape_data = gains.shape
maxNum = 352



result_filename = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/av-r0143-panel8.h5'

panel = 8

#d = {i:0 for i in range(maxNum)}

d = {}

all_data = np.zeros(shape=(maxNum,512,128))
mult_all_data = np.zeros(shape=(maxNum,512,128))
all_data2 = np.zeros(shape=(maxNum,512,128))
total = 0

for filename_data in files:
    dataRead = h5.File(filename_data, 'r')
    data = dataRead[p]
    cellIDs = dataRead[pathCELLId][:]
    
    for ind in range(len(cellIDs)):
        cellId = int(cellIDs[ind])
        print(cellId)
        
        data_need = data[ind, panel*512:(panel+1)*512,:]
        

        all_data2[cellId, :,:] += data_need
        all_data[cellId, :,:] += data_need
        mult_all_data[cellId, :,:] += np.multiply(data_need, gains[cellId, :,:])
        #d[cellId] += 1
        d[cellId] = d.get(cellId, 0) + 1
        total +=1




print(d)

print(list(d.keys()).sort())
#for cellId in range(352):
for cellId in d.keys():
    all_data2[cellId, :,:] /= d[cellId]

writeFile = h5.File(result_filename, 'a')
writeFile.create_dataset('/data/data', data=all_data)
writeFile.create_dataset('/multdata/data', data=mult_all_data)
writeFile.create_dataset('/raw/data', data=all_data2)
writeFile.create_dataset('/gain/data', data=gains)
writeFile.close()