from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QTimer
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as cm
import scipy.optimize as opt
import time
import numpy
from beamstopGUI import Ui_Beamstop
import scanThread
class beamstopCentering(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Beamstop()
        self.ui.setupUi(self)
        self.stdErrBar = self.ui.textEditBeamstopCenterLog.verticalScrollBar()
        self.scanActive = False
        self.piezoThread = parent.piezoThread
        self.detectorTowerThread = parent.detectorTowerThread
        self.updateTimer = QtCore.QTimer(self) #This one updates GUI elements at a slow rate 
        self.updateTimer.timeout.connect(self.updateValues)
        self.updateTimer.start(100)
        self.main_frame = QtGui.QWidget()
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        matplotlib.rc('xtick', labelsize=10)
        matplotlib.rc('ytick', labelsize=10)
        self.axes2Dplot = self.fig.add_subplot(131,rasterized=True)
        self.axes2Dplot.set_xlabel('2D flux map')
        self.verticalRefinementValues = numpy.zeros(50)
        self.horizontalRefinementValues = numpy.zeros(50)
        self.axesVerticalRef = self.fig.add_subplot(132,rasterized=True)
        self.axesVerticalRef.set_xlabel('Vertical refinement')
        self.axesHorizontalRef = self.fig.add_subplot(133,rasterized=True)
        self.axesHorizontalRef.set_xlabel('Horizontal refinement')
        self.fig.subplots_adjust(wspace=0.3, hspace=0.3)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.canvas)
        self.main_frame.setLayout(vbox)
        self.ui.horizontalLayout_2Dplot.addWidget(self.main_frame)
        QtCore.QObject.connect(self.ui.pushButtonAutocenterBeamstop, QtCore.SIGNAL("clicked()"), self.autoCenterBeamstop)
        QtCore.QObject.connect(self.ui.pushButtonStopAutocenter, QtCore.SIGNAL("clicked()"), self.abortScan)
        self.ui.pushButtonAutocenterBeamstop.setEnabled(True)
        self.ui.pushButtonStopAutocenter.setEnabled(False)
        self.ui.progressBarScan.setFormat("Idle %p%")
    
    def updateValues(self):
        self.ui.labelBeamstopYposition.setText("%6.1f" %self.piezoThread.currBeamstopY)
        self.ui.labelBeamstopZposition.setText("%6.1f" %self.piezoThread.currBeamstopZ)
        self.ui.doubleSpinBoxCurrentDiodeFlux.setValue(self.detectorTowerThread.diodeVoltage)

    def writeToLog(self,text):
        z = time.localtime() 
        self.stdErrBar.setValue(self.stdErrBar.maximum())
        self.ui.textEditBeamstopCenterLog.append("[%02d:%02d:%02d] " % (z[3], z[4], z[5]) + text)

    def autoCenterBeamstop(self):
        self.writeToLog("Starting autocentering")
        self.motorY = self.piezoThread.proxyPiezoBeamstopY
        self.motorZ = self.piezoThread.proxyPiezoBeamstopZ
        self.startY = self.piezoThread.beamstopYMin
        self.stopY = self.piezoThread.beamstopYMax
        self.stepsY = 10
        self.startZ = self.piezoThread.beamstopZMax
        self.stopZ = self.piezoThread.beamstopZMin
        self.stepsZ = 10
        self.simulation = 0
        self.scanThread = scanThread.ScanThread2D(self.motorY, self.motorZ, self.startZ, self.stepsZ, self.stopZ, self.startY, self.stepsY, self.stopY, self.simulation)
        self.backgroundFigure = numpy.zeros((len(self.scanThread.positionsY),len(self.scanThread.positionsZ)))
        #self.backgroundFigure.fill(0)
        QtCore.QObject.connect(self.scanThread, QtCore.SIGNAL("shot(int)"), self.scan2DUpdate)
        self.scanThread.start()
        self.scanActive = True
        self.ui.pushButtonAutocenterBeamstop.setEnabled(False)
        self.ui.pushButtonStopAutocenter.setEnabled(True)
        self.axesVerticalRef.plot(self.verticalRefinementValues)
        self.updateTimerFigure = QTimer(self) #This one updates GUI elements at a slow rate 
        self.updateTimerFigure.timeout.connect(self.updateFigure2Dscan)
        self.updateTimerFigure.start(1000)
        self.ui.progressBarScan.setFormat("Doing coarse scan...%p%")
    
    def abortScan(self):
        if self.scanThread is not None:
            self.scanThread.stop()
        self.scanActive = False
        self.ui.pushButtonAutocenterBeamstop.setEnabled(True)
        self.ui.pushButtonStopAutocenter.setEnabled(False)
        
    def scan2DUpdate(self,pos):
        if not self.scanActive:
            return
        if not pos:
            return
        pos = pos-1
        time.sleep(0.1)
        voltage = 10-self.detectorTowerThread.diodeVoltage
        row = int(pos/len(self.scanThread.positionsY))
        column = pos % len(self.scanThread.positionsZ)
        if row%2==0: #from left to right
            self.backgroundFigure[row][column] = voltage
        else: #from right to left
            rightToLeftColumn = self.backgroundFigure.shape[1]-1-column
            self.backgroundFigure[row][rightToLeftColumn] = voltage
        self.ui.progressBarScan.setValue(self.scanThread.percentDone)
        if pos+2 > self.scanThread.numOfSteps:
            self.writeToLog("Scan done. Fitting gaussians...")
            self.scanActive = False
            self.scanThread.stop()
            self.updateFigure2Dscan()
            self.updateTimerFigure.stop()
            self.fitGaussian2D()
            return
        
    def updateFigure2Dscan(self):
        #self.axes2Dplot.clear()        
        self.axes2Dplot.matshow(self.backgroundFigure,cmap=cm.jet,vmin=0,vmax=10,extent=[self.startY,self.stopY,self.stopZ,self.startZ],rasterized=True)
        self.axes2Dplot.set_rasterized(True)
        self.canvas.draw()
        
    def updateFigureVerticalScan(self):
        self.axesVerticalRef.cla()
        self.axesVerticalRef.plot(self.scanThread2.positionsZ,self.verticalRefinementValues)
        self.axesVerticalRef.set_xlabel('Vertical refinement')
        self.canvas.draw()
        
    def updateFigureHorizontalScan(self):
        self.axesHorizontalRef.cla()
        self.axesHorizontalRef.plot(self.scanThreadHorizontalRefinement.positionsY,self.horizontalRefinementValues)
        self.axesHorizontalRef.set_xlabel('Horizontal refinement')
        self.canvas.draw()
    
    def fitGaussian2D(self):
        # Average the pixel values along horizontal axis
        pic_avg = self.backgroundFigure.mean(axis=0)
        width = self.backgroundFigure.shape[1]
        height = self.backgroundFigure.shape[0]
        X = numpy.arange(0,width,1)
        projection = pic_avg
        # Set the min value to zero for a nice fit
        projection /= projection.mean()
        projection -= projection.min()
        Y = projection
        Y /= Y.sum()
        # Fit a gaussian
        p0 = [0,width] # Inital guess is a normal distribution
        errfunc = lambda p, x, y: self.gauss(x, p) - y # Distance to the target function
        p1, success = opt.leastsq(errfunc, p0[:], args=(X, Y))
        fit_mu, fit_stdev = p1
        horizontalFWHM = 2*numpy.sqrt(2*numpy.log(2))*fit_stdev
        gaussfit = self.gauss(X,p1)
        horizMax = self.scanThread.positionsY[numpy.argmax(gaussfit)]
        horizMin = self.scanThread.positionsY[numpy.argmin(gaussfit)]
        #self.writeToLog("Horizontal max at %d" % horizMax)
        #self.writeToLog("Horizontal min at %d" % horizMin)
        #plot(X,Y)
        #plot(X, self.gauss(X,p1),lw=3,alpha=.5, color='r')
        #axvspan(fit_mu-horizontalFWHM/2, fit_mu+horizontalFWHM/2, facecolor='g', alpha=0.5)
        #show()
        # Average the pixel values along vertical axis
        pic_avg     = self.backgroundFigure.mean(axis=1)
        #width = self.backgroundFigure.shape[1]
        #height = self.backgroundFigure.shape[0]
        X = numpy.arange(0,height,1)
        projection = pic_avg
        # Set the min value to zero for a nice fit
        projection /= projection.mean()
        projection -= projection.min()
        Y = projection
        Y /= Y.sum()
        # Fit a gaussian
        p0 = [0,height] # Inital guess is a normal distribution
        errfunc = lambda p, x, y: self.gauss(x, p) - y # Distance to the target function
        p1, success = opt.leastsq(errfunc, p0[:], args=(X, Y))
        fit_mu, fit_stdev = p1
        verticalFWHM = 2*numpy.sqrt(2*numpy.log(2))*fit_stdev
        gaussfit = self.gauss(X,p1)
        verticalMax = self.scanThread.positionsZ[numpy.argmax(gaussfit)]
        verticalMin = self.scanThread.positionsZ[numpy.argmin(gaussfit)]
        self.writeToLog("Vertical max at %d" % verticalMax)
        self.writeToLog("Vertical min at %d" % verticalMin)
        #fluxMaximum = self.backgroundFigure[numpy.argmin(self.backgroundFigure)]
        #FIXME
        self.refineScanVertically(horizMax)

    def fitGaussian1D(self,input):
        # Average the pixel values along horizontal axis
        pic_avg = input
        width = len(input)
        X = numpy.arange(0,width,1)
        projection = pic_avg
        # Set the min value to zero for a nice fit
        projection /= projection.mean()
        projection -= projection.min()
        Y = projection
        Y /= Y.sum()
        # Fit a gaussian
        p0 = [0,width] # Inital guess is a normal distribution
        errfunc = lambda p, x, y: self.gauss(x, p) - y # Distance to the target function
        p1, success = opt.leastsq(errfunc, p0[:], args=(X, Y))
        fit_mu, fit_stdev = p1
        horizontalFWHM = 2*numpy.sqrt(2*numpy.log(2))*fit_stdev
        gaussfit = self.gauss(X,p1)
        horizMax = numpy.argmax(gaussfit)
        horizMin = numpy.argmin(gaussfit)
        #horizMax = self.scanThread.positionsY[numpy.argmax(gaussfit)]
        #self.writeToLog("Fit max at %d" % horizMax)
        #self.writeToLog("Fit min at %d" % horizMin)
        return horizMax
        #return horizMin
        
    def refineScanVertically(self,horizontalMax):
        self.writeToLog("Refining scan vertically")
        self.ui.progressBarScan.setFormat("Refining scan vertically...%p%")
        self.startY = horizontalMax
        self.stopY = horizontalMax
        self.stepsY = 1
        #self.startZ = self.piezoThread.proxyPiezoBeamstopZ.read_attribute("SoftLimitMinUnits").value
        #self.stopZ = self.piezoThread.proxyPiezoBeamstopZ.read_attribute("SoftLimitMaxUnits").value
        self.startZ = self.piezoThread.beamstopZMin
        self.stopZ = self.piezoThread.beamstopZMax
        self.stepsZ = 200
        self.scanThread2 = scanThread.ScanThread2D(self.motorY, self.motorZ, self.startZ, self.stepsZ, self.stopZ, self.startY, self.stepsY, self.stopY, self.simulation)
        self.verticalRefinementValues = numpy.zeros(len(self.scanThread2.positionsZ))
        self.scanThread2.start()
        self.scanActive = True
        QtCore.QObject.connect(self.scanThread2, QtCore.SIGNAL("shot(int)"), self.refineScanVerticalUpdate)
        self.updateTimerFigure = QTimer(self) #This one updates GUI elements at a slow rate 
        self.updateTimerFigure.timeout.connect(self.updateFigureVerticalScan)
        self.updateTimerFigure.start(700)

    def refineScanVerticalUpdate(self,pos):
        if not self.scanActive:
            self.writeToLog("scan inactive")
            return
        #pos = self.scanThread.pos
        #self.writeToLog("posRefineVet,%d"%pos)
        if not pos:
            self.writeToLog("Pos is false")
            return
        #print "refineScanVerticalUpdate pos", pos
        if pos >= self.scanThread2.numOfSteps:
            #voltage = abs((10.+(-(25.-pos)**2.)))
            time.sleep(0.1)
            voltage = 10-self.detectorTowerThread.diodeVoltage
            self.verticalRefinementValues[pos-1] = voltage
            self.writeToLog("Vertical refinement scan done. Fitting gaussian...")
            self.scanActive = False
            self.scanThread2.stop()
            self.updateFigureVerticalScan()
            self.updateTimerFigure.stop()
            horizMax = self.fitGaussian1D(self.verticalRefinementValues)
            verticalMax = self.scanThread2.positionsZ[horizMax]
            self.beamVerticalFit = verticalMax 
            self.writeToLog("Vertical fit max at %f um" % verticalMax)
            self.updateTimerFigure.stop()
            self.writeToLog("Performing horizontal refinement scan")
            self.refineScanHorizontally(verticalMax)
            return
        time.sleep(0.1)        
        voltage = 10 -self.detectorTowerThread.diodeVoltage
        self.verticalRefinementValues[pos-1] = voltage
        self.ui.progressBarScan.setValue(self.scanThread2.percentDone)
        
    def refineScanHorizontally(self,verticalMax):
        self.writeToLog("Refining scan horizontally")
        self.ui.progressBarScan.setFormat("Refining scan vertically...%p%")
        self.startY = self.piezoThread.beamstopYMin
        self.stopY = self.piezoThread.beamstopYMax
        self.stepsY = 200
        #self.startZ = self.piezoThread.proxyPiezoBeamstopZ.read_attribute("SoftLimitMinUnits").value
        #self.stopZ = self.piezoThread.proxyPiezoBeamstopZ.read_attribute("SoftLimitMaxUnits").value
        self.startZ = verticalMax
        self.stopZ = verticalMax
        self.stepsZ = 1
        self.scanThreadHorizontalRefinement = scanThread.ScanThread2D(self.motorY, self.motorZ, self.startZ, self.stepsZ, self.stopZ, self.startY, self.stepsY, self.stopY, self.simulation)
        self.horizontalRefinementValues = numpy.zeros(len(self.scanThreadHorizontalRefinement.positionsY))
        self.scanThreadHorizontalRefinement.start()
        self.scanActive = True
        QtCore.QObject.connect(self.scanThreadHorizontalRefinement, QtCore.SIGNAL("shot(int)"), self.refineScanHorizontalUpdate)
        self.updateTimerFigure = QTimer(self) #This one updates GUI elements at a slow rate 
        self.updateTimerFigure.timeout.connect(self.updateFigureHorizontalScan)
        self.updateTimerFigure.start(700)
        
    def refineScanHorizontalUpdate(self,pos):
        if not self.scanActive:
            self.writeToLog("scan inactive")
            return
        if not pos:
            self.writeToLog("Pos is false")
            return
        if pos >= self.scanThreadHorizontalRefinement.numOfSteps:
            time.sleep(0.1)
            voltage = 10-self.detectorTowerThread.diodeVoltage
            self.horizontalRefinementValues[pos-1] = voltage
            self.writeToLog("Horizontal refinement scan done. Fitting gaussian...")
            self.scanActive = False
            self.scanThreadHorizontalRefinement.stop()
            self.updateFigureHorizontalScan()
            self.updateTimerFigure.stop()
            horizMax = self.fitGaussian1D(self.horizontalRefinementValues)
            self.beamHorizontalFit = self.scanThreadHorizontalRefinement.positionsY[horizMax]
            self.writeToLog("Horizontal fit max at %f um" % self.scanThreadHorizontalRefinement.positionsY[horizMax])
            
            self.updateTimerFigure.stop()
            self.ui.progressBarScan.setValue(100)
            self.moveToBeamCenter()
            return
        time.sleep(0.1)
        voltage = 10 -self.detectorTowerThread.diodeVoltage
        self.horizontalRefinementValues[pos-1] = voltage
        self.ui.progressBarScan.setValue(self.scanThreadHorizontalRefinement.percentDone)
        
    def moveToBeamCenter(self):
        self.writeToLog("Moving beamstop to center.")
        self.piezoThread.setBeamstopPositionY(self.beamHorizontalFit)
        self.piezoThread.setBeamstopPositionZ(self.beamVerticalFit)
        while self.piezoThread.stateBeamstop != "ON":
            time.sleep(0.1)
        self.writeToLog("Checking if beam is centered.")
        voltage = self.detectorTowerThread.diodeVoltage
        if voltage < 0.3:
            self.writeToLog("Beam is still on detector. Center manually instead.")
        else:
            self.writeToLog("Passed. Beamstop autocentering successful")
        
    def gauss(self,x, p): # p[0]==mean, p[1]==stdev
        return 1.0/(p[1]*numpy.sqrt(2*numpy.pi))*numpy.exp(-(x-p[0])**2/(2*p[1]**2))
