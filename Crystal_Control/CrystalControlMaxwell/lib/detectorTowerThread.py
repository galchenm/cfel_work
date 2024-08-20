# -*- coding: utf-8 -*-
import sys
from PyTango import *
from PyQt4 import QtCore, QtGui
import time
import string
import random
import os
from PyQt4.QtCore import SIGNAL, QThread
import configparser
import random
import math
import queue
from simulationDevice import SimulationDevice

class DetectorTower(QThread):
    proxy = 0
    device = 0
    status = 0    
    
    # A thread is started by calling QThread.start() never by calling run() directly!
    def __init__(self, deviceserver,detectorManualMountPosition, k,m, parent = None, simulation = False):
        QThread.__init__(self, parent)
        #self.MainWindow = mainwindowPassing
        print("Detector tower thread: Starting thread")

        self.alive = True
        self.simulationMode = simulation
        self.debugMode = 0
        self.corrK = k
        self.corrM = m
        self.deviceserver = deviceserver
        self.detectorManualMountPosition = detectorManualMountPosition
        self.currentPositionDetectorTowerServer = 100
        self.statusInterlock = 0
        self.stateDetectorTower = "OFF"
        self.diodeThresholdOK = False
        self.diodeVoltage = 0.0
        self.lubricationOK = 0
        self.shieldIsUp = True
        self.shieldIsDown = False
        self.interlockWasBroken = True
        if self.simulationMode:
            print("Detector tower in simulation mode")
            self.proxyDetectorTower =  SimulationDevice()
            
            self.stateDetectorTower = "ON"
            
            self.statusFastShutter = False
            self.currentPositionDetectorTowerServer = 1000
            self.currentLaserPositionDetectorTowerServer = 1000
            self.shieldIsUp = True
            self.shieldIsDown = False
            self.statusInterlock = True
            self.minPositionDetectorTowerServer = 154
            self.maxPositionDetectorTowerServer = 2000
            self.lubricationOK = 1
            self.diodeThresholdOK = True
            
        else:
            try:
                self.proxyDetectorTower = DeviceProxy(self.deviceserver)
                self.proxyDetectorTower.ping()
                self.minPositionDetectorTowerServer = self.proxyDetectorTower.read_attribute("DetectorDistanceMin").value
                self.maxPositionDetectorTowerServer = self.proxyDetectorTower.read_attribute("DetectorDistanceMax").value
                self.lubricationOK = self.proxyDetectorTower.read_attribute("LubricationSensorOK").value
            except:
                print("Deviceservers not running")
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
                self.alive = False
                self.connected = 0

    def stop(self):
        print("Detector tower thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own
        
    def run(self):
        print("Detector tower thread: started")
        self.connected = 1
        while self.alive:
            if not self.simulationMode:
                time.sleep(0.1)
            
                try:
                   
                    self.stateDetectorTower = str(self.proxyDetectorTower.state())
                    self.currentPositionDetectorTowerServer = self.proxyDetectorTower.read_attribute("DetectorDistance").value
                    self.currentLaserPositionDetectorTowerServer = self.proxyDetectorTower.read_attribute("DetectorDistanceLaser").value
                    self.diodeThresholdOK = self.proxyDetectorTower.read_attribute("DiodeFluxBelowThreshold").value
                    
                    if self.proxyDetectorTower.read_attribute("ShieldIsUp").value and not self.proxyDetectorTower.read_attribute("ShieldIsDown").value:
                        self.shieldIsUp = True
                        self.shieldIsDown = False
                    elif self.proxyDetectorTower.read_attribute("ShieldIsDown").value and not self.proxyDetectorTower.read_attribute("ShieldIsUp").value:
                        self.shieldIsUp = False
                        self.shieldIsDown = True
                    else:
                        self.shieldIsUp = False
                        self.shieldIsDown = False
                    
                    self.statusInterlock = self.proxyDetectorTower.read_attribute("InterlockSet").value
                    if not self.statusInterlock:
                        self.interlockWasBroken = True
                    #self.statusInterlock = 1
                    self.diodeVoltage = self.proxyDetectorTower.read_attribute("DiodeVoltage").value
                    
                except:
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
                    print(sys.exc_info())
            else:
            #    self.diodeVoltage = self.proxyDetectorTower.read_attribute("DiodeVoltageSimulation").value
                time.sleep(0.1)
            
        # exit position of run function of thread. if exiting == true we end up here
        self.valid = 0
        self.status = "OFFLINE"
        self.connected = 0
        print("Detector tower thread: Thread for Detector tower died")
    
    def join(self, timeout=None):
        print("Detector tower thread: join method")
        self.alive = False

    def setPositionDetectorTower(self,arg):
        if self.debugMode: print("Detector tower thread: setPositionDetectorTower(), arg:", arg)
        if not self.simulationMode:
            try:
                self.proxyDetectorTower.command_inout("RecalibrateDetectorDistance")
                time.sleep(0.5)
                self.proxyDetectorTower.write_attribute("DetectorDistance",arg)
            except:
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        else:            
            self.currentPositionDetectorTower = arg
            self.currentLaserPositionDetectorTowerServer = arg
            self.stateDetectorTowerServer = "ON"

    def resetPositionDetectorTower(self):
        if self.debugMode: print("Detector tower thread: resetPositionDetectorTower(), arg:none", end=' ')
        try:
            self.proxyDetectorTower.write_attribute("DetectorDistance",self.detectorManualMountPosition)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def stopDetectorTower(self):
        if self.debugMode: print("Detector tower thread: stopDetectorTower(), arg:none", end=' ')
        try:
            self.proxyDetectorTower.command_inout("Stop")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        moving = True
        while moving:
            try:
                state = str(self.proxyDetectorTower.state())
            except:
                moving = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
                
            if state == "MOVING":
                moving = True
            else:
                moving = False
    def shieldUp(self):
        if self.debugMode: print("Goniometer thread: shieldUp(), arg:")
        if not self.simulationMode:
            try:
                self.proxyDetectorTower.command_inout("ShieldUp") #FIXME
                #self.shieldIsUp = True
                #self.shieldIsDown = False
            except:
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        else:
            self.shieldIsUp = True
            self.shieldIsDown = False
            
    def shieldDown(self):
        if self.debugMode: print("Detector tower thread: shieldDown(), arg:")
        if not self.simulationMode:
            try:
                #self.shieldIsUp = False
                #self.shieldIsDown = True
                self.proxyDetectorTower.command_inout("ShieldDown") #FIXME
            except:
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        else:
            self.shieldIsUp = False
            self.shieldIsDown = True

    def recalibrateDistance(self):
        if self.debugMode: print("Detector tower thread: RecalibrateDetectorDistance(), arg:")
        try:
            self.proxyDetectorTower.command_inout("RecalibrateDetectorDistance")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
            
