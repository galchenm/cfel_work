#!/usr/bin/env python


import sys, os
import numpy as np
import re


resolution_cutoff = 6. #Angstrom
n_split = 20000

stream_fn = sys.argv[1]
stream = open(stream_fn, 'r')

clean_stream_fn = os.path.splitext(stream_fn)[0] + '_clean.stream'

clean_stream = open(clean_stream_fn, 'w')

reading_chunk = False
a = []
for line in stream:
    
    if line.strip() == '----- Begin chunk -----':
        reading_chunk = True
        chunk = line    
        indexed = False
        cell = []

    elif line.strip() == '----- End chunk -----':
        reading_chunk = False
        chunk += line
        if indexed and resolution < resolution_cutoff:
            a.append(1/np.linalg.det(cell))
            clean_stream.write(chunk)
            

    elif reading_chunk:
        chunk += line
        if line.strip() == 'Reflections measured after indexing':
            indexed = True
        elif line[:5] in ('astar', 'bstar', 'cstar'):
            cell.append([float(i) for i in line.split()[2:5]])
        elif line.startswith('diffraction_resolution_limit'):
            resolution = float(line.split()[-2])
                    
    else:
        clean_stream.write(line)

stream.close()
clean_stream.close()

n = len(a)
print "%s indexed patterns in %s"%(n, clean_stream_fn)

a.sort()
limits = []
shift = int(n % n_split / 2)
for j in xrange(n/n_split):
    limits.append((a[shift + j*n_split], a[shift + (j+1)*n_split] if j < n/n_split else a[-1]))
    print os.path.splitext(stream_fn)[0] + '_%s.stream:'%j, 'V in', limits[-1], ', %s patterns'%(n_split if j < n/n_split else n - j*n_split)

split_streams = []
for j in xrange(len(limits)):
    split_streams.append(open(os.path.splitext(stream_fn)[0] + '_%s.stream'%j, 'w'))

csplit = open(os.path.splitext(stream_fn)[0] + '_csplit.dat', 'w')

with open(clean_stream_fn, 'r') as stream:
    reading_chunk = False
    
    for line in stream:
        
        if line.strip() == '----- Begin chunk -----':
            reading_chunk = True
            chunk = line    
            indexed = False
            cell = []

        elif line.strip() == '----- End chunk -----':
            reading_chunk = False
            chunk += line
            for j in xrange(len(limits)):
                if limits[j][0] < 1/np.linalg.det(cell) <= limits[j][1]:
                    split_streams[j].write(chunk)
                    csplit.write('%s split%s\n'%(pattern.strip(), j))
                    break
                

        elif reading_chunk:
            chunk += line
            if line.startswith('Image filename: '):
                pattern = line.split(':')[-1].strip()
            elif line.startswith('Event:'):
                pattern += line.split(':')[-1]
            elif line[:5] in ('astar', 'bstar', 'cstar'):
                cell.append([float(i) for i in line.split()[2:5]])
                        
        else:
            for s in split_streams:
                s.write(line)
