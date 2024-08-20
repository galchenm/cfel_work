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

maskFilename = "/asap3/petra3/gpfs/p11/2022/data/11013278/processed/mask_v0.h5"
maskPathInFile = "/data/data"

geometryFileName = "/asap3/petra3/gpfs/p11/2022/data/11013278/processed/eiger16M-P11_160mm.geom"

MIN_NUM_PEAKS = 10
SET_OFFSET_X = 1
SET_OFFSET_Y = 0

def _np_ptr(np_array):
    return ct.c_void_p(np_array.ctypes.data)

def pUptLinearPixRmodifWithArrayOfIndexV2(NxNy, maxRad, pix_r, lenLinearArrayRandomInd, tmpLinearArrayRandomInd, tmpOffset1DArray, numPerShell1):
    #void UptLinearPixRmodifWithArrayOfIndexV2(int numEl, int maxRad, int *pix_r, int lenLinearArrayRandomInd, int* tmpLinearArrayRandomInd, int* tmpOffset1DArray, int* numPerShell1)
    pix_r = np.array(pix_r, dtype=np.int32)
    tmpLinearArrayRandomInd = np.array(tmpLinearArrayRandomInd, dtype=np.int32)
    tmpOffset1DArray = np.array(tmpOffset1DArray, dtype=np.int32)
    numPerShell1 = np.array(numPerShell1, dtype=np.int32)
    lib = ct.CDLL( '/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/RandSelForR.so')
    pfun = lib.UptLinearPixRmodifWithArrayOfIndexV2
    pfun.restype = ct.c_void_p
    pfun.argtypes = (ct.c_size_t, ct.c_int, ct.c_void_p, ct.c_int, ct.c_void_p, ct.c_void_p, ct.c_void_p)
    pfun(NxNy, maxRad, _np_ptr(pix_r),lenLinearArrayRandomInd, _np_ptr(tmpLinearArrayRandomInd),_np_ptr(tmpOffset1DArray), _np_ptr(numPerShell1))
    return tmpLinearArrayRandomInd, tmpOffset1DArray

def pfLenArrayForLinearArrayRandomInd(maxRad, numPerShell1):
    #int fLenArrayForLinearArrayRandomInd(int maxRad, int* numPerShell1)
    numPerShell1 = np.array(numPerShell1, dtype=np.int32)
    lib = ct.CDLL('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/RandSelForR.so')
    pfun = lib.fLenArrayForLinearArrayRandomInd
    pfun.restype = ct.c_int
    pfun.argtypes = (ct.c_int, ct.c_void_p)
    lenLinearArrayRandomInd = pfun(maxRad, _np_ptr(numPerShell1))
    return lenLinearArrayRandomInd

def pfuncNumPerShellC(NxNy, maxRad, pix_r, numPerShell1):
    #void funcNumPerShellC(int numEl, int maxRad, int* pix_r, int *numPerShell1)
    pix_r = np.array(pix_r, dtype=np.int32)
    numPerShell1 = np.array(numPerShell1, dtype=np.int32)
    lib = ct.CDLL('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/RandSelForR.so')
    pfun = lib.funcNumPerShellC
    pfun.restype = ct.c_void_p
    pfun.argtypes = (ct.c_int, ct.c_int, ct.c_void_p, ct.c_void_p)
    pfun(NxNy, maxRad, _np_ptr(pix_r), _np_ptr(numPerShell1))
    return numPerShell1


def _np_ptr(np_array):
    return ct.c_void_p(np_array.ctypes.data)

class PeakFinderStructure(ct.Structure):
    '''
    typedef struct {
    public:
        long        nPeaks;
        long        nHot;
        float       peakResolution;         // Radius of 80% of peaks
        float       peakResolutionA;        // Radius of 80% of peaks
        float       peakDensity;            // Density of peaks within this 80% figure
        float       peakNpix;               // Number of pixels in peaks
        float       peakTotal;              // Total integrated intensity in peaks
        int     memoryAllocated;
        long        nPeaks_max;

        float       *peak_maxintensity;     // Maximum intensity in peak
        float       *peak_totalintensity;   // Integrated intensity in peak
        float       *peak_sigma;            // Signal-to-noise ratio of peak
        float       *peak_snr;              // Signal-to-noise ratio of peak
        float       *peak_npix;             // Number of pixels in peak
        float       *peak_com_x;            // peak center of mass x (in raw layout)
        float       *peak_com_y;            // peak center of mass y (in raw layout)
        long        *peak_com_index;        // closest pixel corresponding to peak
        float       *peak_com_x_assembled;  // peak center of mass x (in assembled layout)
        float       *peak_com_y_assembled;  // peak center of mass y (in assembled layout)
        float       *peak_com_r_assembled;  // peak center of mass r (in assembled layout)
        float       *peak_com_q;            // Scattering vector of this peak
        float       *peak_com_res;          // REsolution of this peak
    } tPeakList;
    '''
    _fields_=[('nPeaks',ct.c_long), ('nHot',ct.c_long), ('peakResolution',ct.c_float), ('peakResolutionA',ct.c_float), ('peakDensity',ct.c_float), ('peakNpix',ct.c_float), 
              ('peakTotal',ct.c_float), ('memoryAllocated',ct.c_int), ('nPeaks_max',ct.c_long), ('peak_maxintensity',ct.POINTER(ct.c_float)), ('peak_totalintensity',ct.POINTER(ct.c_float)), 
              ('peak_sigma',ct.POINTER(ct.c_float)), ('peak_snr',ct.POINTER(ct.c_float)), ('peak_npix',ct.POINTER(ct.c_float)), ('peak_com_x',ct.POINTER(ct.c_float)), ('peak_com_y',ct.POINTER(ct.c_float)), ('peak_com_index',ct.POINTER(ct.c_long)), 
              ('peak_com_x_assembled',ct.POINTER(ct.c_float)), ('peak_com_y_assembled',ct.POINTER(ct.c_float)), ('peak_com_r_assembled',ct.POINTER(ct.c_float)), ('peak_com_q',ct.POINTER(ct.c_float)), ('peak_com_res',ct.POINTER(ct.c_float))]
    # pass


def PeakFinder8py(peaklist, data, mask, pix_r,
                  asic_nx, asic_ny, nasics_x, nasics_y,
                  ADCthresh, hitfinderMinSNR,
                  hitfinderMinPixCount, hitfinderMaxPixCount,
                  hitfinderLocalBGRadius, outliersMask):

    req = PeakFinderStructure()
    req.nPeaks_max = 10000
    lib = ct.CDLL('/gpfs/cfel/user/atolstik/aps_Jun2019/convert/peakfinder8.so')
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
    
    maskFile = h5.File(maskFilename, "r")
    mask = maskFile[maskPathInFile][:]
    
    geometry = crystfel_utils.load_crystfel_geometry(geometryFileName)
    pixel_maps = geometry_utils.compute_pixel_maps(geometry)
    pixel_maps_for_visualization = geometry_utils.adjust_pixel_maps_for_pyqtgraph(pixel_maps)

    
    x_map = pixel_maps.x.astype(np.float32)
    y_map = pixel_maps.y.astype(np.float32)
    r_map = pixel_maps.r.astype(np.float32)
    
    maxRad = int(np.rint(max(r_map.flatten()))) + 2

    len_x_map = len(x_map.flatten())
    pix_r = r_map.flatten().astype(np.int32)

    rawImages = np.array(dataFile[dataPathInFile][()], dtype=np.float32)
    
    for imageNumber in range(rawImages.shape[0]):
        if imageNumber % 50 == 0:
            print(imageNumber/rawImages.shape[0], "%")
            
        image_shape = rawImages[imageNumber, ].shape

        Int = rawImages[imageNumber, ].ravel()
        max_num = 0

        index = Int >= 0

        mask = mask.ravel().astype(np.int32) #np.reshape(mask, len_x_map)

        
        dump, req = PeakFinder8py(None, Int, mask, \
                                        pix_r, asic_nx, asic_ny, nasics_x, nasics_y, \
                                        ADCthresh, hitfinderMinSNR, \
                                        hitfinderMinPixCount, hitfinderMaxPixCount, hitfinderLocalBGRadius, None)
        
        '''
        PeakFinder8py(peaklist, data, mask, \
                        pix_r, asic_nx, asic_ny, nasics_x, nasics_y,\
                        ADCthresh, hitfinderMinSNR,\
                        hitfinderMinPixCount, hitfinderMaxPixCount, hitfinderLocalBGRadius, outliersMask)
        '''
        
        
        print(os.path.basename(h5Filename) , req.nPeaks) 
        if(req.nPeaks > MIN_NUM_PEAKS):
            NumOFline = re.search(r'\d+\.h5',os.path.basename(h5Filename)).group().split('.')[0]
            dirname = os.path.join(output_dir, os.path.basename(h5Filename).split('_'+str(NumOFline))[0])
            print(dirname)
            if not(os.path.exists(dirname)):
                os.mkdir(dirname)
            filename = os.path.join(dirname, NumOFline+'.lst')
            print(' ', filename)
            print('\n')
            if os.path.exists(filename):
                append_write = 'a' # append if already exists
            else:
                append_write = 'w' # make a new file if not

            highscore = open(filename, append_write)
            highscore.write(f'{imageNumber + SET_OFFSET_X},{int(NumOFline)-1 + SET_OFFSET_Y}\n')
            highscore.close()
        

if __name__ == '__main__':
    h5Filename = sys.argv[1]
    output_dir = sys.argv[2]
    print(h5Filename)
    calling_peakfinder8(h5Filename)