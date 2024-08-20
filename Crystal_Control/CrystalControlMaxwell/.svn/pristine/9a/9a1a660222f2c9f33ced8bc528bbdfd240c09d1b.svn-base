# -*- coding: utf-8 -*-
try:    
    from PyTango import DeviceProxy, DevFailed
except:
    pass
from PyQt4.QtCore import SIGNAL, QThread, QTimer
from PyQt4.QtGui import QApplication
import time
import numpy
import datetime
import math
import sys
'''
            eCol [C] 
            epsilon [eV]
            RhoSi [g/cm^3]
            RhoAir [g/cm^3]
            RhoAlu [g/cm^3]
            ThicknessSi [um]
            ThicknessAlu [um]
            ThicknessAir [mm]
            I_Measure [A]
            Energy [keV]
'''
class photonThread(QThread):           
    def __init__(self, devPathADC, devPathVFC, devPathTimer, devPathMono, sampleTime, plotDuration, gain, thickness, bunches, mod, simulation = False):
            QThread.__init__(self) 
            self.devPathADC = devPathADC
            self.devPathVFC = devPathVFC
            self.devPathTimer = devPathTimer
            self.devPathMono = devPathMono
            self.exiting = False
            self.mod = mod
            self.sampleTime = sampleTime
            self.plotDuration = plotDuration
            self.connected = 1
            self.Energy = 0
            self.lastMeasure = None
            self.plotActive = False
            self.Gain = gain#arg = self.ui.spinBoxDataCollectionImageFileNumber.value()
            self.Photons = 0
            self.I_Measure = 0 
            self.NumberOfBunches = bunches
            self.eCol = 1.6021765314e-19 
            self.epsilon = 3.66 
            self.RhoSi = 2.336 
            self.RhoAir = 1.205*10**-3 
            self.RhoAlu = 2.7 
            self.ThicknessSi = thickness 
            self.ThicknessAlu = 0 
            self.ThicknessAir = 0
            self.simulation = simulation
            if not simulation: 
                try: 
                    self.devTimer = DeviceProxy(self.devPathTimer)
                except:
                    print("Can't connect to devTimer", sys.exc_info())
                    self.connected = 0
                try:
                    self.Mono = DeviceProxy(self.devPathMono)
                except:
                    print("Can't connect to Monochromator")
                    self.connected = 0
                if self.mod:
                    try: 
                        self.devVFC = DeviceProxy(self.devPathVFC)
                    except:
                        print("Can't connect to VFC")
                        self.connected = 0
                elif not self.mod:
                    try: 
                        self.devADC = DeviceProxy(self.devPathADC)
                    except:
                        print("Can't connect to ADC")
                        self.connected = 0
            else:
                print("Photon thread in simulation mode")
                self.Photons = 6666
                self.connected = 1
            if self.connected and not self.simulation:
                self.startTimeOfPlot = datetime.datetime.now()
                self.getValues()
                self.resetPlot()
            else:
                self.emit(SIGNAL("notConnected()"))
    def run(self):
        self.exiting = False
        while self.exiting == False:
            if not self.simulation:
                self.getValues()
                if self.plotActive:
                    self.updatePlot()
                if not self.mod:
                    time.sleep(self.sampleTime)
            else:    
                time.sleep(1)
            self.emit(SIGNAL("update()"))
    
            QApplication.processEvents()

    def stop(self):
        print("Stopping thread")
        self.exiting = True
        self.wait()

    def setBunches(self, value):
        if self.connected:
            self.NumberOfBunches = value
                
    def getValues(self):
        if self.connected:
            if self.mod:
                self.devTimer.write_attribute("SampleTime", self.sampleTime)
                self.devVFC.command_inout("Reset")
                self.devTimer.command_inout("Start")
    
                while self.devTimer.command_inout("Check"):
                    time.sleep(0.1)
                self.I_Measure = self.devVFC.read_attribute("Value").value
                self.lastMeasure = datetime.datetime.now()
            elif not self.mod:
                self.I_Measure = self.devADC.read_attribute("Value").value
                self.lastMeasure = datetime.datetime.now()
           
            try: 
                self.Energy = self.Mono.read_attribute("Position").value/1000
            except:
                self.Energy = self.Energy
            
            if self.Energy > 0:
                self.I = self.I_Measure*10**(-self.Gain)
                PhotoElectricCrossSi = 10**((4.158 - 2.238*math.log10(self.Energy) - 0.477*(math.log10(self.Energy))**2+0.0789*(math.log10(self.Energy))**3))
                Exponent = -PhotoElectricCrossSi*(self.ThicknessSi/10000.0)*self.RhoSi
                try:
                    self.Photons = self.I*self.epsilon/(self.eCol*1000*self.Energy*(1-math.exp(Exponent)))
                except:
                    self.Photons = 0
                if self.ThicknessAlu != 0:                
                    PhotoElectricCrossAlu = 10**((4.04910345 - 2.18663049*math.log10(self.Energy) - 0.55272731*(math.log10(self.Energy))**2+0.10084739*(math.log10(self.Energy))**3))
                    ExponentAlu =  -PhotoElectricCrossAlu*(self.ThicknessAlu/10000.0)*self.RhoAlu
                    self.Photons = self.Photons/math.exp(ExponentAlu)
                
                if self.ThicknessAir != 0:                
                    PhotoElectricCrossAir = 10**((3.38154401 -1.6461732*math.log10(self.Energy) -1.87482661*(math.log10(self.Energy))**2+0.83996503*(math.log10(self.Energy))**3))
                    ExponentAir =  -PhotoElectricCrossAir*(self.ThicknessAir/10.0)*self.RhoAir
                    self.Photons = self.Photons/math.exp(ExponentAir)                
            
                self.BunchPhotons = self.Photons/(self.NumberOfBunches*130200.0)
            else:
                self.Photons = 0
                self.BunchPhotons = 0

    def setGain(self, value):
        if self.connected:
            self.Gain = value
            
    def setThicknessSi(self, value):
        if self.connected:
            self.ThicknessSi = value 
               
    def setThicknessAlu(self, value):
        if self.connected:
            self.ThicknessAlu = value 
            
    def setThicknessAir(self, value):
        if self.connected:
            self.ThicknessAir = value
            
    def startPlot(self):
        if self.connected:
            self.plotActive = True

    def stopPlot(self):
        if self.connected:
            self.plotActive = False

    def setPlotDuration(self, duration):
        if self.connected:
            self.plotDuration = duration
            self.resetPlot()
            self.startTimeOfPlot = datetime.datetime.now()

    def setSampleTime(self, sampleTime):
        if self.connected:
            self.sampleTime = sampleTime
            self.resetPlot()
            self.startTimeOfPlot = datetime.datetime.now()
            
    def resetPlot(self):
        if self.connected:
            self.plotTime = numpy.arange(-self.plotDuration, 0.0, self.sampleTime)
            self.plotPhotons = numpy.zeros(len(self.plotTime), numpy.float)
            self.plotPhotons[:] = self.Photons
            self.plotBunchPhotons = numpy.zeros(len(self.plotTime), numpy.float)
            self.plotBunchPhotons[:] = self.BunchPhotons
            
    def updatePlot(self):
        if self.connected:
            deltatime = self.lastMeasure - self.startTimeOfPlot
            newtime = float(deltatime.seconds) + float(float(deltatime.microseconds)/1e6)
            self.plotTime = numpy.concatenate((self.plotTime[1:], self.plotTime[:1]), 1)
            self.plotTime[-1] = newtime
            self.plotPhotons = numpy.concatenate((self.plotPhotons[1:], self.plotPhotons[:1]), 1)
            self.plotPhotons[-1] = float(self.Photons)
            self.plotBunchPhotons = numpy.concatenate((self.plotBunchPhotons[1:], self.plotBunchPhotons[:1]), 1)
            self.plotBunchPhotons[-1] = float(self.BunchPhotons)
            
if __name__ == "__main__":
    myphoton = photonThread()
