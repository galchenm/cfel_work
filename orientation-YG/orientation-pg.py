import numpy as np
import re
import sys
#import pylab
#from mpl_toolkits.mplot3d import Axes3D

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 0.5
w.show()
g = gl.GLGridItem()
w.addItem(g)
w.setWindowTitle('Test')

streamFileName = sys.argv[1]
#streamFileName = "/reg/d/psdm/mfx/mfxlq4815/scratch/natasha/indexing/chip137-139.stream"
markerSize = 0.5 #2
if len(sys.argv) >= 3:
    markerSize = float(sys.argv[2])

f = open(streamFileName, 'r')
stream = f.read()
f.close()



#colors = ["r", "g", "b"]
colors = [(1.0, 0.0, 0.0, 0.5), (0.0, 2.0, 0.0, 3.5), (0.0, 0.0, 4.0, 6.5)]

xStarNames = ["astar","bstar","cstar"]

'''
for i in np.arange(1):
    p = re.compile(xStarNames[i] + " = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
    xStarStrings = p.findall(stream)

    xStars = np.zeros((len(xStarStrings),3), float)

    for j in np.arange(len(xStarStrings)):
        
        xStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])


    sp[i] = gl.GLScatterPlotItem(pos=xStars, color=colors[i], size=markerSize)
    w.addItem(sp[i])
'''
'''
p = re.compile(xStarNames[0] + " = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
xStarStrings = p.findall(stream)
xStars = np.zeros((len(xStarStrings),3), float)
for j in np.arange(len(xStarStrings)):
    xStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])

sp1 = gl.GLScatterPlotItem(pos=xStars, color=colors[0], size=markerSize)
w.addItem(sp1)

p = re.compile(xStarNames[1] + " = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
xStarStrings = p.findall(stream)
xStars = np.zeros((len(xStarStrings),3), float)
for j in np.arange(len(xStarStrings)):
    xStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])

sp2 = gl.GLScatterPlotItem(pos=xStars, color=colors[1], size=markerSize)
w.addItem(sp2)

p = re.compile(xStarNames[2] + " = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
xStarStrings = p.findall(stream)
xStars = np.zeros((len(xStarStrings),3), float)
for j in np.arange(len(xStarStrings)):
    xStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])

sp3 = gl.GLScatterPlotItem(pos=xStars, color=colors[2], size=markerSize)
w.addItem(sp3)

    
'''

colors = ["r", "g", "b"]
colors = [(1.0, 0.0, 0.0, 0.5), (0.0, 1.0, 0.0, 0.5), (0.0, 0.0, 1.0, 0.5)]
xStarNames = ["astar","bstar","cstar"]

p = re.compile(xStarNames[0] + " = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
xStarStrings = p.findall(stream)
print(xStarStrings)

xStars = np.zeros((len(xStarStrings)//2,3), float)
print(xStars)

for j in np.arange(len(xStarStrings)//2):

    xStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])


sp2 = gl.GLScatterPlotItem(pos=xStars, color=colors[2], size=markerSize)
sp2.setGLOptions('opaque')
w.addItem(sp2)


app.exec_()
