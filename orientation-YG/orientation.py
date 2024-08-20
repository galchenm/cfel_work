import numpy as np
import re
import sys
import pylab
from mpl_toolkits.mplot3d import Axes3D



streamFileName = sys.argv[1]
#streamFileName = "/reg/d/psdm/mfx/mfxlq4815/scratch/natasha/indexing/chip137-139.stream"
markerSize = 0.5 #2
if len(sys.argv) >= 3:
    markerSize = float(sys.argv[2])

f = open(streamFileName, 'r')
stream = f.read()
f.close()


pylab.ion()
collectedAxes = Axes3D(pylab.figure())
pylab.title("all together")

colors = ["r", "g", "b"]
xStarNames = ["astar","bstar","cstar"]
for i in np.arange(3):
    p = re.compile(xStarNames[i] + " = ([\+\-\d\.]* [\+\-\d\.]* [\+\-\d\.]*)")
    xStarStrings = p.findall(stream)
    #print(xStarStrings)
    xStars = np.zeros((3, len(xStarStrings)), float)
    #print(xStars)
    for j in np.arange(len(xStarStrings)):
        xStars[:,j] = np.array([float(s) for s in xStarStrings[j].split(' ')])

    pylab.ion()
    ax = Axes3D(pylab.figure())
    ax.scatter(xStars[0,:],xStars[1,:],xStars[2,:], marker=".", color=colors[i], s=markerSize)
    pylab.title(xStarNames[i] + "s")

    collectedAxes.scatter(xStars[0,:],xStars[1,:],xStars[2,:], marker=".", color=colors[i], s=markerSize)
    



input("Press Enter to continue...")
i = 0


