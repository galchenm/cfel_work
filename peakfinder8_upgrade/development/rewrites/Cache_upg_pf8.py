import h5py as h5
import numpy as np
import sys
import os
from cfelpyutils import crystfel_utils, geometry_utils
import matplotlib.pyplot as plt

###### reading raw data
'''
h5ls MPro_5488_1_copy.h5/data/data
data                     Dataset {1000, 2527, 2463}
'''

h5Filename = "MPro_5488_short.h5"
dataPathInFile = "/data/data"
# dataFile = h5.File(h5Filename, "r")
# rawImage = np.array(dataFile[dataPathInFile][0,], dtype=np.float32)

###### reading mask
maskFilename = "mask_MPro_5488_copy.h5"
# maskPathInFile = "/data/data"
# maskFile = h5.File(maskFilename, "r")
#
# maskBad = int('0x00',16)
# maskGood = int('0x01',16)
#
# mask = maskFile[maskPathInFile][:].astype(np.int32)
# ### from Crsytfel
# bitwise_bad = np.bitwise_and(mask, maskBad) > 0
# bitwise_good = np.bitwise_and(mask, maskGood) == maskGood
# mask = np.logical_or(np.logical_not(bitwise_good), bitwise_bad)
#
# intensity = np.where(mask == True, 0, rawImage) #applying mask to raw data

###### reading geometry file
geometryFileName = "pilatus6M_200mm.geom"

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
Nbins = 500 #number of bins with the same width
rs, bin_edges = np.histogram(pix_r.flatten(), bins=Nbins)
# print(rs)
# print(bins)
# print(rs)
# print(len(pix_r))

# plt.hist(pix_r, bins=Nbins)
# plt.show()

def compute_radius_bin_image(r_map, bin_edges):
    bin_image = np.zeros_like(r_map)
    previousEdge = 0
    binCount = 0
    for edge in bin_edges[1:]:
        bin_image[np.logical_and(previousEdge < r_map, r_map <= edge)] = binCount
        binCount += 1
        previousEdge = edge

    return bin_image

def compute_masked_pixels_count_per_bin(mask, bin_image, bin_number):
    return np.sum(mask[bin_image == bin_number])


bin_image = compute_radius_bin_image(r_map, bin_edges)

lineLenght = 8
line_mask = np.zeros_like(bin_image, dtype=int)
min_pixels_per_bin = 100
lineStartIndices = []
for bin_number in range(Nbins):
    print(f"bin_number = {bin_number}")
    while compute_masked_pixels_count_per_bin(line_mask, bin_image, bin_number) < min_pixels_per_bin:
        possible_indices = np.argwhere(np.logical_and(bin_image.ravel() == bin_number, line_mask.ravel() != 1))
        possible_indices = possible_indices[possible_indices < np.size(line_mask) - lineLenght]

        if np.size(possible_indices) == 0:
            break

        selected_index = np.random.choice(possible_indices.ravel(), size=1)[0]

        while line_mask.ravel()[selected_index + lineLenght - 1] > 0 and selected_index > 0:
            selected_index -= 1

        lineStartIndices.append(selected_index)
        line_mask.ravel()[selected_index:selected_index + lineLenght] = 1

        a = 1

    a = 1

a = 1




