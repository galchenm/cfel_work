import os
import sys
import h5py as h5
import numpy as np
import time
import configparser
import ctypes as ct
import re
from cfelpyutils import crystfel_utils, geometry_utils

from numpy.ctypeslib import ndpointer

#Constants for peakfinder8
MASK_GOOD = 1
MASK_BAD = 0
bstpReg=-0.5
hitfinderMinSNR=3.0 
ADCthresh=10
hitfinderMinPixCount=2
hitfinderMaxPixCount=50
hitfinderLocalBGRadius=3
istep=1
degree=0.99
#maxShellsMerged=5
#NumberOfRandomS=100

asic_nx=4148
asic_ny=4362

nasics_x=1
nasics_y=1

dataPathInFile = "/entry/data/data"

maskFilename = "mask_v0.h5"
maskPathInFile = "/data/data"

geometryFileName = "eiger16M-P11_200mm_sh1.geom"

MIN_NUM_PEAKS = 10
SET_OFFSET_X = 1
SET_OFFSET_Y = 0

chunk_size = 5


def _np_ptr(np_array):
    return ct.c_void_p(np_array.ctypes.data)

class PeakFinderStructure(ct.Structure):
    _fields_=[('nPeaks',ct.c_long), ('nHot',ct.c_long), ('peakResolution',ct.c_float), ('peakResolutionA',ct.c_float), ('peakDensity',ct.c_float), ('peakNpix',ct.c_float), 
              ('peakTotal',ct.c_float), ('memoryAllocated',ct.c_int), ('nPeaks_max',ct.c_long), ('peak_maxintensity',ct.POINTER(ct.c_float)), ('peak_totalintensity',ct.POINTER(ct.c_float)), 
              ('peak_sigma',ct.POINTER(ct.c_float)), ('peak_snr',ct.POINTER(ct.c_float)), ('peak_npix',ct.POINTER(ct.c_float)), ('peak_com_x',ct.POINTER(ct.c_float)), ('peak_com_y',ct.POINTER(ct.c_float)), ('peak_com_index',ct.POINTER(ct.c_long)), 
              ('peak_com_x_assembled',ct.POINTER(ct.c_float)), ('peak_com_y_assembled',ct.POINTER(ct.c_float)), ('peak_com_r_assembled',ct.POINTER(ct.c_float)), ('peak_com_q',ct.POINTER(ct.c_float)), ('peak_com_res',ct.POINTER(ct.c_float))]



def PeakFinder8py(peaklist, data, mask, pix_r,
                  asic_nx, asic_ny, nasics_x, nasics_y,
                  ADCthresh, hitfinderMinSNR,
                  hitfinderMinPixCount, hitfinderMaxPixCount,
                  hitfinderLocalBGRadius, outliersMask):

    req = PeakFinderStructure()
    req.nPeaks_max = 10000
    lib = ct.CDLL('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/adding_several_patterns/peakfinder8.so')
    pfun = lib.peakfinder8
    pfun.restype = ct.c_int
    data = np.array(data, dtype=np.float32)
    pix_r = np.array(pix_r,dtype=np.float32)
    mask = np.array(mask, dtype=np.int8)
    len_outliersMask = len(data)
    outliersMask_buf = np.zeros(len_outliersMask, dtype=np.int8)
    

    pfun.argtypes = (ct.POINTER(PeakFinderStructure),ct.c_void_p,ct.c_void_p,ct.c_void_p,ct.c_long,ct.c_long,ct.c_long,ct.c_long,ct.c_float,ct.c_float,ct.c_long,ct.c_long,ct.c_long,ct.c_void_p)
    int_flag = pfun(ct.byref(req),_np_ptr(data),_np_ptr(mask),_np_ptr(pix_r),asic_nx, asic_ny, nasics_x, nasics_y,
                    ADCthresh, hitfinderMinSNR,
                    hitfinderMinPixCount, hitfinderMaxPixCount,
                    hitfinderLocalBGRadius, _np_ptr(outliersMask_buf))
                    
    return int_flag, req


def calling_peakfinder8(h5Filename):
    global output_dir
    dataFile = h5.File(h5Filename, "r")
    print(87)
    maskFile = h5.File(maskFilename, "r")
    mask = maskFile[maskPathInFile][:]
    
    geometry = crystfel_utils.load_crystfel_geometry(geometryFileName)
    pixel_maps = geometry_utils.compute_pixel_maps(geometry)
    pixel_maps_for_visualization = geometry_utils.adjust_pixel_maps_for_pyqtgraph(pixel_maps)
    print(94)
    
    x_map = pixel_maps.x.astype(np.float32)
    y_map = pixel_maps.y.astype(np.float32)
    r_map = pixel_maps.r.astype(np.float32)
    print(99)
    maxRad = int(np.rint(max(r_map.flatten()))) + 2
    print(101)
    len_x_map = len(x_map.flatten())
    pix_r = r_map.flatten().astype(np.int32)
    print(104)
    rawImages = dataFile[dataPathInFile]
    print(106)
    print('Running...\n')
    num = rawImages.shape[0]
    new_data = np.zeros((num//chunk_size,)+ rawImages.shape[1:])
    print(new_data.shape)
    chunk_index = 0
    for i in range(0, num, chunk_size):
        print('Chunking...\n')
        print('Index of chunk is {}\n'.format(i))

        data = rawImages[i:i+chunk_size,]
        new_data[chunk_index,] = np.sum(data, axis=0)
        chunk_index += 1
        total_peak_list_x = []
        for imageNumber in range(data.shape[0]):            
            image_shape = rawImages[imageNumber, ].shape

            Int = rawImages[imageNumber, ].ravel()
            max_num = 0

            index = Int >= 0

            mask = mask.ravel().astype(np.int32) 

            
            dump, req = PeakFinder8py(None, Int, mask, \
                                            pix_r, asic_nx, asic_ny, nasics_x, nasics_y, \
                                            ADCthresh, hitfinderMinSNR, \
                                            hitfinderMinPixCount, hitfinderMaxPixCount, hitfinderLocalBGRadius, None)
            
            print(req.nPeaks)
            print(req.peak_com_x)#[0])
            total_peak_list_x.append(req.peak_com_x)
            print(req.peak_com_y)#[0])
            print(req.peak_totalintensity)#[0])
    print(len(total_peak_list_x))
    dataFile.close()
    maskFile.close()

if __name__ == '__main__':
    h5Filename = sys.argv[1]
    #output_dir = sys.argv[2]
    
    calling_peakfinder8(h5Filename)