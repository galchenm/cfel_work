import os
import sys
import h5py as h5
import numpy as np
import subprocess
import re
import argparse
import glob
from collections import defaultdict
import numpy as np
from random import sample
import itertools
from scipy import stats

mask_bad = 1 #0
mask_good = 0 #1

path_with_darks = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/darks/darks141_all' 

template_path_with_data = '/pnfs/xfel.eu/exfel/archive/XFEL/raw/SPB/202002/p002442/r0{}'

ppath_with_data = [template_path_with_data.format(i) for i in range(143,144)]


print(ppath_with_data)

dataFiles = []

for path_with_data in ppath_with_data:
    dataFiles += glob.glob(os.path.join(path_with_data,"*.h5"))

print(dataFiles)

data_files_for_each_panel  = defaultdict(list)
const_path_cellId = "/INSTRUMENT/SPB_DET_AGIPD1M-1/DET/{}CH0:xtdf/image/cellId"
const_path_data = "/INSTRUMENT/SPB_DET_AGIPD1M-1/DET/{}CH0:xtdf/image/data"
cellIds = None
shape_data = None

for dataFile in dataFiles:
    panel_num = os.path.basename(dataFile)
    if re.search(r"AGIPD[\d]+[-]+",panel_num):
        panel_num = re.search(r"AGIPD[\d]+[-]+",panel_num).group()
        panel_num = re.search(r"[\d]+",panel_num).group()
        data_files_for_each_panel[int(panel_num)].append(dataFile)
        if cellIds is None:
            f = h5.File(dataFile, 'r')
            path_to_cellId = const_path_cellId.format(int(panel_num))
            shape_id = f[path_to_cellId][:].shape
            mcellId = np.reshape(f[path_to_cellId][:],(shape_id[1],shape_id[0]))[0]
            cellIds, counts = np.unique(mcellId, return_counts=True)
            if shape_data is None:
                shape_data = f[const_path_data.format(int(panel_num))].shape[2:]

darkFiles = glob.glob(os.path.join(path_with_darks,"*.h5"))
dark_files_for_each_panel  = defaultdict(list)


for darkFile in darkFiles:
    panel_num = os.path.basename(darkFile)
    if re.search(r"AGIPD[\d]+[-]+",panel_num):
        panel_num = re.search(r"AGIPD[\d]+[-]+",panel_num).group()
        panel_num = re.search(r"[\d]+",panel_num).group()
        dark_files_for_each_panel[int(panel_num)].append(darkFile)
        

#panels = list(data_files_for_each_panel.keys())
#panels.sort(reverse=True)
panels = [8]

statistics = {panel: {cellId: 0 for cellId in cellIds} for panel in panels}

rawData_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}

ShadowMean_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}
ShadowVariance_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}

comModeMean_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}
comModeVariance_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}



path_to = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData'    

dark_signal = "/AnalogOffset"
BadpixelPath = "/Badpixel"
dataHdf5 = "/data/data"
#gains_path = '/gain/data'
#means_path = '/mean/data'


shadow_mask_filename = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/shadowMask.h5'
path_to_mask = '/data/data'

shadow = h5.File(shadow_mask_filename, 'r')
shadowMaskData = shadow[path_to_mask][:] # 1 - good, 0 - bad

static_mask_filename = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/badMask.h5'
staticMask = h5.File(static_mask_filename, 'r') # 1 - good, 0 - bad
staticBadMaskData = 1 - staticMask[path_to_mask][:] # 0 - good, 1 - bad

for panel in panels:
    data_files = data_files_for_each_panel[panel]
    data_files.sort()
    print('Statistics')
    ######################################################
    darkFileName = dark_files_for_each_panel[panel][0]
    print(panel, darkFileName)
    
    darks = h5.File(darkFileName, 'r')
    darks_data = darks[dark_signal][0,]
    
    badpixel = darks[BadpixelPath][0,]
    
    ######################################################
    
    for file_cxi in data_files:
        path_to_data = const_path_data.format(int(panel))
        path_to_cellId = const_path_cellId.format(int(panel))
        f = h5.File(file_cxi,'r')
        data = f[path_to_data]
        cellIds_data = f[path_to_cellId]
        for ind in range(0, cellIds_data.shape[0]):
            cellId = cellIds_data[ind][0]
            
            UnionBadMask = np.bitwise_or(badpixel[cellId,], staticBadMaskData) # >0 - bad pixels
            mask = np.where(UnionBadMask > 0, np.nan, shadowMaskData)
            
            ##Common Mode calculation####################################################
            all_data = data[ind,0,:,:] - darks_data[cellId,]
            baddata = np.where(badpixel[cellId, :,:] > 0, all_data, np.nan)
            gooddata = np.where(UnionBadMask > 0, np.nan, all_data)

            
            for i in range(0,8):
                start = i * 64
                end = start + 64
                
                top = np.where((baddata[start:end, :64] > -np.abs(np.nanmedian(gooddata[start:end, :64]))) & (baddata[start:end, :64] < np.abs(np.nanmedian(gooddata[start:end, :64]))), baddata[start:end, :64], np.nan)
                down = np.where((baddata[start:end, 64:] > -np.abs(np.nanmedian(gooddata[start:end, 64:]))) & (baddata[start:end, 64:] < np.abs(np.nanmedian(gooddata[start:end, 64:]))), baddata[start:end, 64:], np.nan)
                
                top = np.nanmedian(top) if not(np.isnan(np.nanmedian(top))) else 0.
                down = np.nanmedian(down) if not(np.isnan(np.nanmedian(down))) else 0.
                print('cellId = {}, top = {}, down = {}'.format(cellId, top, down))
                all_data[start:end, :64] = data[ind,0,start:end, :64] - darks_data[cellId, start:end, :64] - top
                all_data[start:end, 64:] = data[ind,0,start:end, 64:] - darks_data[cellId,start:end, 64:] - down
                
            comModeMean_for_each_panel[panel][cellId] +=  all_data
            #############################################################################
            
            ##Shadow Mean calculation####################################################
            tmp_data = data[ind,0,:,:] - darks_data[cellId,]
            tmp_data = np.where(mask == mask_good, tmp_data, np.nan)
            mean_upp = np.nanmedian(tmp_data[:,0:64]) if not(np.isnan(np.nanmedian(tmp_data[:,0:64]))) else 0.
            mean_down = np.nanmedian(tmp_data[:,64:128]) if not(np.isnan(np.nanmedian(tmp_data[:,64:128]))) else 0.
            
            tmp_data[:,0:64] = data[ind,0,:,0:64] - darks_data[cellId,:,0:64] - mean_upp
            tmp_data[:,64:128] = data[ind,0,:,64:128] - darks_data[cellId,:,64:128] - mean_down
            ShadowMean_for_each_panel[panel][cellId] +=  tmp_data
            print(cellId, mean_upp, mean_down)
            #############################################################################
            
            rawData_for_each_panel[panel][cellId] += (data[ind,0,:,:] - darks_data[cellId,])
            
            
            statistics[panel][cellId] += 1
        f.close()
        darks.close()

print('End statistics')

for panel in panels:
    for cellId in cellIds:
        ShadowMean_for_each_panel[panel][cellId] /= statistics[panel][cellId]
        rawData_for_each_panel[panel][cellId] /= statistics[panel][cellId]
        comModeMean_for_each_panel[panel][cellId] /= statistics[panel][cellId]
        


for panel in panels:
    data_files = data_files_for_each_panel[panel]
    data_files.sort()
    print('Variance')
    ######################################################
    darkFileName = dark_files_for_each_panel[panel][0]
    print(panel, darkFileName)
    
    darks = h5.File(darkFileName, 'r')
    darks_data = darks[dark_signal][0,]
    badpixel = darks[BadpixelPath][0,]
    ######################################################
    
    for file_cxi in data_files:
        path_to_data = const_path_data.format(int(panel))
        path_to_cellId = const_path_cellId.format(int(panel))
        f = h5.File(file_cxi,'r')
        data = f[path_to_data]
        
        cellIds_data = f[path_to_cellId]
        for ind in range(0, cellIds_data.shape[0]):
            cellId = cellIds_data[ind][0]
            
            UnionBadMask = np.bitwise_or(badpixel[cellId,], staticBadMaskData) # >0 - bad pixels
            mask = np.where(UnionBadMask > 0, np.nan, shadowMaskData)
            
            ##Common Mode calculation####################################################
            all_data = data[ind,0,:,:] - darks_data[cellId,]
            baddata = np.where(badpixel[cellId, :,:] > 0, all_data, np.nan)
            gooddata = np.where(UnionBadMask > 0, np.nan, all_data)

            
            for i in range(0,8):
                start = i * 64
                end = start + 64
                
                top = np.where((baddata[start:end, :64] > -np.abs(np.nanmedian(gooddata[start:end, :64]))) & (baddata[start:end, :64] < np.abs(np.nanmedian(gooddata[start:end, :64]))), baddata[start:end, :64], np.nan)
                down = np.where((baddata[start:end, 64:] > -np.abs(np.nanmedian(gooddata[start:end, 64:]))) & (baddata[start:end, 64:] < np.abs(np.nanmedian(gooddata[start:end, 64:]))), baddata[start:end, 64:], np.nan)
                top = np.nanmedian(top) if not(np.isnan(np.nanmedian(top))) else 0.
                down = np.nanmedian(down) if not(np.isnan(np.nanmedian(down))) else 0.                

                all_data[start:end, :64] = data[ind,0,start:end, :64] - darks_data[cellId, start:end, :64] - top
                all_data[start:end, 64:] = data[ind,0,start:end, 64:] - darks_data[cellId,start:end, 64:] - down
                
            comModeVariance_for_each_panel[panel][cellId] +=  (all_data - comModeMean_for_each_panel[panel][cellId]) ** 2
            #############################################################################
            
            ##Shadow Mean calculation####################################################
            tmp_data = data[ind,0,:,:] - darks_data[cellId,]
            tmp_data = np.where(mask == mask_good, tmp_data, np.nan)
            mean_upp = np.nanmedian(tmp_data[:,0:64]) if not(np.isnan(np.nanmedian(tmp_data[:,0:64]))) else 0.
            mean_down = np.nanmedian(tmp_data[:,64:128]) if not(np.isnan(np.nanmedian(tmp_data[:,64:128]))) else 0.
            
            tmp_data[:,0:64] = data[ind,0,:,0:64] - darks_data[cellId,:,0:64] - mean_upp
            tmp_data[:,64:128] = data[ind,0,:,64:128] - darks_data[cellId,:,64:128] - mean_down
            ShadowVariance_for_each_panel[panel][cellId] += (tmp_data - ShadowMean_for_each_panel[panel][cellId])**2
            print(cellId)
            #############################################################################
             
        f.close()
        darks.close()

print('End variance')

shadow.close()


for panel in panels:
    print('recording...')
    file_name = os.path.join(path_to, "new-Cheetah-AGIPD{}-subtracted-143-dark141.h5".format(panel if len(str(panel)) > 1 else ('0' + str(panel))))
    f = h5.File(file_name, 'a')
    init_shape = (1,) + shape_data
    max_shape = (max(cellIds)+1,) + shape_data
    
    shadow_data = f.create_dataset('/shadow/data', init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    shadow_mean = f.create_dataset('/shadowMean/data', init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    shadow_gain = f.create_dataset('/shadow/gain', init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)

    comMode_data = f.create_dataset('/comMode/data', init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    comMode_mean = f.create_dataset('/comModeMean/data', init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    comMode_gain = f.create_dataset('/comMode/gain', init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)

    raw_data = f.create_dataset('/raw/data', init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    

    darkFileName = dark_files_for_each_panel[panel][0]
    print(panel, darkFileName)
    
    darks = h5.File(darkFileName, 'r')
    darks_data = darks[dark_signal][0,]
    badpixel = darks[BadpixelPath][0,]
    for cellId in cellIds:
        
        raw_data.resize((cellId+1,) + shape_data)
        
        shadow_data.resize((cellId+1,) + shape_data)
        shadow_gain.resize((cellId+1,) + shape_data)
        shadow_mean.resize((cellId+1,) + shape_data)
        
        comMode_data.resize((cellId+1,) + shape_data)
        comMode_gain.resize((cellId+1,) + shape_data)
        comMode_mean.resize((cellId+1,) + shape_data)
        
        #UnionBadMask = np.bitwise_or(badpixel[cellId,], staticBadMaskData)
        
        raw_data[cellId,:,:] = rawData_for_each_panel[panel][cellId]
        
        
        shadow_mean[cellId, :,:]= ShadowMean_for_each_panel[panel][cellId] + darks_data[cellId,] #np.where(UnionBadMask == 0, ShadowMean_for_each_panel[panel][cellId] + darks_data[cellId,], np.nan)
        shadow_data[cellId,:,:] = ShadowMean_for_each_panel[panel][cellId] #np.where(UnionBadMask == 0, ShadowMean_for_each_panel[panel][cellId], np.nan)
        shadow_gain[cellId, :,:] = ShadowVariance_for_each_panel[panel][cellId]/((statistics[panel][cellId]-1)*(ShadowMean_for_each_panel[panel][cellId])) #np.where(UnionBadMask == 0, ShadowVariance_for_each_panel[panel][cellId]/((statistics[panel][cellId]-1)*(ShadowMean_for_each_panel[panel][cellId])), np.nan)
        
        comMode_mean[cellId, :,:]= comModeMean_for_each_panel[panel][cellId] + darks_data[cellId,] #np.where(UnionBadMask == 0, ShadowMean_for_each_panel[panel][cellId] + darks_data[cellId,], np.nan)
        comMode_data[cellId,:,:] = comModeMean_for_each_panel[panel][cellId] #np.where(UnionBadMask == 0, ShadowMean_for_each_panel[panel][cellId], np.nan)
        comMode_gain[cellId, :,:] = comModeVariance_for_each_panel[panel][cellId]/((statistics[panel][cellId]-1)*(comModeMean_for_each_panel[panel][cellId])) #np.where(UnionBadMask == 0, ShadowVariance_for_each_panel[panel][cellId]/((statistics[panel][cellId]-1)*(ShadowMean_for_each_panel[panel][cellId])), np.nan)
       
    f.close()
    darks.close()
    
staticMask.close()