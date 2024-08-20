from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import re

streamFileName = '/gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/orientation-YG/xg-20210916_6845-20210916_6846-lyso9-199p6mm.stream'
markerSize = 0.5
f = open(streamFileName, 'r')
stream = f.read()
f.close()

colors = [(1.0, 0.0, 0.0, 0.5), (0.0, 2.0, 0.0, 3.5), (0.0, 0.0, 4.0, 6.5)]
xStarNames = ["astar","bstar","cstar"]




app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="A 3d plot window")

#p1 = pg.PlotWidget()

glvw1 = gl.GLViewWidget()
glvw1.opts['distance'] = 0.4

ax = gl.GLAxisItem()
ax.setSize(10, 10, 10)
glvw1.addItem(ax)

glvw1.setWindowTitle('a*')
p = re.compile("astar = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
xStarStrings = p.findall(stream)
aStars = np.zeros((len(xStarStrings),3), float)
for j in np.arange(len(xStarStrings)):
    aStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])

print('I am here')
#z = pg.gaussianFilter(np.random.normal(size=(50,50)), (1,1))
p1 = gl.GLScatterPlotItem(pos=aStars, color=colors[0], size=markerSize)
glvw1.addItem(p1)


# try adding a 3d plot

glvw = gl.GLViewWidget()
glvw.opts['distance'] = 0.4
glvw.setWindowTitle('b*')
glvw.addItem(ax)
#z = pg.gaussianFilter(np.random.normal(size=(50,50)), (1,1))
p = re.compile("bstar = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
xStarStrings = p.findall(stream)
bStars = np.zeros((len(xStarStrings),3), float)
for j in np.arange(len(xStarStrings)):
    bStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])

p13d = gl.GLScatterPlotItem(pos=bStars, color=colors[1], size=markerSize) #gl.GLSurfacePlotItem(z=z, shader='shaded', color=(0.5, 0.5, 1, 1))
glvw.addItem(p13d)


print('I am here 2')
# try adding a 3d plot
p = re.compile("bstar = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
xStarStrings = p.findall(stream)
cStars = np.zeros((len(xStarStrings),3), float)
for j in np.arange(len(xStarStrings)):
    cStars[j,:] = np.array([float(s) for s in xStarStrings[j].split(' ')])
    
glvw2 = gl.GLViewWidget()
glvw2.opts['distance'] = 0.4
glvw2.setWindowTitle('c*')
glvw2.addItem(ax)
#z = pg.gaussianFilter(np.random.normal(size=(50,50)), (1,1))
p23d = gl.GLScatterPlotItem(pos=cStars, color=colors[2], size=markerSize)
print(aStars.shape)
glvw2.addItem(p23d)

print('I am here 3')

# get a layout
layoutgb = QtGui.QGridLayout()
win.setLayout(layoutgb)

layoutgb.addWidget(glvw, 0, 0)
layoutgb.addWidget(glvw1, 0, 1)  
layoutgb.addWidget(glvw2, 0, 2)
### uncommenting this line causes 
       # the plot widget to appear and the 3d widget to disappear

glvw1.sizeHint = lambda: pg.QtCore.QSize(500, 500)
glvw.sizeHint = lambda: pg.QtCore.QSize(500, 500)
glvw2.sizeHint = lambda: pg.QtCore.QSize(500, 500)
glvw.setSizePolicy(glvw1.sizePolicy())
glvw.setSizePolicy(glvw2.sizePolicy())

QtGui.QApplication.instance().exec_()