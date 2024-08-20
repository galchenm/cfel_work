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
print(darks)

path_to = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/res139'

for dark in darks:
    panel_num = os.path.basename(dark)
    if re.search(r"AGIPD[\d]+[-]+",panel_num):
        panel_num = re.search(r"AGIPD[\d]+[-]+",panel_num).group()
        panel_num = re.search(r"[\d]+",panel_num).group()
        files_for_each_panel[int(panel_num)].append(dark)

panels = list(files_for_each_panel.keys())
panels.sort(reverse=True)
all_files = list(itertools.chain(*files_for_each_panel.values()))
print("files ", all_files)
NumPatterns_for_each_file = defaultdict(dict)
TotalNumPatterns_for_panel = {k: 0 for k in files_for_each_panel.keys()}
NumCellId_per_panel = {k: 0 for k in files_for_each_panel.keys()}
AvgNumPatterns_per_CellId = {k: 0 for k in files_for_each_panel.keys()}

cellIds = None
for panel in panels:
    for file_cxi in files_for_each_panel[panel]:
        path_to_data = const_path_cellId.format(panel)
        num_events = subprocess.check_output(['/opt/hdf5/hdf5-1.10.6/bin/h5ls', str(file_cxi)+'/'+str(path_to_data)])
        num_events = num_events.strip().decode('utf-8').split('Dataset ')[1]
        num = int(re.search(r"[\d]+",num_events).group())
        NumPatterns_for_each_file[panel][file_cxi] = num
        TotalNumPatterns_for_panel[panel] += num
        f = h5.File(file_cxi,'r')
        shape_id = f[path_to_data][:].shape
        mcellId = np.reshape(f[path_to_data][:],(shape_id[1],shape_id[0]))[0]
        cellId, counts = np.unique(mcellId, return_counts=True)
        if cellIds is None or len(cellId) > len(cellIds):
            cellIds = cellId
        NumCellId_per_panel[panel] = len(cellId)
        f.close()

for panel in panels:
    AvgNumPatterns_per_CellId[panel] = int(round(TotalNumPatterns_for_panel[panel] / NumCellId_per_panel[panel], 0))

print(NumPatterns_for_each_file)
cellIds.sort()


NumStat = 100
dataset_for_each_panel = {panel: {cellId: [] for cellId in cellIds} for panel in panels}
freq_for_each_panel = {panel: {cellId: 0 for cellId in cellIds} for panel in panels}

indicies_per_file = {file: [] for file in all_files}
data_shape = None
for panel in panels:
    files = files_for_each_panel[panel]
    files.sort()
    nPatterns_each_File = [NumPatterns_for_each_file[panel][file] for file in files]
    
    cumSum_nPatterns_each_File = list(np.cumsum(nPatterns_each_File))
    cumSum_nPatterns_each_File.append(0)
    cumSum_nPatterns_each_File.sort()
    cumSum_nPatterns_each_File = np.array(cumSum_nPatterns_each_File)
    print(type(cumSum_nPatterns_each_File))
    #print(files)
    #print(nPatterns_each_File)
    print('cumSum_nPatterns_each_File', cumSum_nPatterns_each_File)
    step = int(AvgNumPatterns_per_CellId[panel] // (NumStat - 1))
    randomSelectedIndRange = sorted(list(range(0, int(round(AvgNumPatterns_per_CellId[panel] +1,0)), step)))
    randomSelectedIndSample = sorted(sample(range(0,int(round(AvgNumPatterns_per_CellId[panel],0))), NumStat))
    print(randomSelectedIndRange, len(randomSelectedIndRange))
    #######
    for ind in randomSelectedIndSample: #randomSelectedIndRange
        tmpInd = ind * 352
        print('tmpInd', tmpInd)
        indOfFile = np.argwhere(tmpInd <= cumSum_nPatterns_each_File).min() -1
        
        file_cxi = files[indOfFile]
        print('indOfFile', indOfFile)
        print('file', file_cxi)
        start_pattern =  tmpInd % cumSum_nPatterns_each_File[indOfFile] if cumSum_nPatterns_each_File[indOfFile] != 0 else 0
        if start_pattern not in indicies_per_file[file_cxi]:
            indicies_per_file[file_cxi].append(start_pattern)
        else:
            while start_pattern in indicies_per_file[file_cxi]:
                start_pattern += 352
            indicies_per_file[file_cxi].append(start_pattern)
            
        
        end_pattern = start_pattern + 352
        print('cumSum_nPatterns_each_File', cumSum_nPatterns_each_File[indOfFile], 'nPatterns_each_File' , nPatterns_each_File[indOfFile])
        
        if nPatterns_each_File[indOfFile] - start_pattern < 352:
            
            start_pattern = nPatterns_each_File[indOfFile] - 352
            
            if start_pattern not in indicies_per_file[file_cxi]:
                indicies_per_file[file_cxi].append(start_pattern)
                end_pattern = nPatterns_each_File[indOfFile]
            else:
                indOfFile += 1
                file_cxi = files[indOfFile]
                print("new file open ", file_cxi)
                start_pattern = 0
                end_pattern = 352
                indicies_per_file[file_cxi].append(start_pattern)
            
        print('start ', start_pattern, 'end ', end_pattern)
        print("len range ",len(range(start_pattern, end_pattern)))
        path_to_data = const_path_data.format(panel)
        path_to_cellId = const_path_cellId.format(panel)
        f = h5.File(file_cxi,'r')
        for i in range(start_pattern, end_pattern):
            #print('cellId', f[path_to_cellId][i][0])
            if data_shape is None:
                #data_shape = f[path_to_data][i,0,].shape
                data_shape = f[path_to_data][i,1,].shape
                print("DATA SHAPE is ", data_shape)
            dataset_for_each_panel[panel][f[path_to_cellId][i][0]].append(f[path_to_data][i,0,])
            #dataset_for_each_panel[panel][f[path_to_cellId][i][0]].append(f[path_to_data][i,1,])
            freq_for_each_panel[panel][f[path_to_cellId][i][0]] += 1            
        f.close()
print(freq_for_each_panel[14])
print(np.array(dataset_for_each_panel[14][351]).shape)


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

for panel in panels:
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

print(iPixMean[14][351].shape)
print(iPixSigma[14][351].shape)
print('allPixSigmaSigma ',allPixSigmaSigma[14][351])
print('allPixSigmaMean ' ,allPixSigmaMean[14][351])
print('allPixMeanSigma ' ,allPixMeanSigma[14][351])
print('allPixMeanMean ' ,allPixMeanMean[14][351])
print('bad_pixels_cellId_per_panel', bad_pixels_cellId_per_panel[14][351][bad_pixels_cellId_per_panel[14][351] >2])




    
