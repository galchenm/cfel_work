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


const_path_cellId = "/INSTRUMENT/SPB_DET_AGIPD1M-1/DET/{}CH0:xtdf/image/cellId"
const_path_data = "/INSTRUMENT/SPB_DET_AGIPD1M-1/DET/{}CH0:xtdf/image/data"

path = '/pnfs/xfel.eu/exfel/archive/XFEL/raw/SPB/202002/p002442/r0141' #r0139'
darks = glob.glob(os.path.join(path,"*.h5"))
files_for_each_panel  = defaultdict(list)


path_to = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/darks/darks141_all'

for dark in darks:
    panel_num = os.path.basename(dark)
    if re.search(r"AGIPD[\d]+[-]+",panel_num):
        panel_num = re.search(r"AGIPD[\d]+[-]+",panel_num).group()
        panel_num = re.search(r"[\d]+",panel_num).group()
        files_for_each_panel[int(panel_num)].append(dark)

panels = list(files_for_each_panel.keys())
panels.sort(reverse=True)
all_files = list(itertools.chain(*files_for_each_panel.values()))


cellIds = [i for i in range(0,352)]
cellIds.sort()

dataset_for_each_panel = {panel: {cellId: [] for cellId in cellIds} for panel in panels}


data_shape = None
for panel in [11,12]: #panels:
    files = files_for_each_panel[panel]
    files.sort()

    for file_cxi in files:
        print(file_cxi)
        path_to_data = const_path_data.format(panel)
        path_to_cellId = const_path_cellId.format(panel)

        
        f = h5.File(file_cxi,'r')
        data = f[path_to_data]
        
        cellIDs = f[path_to_cellId]
        
        start_pattern = 0
        path_to_data = const_path_cellId.format(panel)
        num_events = subprocess.check_output(['/opt/hdf5/hdf5-1.10.6/bin/h5ls', str(file_cxi)+'/'+str(path_to_data)])
        num_events = num_events.strip().decode('utf-8').split('Dataset ')[1]
        end_pattern = int(re.search(r"[\d]+",num_events).group())
        
        
        print('end pattern is ', end_pattern)
        for i in range(start_pattern, end_pattern):
            cellId = cellIDs[i][0]
            data_tmp = data[i,0,]
            
            if data_shape is None:
                data_shape = data_tmp.shape
                
                print("DATA SHAPE is ", data_shape)
            dataset_for_each_panel[panel][cellId].append(data_tmp)
            
                        
        f.close()
        print('finish append')


print('I AM HERE!')

iPixMean = defaultdict(dict)
iPixSigma = defaultdict(dict)

allPixSigmaSigma = defaultdict(dict)
allPixSigmaMean = defaultdict(dict)
allPixMeanSigma = defaultdict(dict)
allPixMeanMean = defaultdict(dict)
bad_pixels_cellId_per_panel = defaultdict(dict)

BadpixelPath = "/Badpixel"
dark_signal = "/AnalogOffset" #"/darkSignal/data"
sigma_path = "/sigma/data"

for panel in [11,12]: #panels:
    print("Data writing")
    file_name = os.path.join(path_to, "Cheetah-AGIPD{}-calib.h5".format(panel if len(str(panel)) > 1 else ('0' + str(panel))))
    #file_name_upt = os.path.join(path_to, "upt-Cheetah-calib-AGIPD{}.h5".format(panel if len(str(panel)) > 1 else ('0' + str(panel))))
    print("file_name ", file_name)
    f = h5.File(file_name, 'a')
    #f = h5.File(file_name_upt,'a')
    init_shape = (3, 1,) + data_shape
    max_shape = (3, max(cellIds)+1,) + data_shape
    print("init_shape ", init_shape, " max_shape " , max_shape)
    darkSignal_data = f.create_dataset(dark_signal, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    BadpixelPath_data = f.create_dataset(BadpixelPath, init_shape, maxshape=max_shape, dtype=np.uint8, chunks=init_shape, compression="gzip", compression_opts=4)   
    sigma_data = f.create_dataset(sigma_path, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)
    
    
    #dataWrite = []
    for cellId in cellIds:
        print("cellId ", cellId)
        dataset = np.array(dataset_for_each_panel[panel][cellId])
        iPixMean[panel][cellId] = np.mean(dataset, axis=0) #mean, dtype=np.int32
        iPixSigma[panel][cellId] = np.std(dataset, axis=0) #std
        #iPixSigma[panel][cellId] = stats.median_absolute_deviation(dataset, axis=0) #MAD
        print(iPixMean[panel][cellId].shape)
        darkSignal_data.resize((3,cellId+1,) + data_shape)
        darkSignal_data[0,cellId,:,:] = np.array([iPixMean[panel][cellId]])
        darkSignal_data[1,cellId,:,:] = np.array([iPixMean[panel][cellId]])
        darkSignal_data[2,cellId,:,:] = np.array([iPixMean[panel][cellId]])
        
        sigma_data.resize((3,cellId+1,) + data_shape)
        sigma_data[0,cellId,:,:] = np.array([iPixSigma[panel][cellId]])
        sigma_data[1,cellId,:,:] = np.array([iPixSigma[panel][cellId]])
        sigma_data[2,cellId,:,:] = np.array([iPixSigma[panel][cellId]])
        
        allPixMeanMean[panel][cellId] = np.mean(iPixMean[panel][cellId]) #mean
        allPixSigmaMean[panel][cellId] = np.std(iPixMean[panel][cellId]) # std
        #allPixSigmaMean[panel][cellId] = stats.median_absolute_deviation(iPixMean[panel][cellId], axis=None) #MAD
        
        
        allPixMeanSigma[panel][cellId] = np.mean(iPixSigma[panel][cellId]) #mean
        allPixSigmaSigma[panel][cellId] = np.std(iPixSigma[panel][cellId]) #std
        #allPixSigmaSigma[panel][cellId] = stats.median_absolute_deviation(iPixSigma[panel][cellId], axis=None)
        
        print("panel = {}, cellId = {}, MeanMean = {}, SigmaMean = {}, MeanSigma = {}, SigmaSigma = {}".format(panel, cellId, allPixMeanMean[panel][cellId], allPixSigmaMean[panel][cellId], allPixMeanSigma[panel][cellId], allPixSigmaSigma[panel][cellId]))
        
        #histogram
        #MaxSigmaDeviate = np.max(allPixSigmaSigma[panel][cellId])
        #MaxMeanDeviate = np.max(allPixMeanSigma[panel][cellId])
        #print("panel = {}, cellId = {}, MaxSigmaDeviate = {}, MaxMeanDeviate = {}".format(panel, cellId, MaxSigmaDeviate, MaxMeanDeviate))
        
        bad_pixels_cellId_per_panel[panel][cellId] = np.zeros(iPixMean[panel][cellId].shape,dtype=np.uint8)
        
        #fabs(iPixSigma -  allPixSigmaMean) > MaxSigmaDeviate * allPixSigmaSigma -->2
        #bad_pixels_cellId_per_panel[panel][cellId] = np.add(bad_pixels_cellId_per_panel[panel][cellId], np.where(np.abs(iPixSigma[panel][cellId] - allPixSigmaMean[panel][cellId]) > MaxSigmaDeviate * allPixSigmaSigma[panel][cellId], 2, 0), out=bad_pixels_cellId_per_panel[panel][cellId], casting="unsafe")
        #fabs(iPixMean -  allPixMeanMean) > MaxMeanDeviate * allPixMeanSigma
        #bad_pixels_cellId_per_panel[panel][cellId] = np.add(bad_pixels_cellId_per_panel[panel][cellId], np.where(np.abs(iPixMean[panel][cellId] - allPixMeanMean[panel][cellId]) > MaxMeanDeviate * allPixMeanSigma[panel][cellId], 4, 0), out=bad_pixels_cellId_per_panel[panel][cellId], casting="unsafe")
        
        
        bad_pixels_cellId_per_panel[panel][cellId] = np.where(np.abs(iPixSigma[panel][cellId] - allPixMeanSigma[panel][cellId]) < 3*allPixSigmaSigma[panel][cellId], 0 , 4)
        bad_pixels_cellId_per_panel[panel][cellId] = np.where(np.abs(iPixMean[panel][cellId] - allPixMeanMean[panel][cellId]) < 3*allPixSigmaMean[panel][cellId], 0 , 2)
        
        
        #dataWrite.append(bad_pixels_cellId_per_panel[panel][cellId])
        BadpixelPath_data.resize((3,cellId+1,) + data_shape)
        BadpixelPath_data[0,cellId,:,:] = np.array([bad_pixels_cellId_per_panel[panel][cellId]])
        BadpixelPath_data[1,cellId,:,:] = np.array([bad_pixels_cellId_per_panel[panel][cellId]])
        BadpixelPath_data[2,cellId,:,:] = np.array([bad_pixels_cellId_per_panel[panel][cellId]])
        
    #dataWrite = np.array([dataWrite, dataWrite,dataWrite])
    #print("dataWrite ", dataWrite.shape, type(dataWrite))
    #f_write.create_dataset(BadpixelPath, data=dataWrite)
    f.close()
    print("Added")

print('FINISH!')

    
