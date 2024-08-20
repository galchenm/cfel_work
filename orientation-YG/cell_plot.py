#!/usr/bin/env python

from collections import defaultdict
import numpy as np
import pyqtgraph as pg
import time
import os
import sys
import click
from sortedcontainers import SortedDict

def read_stream(filename):
    data = {"cell":[], "resolution":[]}
    
    stream = open(filename, "r")
    while stream is not None:
        for line in stream:
            print(line, end='\x1b[1K\r')
            if line.startswith("----- Begin chunk -----"):
                indexed = False

                
            elif line.startswith("Cell parameters"):
                indexed = True
                cell = [float(i) for i in line.split()[2:9] if i[0] != "n"]
                # Convert a, b, c to Angstrom:
                for i in range(3):
                    cell[i] *= 10

            elif line.startswith("diffraction_resolution_limit"):
                resolution = float(line.split()[-2])

            elif line.startswith("----- End chunk"):
                if not indexed:
                    continue

                data["cell"].append(cell) 
                data["resolution"].append(resolution)
    stream.close()
    return data

stream_filename = sys.argv[1]
data = read_stream(stream_filename)

print(data)
            
fig_plots = []


fig_ranges = [
    [0, 500],
    [0, 500],
    [0, 500],
    [0, 180],
    [0, 180],
    [0, 180]
]    


fig_curves = []

for i in range(6):
    fig_curves.append(fig_plots[i].plot())

fig_curves_parameters = {
    "stepMode": "center", 
    "fillLevel": 0,
    "fillOutline": False,
    "brush": (0,0,255,150),
}



for i in range(6):
    values = [data["cell"][i] for data in data.values()]
    
    y,x = np.histogram(values, bins=30, range=fig_ranges[i])
    
    fig_curves[i].setData(x, y/y.max(), **fig_curves_parameters)

plt.show()