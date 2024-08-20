import h5py as h5
import numpy as np
import sys
import os
from cfelpyutils import crystfel_utils, geometry_utils


###### reading raw data
'''
h5ls /gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/soft/fdip_test/files_for_test/MPro_5488_1_copy.h5/data/data
data                     Dataset {1000, 2527, 2463}
'''

h5Filename = "/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/soft/fdip_test/files_for_test/MPro_5488_1_copy.h5"
dataPathInFile = "/data/data"
dataFile = h5.File(h5Filename, "r")
rawImage = np.array(dataFile[dataPathInFile][0,], dtype=np.float32)

###### reading mask
maskFilename = "/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/soft/fdip_test/files_for_test/mask_MPro_5488_copy.h5"
maskPathInFile = "/data/data"
maskFile = h5.File(maskFilename, "r")

maskBad = int('0x00',16)
maskGood = int('0x01',16)

mask = maskFile[maskPathInFile][:].astype(np.int32)

bitwise_bad = np.bitwise_and(mask, maskBad) > 0
bitwise_good = np.bitwise_and(mask, maskGood) == maskGood     
mask = np.logical_or(np.logical_not(bitwise_good) , bitwise_bad)

intensity = np.where(mask == True, 0, rawImage) #applying mask to raw data

###### reading geometry file
geometryFileName = "/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/soft/fdip_test/files_for_test/pilatus6M_200mm.geom"

###### calculating radii
geometry = crystfel_utils.load_crystfel_geometry(geometryFileName)
pixel_maps = geometry_utils.compute_pixel_maps(geometry)

x_map = pixel_maps.x.astype(np.float32)
y_map = pixel_maps.y.astype(np.float32)
r_map = pixel_maps.r.astype(np.float32)

len_x_map = len(x_map.flatten())
pix_r = r_map.flatten().astype(np.int32)

minRad = min(pix_r)
maxRad = max(pix_r)

###########binning radii https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
Nbins = 100 #number of bins with the same width
rs, bins = np.histogram(pix_r, bins=Nbins)
print(rs)
print(bins)
print(np.sum(rs))
print(len(pix_r))