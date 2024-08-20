import h5py as h5
import os
import sys
import numpy as np


mask_bad = 0
mask_good = 1

path_to_mask = '/data/data'
static_mask_filename = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/badMask.h5'
staticMask = h5.File(static_mask_filename, 'r') # 1 - good, 0 - bad
staticBadMaskData = 1 - staticMask[path_to_mask][:] # 0 - good, 1 - bad

darkFileName = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/darks/darks141_all/Cheetah-AGIPD08-calib.h5'
BadpixelPath = "/Badpixel"



darks = h5.File(darkFileName, 'r')

badpixel = darks[BadpixelPath][0,]


filename_data = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/Cheetah-AGIPD08-subtracted-142_162-dark141_all-corrected-screen-v2.h5'
path_to_data = '/unchanged/data' #'/data/data'
path_to_gains = '/gain/data'

path_to_file = os.path.dirname(filename_data)
result_filename = filename_data.split('.')[0] + '-mode.h5'
dataHdf5 = '/data/data'

readFile = h5.File(filename_data, 'r')
data = readFile[path_to_data]

data_shape = data.shape
shape_data = data_shape[1:]
maxNum = data_shape[0]


gains = readFile[path_to_gains]


writeFile = h5.File(result_filename, 'a')
init_shape = (1,) + shape_data
max_shape = (maxNum,) + shape_data
    
subtracted_data = writeFile.create_dataset(dataHdf5, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
common_mode = writeFile.create_dataset('/mode/data', init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
woMult = writeFile.create_dataset('/woMult/data', init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
Mult = writeFile.create_dataset('/Mult/data', init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)


for cellId in range(0,maxNum):
    print(cellId)
    UnionBadMask = np.bitwise_or(badpixel[cellId,], staticBadMaskData) # >0 - bad pixels
    
    common_mode.resize((cellId+1,) + shape_data)
    subtracted_data.resize((cellId+1,) + shape_data)
    woMult.resize((cellId+1,) + shape_data)
    Mult.resize((cellId+1,) + shape_data)
    all_data = data[cellId, :,:]
    
    #baddata = np.where(UnionBadMask > 0, data[cellId, :,:], np.nan)
    baddata = np.where(badpixel[cellId, :,:] > 0, data[cellId, :,:], np.nan)
    print(np.nanmedian(baddata))
    gooddata = np.where(UnionBadMask > 0, np.nan, data[cellId, :,:])
    
    
    mode = np.zeros(shape=shape_data)
    
    for ind in range(0,8):
        start = ind * 64
        end = start + 64
        
        #top = np.where((baddata[start:end, :64] > 0) & (baddata[start:end, :64] < np.nanmean(data[cellId,start:end, :64])), baddata[start:end, :64], np.nan)
        #down = np.where((baddata[start:end, 64:] > 0) & (baddata[start:end, 64:] < np.nanmean(data[cellId,start:end, 64:])), baddata[start:end, 64:], np.nan)
        
        
        top = np.where((baddata[start:end, :64] > -np.abs(np.nanmedian(gooddata[start:end, :64]))) & (baddata[start:end, :64] < np.abs(np.nanmedian(gooddata[start:end, :64]))), baddata[start:end, :64], np.nan)
        down = np.where((baddata[start:end, 64:] > -np.abs(np.nanmedian(gooddata[start:end, 64:]))) & (baddata[start:end, 64:] < np.abs(np.nanmedian(gooddata[start:end, 64:]))), baddata[start:end, 64:], np.nan)
        
        #print('np.nanmedian(top) = ', np.nanmedian(top))
        #print('np.nanmedian(down) = ', np.nanmedian(down))
        
        
        all_data[start:end, :64] -= np.nanmedian(top)
        all_data[start:end, 64:] -= np.nanmedian(down)
        
        mode[start:end, :64] += np.nanmedian(top)
        mode[start:end, 64:] += np.nanmedian(down)
    
    common_mode[cellId, :,:] =  mode  
    woMult[cellId, :,:] = all_data
    subtracted_data[cellId, :,:] = np.multiply(all_data, gains[cellId, :,:])
    Mult[cellId, :,:] = np.multiply(data[cellId, :,:], gains[cellId, :,:])


readFile.close()
writeFile.close()
staticMask.close()
darks.close()