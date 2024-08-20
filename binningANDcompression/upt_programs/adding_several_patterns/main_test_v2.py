import os
import sys
import h5py as h5
import numpy as np
import time
import configparser
import ctypes as ct
import re
from cfelpyutils import crystfel_utils, geometry_utils
import math
from numpy.ctypeslib import ndpointer


lim_up = 65535
dataPathInFile = "/entry/data/data"

nPeaks = '/entry_1/result_1/nPeaks'                                #

peakMaximumValue = '/entry_1/result_1/peakMaximumValue'            #
peakNPixels = '/entry_1/result_1/peakNPixels'                      #
peakSNR = '/entry_1/result_1/peakSNR'                              #
peakTotalIntensity = '/entry_1/result_1/peakTotalIntensity'        #
peakXPosRaw = '/entry_1/result_1/peakXPosRaw'                      #
peakYPosRaw = '/entry_1/result_1/peakYPosRaw'                      #


chunk_size = 3


def transformation(old_array):
    #f = h5.File(file,'r')
    #old_array = f[x_hdf5path]
    update_2d_dim = old_array.shape[1] * chunk_size
    new_array = np.zeros((math.ceil(old_array.shape[0] / chunk_size), update_2d_dim))
    new_index = 0
    for i in range(0, old_array.shape[0], chunk_size):
        to_add = np.array([])
        current = old_array[i:i+chunk_size,]
        for index in range(0,current.shape[0]):
            tmp = current[index,]
            tmp = tmp[tmp != 0.]
            to_add = np.append(to_add, tmp)
        add = np.zeros((update_2d_dim))
        add[:to_add.shape[0]] += to_add[()]
        new_array[new_index, ] += add[()]
        new_index += 1
    #f.close()
    return new_array
    
def processing(h5Filename):
    global output_dir
    
    outputh5Filename = os.path.join(output_dir, os.path.basename(h5Filename))
    
    outputDataFile = h5.File(outputh5Filename, "w")
    dataFile = h5.File(h5Filename, "r")
    
    rawImages = dataFile[dataPathInFile]

    number_of_patterns = rawImages.shape[0]
    shape_data = rawImages.shape[1:]
    initShape = (1,)+ shape_data
    new_rawImages_shape = (math.ceil(number_of_patterns/chunk_size),)+ rawImages.shape[1:]
    #new_rawImages = np.zeros((math.ceil(number_of_patterns/chunk_size),)+ rawImages.shape[1:])
    print(new_rawImages_shape)
    print(initShape)
    print(shape_data)
    
    
    peak_maximum_value = dataFile[peakMaximumValue][()]
    peak_num_pixels = dataFile[peakNPixels][()]
    
    
    peak_snr = dataFile[peakSNR][()]
    peak_total_intensity = dataFile[peakTotalIntensity][()]
    
    x_pos_raw = dataFile[peakXPosRaw][()]
    y_pos_raw = dataFile[peakYPosRaw][()]
    
    update_2d_dim = x_pos_raw.shape[1] * chunk_size

    new_peak_snr, new_peak_total_intensity, new_peak_num_pixels, new_peak_maximum_value, new_x_pos_raw, new_y_pos_raw = list(map(transformation, [peak_snr, peak_total_intensity, peak_num_pixels, peak_maximum_value, x_pos_raw, y_pos_raw]))

    outputDataFile.create_dataset(peakSNR,data=new_peak_snr)
    outputDataFile.create_dataset(peakTotalIntensity,data=new_peak_total_intensity)
    outputDataFile.create_dataset(peakNPixels,data=new_peak_num_pixels)
    outputDataFile.create_dataset(peakMaximumValue,data=new_peak_maximum_value)
    outputDataFile.create_dataset(peakXPosRaw,data=new_x_pos_raw)
    outputDataFile.create_dataset(peakYPosRaw,data=new_y_pos_raw)
    
    ###########################################################################################################################################  
    #Not to change
    number_of_peaks = dataFile[nPeaks][()]
    new_number_of_peaks = np.zeros(((math.ceil(number_of_peaks.shape[0] / chunk_size))))
    new_number_of_peaks += np.array([np.sum(number_of_peaks[i:i+chunk_size,],axis=0) for i in range(0, number_of_peaks.shape[0], chunk_size)])
    outputDataFile.create_dataset(nPeaks,data=new_number_of_peaks)
    ############################################################################################################################################ 
    outputDataFile.close()
    
    with h5.File(outputh5Filename, "a") as outputDataFile:
        chunk_index = 0
        d = outputDataFile.create_dataset(dataPathInFile, initShape, maxshape=new_rawImages_shape, dtype=np.int16, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
        for i in range(0, number_of_patterns, chunk_size):
            d.resize((chunk_index+1,) + shape_data) 
            print('Index of chunk is {}\n'.format(chunk_index))
            
            data = rawImages[i:i+chunk_size,]
            
            d[chunk_index,] = np.sum(data, axis=0)
            d[chunk_index,] = np.where(d[chunk_index,] < lim_up, d[chunk_index,], lim_up)
            
            chunk_index += 1
            
    
    dataFile.close()
    
    
    
if __name__ == '__main__':
    h5Filename = sys.argv[1] #'/asap3/petra3/gpfs/p11/2021/data/11010507/raw/20210916_6963/20210916_6963_data_1.h5' #sys.argv[1]
    output_dir = sys.argv[2] #'/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/adding_several_patterns/test_test' #sys.argv[2]
    
    if not os.path.exists(output_dir):
        '''
        If the folder for processing doesn't exist,
        create it
        '''
        os.makedirs(output_dir)    
        
    processing(h5Filename)