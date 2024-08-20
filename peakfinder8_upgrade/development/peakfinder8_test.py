import h5py as h5
import numpy as np
import time
import sys
import configparser
import ctypes as ct

from cfelpyutils import crystfel_utils, geometry_utils

from numpy.ctypeslib import ndpointer

#from fdip_extension import *


MASK_GOOD = 1
MASK_BAD = 0
bstpReg=-0.5
hitfinderMinSNR=4.0 
ADCthresh=10
hitfinderMinPixCount=2
hitfinderMaxPixCount=1
hitfinderLocalBGRadius=10
istep=1
degree=0.99
maxShellsMerged=5
NumberOfRandomS=100

#asic_nx=4150
#asic_ny=4371
asic_nx=2463
asic_ny=2527

nasics_x=1
nasics_y=1

def _np_ptr(np_array):
    return ct.c_void_p(np_array.ctypes.data)

def pUptLinearPixRmodifWithArrayOfIndexV2(NxNy, maxRad, pix_r, lenLinearArrayRandomInd, tmpLinearArrayRandomInd, tmpOffset1DArray, numPerShell1):
    #void UptLinearPixRmodifWithArrayOfIndexV2(int numEl, int maxRad, int *pix_r, int lenLinearArrayRandomInd, int* tmpLinearArrayRandomInd, int* tmpOffset1DArray, int* numPerShell1)
    pix_r = np.array(pix_r, dtype=np.int32)
    tmpLinearArrayRandomInd = np.array(tmpLinearArrayRandomInd, dtype=np.int32)
    tmpOffset1DArray = np.array(tmpOffset1DArray, dtype=np.int32)
    numPerShell1 = np.array(numPerShell1, dtype=np.int32)
    lib = ct.CDLL( '/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/development/RandSelForR.so')
    pfun = lib.UptLinearPixRmodifWithArrayOfIndexV2
    pfun.restype = ct.c_void_p
    pfun.argtypes = (ct.c_size_t, ct.c_int, ct.c_void_p, ct.c_int, ct.c_void_p, ct.c_void_p, ct.c_void_p)
    pfun(NxNy, maxRad, _np_ptr(pix_r),lenLinearArrayRandomInd, _np_ptr(tmpLinearArrayRandomInd),_np_ptr(tmpOffset1DArray), _np_ptr(numPerShell1))
    return tmpLinearArrayRandomInd, tmpOffset1DArray


def pUptLinearPixRmodifWithArrayOfIndexV3(NxNy, maxRad, pix_r, lenLinearArrayRandomInd, tmpLinearArrayRandomInd, tmpOffset1DArray, numPerShell1):
    #void UptLinearPixRmodifWithArrayOfIndexV2(int numEl, int maxRad, int *pix_r, int lenLinearArrayRandomInd, int* tmpLinearArrayRandomInd, int* tmpOffset1DArray, int* numPerShell1)
    pix_r = np.array(pix_r, dtype=np.int32)
    tmpLinearArrayRandomInd = np.array(tmpLinearArrayRandomInd, dtype=np.int32)
    tmpOffset1DArray = np.array(tmpOffset1DArray, dtype=np.int32)
    numPerShell1 = np.array(numPerShell1, dtype=np.int32)
    lib = ct.CDLL( '/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/development/RandSelForR.so')
    pfun = lib.UptLinearPixRmodifWithArrayOfIndexV3
    pfun.restype = ct.c_void_p
    pfun.argtypes = (ct.c_size_t, ct.c_int, ct.c_void_p, ct.c_int, ct.c_void_p, ct.c_void_p, ct.c_void_p)
    pfun(NxNy, maxRad, _np_ptr(pix_r),lenLinearArrayRandomInd, _np_ptr(tmpLinearArrayRandomInd),_np_ptr(tmpOffset1DArray), _np_ptr(numPerShell1))
    return tmpLinearArrayRandomInd, tmpOffset1DArray

def pfLenArrayForLinearArrayRandomInd(maxRad, numPerShell1):
    #int fLenArrayForLinearArrayRandomInd(int maxRad, int* numPerShell1)
    numPerShell1 = np.array(numPerShell1, dtype=np.int32)
    lib = ct.CDLL('/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/development/RandSelForR.so')
    pfun = lib.fLenArrayForLinearArrayRandomInd
    pfun.restype = ct.c_int
    pfun.argtypes = (ct.c_int, ct.c_void_p)
    lenLinearArrayRandomInd = pfun(maxRad, _np_ptr(numPerShell1))
    return lenLinearArrayRandomInd


def pfuncNumPerShellC(NxNy, maxRad, pix_r, numPerShell1):
    #void funcNumPerShellC(int numEl, int maxRad, int* pix_r, int *numPerShell1)
    pix_r = np.array(pix_r, dtype=np.int32)
    numPerShell1 = np.array(numPerShell1, dtype=np.int32)
    lib = ct.CDLL('/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/development/RandSelForR.so')
    pfun = lib.funcNumPerShellC
    pfun.restype = ct.c_void_p
    pfun.argtypes = (ct.c_int, ct.c_int, ct.c_void_p, ct.c_void_p)
    pfun(NxNy, maxRad, _np_ptr(pix_r), _np_ptr(numPerShell1))
    return numPerShell1

def ptest_funcNumPerShellC(maxRad, pix_r, numPerShell1):
    #void funcNumPerShellC(int maxRad, const std::vector<int>* pix_r, std::vector<int>* numPerShell1)
    pix_r = np.array(pix_r, dtype=np.int32)
    numPerShell1 = np.array(numPerShell1, dtype=np.int32)
    lib = ct.CDLL('/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/development/RandSelForR.so')
    pfun = lib.test_funcNumPerShellC
    pfun.restype = ct.c_void_p
    pfun.argtypes = (ct.c_int, ct.c_void_p, ct.c_void_p)
    
    pfun(maxRad, _np_ptr(pix_r), _np_ptr(numPerShell1))
    return numPerShell1


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
    lib = ct.CDLL('/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/development/peakfinder8.so')
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
    if outliersMask is not None:
        outliersMask[:] = outliersMask_buf.copy()
    return int_flag, outliersMask_buf

def PeakFinder8py_offset(peaklist, data, mask, pix_r,
                    asic_nx, asic_ny, nasics_x, nasics_y,
                    ADCthresh, hitfinderMinSNR,
                    hitfinderMinPixCount, hitfinderMaxPixCount,
                    hitfinderLocalBGRadius, maxRad,
                    lenLinearArrayRandomInd, LinearArrayRandomInd,
                    Offset1DArray, outliersMask):
    req = PeakFinderStructure()
    lib = ct.CDLL('/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/development/peakfinder8.so')
    pfun = lib.peakfinder8_offset
    pfun.restype = ct.c_int
    data = np.array(data, dtype=np.float32)
    pix_r = np.array(pix_r,dtype=np.int32)
    mask = np.array(mask, dtype=np.int8)
    len_outliersMask = len(data)
    outliersMask_buf = np.zeros(len_outliersMask, dtype=np.int8)
    
    pfun.argtypes = (ct.POINTER(PeakFinderStructure),ct.c_void_p,ct.c_void_p,ct.c_void_p,ct.c_long,ct.c_long,ct.c_long,ct.c_long,ct.c_float,ct.c_float,ct.c_long,ct.c_long,ct.c_long,ct.c_int,ct.c_int,ct.c_void_p,ct.c_void_p,ct.c_void_p)
    int_flag = pfun(ct.byref(req),_np_ptr(data),_np_ptr(mask),_np_ptr(pix_r),asic_nx, asic_ny, nasics_x, nasics_y,
                    ADCthresh, hitfinderMinSNR,
                    hitfinderMinPixCount, hitfinderMaxPixCount,
                    hitfinderLocalBGRadius, maxRad,
                    lenLinearArrayRandomInd, _np_ptr(LinearArrayRandomInd),
                    _np_ptr(Offset1DArray), _np_ptr(outliersMask_buf))
    if outliersMask is not None:
        outliersMask[:] = outliersMask_buf.copy()
    return int_flag, outliersMask_buf

def PeakFinder8py_offset_median(peaklist, data, mask, pix_r,
                    asic_nx, asic_ny, nasics_x, nasics_y,
                    ADCthresh, hitfinderMinSNR,
                    hitfinderMinPixCount, hitfinderMaxPixCount,
                    hitfinderLocalBGRadius, maxRad,
                    lenLinearArrayRandomInd, LinearArrayRandomInd,
                    Offset1DArray, outliersMask):

    '''
    (tPeakList *peaklist, float *data, char *mask, int *pix_r,
                long asic_nx, long asic_ny, long nasics_x, long nasics_y,
                float ADCthresh, float hitfinderMinSNR,
                long hitfinderMinPixCount, long hitfinderMaxPixCount,
                long hitfinderLocalBGRadius, int maxRad,
                int lenLinearArrayRandomInd, int* LinearArrayRandomInd,
                int* Offset1DArray, char* outliersMask)
    '''
    req = PeakFinderStructure()
    lib = ct.CDLL('/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/development/peakfinder8.so')
    pfun = lib.peakfinder8_offset_median
    pfun.restype = ct.c_int
    data = np.array(data, dtype=np.float32)
    pix_r = np.array(pix_r,dtype=np.int32)
    mask = np.array(mask, dtype=np.int8)
    len_outliersMask = len(data)
    outliersMask_buf = np.zeros(len_outliersMask, dtype=np.int8)
    
    pfun.argtypes = (ct.POINTER(PeakFinderStructure),ct.c_void_p,ct.c_void_p,ct.c_void_p,ct.c_long,ct.c_long,ct.c_long,ct.c_long,ct.c_float,ct.c_float,ct.c_long,ct.c_long,ct.c_long,ct.c_int,ct.c_int,ct.c_void_p,ct.c_void_p,ct.c_void_p)
    int_flag = pfun(ct.byref(req),_np_ptr(data),_np_ptr(mask),_np_ptr(pix_r),asic_nx, asic_ny, nasics_x, nasics_y,
                    ADCthresh, hitfinderMinSNR,
                    hitfinderMinPixCount, hitfinderMaxPixCount,
                    hitfinderLocalBGRadius, maxRad,
                    lenLinearArrayRandomInd, _np_ptr(LinearArrayRandomInd),
                    _np_ptr(Offset1DArray), _np_ptr(outliersMask_buf))
    if outliersMask is not None:
        outliersMask[:] = outliersMask_buf.copy()
    return int_flag, outliersMask_buf


h5Filename = "/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/soft/fdip_test/files_for_test/MPro_5488_1_copy.h5"
dataPathInFile = "/data/data"
dataFile = h5.File(h5Filename, "r")


maskFilename = "/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/soft/fdip_test/files_for_test/mask_MPro_5488_copy.h5"
maskPathInFile = "/data/data"
maskFile = h5.File(maskFilename, "r")

mask = maskFile[maskPathInFile][:]

geometryFileName = "/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/soft/fdip_test/files_for_test/pilatus6M_200mm.geom"

geometry = crystfel_utils.load_crystfel_geometry(geometryFileName)
pixel_maps = geometry_utils.compute_pixel_maps(geometry)
pixel_maps_for_visualization = geometry_utils.adjust_pixel_maps_for_pyqtgraph(pixel_maps)


x_map = pixel_maps.x.astype(np.float32)
y_map = pixel_maps.y.astype(np.float32)
r_map = pixel_maps.r.astype(np.float32)


maxRad = int(np.rint(max(r_map.flatten()))) + 2

len_x_map = len(x_map.flatten())
pix_r = r_map.flatten().astype(np.int32)


numPerShell1 = np.array([0]*maxRad, dtype=np.int32)
'''
pfuncNumPerShellC: funcNumPerShellC from RandSelForR.so - num per shell : don't need maxRad there

void funcNumPerShellC(int numEl, int* pix_r, int *numPerShell1){
  
  for (int* pix = pix_r; pix<pix_r + numEl; ++pix){
    if(*pix <0)
    {
      continue;
    }
    numPerShell1[*pix]++;
  }
  
  for (int i=0; i<numEl; ++i){
    if(pix_r[i] <0)
    {
      continue;
    }
    numPerShell1[pix_r[i]]++;
  }
};

Can be rewritten in the wollowing way?

void funcNumPerShellC(const std::vector<int>& pix_r, std::vector<int>& numPerShell1){
  for (auto pix : pix_r){
    if(pix < 0)
    {
      continue;
    }
    numPerShell1[pix]++;
  }
};

void funcNumPerShellC(int* pix_r, int* numPerShell1){
  for (auto pix : pix_r){
    if(pix < 0)
    {
      continue;
    }
    numPerShell1[pix]++;
  }
};

def pfuncNumPerShellC(NxNy, pix_r, numPerShell1):
    #void funcNumPerShellC(int maxRad, const std::vector<int>& pix_r, std::vector<int>& numPerShell1)
    pix_r = np.array(pix_r, dtype=np.int32)
    numPerShell1 = np.array(numPerShell1, dtype=np.int32)
    lib = ct.CDLL('/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/development/RandSelForR.so')
    pfun = lib.funcNumPerShellC
    pfun.restype = ct.c_void_p
    pfun.argtypes = (ct.c_int, ct.c_void_p, ct.c_void_p)
    pfun(NxNy, _np_ptr(pix_r), _np_ptr(numPerShell1))
    return numPerShell1

'''
#numPerShell1 = pfuncNumPerShellC(len_x_map, maxRad, pix_r, numPerShell1)

numPerShell1 = ptest_funcNumPerShellC(maxRad, pix_r, numPerShell1)

#-------------------------------------------------------------------------------------------------------
'''
int fLenArrayForLinearArrayRandomInd(int maxRad, int* numPerShell1){
  int lenShellR;
  int lenLinearArrayRandomInd = 0;
  for(int r=0; r < maxRad; r++)
  {
    lenShellR = numPerShell1[r];
    lenLinearArrayRandomInd += ((lenShellR <= NumberOfRandomS) ? lenShellR : NumberOfRandomS);
  }
  return lenLinearArrayRandomInd;
};


to:

int fLenArrayForLinearArrayRandomInd(int maxRad, std::vector<int>& numPerShell1){
  int lenShellR;
  int lenLinearArrayRandomInd = 0;
  for(int r=0; r<maxRad; ++r)
  {
    lenShellR = numPerShell1[r];
    lenLinearArrayRandomInd += ((lenShellR <= NumberOfRandomS) ? lenShellR : NumberOfRandomS);
  }
  return lenLinearArrayRandomInd;
};



'''
lenLinearArrayRandomInd = pfLenArrayForLinearArrayRandomInd(maxRad, numPerShell1)


#-------------------------------------------------------------------------------------------------------

tmpLinearArrayRandomInd = np.array([0]*lenLinearArrayRandomInd, dtype=np.int32)
tmpOffset1DArray = np.array([0]*maxRad, dtype=np.int32)
'''
UptLinearPixRmodifWithArrayOfIndexV2:

void UptLinearPixRmodifWithArrayOfIndexV2(int numEl, int maxRad, int *pix_r, int lenLinearArrayRandomInd, int* tmpLinearArrayRandomInd, int* tmpOffset1DArray, int *numPerShell1)
{
  int* RIndex = (int*) malloc(NumberOfRandomS*sizeof(int));
  memset(RIndex, 0, NumberOfRandomS*sizeof(int));

  int** _IndexForEachR;
  
  //2D array where each r > 0 relates to the list if its indexes
  GetIndexForNonNegativeR(numEl, maxRad, pix_r, numPerShell1, &_IndexForEachR);

  int lenShellR;

  int indOffset1DArray = 0;
  int indLinearArrayRandomInd = 0;
  int prevOffset = 0;

  for(int r =0; r<maxRad; r++)
  {
    lenShellR = numPerShell1[r];

    //if number of items for this r is less than should be
    //selected, skip it. It means that we selected all items 
    //for this r
    if(lenShellR <= NumberOfRandomS){
      for(int ir = 0; ir <lenShellR; ir++)
      {
        tmpLinearArrayRandomInd[indLinearArrayRandomInd] = _IndexForEachR[r][ir];
        
        indLinearArrayRandomInd++;
      }
      tmpOffset1DArray[indOffset1DArray] = prevOffset;
      prevOffset = indLinearArrayRandomInd;

      indOffset1DArray++;
      continue;
    }

    //get array that includes a list of random indexes for each r
    RandomIndexF(lenShellR, _IndexForEachR[r], RIndex);
    for(int ir = 0; ir<NumberOfRandomS; ir++)
      {
        tmpLinearArrayRandomInd[indLinearArrayRandomInd] = RIndex[ir];
        
        indLinearArrayRandomInd++;
      }
    tmpOffset1DArray[indOffset1DArray] = prevOffset;
    prevOffset = indLinearArrayRandomInd;
    indOffset1DArray++;
  }

  return;
};

'''
tmpLinearArrayRandomInd, tmpOffset1DArray = pUptLinearPixRmodifWithArrayOfIndexV2(len_x_map, maxRad, pix_r, lenLinearArrayRandomInd, tmpLinearArrayRandomInd, tmpOffset1DArray, numPerShell1)

#tmpLinearArrayRandomInd, tmpOffset1DArray = pUptLinearPixRmodifWithArrayOfIndexV3(len_x_map, maxRad, pix_r, lenLinearArrayRandomInd, tmpLinearArrayRandomInd, tmpOffset1DArray, numPerShell1)



#print("tmpLinearArrayRandomInd")
#for i in tmpLinearArrayRandomInd:
#    print("ind = {}".format(i))

#print("END")

rawImages = np.array(dataFile[dataPathInFile][0:100], dtype=np.float32)

#
#for imageNumber in range(rawImages.shape[0]):
#for imageNumber in [0]:
for imageNumber in [0]:
    if imageNumber % 50 == 0:
        print(imageNumber/rawImages.shape[0], "%")

    
    image_shape = rawImages[imageNumber, ].shape

    Int = np.reshape(rawImages[imageNumber, ], len_x_map)
    max_num = 0


    
    index = Int >= 0
    mask = np.zeros(len_x_map, dtype=np.int32)
    mask[index] += MASK_GOOD

   
    int_PeakFinder_flag, outliersMask = PeakFinder8py_offset_median(None, Int, mask, pix_r,
                    asic_nx, asic_ny, nasics_x, nasics_y,
                    ADCthresh, hitfinderMinSNR,
                    hitfinderMinPixCount, hitfinderMaxPixCount,
                    hitfinderLocalBGRadius, maxRad,
                    lenLinearArrayRandomInd, tmpLinearArrayRandomInd,
                    tmpOffset1DArray, None)
    
    '''
    int_PeakFinder_flag, outliersMask = PeakFinder8py_offset(None, Int, mask, pix_r,
                asic_nx, asic_ny, nasics_x, nasics_y,
                ADCthresh, hitfinderMinSNR,
                hitfinderMinPixCount, hitfinderMaxPixCount,
                hitfinderLocalBGRadius, maxRad,
                lenLinearArrayRandomInd, tmpLinearArrayRandomInd ,
                tmpOffset1DArray, None)
    '''

    '''
    int_PeakFinder_flag, outliersMask = PeakFinder8py(None, Int, mask, pix_r,
                    asic_nx, asic_ny, nasics_x, nasics_y,
                    ADCthresh, hitfinderMinSNR,
                    hitfinderMinPixCount, hitfinderMaxPixCount,
                    hitfinderLocalBGRadius, None)
    '''
    
    
print('END')

