# -*- coding: utf-8 -*-
import sys
from PyTango import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time
import string
import random
import _thread
import os
from PyQt4.QtCore import SIGNAL, QThread
import configparser
import random
import math
import queue
from simulationDevice import SimulationDevice

class PiezoThread(QThread):

    TYPE_UNKNOWN = 0
    TYPE_OMS_MAX_V = 1
    TYPE_OMS_VME_58 = 2
    TYPE_GALIL_DMC = 3

    # A thread is started by calling QThread.start() never by calling run() directly!
    def __init__(self, deviceservers, pinholePositions, beamstopPosition, screenPositions, pinholeZminimumHeight,simulation = False, parent = None):
        QThread.__init__(self, parent)
        print("Piezo thread: Starting thread")
        self.alive = False
        self.debugMode = 0
        self.simulation = simulation
        #self.stateBeamstop = "ON"
        self.statePinhole = "ON"
        self.stateScreen = "ON"
        self.stateCollimator = "ON"
        self.pinholePositions = pinholePositions
        self.contrastScreenInPlace = False
        self.currentScreenPosition = "Out"
        self.currentYAGScreenPosition = "Out"
        self.currentPinholePosition = 0
        self.currentFilter1Position = 0
        self.currentFilter2Position = 0
        self.currCollimatorY = 0
        self.currCollimatorZ = 0
        self.currBeamstopX = 0
        self.currBeamstopY = 0
        self.currBeamstopZ = 0
        self.beamstopXInOut = "In"
        self.beamstopXMax = 0
        self.beamstopXMin = 0
        self.motorTypeBeamstopX = self.TYPE_UNKNOWN
        self.motorTypeBeamstopY = self.TYPE_UNKNOWN
        self.motorTypeBeamstopZ = self.TYPE_UNKNOWN
        self.motorTypePinholeY = self.TYPE_UNKNOWN
        self.motorTypePinholeZ = self.TYPE_UNKNOWN
        self.motorTypeScreenX = self.TYPE_UNKNOWN
        self.motorTypeScreenZ = self.TYPE_UNKNOWN
        self.motorTypeCollimatorY = self.TYPE_UNKNOWN
        self.motorTypeCollimatorZ = self.TYPE_UNKNOWN
        self.deviceservers = deviceservers
        self.pinholeAboveMinimumZ = False
        self.pinholeZminimumHeight = pinholeZminimumHeight
        self.beamstopInPositionY = self.currBeamstopY 
        self.beamstopInPositionZ = self.currBeamstopZ
        
        self.stateProxyPiezoBeamstopX = "OFF"
        self.stateProxyPiezoBeamstopY = "OFF"
        self.stateProxyPiezoBeamstopZ = "OFF"
        self.stateProxyPiezoPinholeY = "OFF"
        self.stateProxyPiezoPinholeZ = "OFF"
        self.stateProxyPiezoScreenX = "OFF"
        self.stateProxyPiezoScreenZ = "OFF"
        self.stateProxyPiezoCollimatorY = "OFF"
        self.stateProxyPiezoCollimatorZ = "OFF"
        
        if simulation:
            print("Piezo thread in simulation mode")
            self.proxyPiezoBeamstopX = SimulationDevice()
            self.proxyPiezoBeamstopY = SimulationDevice()
            self.proxyPiezoBeamstopZ = SimulationDevice()
            self.proxyPiezoPinholeY = SimulationDevice()
            self.proxyPiezoPinholeZ = SimulationDevice()
            self.proxyPiezoScreenX = SimulationDevice()
            self.proxyPiezoScreenZ = SimulationDevice()
            self.proxyPiezoCollimatorY = SimulationDevice()
            self.proxyPiezoCollimatorZ = SimulationDevice()
            
            self.proxyPiezoBeamstopX.write_attribute("VelocityUnits",3000)
            self.proxyPiezoBeamstopY.write_attribute("VelocityUnits",3000)
            self.proxyPiezoBeamstopZ.write_attribute("VelocityUnits",3000)
            self.proxyPiezoPinholeY.write_attribute("VelocityUnits",3000)
            self.proxyPiezoPinholeZ.write_attribute("VelocityUnits",3000)
            self.proxyPiezoScreenX.write_attribute("VelocityUnits",3000)
            self.proxyPiezoScreenZ.write_attribute("VelocityUnits",3000)
            self.proxyPiezoCollimatorY.write_attribute("VelocityUnits",3000)
            self.proxyPiezoCollimatorZ.write_attribute("VelocityUnits",3000)
            
            self.collimatorInPlace = True
            self.beamstopXMax = 1500
            self.beamstopXMin = -1500
            self.beamstopYMax = 1500
            self.beamstopYMin = -1500
            self.beamstopXMax = 80000
            self.beamstopXMin = 20000
            self.pinholeYMax = 1500
            self.pinholeYMin = -1500
            self.pinholeZMax = 15000
            self.pinholeZMin = -15000
            self.screenXMax = 1500
            self.screenXMin = -1500
            self.screenZMax = 15000
            self.screenZMin = -15000
        
        else:
            print("Piezo thread: started")
            #BeamstopX
            try:
                self.proxyPiezoBeamstopX = DeviceProxy(deviceservers[8])
            except:
                self.alive = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                raise
            if(self.proxyPiezoBeamstopX.info().dev_class == "OmsMaxV"):
                self.motorTypeBeamstopX = self.TYPE_OMS_MAX_V
            elif(self.proxyPiezoBeamstopX.info().dev_class == "GalilDMCMotor"):
                self.motorTypeBeamstopX = self.TYPE_GALIL_DMC
            elif(self.proxyPiezoBeamstopX.info().dev_class == "OmsVme58"):
                self.motorTypeBeamstopX = self.TYPE_OMS_VME_58
            #BeamstopY
            try:
                self.proxyPiezoBeamstopY = DeviceProxy(deviceservers[0])
            except:
                self.alive = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                raise
            if(self.proxyPiezoBeamstopY.info().dev_class == "OmsMaxV"):
                self.motorTypeBeamstopY = self.TYPE_OMS_MAX_V
            elif(self.proxyPiezoBeamstopY.info().dev_class == "GalilDMCMotor"):
                self.motorTypeBeamstopY = self.TYPE_GALIL_DMC
            #BeamstopZ
            try:
                self.proxyPiezoBeamstopZ = DeviceProxy(deviceservers[1])
            except:
                self.alive = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                raise
            if(self.proxyPiezoBeamstopZ.info().dev_class == "OmsMaxV"):
                self.motorTypeBeamstopZ = self.TYPE_OMS_MAX_V
            elif(self.proxyPiezoBeamstopZ.info().dev_class == "GalilDMCMotor"):
                self.motorTypeBeamstopZ = self.TYPE_GALIL_DMC
            #PinholeY
            try:
                self.proxyPiezoPinholeY = DeviceProxy(deviceservers[2])
            except:
                self.alive = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                raise
            if(self.proxyPiezoPinholeY.info().dev_class == "OmsMaxV"):
                self.motorTypePinholeY = self.TYPE_OMS_MAX_V
            elif(self.proxyPiezoPinholeY.info().dev_class == "GalilDMCMotor"):
                self.motorTypePinholeY = self.TYPE_GALIL_DMC
            #PinholeZ
            try:
                self.proxyPiezoPinholeZ = DeviceProxy(deviceservers[3])
            except:
                self.alive = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                raise
            if(self.proxyPiezoPinholeZ.info().dev_class == "OmsMaxV"):
                self.motorTypePinholeZ = self.TYPE_OMS_MAX_V
            elif(self.proxyPiezoPinholeZ.info().dev_class == "GalilDMCMotor"):
                self.motorTypePinholeZ = self.TYPE_GALIL_DMC
            #ScreenX
            try:
                self.proxyPiezoScreenX = DeviceProxy(deviceservers[4])
            except:
                self.alive = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
                raise
            if(self.proxyPiezoScreenX.info().dev_class == "OmsMaxV"):
                self.motorTypeScreenX = self.TYPE_OMS_MAX_V
            elif(self.proxyPiezoScreenX.info().dev_class == "GalilDMCMotor"):
                self.motorTypeScreenX = self.TYPE_GALIL_DMC
            #ScreenZ
            try:
                self.proxyPiezoScreenZ = DeviceProxy(deviceservers[5])
            except:
                self.alive = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                raise
            if(self.proxyPiezoScreenZ.info().dev_class == "OmsMaxV"):
                self.motorTypeScreenZ = self.TYPE_OMS_MAX_V
            elif(self.proxyPiezoScreenZ.info().dev_class == "GalilDMCMotor"):
                self.motorTypeScreenZ = self.TYPE_GALIL_DMC
            #CollimatorY
            try:
                self.proxyPiezoCollimatorY = DeviceProxy(deviceservers[6])
            except:
                self.alive = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                raise
            if(self.proxyPiezoCollimatorY.info().dev_class == "OmsMaxV"):
                self.motorTypeCollimatorY = self.TYPE_OMS_MAX_V
            elif(self.proxyPiezoCollimatorY.info().dev_class == "GalilDMCMotor"):
                self.motorTypeCollimatorY = self.TYPE_GALIL_DMC
            #CollimatorZ
            try:
                self.proxyPiezoCollimatorZ = DeviceProxy(deviceservers[7])
            except:
                self.alive = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                raise
            if(self.proxyPiezoCollimatorZ.info().dev_class == "OmsMaxV"):
                self.motorTypeCollimatorZ = self.TYPE_OMS_MAX_V
            elif(self.proxyPiezoCollimatorZ.info().dev_class == "GalilDMCMotor"):
                self.motorTypeCollimatorZ = self.TYPE_GALIL_DMC

            self.beamstopPosition = beamstopPosition
            try:
                if self.motorTypeBeamstopX == self.TYPE_GALIL_DMC:
                    self.beamstopXMax = self.proxyPiezoBeamstopX.read_attribute("SoftCwLimit").value
                    self.beamstopXMin = self.proxyPiezoBeamstopX.read_attribute("SoftCcwLimit").value
                elif self.motorTypeBeamstopX == self.TYPE_OMS_VME_58:
                    self.beamstopXMax = self.proxyPiezoBeamstopX.read_attribute("UnitLimitMax").value
                    self.beamstopXMin = self.proxyPiezoBeamstopX.read_attribute("UnitLimitMin").value
                elif (self.proxyPiezoBeamstopX.info().dev_class == "VirtualMotors"):
                    self.beamstopXMax = self.proxyPiezoBeamstopX.read_attribute("SoftCwLimit").value
                    self.beamstopXMin = self.proxyPiezoBeamstopX.read_attribute("SoftCcwLimit").value                    
                else:
                    self.beamstopXMax = self.proxyPiezoBeamstopX.read_attribute("SoftLimitMaxUnits").value
                    self.beamstopXMin = self.proxyPiezoBeamstopX.read_attribute("SoftLimitMinUnits").value
                if self.motorTypeBeamstopY == self.TYPE_GALIL_DMC:
                    self.beamstopYMax = self.proxyPiezoBeamstopY.read_attribute("SoftCwLimit").value
                    self.beamstopYMin = self.proxyPiezoBeamstopY.read_attribute("SoftCcwLimit").value
                elif (self.proxyPiezoBeamstopY.info().dev_class == "VirtualMotors"):
                    self.beamstopYMax = self.proxyPiezoBeamstopY.read_attribute("SoftCwLimit").value
                    self.beamstopYMin = self.proxyPiezoBeamstopY.read_attribute("SoftCcwLimit").value                    
                else:
                    self.beamstopYMax = self.proxyPiezoBeamstopY.read_attribute("SoftLimitMaxUnits").value
                    self.beamstopYMin = self.proxyPiezoBeamstopY.read_attribute("SoftLimitMinUnits").value
                if self.motorTypeBeamstopZ == self.TYPE_GALIL_DMC:
                    self.beamstopZMax = self.proxyPiezoBeamstopZ.read_attribute("SoftCwLimit").value
                    self.beamstopZMin = self.proxyPiezoBeamstopZ.read_attribute("SoftCcwLimit").value
                elif (self.proxyPiezoBeamstopZ.info().dev_class == "VirtualMotors"):
                    self.beamstopZMax = self.proxyPiezoBeamstopZ.read_attribute("SoftCwLimit").value
                    self.beamstopZMin = self.proxyPiezoBeamstopZ.read_attribute("SoftCcwLimit").value
                else:
                    self.beamstopZMax = self.proxyPiezoBeamstopZ.read_attribute("SoftLimitMaxUnits").value
                    self.beamstopZMin = self.proxyPiezoBeamstopZ.read_attribute("SoftLimitMinUnits").value
                if self.motorTypeScreenX == self.TYPE_GALIL_DMC:
                    self.screenXMax = self.proxyPiezoScreenX.read_attribute("SoftCwLimit").value
                    self.screenXMin = self.proxyPiezoScreenX.read_attribute("SoftCcwLimit").value
                elif (self.proxyPiezoScreenX.info().dev_class == "VirtualMotors"):
                    self.screenXMax = self.proxyPiezoScreenX.read_attribute("SoftCwLimit").value
                    self.screenXMin = self.proxyPiezoScreenX.read_attribute("SoftCcwLimit").value
                else:
                    self.screenXMax = self.proxyPiezoScreenX.read_attribute("SoftLimitMaxUnits").value
                    self.screenXMin = self.proxyPiezoScreenX.read_attribute("SoftLimitMinUnits").value
                    
                if self.motorTypeScreenZ == self.TYPE_GALIL_DMC:
                    self.screenZMax = self.proxyPiezoScreenZ.read_attribute("SoftCwLimit").value
                    self.screenZMin = self.proxyPiezoScreenZ.read_attribute("SoftCcwLimit").value
                elif (self.proxyPiezoScreenZ.info().dev_class == "VirtualMotors"):
                    self.screenZMax = self.proxyPiezoScreenZ.read_attribute("SoftCwLimit").value
                    self.screenZMin = self.proxyPiezoScreenZ.read_attribute("SoftCcwLimit").value                
                else:
                    self.screenZMax = self.proxyPiezoScreenZ.read_attribute("SoftLimitMaxUnits").value
                    self.screenZMin = self.proxyPiezoScreenZ.read_attribute("SoftLimitMinUnits").value
                    
                if self.motorTypePinholeY == self.TYPE_GALIL_DMC:
                    self.pinholeYMax = self.proxyPiezoPinholeY.read_attribute("SoftCwLimit").value
                    self.pinholeYMin = self.proxyPiezoPinholeY.read_attribute("SoftCcwLimit").value
                elif (self.proxyPiezoPinholeY.info().dev_class == "VirtualMotors"):
                    self.pinholeYMax = self.proxyPiezoPinholeY.read_attribute("SoftCwLimit").value
                    self.pinholeYMin = self.proxyPiezoPinholeY.read_attribute("SoftCcwLimit").value                
                else:
                    self.pinholeYMax = self.proxyPiezoPinholeY.read_attribute("SoftLimitMaxUnits").value
                    self.pinholeYMin = self.proxyPiezoPinholeY.read_attribute("SoftLimitMinUnits").value
                if self.motorTypePinholeZ == self.TYPE_GALIL_DMC:
                    self.pinholeZMax = self.proxyPiezoPinholeZ.read_attribute("SoftCwLimit").value
                    self.pinholeZMin = self.proxyPiezoPinholeZ.read_attribute("SoftCcwLimit").value
                elif (self.proxyPiezoPinholeZ.info().dev_class == "VirtualMotors"):
                    self.pinholeZMax = self.proxyPiezoPinholeZ.read_attribute("SoftCwLimit").value
                    self.pinholeZMin = self.proxyPiezoPinholeZ.read_attribute("SoftCcwLimit").value                
                else:
                    self.pinholeZMax = self.proxyPiezoPinholeZ.read_attribute("SoftLimitMaxUnits").value
                    self.pinholeZMin = self.proxyPiezoPinholeZ.read_attribute("SoftLimitMinUnits").value
            except:
                self.alive = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                raise
        self.YAGInPositionY = screenPositions[0]
        self.YAGInPositionZ = screenPositions[1]
        self.DiodeInPositionY = screenPositions[2]
        self.DiodeInPositionZ = screenPositions[3]
        self.YAGscreenOutPositionY = screenPositions[4]
        self.YAGscreenOutPositionZ = screenPositions[5]
        self.collimatorInPositionY = screenPositions[6]
        self.collimatorInPositionZ = screenPositions[7]
        self.collimatorOutPositionY = screenPositions[8]
        self.collimatorOutPositionZ = screenPositions[9]
        self.beamstopOutPositionX = screenPositions[10]
        self.beamstopInPositionX = screenPositions[11]
        
        self.readAttributes()
        self.alive = True

    def stop(self):
        print("Piezo thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own

    def run(self):
        #print "Piezo thread: started"
        self.alive = True
        while self.alive:
            time.sleep(0.05)
            self.readAttributes()
        # exit position of run function of thread. if exiting == true we end up here
        self.valid = 0
        self.status = "OFFLINE"
        
        print("Piezo thread: Thread for Piezos died")

    def join(self, timeout=None):
        print("Piezo thread: join method")
        self.alive = False

    def readAttributes(self):
        try:
            # There is sometimes exception in this block. 
            # then the program stops and we must search reason. 
            # to facilitate the search, the variable ReadFromDevice 
            # is added. 
            # In case of exception, the variable will contain the name of tango device, where  
            # exception appeared. 
            
            #ReadFromDevice = self.proxyPiezoBeamstopX.adm_name()
            # it was initially done via: self.proxyPiezoBeamstopX.adm_name() function, but it 
            # is additional possibly source of exceptopns therefore:
            ReadFromDevice = " proxyPiezoBeamstopX "                                     
            self.stateProxyPiezoBeamstopX = str(self.proxyPiezoBeamstopX.state())
            
            ReadFromDevice = "proxyPiezoBeamstopY "            
            self.stateProxyPiezoBeamstopY = str(self.proxyPiezoBeamstopY.state())
            
            ReadFromDevice = "proxyPiezoBeamstopZ "
            self.stateProxyPiezoBeamstopZ = str(self.proxyPiezoBeamstopZ.state())
            
            ReadFromDevice = "proxyPiezoPinholeY "
            self.stateProxyPiezoPinholeY = str(self.proxyPiezoPinholeY.state())
            
            ReadFromDevice = "proxyPiezoPinholeZ "
            self.stateProxyPiezoPinholeZ = str(self.proxyPiezoPinholeZ.state())
            
            ReadFromDevice = "proxyPiezoScreenX "
            self.stateProxyPiezoScreenX = str(self.proxyPiezoScreenX.state())

            ReadFromDevice = "proxyPiezoScreenZ "
            self.stateProxyPiezoScreenZ = str(self.proxyPiezoScreenZ.state())
            
            ReadFromDevice = "proxyPiezoCollimatorY "
            self.stateProxyPiezoCollimatorY = str(self.proxyPiezoCollimatorY.state())
            
            ReadFromDevice = "proxyPiezoCollimatorZ "
            self.stateProxyPiezoCollimatorZ = str(self.proxyPiezoCollimatorZ.state())
            
            ReadFromDevice = "proxyPiezoCollimatorY "
            self.currCollimatorY = self.proxyPiezoCollimatorY.read_attribute("Position").value
            
            ReadFromDevice = "proxyPiezoCollimatorZ "
            self.currCollimatorZ = self.proxyPiezoCollimatorZ.read_attribute("Position").value
            
            ReadFromDevice = "proxyPiezoPinholeY "
            self.currPinholeY = self.proxyPiezoPinholeY.read_attribute("Position").value
            
            ReadFromDevice = "proxyPiezoPinholeZ "
            self.currPinholeZ = self.proxyPiezoPinholeZ.read_attribute("Position").value
            
            ReadFromDevice = "proxyPiezoBeamstopX "
            self.currBeamstopX = self.proxyPiezoBeamstopX.read_attribute("Position").value
            
            ReadFromDevice = "proxyPiezoBeamstopY "
            self.currBeamstopY = self.proxyPiezoBeamstopY.read_attribute("Position").value
            
            ReadFromDevice = "proxyPiezoBeamstopZ "
            self.currBeamstopZ = self.proxyPiezoBeamstopZ.read_attribute("Position").value

            ReadFromDevice = "proxyPiezoScreenX"            
            self.currScreenX = self.proxyPiezoScreenX.read_attribute("Position").value
            
            ReadFromDevice = "proxyPiezoScreenZ"
            self.currScreenZ = self.proxyPiezoScreenZ.read_attribute("Position").value

            if (abs(self.currBeamstopX-self.beamstopInPositionX) > 500):
                self.beamstopXInOut = "Out"
            else:
                self.beamstopXInOut = "In"
            
            if self.currCollimatorY < (self.collimatorInPositionY+5) and self.currCollimatorY > (self.collimatorInPositionY-5) and self.currCollimatorZ < (self.collimatorInPositionZ+5) and self.currCollimatorZ > (self.collimatorInPositionZ-5):
                self.collimatorInPlace = True
            else:
                self.collimatorInPlace = False
            
            if self.currScreenZ < (self.YAGscreenOutPositionZ+100):
                self.currentYAGScreenPosition = "Out"
            else:
                self.currentYAGScreenPosition = "In"

            pinholeFound = False
            pinholeNrFound = 0
            for i in range(len(self.pinholePositions)):
                if self.currPinholeY < (self.pinholePositions[i][0]+5) and self.currPinholeY > (self.pinholePositions[i][0]-5) and self.currPinholeZ < (self.pinholePositions[i][1]+5) and self.currPinholeZ > (self.pinholePositions[i][1]-5):
                    pinholeNrFound = i
                    pinholeFound = True
            if pinholeFound:
                self.currentPinholePosition = pinholeNrFound
            else:
                self.currentPinholePosition = -1
            
            if self.stateProxyPiezoBeamstopY == "MOVING" or self.stateProxyPiezoBeamstopZ == "MOVING":
                self.stateBeamstop = "MOVING"
            else:
                self.stateBeamstop = "ON"
            
            if self.stateProxyPiezoPinholeY == "MOVING" or self.stateProxyPiezoPinholeZ == "MOVING":
                self.statePinhole = "MOVING"
            else:
                self.statePinhole = "ON"
            
            if self.currPinholeZ > float(self.pinholeZminimumHeight):
                self.pinholeAboveMinimumZ = True
            else:
                self.pinholeAboveMinimumZ = False
            
            if  self.stateProxyPiezoScreenX == "MOVING" or self.stateProxyPiezoScreenZ == "MOVING":
                self.stateScreen = "MOVING"
            else:
                self.stateScreen = "ON"
                
            if  self.stateProxyPiezoCollimatorY == "MOVING" or self.stateProxyPiezoCollimatorZ == "MOVING":
                self.stateCollimator = "MOVING"
            else:
                self.stateCollimator = "ON"
                
        except:
            print((" Exception appeared during read from device: ", ReadFromDevice))
            print((sys.exc_info()))
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setPinhole(self,arg):
        arg = int(arg)
        if self.debugMode: print("Piezo thread: setPinhole(), arg:", arg)
        try:
            self.proxyPiezoPinholeY.write_attribute("Position", self.pinholePositions[arg][0])  
            self.proxyPiezoPinholeZ.write_attribute("Position", self.pinholePositions[arg][1])
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            
    def moveBeamStopOut(self):
        if self.debugMode: print("Piezo thread: moveBeamStopOut(), arg:", arg)
        try:
            self.proxyPiezoBeamstopX.write_attribute("Position", self.beamstopOutPositionX)  
            
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            
    def moveBeamStopIn(self):
        if self.debugMode: print("Piezo thread: moveBeamStopIn(), arg:", arg)
        try:
            self.proxyPiezoBeamstopX.write_attribute("Position", self.beamstopInPositionX)  
            
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            
    def setBeamstopPositionX(self,arg):
        if self.debugMode: print("Piezo thread: setBeamstopPositionX(), arg:", arg)
        try:
            self.proxyPiezoBeamstopX.write_attribute("Position", arg)  
            
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            
    def setBeamstopPositionY(self,arg):
        if self.debugMode: print("Piezo thread: setBeamstopPositionY(), arg:", arg)
        try:
            self.proxyPiezoBeamstopY.write_attribute("Position", arg)  
            
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setBeamstopPositionZ(self,arg):
        if self.debugMode: print("Piezo thread: setBeamstopPositionZ(), arg:", arg)
        try:
            self.proxyPiezoBeamstopZ.write_attribute("Position", arg)
                  
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setBeamstopDirectBeam(self):
        self.beamstopInPositionY = self.currBeamstopY 
        self.beamstopInPositionZ = self.currBeamstopZ
        try:
            self.proxyPiezoBeamstopY.write_attribute("Position", self.beamstopYMax)
            self.proxyPiezoBeamstopZ.write_attribute("Position", self.beamstopZMax)
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            
    def unsetBeamstopDirectBeam(self):
        try:
            self.proxyPiezoBeamstopY.write_attribute("Position", self.beamstopInPositionY)
            self.proxyPiezoBeamstopZ.write_attribute("Position", self.beamstopInPositionZ)
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
        
            
        
    def stopBeamstop(self):
        if self.debugMode: print("Piezo thread: stopBeamstop()")
        try:
            if self.motorTypeBeamstopX == self.TYPE_GALIL_DMC:
                self.proxyPiezoBeamstopX.command_inout("Stop")
            elif self.motorTypeBeamstopX == self.TYPE_OMS_VME_58:
                self.proxyPiezoBeamstopX.command_inout("StopMove")
            else:
                self.proxyPiezoBeamstopX.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
        try:
            if self.motorTypeBeamstopY == self.TYPE_GALIL_DMC:
                self.proxyPiezoBeamstopY.command_inout("Stop")
            else:
                self.proxyPiezoBeamstopY.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
        try:
            if self.motorTypeBeamstopZ == self.TYPE_GALIL_DMC:
                self.proxyPiezoBeamstopZ.command_inout("Stop")
            else:
                self.proxyPiezoBeamstopZ.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
        moving = True
        while moving:
            try:
                statePiezoX = str(self.proxyPiezoBeamstopX.state())
            except:
                moving = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            try:
                statePiezoY = str(self.proxyPiezoBeamstopY.state())
            except:
                moving = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            try:
                statePiezoZ = str(self.proxyPiezoBeamstopZ.state())
            except:
                moving = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            if statePiezoX == "MOVING" or statePiezoY == "MOVING" or statePiezoZ == "MOVING":
                moving = True
            else:
                moving = False
                
    def setPinholePositionY(self,arg):
        if self.debugMode: print("Piezo thread: setPinholePositionY(), arg:", arg)
        try:
            self.proxyPiezoPinholeY.write_attribute("Position", arg)  
            
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setPinholePositionZ(self,arg):
        if self.debugMode: print("Piezo thread: setPinholePositionZ(), arg:", arg)
        try:
            self.proxyPiezoPinholeZ.write_attribute("Position", arg)
              
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
    
    def stopPinhole(self):
        if self.debugMode: print("Piezo thread: stopPinhole()")
        try:
            if self.motorTypePinholeY == self.TYPE_GALIL_DMC:
                self.proxyPiezoPinholeY.command_inout("Stop")
            else:
                self.proxyPiezoPinholeY.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
        try:
            if self.motorTypePinholeZ == self.TYPE_GALIL_DMC:
                self.proxyPiezoPinholeZ.command_inout("Stop")
            else:
                self.proxyPiezoPinholeZ.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
        moving = True
        while moving:
            try:
                statePiezoY = str(self.proxyPiezoPinholeY.state())
            except:
                moving = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            try:
                statePiezoZ = str(self.proxyPiezoPinholeZ.state())
            except:
                moving = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            if statePiezoY == "MOVING" or statePiezoZ == "MOVING":
                moving = True
            else:
                moving = False

    def setScreenFocus(self,arg):
        if self.debugMode: print("Piezo thread: setScreenFocus(), arg:",arg)
        try:
            self.proxyPiezoScreenX.write_attribute("Position", arg)
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            return

    def yagIn(self):
        if self.debugMode: print("Piezo thread: screenIn()")
        try:
            #self.proxyPiezoScreenX.write_attribute("Position", self.YAGInPositionX)
            #FIXME: this stage doesnt work currently
            self.proxyPiezoScreenZ.write_attribute("Position", self.YAGInPositionZ)
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            return
        self.currentScreenPosition = "YAGIn"

    def diodeIn(self):
        if self.debugMode: print("Piezo thread: screenIn()")
        try:
            #self.proxyPiezoScreenX.write_attribute("Position", self.DiodeInPositionX)
            #FIXME: this stage doesnt work currently
            self.proxyPiezoScreenZ.write_attribute("Position", self.DiodeInPositionZ)
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            return
        self.currentScreenPosition = "DiodeIn"

    def screenOut(self):
        if self.debugMode: print("Piezo thread: screenOut()")
        try:
            #self.proxyPiezoScreenX.write_attribute("Position", self.YAGscreenOutPositionY)
            #FIXME: this stage doesnt work currently
            self.proxyPiezoScreenZ.write_attribute("Position", self.YAGscreenOutPositionZ)
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            return
        self.currentScreenPosition = "Out"

    def stopScreen(self):
        if self.debugMode: print("Piezo thread: stopScreen()")
        try:
            if self.motorTypeScreenX == self.TYPE_GALIL_DMC:
                self.proxyPiezoScreenX.command_inout("Stop")
            else:
                self.proxyPiezoScreenX.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
        try:
            if self.motorTypeScreenZ == self.TYPE_GALIL_DMC:
                self.proxyPiezoScreenZ.command_inout("Stop")
            else:
                self.proxyPiezoScreenZ.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
        moving = True
        while moving:
            try:
                statePiezoX = str(self.proxyPiezoScreenX.state())
            except:
                moving = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
            try:
                statePiezoZ = str(self.proxyPiezoScreenZ.state())
            except:
                moving = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            if statePiezoX == "MOVING" or statePiezoZ == "MOVING":
                moving = True
            else:
                moving = False
    
    def collimatorIn(self):
        if self.debugMode: print("Piezo thread: collimatorIn()")
        try:
            self.proxyPiezoCollimatorY.write_attribute("Position", self.collimatorInPositionY)
            self.proxyPiezoCollimatorZ.write_attribute("Position", self.collimatorInPositionZ)
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            return
        self.currentCollimatorPosition = "In"

    def collimatorOut(self):
        if self.debugMode: print("Piezo thread: collimatorOut()")
        try:
            self.proxyPiezoCollimatorY.write_attribute("Position", self.collimatorOutPositionY)
            self.proxyPiezoCollimatorZ.write_attribute("Position", self.collimatorOutPositionZ)
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            return
        self.currentCollimatorPosition = "Out"

    def stopCollimator(self):
        if self.debugMode: print("Piezo thread: stopScreen()")
        try:
            if self.motorTypeCollimatorY == self.TYPE_GALIL_DMC:
                self.proxyPiezoCollimatorY.command_inout("Stop")
            else:
                self.proxyPiezoCollimatorY.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
        try:
            if self.motorTypeCollimatorZ == self.TYPE_GALIL_DMC:
                self.proxyPiezoCollimatorZ.command_inout("Stop")
            else:
                self.proxyPiezoCollimatorZ.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
        moving = True
        while moving:
            try:
                statePiezoY = str(self.proxyPiezoCollimatorY.state())
            except:
                moving = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                break
            try:
                statePiezoZ = str(self.proxyPiezoCollimatorZ.state())
            except:
                moving = False
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                break
            if statePiezoY == "MOVING" or statePiezoZ == "MOVING":
                moving = True
            else:
                moving = False
    
    def setCollimatorPositionY(self,arg):
        if self.debugMode: print("Piezo thread: setCollimatorY(), arg:", arg)
        try:
            self.proxyPiezoCollimatorY.write_attribute("Position", arg)  
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            
    def setCollimatorPositionZ(self,arg):
        if self.debugMode: print("Piezo thread: setCollimatorZ(), arg:", arg)
        try:
            self.proxyPiezoCollimatorZ.write_attribute("Position", arg)  
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            

