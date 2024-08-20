# coding: utf8

import numpy
import fabio
import h5py as h5


#h5Filename = "fr20load1sam8_scan_001_00010.cbf"
#data =  fabio.open(h5Filename)
#print(data.data)
#data_array = numpy.array(data.data)
#print(data_array.shape)

total_array = []
with open('files.lst','r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        data =  fabio.open(line)
        
        total_array.append(data.data)

total_array = numpy.array(total_array)

f = h5.File('fdip_background.h5', 'w')
f.create_dataset('/data/data', data=total_array)
f.close()