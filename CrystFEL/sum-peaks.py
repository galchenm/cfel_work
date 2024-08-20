#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generate "peak powder" from CrystFEL stream
#
# Copyright В© 2017-2020 Deutsches Elektronen-Synchrotron DESY,
#                       a research centre of the Helmholtz Association.
#
# Author:
#    2017 Alexandra Tolstikova <alexandra.tolstikova@desy.de>
#

import sys
import numpy as np
import h5py
from os.path import basename, splitext
import re

if sys.argv[1] == '-':
    stream = sys.stdin
else:
    stream = open(sys.argv[1], 'r')

reading_geometry = False
reading_chunks = False
reading_peaks = False
max_fs = -100500
max_ss = -100500
max_num_pan = -100
for line in stream:
    if reading_chunks:
        if line.startswith('End of peak list'):
            reading_peaks = False
        elif line.startswith('  fs/px   ss/px (1/d)/nm^-1   Intensity  Panel'):
            reading_peaks = True
        elif reading_peaks:
            fs, ss, dump, intensity, panel = line.split()
            num_panel = int(re.findall(r'[\d\.]+', panel)[0])
            ss, fs = int(float(ss)), int(float(fs))
            powder[ss, fs, num_panel] += float(intensity)
            counter[ss, fs, num_panel] += 1
    elif line.startswith('----- End geometry file -----'):
        reading_geometry = False
        powder = np.zeros((max_ss + 1, max_fs + 1, max_num_pan + 1))
        counter = np.zeros((max_ss + 1, max_fs + 1, max_num_pan + 1))
    elif reading_geometry:
        try:
            par, val = line.split('=')

            if line.startswith('p') and not(line.startswith(';')) and '/' in line:
                num_panel = int(re.findall(r'[\d\.]+', line.split(' = ')[0])[0])
                if num_panel > max_num_pan:
                    max_num_pan = num_panel

            if par.split('/')[-1].strip() == 'max_fs' and int(val) > max_fs:
                max_fs = int(val)

            if par.split('/')[-1].strip() == 'max_ss' and int(val) > max_ss:
                max_ss = int(val)



        except ValueError:
            pass
    elif line.startswith('----- Begin geometry file -----'):
        reading_geometry = True
    elif line.startswith('----- Begin chunk -----'):
        reading_chunks = True

f = h5py.File(splitext(basename(sys.argv[1]))[0]+'-powder-vds.h5', 'w')
f.create_dataset('/data/data', data=powder)
f.close()


f2 = h5py.File(splitext(basename(sys.argv[1]))[0]+'-peaks-count-vds.h5', 'w')
f2.create_dataset('/data/data', data=counter)
f2.close()
print('FINISH\n')