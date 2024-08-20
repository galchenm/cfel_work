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

path_with_darks = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/res'
path_with_data = '/pnfs/xfel.eu/exfel/archive/XFEL/raw/SPB/202002/p002442/r0172'

dataFiles = glob.glob(os.path.join(path_with_data,"*.h5"))
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
            print(path_to_cellId, dataFile)
            shape_id = f[path_to_cellId][:].shape
            mcellId = np.reshape(f[path_to_cellId][:],(shape_id[1],shape_id[0]))[0]
            cellIds, counts = np.unique(mcellId, return_counts=True)
            if shape_data is None:
                shape_data = f[const_path_data.format(int(panel_num))].shape[2:]

darkFiles = glob.glob(os.path.join(path_with_darks,"*.h5"))
dark_files_for_each_panel  = defaultdict(list)

print('cellIds ', cellIds)


for darkFile in darkFiles:
    panel_num = os.path.basename(darkFile)
    if re.search(r"AGIPD[\d]+[-]+",panel_num):
        panel_num = re.search(r"AGIPD[\d]+[-]+",panel_num).group()
        panel_num = re.search(r"[\d]+",panel_num).group()
        dark_files_for_each_panel[int(panel_num)].append(darkFile)
        
panels = list(data_files_for_each_panel.keys())
#panels.sort(reverse=True)

print('panels ', panels)
print('data_files_for_each_panel ', data_files_for_each_panel)
print('dark_files_for_each_panel ', dark_files_for_each_panel[15])
print('shape_data ', shape_data)

statistics = {panel: {cellId: 0 for cellId in cellIds} for panel in panels}
sum_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}
sum_squared_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}

'''
for panel in panels: #panels[0:6]:
    data_files = data_files_for_each_panel[panel]
    data_files.sort()
    
    for file_cxi in data_files:
        path_to_data = const_path_data.format(int(panel))
        path_to_cellId = const_path_cellId.format(int(panel))
        f = h5.File(file_cxi,'r')
        data = f[path_to_data]
        
        cellIds_data = f[path_to_cellId] #list(f[path_to_cellId][:,].flatten())
        print(file_cxi, data.shape)
        print(cellIds_data)
        for ind in range(0, cellIds_data.shape[0]):
            cellId = cellIds_data[ind][0]
            #print(data[ind, 0, ].shape)
            sum_for_each_panel[panel][cellId] += data[ind, 0, ]
            sum_squared_for_each_panel[panel][cellId] - darks
            statistics[panel][cellId] += 1
        f.close()
        
''' 

path_to = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/resData'    
dark_signal = "/AnalogOffset"
dataHdf5 = "/data/data"
BadpixelPath = "/Badpixel"

statistics = {panel: {cellId: 0 for cellId in cellIds} for panel in panels}
sum_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}
sum_squared_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}


for panel in [8]:#panels: #panels[0:6]:
    data_files = data_files_for_each_panel[panel]
    data_files.sort()
    
    darkFileName = dark_files_for_each_panel[panel][0]
    
    #print(darkFileName)
    darks = h5.File(darkFileName, 'r')
    darks_data = darks[dark_signal][0,]
    badpixel = darks[BadpixelPath][0,]
    
    for file_cxi in data_files:
        path_to_data = const_path_data.format(int(panel))
        path_to_cellId = const_path_cellId.format(int(panel))
        f = h5.File(file_cxi,'r')
        data = f[path_to_data]
        
        cellIds_data = f[path_to_cellId] #list(f[path_to_cellId][:,].flatten())
        print(file_cxi, data.shape)
        print(cellIds_data)
        for ind in range(0, cellIds_data.shape[0]):
            cellId = cellIds_data[ind][0]
            #print(data[ind, 0, ].shape)
            diff = (data[ind, 0, ] - darks_data[cellId,])
            sum_for_each_panel[panel][cellId] += diff
            sum_squared_for_each_panel[panel][cellId] += (diff)**2
            statistics[panel][cellId] += 1
        f.close()
        

gains_path = '/gain/data'

import matplotlib.pyplot as plt

for panel in [8]:#panels: #panels[0:6]:
    file_name = os.path.join(path_to, "Cheetah-AGIPD{}-subtracted-upt.h5".format(panel if len(str(panel)) > 1 else ('0' + str(panel))))
    f = h5.File(file_name, 'a')
    init_shape = (1,) + shape_data
    max_shape = (max(cellIds)+1,) + shape_data
    print("init_shape ", init_shape, " max_shape " , max_shape)
    subtracted_data = f.create_dataset(dataHdf5, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    gains = f.create_dataset(gains_path, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    
    darkFileName = dark_files_for_each_panel[panel][0]
    
    #print(darkFileName)
    darks = h5.File(darkFileName, 'r')
    darks_data = darks[dark_signal][0,]
    badpixel = darks[BadpixelPath][0,]
    #print(darks_data.shape)
    for cellId in cellIds:

        subtracted_data.resize((cellId+1,) + shape_data)
        gains.resize((cellId+1,) + shape_data)

        #subtracted_data[cellId,:,:] = np.where(badpixel[cellId,] == 0, sum_for_each_panel[panel][cellId]/statistics[panel][cellId]- darks_data[cellId,], 0)
        meanValue = (sum_for_each_panel[panel][cellId]/statistics[panel][cellId]).astype(np.float32)
        #print('meanValue',meanValue)
        subtracted_data[cellId,:,:] = np.where(badpixel[cellId,] == 0, meanValue, 0)
        variance = sum_squared_for_each_panel[panel][cellId]/statistics[panel][cellId] - (meanValue)**2
        
        #gains[cellId,:,:] = np.where(badpixel[cellId,] == 0, (sum_squared_for_each_panel[panel][cellId]/statistics[panel][cellId] - (sum_for_each_panel[panel][cellId]/statistics[panel][cellId])**2)/(sum_for_each_panel[panel][cellId]/statistics[panel][cellId]), 0)
        
        
        variance = np.where(badpixel[cellId,] == 0, variance, 0)
        gains[cellId, :,:] = np.where(np.abs(meanValue) < 1e-10, 0, variance/meanValue)
        
      
        #plt.imshow(subtracted_data[cellId,:,:], cmap='viridis')
        #plt.savefig(os.path.join(path_to, "Cheetah-AGIPD{}-CellId{}-subtracted-upt.png".format(panel if len(str(panel)) > 1 else ('0' + str(panel)), cellId)))
        
    f.close()