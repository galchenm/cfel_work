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



dataPathInFile = "/entry/data/data"

nPeaks = '/entry_1/result_1/nPeaks'                                #

peakMaximumValue = '/entry_1/result_1/peakMaximumValue'            #
peakNPixels = '/entry_1/result_1/peakNPixels'                      #
peakSNR = '/entry_1/result_1/peakSNR'                              #
peakTotalIntensity = '/entry_1/result_1/peakTotalIntensity'        #
peakXPosRaw = '/entry_1/result_1/peakXPosRaw'                      #
peakYPosRaw = '/entry_1/result_1/peakYPosRaw'                      #



#maskFilename = "mask_v0.h5"
#maskPathInFile = "/data/data"

#geometryFileName = "eiger16M-P11_200mm_sh1.geom"

chunk_size = 5


def calling_peakfinder8(h5Filename):
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
    number_of_peaks = dataFile[nPeaks][()]
    
    peak_maximum_value = dataFile[peakMaximumValue][()]
    peak_num_pixels = dataFile[peakNPixels][()]
    
    
    peak_snr = dataFile[peakSNR][()]
    peak_total_intensity = dataFile[peakTotalIntensity][()]
    
    x_pos_raw = dataFile[peakXPosRaw][()]
    y_pos_raw = dataFile[peakYPosRaw][()]
    
    update_2d_dim = x_pos_raw.shape[1] * chunk_size

    new_peak_snr = np.zeros((math.ceil(peak_snr.shape[0] / chunk_size) * update_2d_dim))
    new_peak_snr[:peak_snr.shape[0]*peak_snr.shape[1],] = peak_snr.flatten()
    new_peak_snr = new_peak_snr.reshape(-1, update_2d_dim)
    outputDataFile.create_dataset(peakSNR,data=new_peak_snr)
    ###########################################################################################################################################
    new_peak_total_intensity = np.zeros((math.ceil(peak_total_intensity.shape[0] / chunk_size) * update_2d_dim))
    new_peak_total_intensity[:peak_total_intensity.shape[0]*peak_total_intensity.shape[1],] = peak_total_intensity.flatten()
    new_peak_total_intensity = new_peak_total_intensity.reshape(-1, update_2d_dim)
    outputDataFile.create_dataset(peakTotalIntensity,data=new_peak_total_intensity)
    
    ###########################################################################################################################################
    new_peak_num_pixels = np.zeros((math.ceil(peak_num_pixels.shape[0] / chunk_size) * update_2d_dim))
    new_peak_num_pixels[:peak_num_pixels.shape[0]*peak_num_pixels.shape[1],] = peak_num_pixels.flatten()
    new_peak_num_pixels = new_peak_num_pixels.reshape(-1, update_2d_dim)
    outputDataFile.create_dataset(peakNPixels,data=new_peak_num_pixels)
    ###########################################################################################################################################

    new_peak_maximum_value = np.zeros((math.ceil(peak_maximum_value.shape[0] / chunk_size) * update_2d_dim))
    new_peak_maximum_value[:peak_maximum_value.shape[0]*peak_maximum_value.shape[1],] = peak_maximum_value.flatten()
    new_peak_maximum_value = new_peak_maximum_value.reshape(-1, update_2d_dim)
    outputDataFile.create_dataset(peakMaximumValue,data=new_peak_maximum_value)
    ###########################################################################################################################################
    
    new_x_pos_raw = np.zeros((math.ceil(x_pos_raw.shape[0] / chunk_size) * update_2d_dim))
    new_x_pos_raw[:x_pos_raw.shape[0]*x_pos_raw.shape[1],] = x_pos_raw.flatten()
    new_x_pos_raw = new_x_pos_raw.reshape(-1, update_2d_dim)
    outputDataFile.create_dataset(peakXPosRaw,data=new_x_pos_raw)
    ###########################################################################################################################################

    new_y_pos_raw = np.zeros((math.ceil(y_pos_raw.shape[0] / chunk_size) * update_2d_dim))
    new_y_pos_raw[:y_pos_raw.shape[0]*y_pos_raw.shape[1],] = y_pos_raw.flatten()
    new_y_pos_raw = new_y_pos_raw.reshape(-1, update_2d_dim)
    outputDataFile.create_dataset(peakYPosRaw,data=new_y_pos_raw)
    ###########################################################################################################################################  
    
    new_number_of_peaks = np.zeros(((math.ceil(number_of_peaks.shape[0] / chunk_size))))
    new_number_of_peaks += np.array([np.sum(number_of_peaks[i:i+chunk_size,],axis=0) for i in range(0, number_of_peaks.shape[0], chunk_size)])
    outputDataFile.create_dataset(nPeaks,data=new_number_of_peaks)
    ############################################################################################################################################ 
    outputDataFile.close()
    
    with h5.File(outputh5Filename, "a") as outputDataFile:
        chunk_index = 0
        d = outputDataFile.create_dataset(dataPathInFile, initShape, maxshape=new_rawImages_shape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
        for i in range(0, number_of_patterns, chunk_size):
            d.resize((chunk_index+1,) + shape_data) 
            print('Chunking...\n')
            print('Index of chunk is {}\n'.format(chunk_index))
            
            data = rawImages[i:i+chunk_size,]
            #new_rawImages[chunk_index,] = np.sum(data, axis=0)
            d[chunk_index,] = np.sum(data, axis=0)
            
            
            chunk_index += 1
            
    
    dataFile.close()
    print(new_x_pos_raw.shape)
    
    
if __name__ == '__main__':
    h5Filename = sys.argv[1] #'/asap3/petra3/gpfs/p11/2021/data/11010507/raw/20210916_6963/20210916_6963_data_1.h5' #sys.argv[1]
    output_dir = sys.argv[2] #'/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/adding_several_patterns/test_test' #sys.argv[2]
    
    if not os.path.exists(output_dir):
        '''
        If the folder for processing doesn't exist,
        create it
        '''
        os.mkdir(output_dir)    
        
    calling_peakfinder8(h5Filename)