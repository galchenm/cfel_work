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
from collections import defaultdict
from itertools import groupby

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

def traverse_datasets(hdf_file):

    """Traverse all datasets across all groups in HDF5 file."""

    def h5py_dataset_iterator(g, prefix=''):
        for key in g.keys():
            item = g[key]
            path = '{}/{}'.format(prefix, key)
            if isinstance(item, h5.Dataset): # test for dataset
                yield (path, item)
            elif isinstance(item, h5.Group): # test for group (go down)
                yield from h5py_dataset_iterator(item, path)

    with h5.File(hdf_file, 'r') as f:
        for (path, dset) in h5py_dataset_iterator(f):
            yield path


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

def append_to_dataset(dataset, data):
    
    data = np.asanyarray(data)
    dataset.resize(len(dataset) + len(data), axis=0)
    dataset[-len(data):] = data

def create_for_append(h5file, name, data):
    data = np.asanyarray(data)
    return h5file.create_dataset(
          name, data=data, maxshape=(None,) + data.shape[1:])

def raw_create_for_append(h5file, name, data):
    data = np.asanyarray(data)
    return h5file.create_dataset(
          name, data=data, maxshape=(None,) + data.shape[1:], dtype=np.int16, compression="gzip", compression_opts=6, shuffle=True)
    
def processing(h5Filename, indices):
    global output_dir
    
    outputh5Filename = os.path.join(output_dir, os.path.basename(h5Filename))
    
    
    dataFile = h5.File(h5Filename, "r")
    all_datasets = set()
    if os.path.exists(outputh5Filename):
        all_datasets = set(traverse_datasets(outputh5Filename))
    
    rawImages = dataFile[dataPathInFile][indices]
    new_rawImages = np.array([np.sum(rawImages, axis=0)])
    new_rawImages[0,] = np.where(new_rawImages[0,] < lim_up, new_rawImages[0,], lim_up)
        
    number_of_patterns = rawImages.shape[0]
    shape_data = rawImages.shape[1:]
    initShape = (1,)+ shape_data
    new_rawImages_shape = (math.ceil(number_of_patterns/chunk_size),)+ rawImages.shape[1:]
    
    
    peak_maximum_value = dataFile[peakMaximumValue][indices]
    peak_num_pixels = dataFile[peakNPixels][indices]
    
    
    peak_snr = dataFile[peakSNR][indices]
    peak_total_intensity = dataFile[peakTotalIntensity][indices]
    
    x_pos_raw = dataFile[peakXPosRaw][indices]
    y_pos_raw = dataFile[peakYPosRaw][indices]
    
    update_2d_dim = x_pos_raw.shape[1] * chunk_size

    new_peak_snr, new_peak_total_intensity, new_peak_num_pixels, new_peak_maximum_value, new_x_pos_raw, new_y_pos_raw = list(map(transformation, [peak_snr, peak_total_intensity, peak_num_pixels, peak_maximum_value, x_pos_raw, y_pos_raw]))


    
    ###########################################################################################################################################  
    #Not to change
    number_of_peaks = dataFile[nPeaks][indices]
    new_number_of_peaks = np.zeros(((math.ceil(number_of_peaks.shape[0] / chunk_size))))
    new_number_of_peaks += np.sum(number_of_peaks,axis=0)
    
    if not all([phdf5 in all_datasets for phdf5 in [dataPathInFile, nPeaks, peakMaximumValue, peakNPixels, peakSNR, peakTotalIntensity, peakXPosRaw, peakYPosRaw]]): #no path there

        with h5.File(outputh5Filename, "w") as outputDataFile:
            raw_create_for_append(outputDataFile, dataPathInFile, new_rawImages)
            create_for_append(outputDataFile, nPeaks, new_number_of_peaks)
            create_for_append(outputDataFile, peakSNR, new_peak_snr)
            create_for_append(outputDataFile, peakTotalIntensity, new_peak_total_intensity)
            create_for_append(outputDataFile, peakNPixels, new_peak_num_pixels)
            create_for_append(outputDataFile, peakMaximumValue, new_peak_maximum_value)
            create_for_append(outputDataFile, peakXPosRaw, new_x_pos_raw)
            create_for_append(outputDataFile, peakYPosRaw, new_y_pos_raw)
    else:
        with h5.File(outputh5Filename, "a") as outputDataFile:
            append_to_dataset(outputDataFile[dataPathInFile], new_rawImages)
            append_to_dataset(outputDataFile[nPeaks], new_number_of_peaks)
            append_to_dataset(outputDataFile[peakSNR], new_peak_snr)
            append_to_dataset(outputDataFile[peakTotalIntensity], new_peak_total_intensity)
            append_to_dataset(outputDataFile[peakNPixels], new_peak_num_pixels)
            append_to_dataset(outputDataFile[peakMaximumValue], new_peak_maximum_value)
            append_to_dataset(outputDataFile[peakXPosRaw], new_x_pos_raw)
            append_to_dataset(outputDataFile[peakYPosRaw], new_y_pos_raw)
    ############################################################################################################################################ 
    dataFile.close()
    
    
    
if __name__ == '__main__':
    file_with_indexed_patterns_from_one_hdf5_file = sys.argv[1] #'/asap3/petra3/gpfs/p11/2021/data/11010507/raw/20210916_6963/20210916_6963_data_1.h5' #sys.argv[1]
    output_dir = sys.argv[2] #'/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/adding_several_patterns/test_test' #sys.argv[2]
    
    if not os.path.exists(output_dir):
        '''
        If the folder for processing doesn't exist,
        create it
        '''
        os.makedirs(output_dir)    
    
    '''
    with open(file_with_indexed_patterns_from_one_hdf5_file, 'r') as file:
        lines = file.readlines()
        number_of_lines = len(lines)
        for i in range(0, number_of_lines, chunk_size):
            chunk_of_lines = lines[i:i+chunk_size]
            print(len(chunk_of_lines))
            h5Filename = chunk_of_lines[0].split(' //')[0]
            print(h5Filename)
            indices = list(map(lambda x: int(x.split(' //')[-1]), chunk_of_lines))
            print(indices)
    '''        
            
    dic = defaultdict(list)
    with open(file_with_indexed_patterns_from_one_hdf5_file, 'r') as file:
        lines = file.readlines()
        mylist = list(map(lambda x: (x.split(' //')[0], int(x.split(' //')[-1])), lines))
        
        dic = { k : [*map(lambda v: v[1], values)]
            for k, values in groupby(sorted(mylist, key=lambda x: x[0]), lambda x: x[0])
            }
        for h5Filename in dic:
            print(h5Filename)
            all_indices = dic[h5Filename]
            number_of_indices = len(all_indices)
            for i in range(0, number_of_indices, chunk_size):
                indices = all_indices[i:i+chunk_size]
                print(indices)
                processing(h5Filename, indices)