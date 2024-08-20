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

path_with_darks = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/darks/darks139' 
path_with_data = '/pnfs/xfel.eu/exfel/archive/XFEL/raw/SPB/202002/p002442/r0145'

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
        
panels = list(data_files_for_each_panel.keys())
panels.sort(reverse=True)


statistics = {panel: {cellId: 0 for cellId in cellIds} for panel in panels}
mean_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}
variance_for_each_panel = {panel: {cellId: np.zeros(shape_data) for cellId in cellIds} for panel in panels}

path_to = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData'    

dark_signal = "/AnalogOffset"
BadpixelPath = "/Badpixel"
dataHdf5 = "/data/data"
gains_path = '/gain/data'
means_path = '/mean/data'


for panel in [8]: #panels:
    data_files = data_files_for_each_panel[panel]
    data_files.sort()
    
    ######################################################
    darkFileName = dark_files_for_each_panel[panel][0]
    print(panel, darkFileName)
    
    darks = h5.File(darkFileName, 'r')
    darks_data = darks[dark_signal][0,]
    ######################################################
    
    for file_cxi in data_files:
        path_to_data = const_path_data.format(int(panel))
        path_to_cellId = const_path_cellId.format(int(panel))
        f = h5.File(file_cxi,'r')
        data = f[path_to_data]
        cellIds_data = f[path_to_cellId]
        for ind in range(0, cellIds_data.shape[0]):
            cellId = cellIds_data[ind][0]
            #mean_for_each_panel[panel][cellId] += data[ind, 0, ]
            mean_for_each_panel[panel][cellId] += (data[ind, 0, ] - darks_data[cellId,]) # + 5000.
            statistics[panel][cellId] += 1
        f.close()
        darks.close()


for panel in [8]: #panels:
    for cellId in cellIds:
        mean_for_each_panel[panel][cellId] /= statistics[panel][cellId]


for panel in [8]: #panels:
    data_files = data_files_for_each_panel[panel]
    data_files.sort()
    
    ######################################################
    darkFileName = dark_files_for_each_panel[panel][0]
    print(panel, darkFileName)
    
    darks = h5.File(darkFileName, 'r')
    darks_data = darks[dark_signal][0,]
    ######################################################
    
    for file_cxi in data_files:
        path_to_data = const_path_data.format(int(panel))
        path_to_cellId = const_path_cellId.format(int(panel))
        f = h5.File(file_cxi,'r')
        data = f[path_to_data]
        
        cellIds_data = f[path_to_cellId]
        for ind in range(0, cellIds_data.shape[0]):
            cellId = cellIds_data[ind][0]
            variance_for_each_panel[panel][cellId] += (data[ind, 0, ] - darks_data[cellId,] - mean_for_each_panel[panel][cellId])**2
            
        f.close()
        darks.close()


for panel in [8]: #panels:
    file_name = os.path.join(path_to, "Cheetah-AGIPD{}-subtracted-145-dark139wo5000.h5".format(panel if len(str(panel)) > 1 else ('0' + str(panel))))
    f = h5.File(file_name, 'a')
    init_shape = (1,) + shape_data
    max_shape = (max(cellIds)+1,) + shape_data
    
    subtracted_data = f.create_dataset(dataHdf5, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    #gains = f.create_dataset(gains_path, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    means = f.create_dataset(means_path, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    
    darkFileName = dark_files_for_each_panel[panel][0]
    print(panel, darkFileName)
    
    darks = h5.File(darkFileName, 'r')
    darks_data = darks[dark_signal][0,]
    badpixel = darks[BadpixelPath][0,]
    for cellId in cellIds:
        subtracted_data.resize((cellId+1,) + shape_data)
        #gains.resize((cellId+1,) + shape_data)
        means.resize((cellId+1,) + shape_data)
        means[cellId, :,:]= np.where(badpixel[cellId,] == 0, mean_for_each_panel[panel][cellId] + darks_data[cellId,], 0)
        
        #subtracted_data[cellId,:,:] = np.where(badpixel[cellId,] == 0, mean_for_each_panel[panel][cellId] - darks_data[cellId,], 0)
        #gains[cellId, :,:] = np.where(badpixel[cellId,] == 0, variance_for_each_panel[panel][cellId]/((statistics[panel][cellId]-1)*(mean_for_each_panel[panel][cellId] - darks_data[cellId,])), 0)
        
        ################################
        subtracted_data[cellId,:,:] = np.where(badpixel[cellId,] == 0, mean_for_each_panel[panel][cellId], 0)
        
        #gains[cellId, :,:] = np.where(badpixel[cellId,] == 0, variance_for_each_panel[panel][cellId]/((statistics[panel][cellId]-1)*(mean_for_each_panel[panel][cellId])), 0)
    f.close()
    darks.close()