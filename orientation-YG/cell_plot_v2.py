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
    data = {"cell": [], "resolution": []}
    indexed = False
    
    with open(filename, "r") as stream:
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
    return data

if len(sys.argv) < 2:
    print("Usage: python script.py <stream_filename>")
    sys.exit(1)

stream_filename = sys.argv[1]
data = read_stream(stream_filename)

print(data)

app = pg.mkQApp()

fig_plots = []

for _ in range(6):
    fig_plots.append(pg.plot())

fig_ranges = [
    [0, 500],
    [0, 500],
    [0, 500],
    [0, 180],
    [0, 180],
    [0, 180]
]    

fig_curves_parameters = {
    "stepMode": "center", 
    "fillLevel": 0,
    "fillOutline": False,
    "brush": (0, 0, 255, 150),
}

for i in range(6):
    values = [cell[i] for cell in data["cell"]]
    y, x = np.histogram(values, bins=30, range=fig_ranges[i])
    fig_plots[i].plot(x, y / y.max(), **fig_curves_parameters)

# Save figures as image files
for i, plot in enumerate(fig_plots):
    export_path = f"figure_{i}.png"
    plot.export(export_path)

if sys.flags.interactive != 1 or not hasattr(pg.QtCore, 'PYQT_VERSION'):
    pg.QtGui.QApplication.exec_()
