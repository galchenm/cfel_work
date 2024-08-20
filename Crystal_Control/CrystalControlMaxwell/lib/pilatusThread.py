# -*- coding: utf-8 -*-
import sys
from PyTango import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *

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

class PilatusClientCommand(object):
    """ A command to the client thread.
        Each command type has its associated data:
    
        setExposureTime                  Float (s)
        setExposurePeriod                Float (s)
        setNumberOfFrames                Int
        setNumberOfExposuresPerFrame     Int
        setDelayTime                     Float(s)
        setShutterControl                Boolean
        setTriggerMode                   Int
        setRamDisk                       Boolean
        setImageFilePath                 String
        setImageFilePrefix               String
        setImageFileNumber               Int
        setImageFileType                 String
        setPhotonEnergy                  Float (eV)
        setMXparameter                   String
        startAcquisition                 None
        stopAcquisition                  None
    """
    setExposureTime, setExposurePeriod, setNumberOfFrames, setNumberOfExposuresPerFrame, \
    setDelayTime, setShutterControl, setTriggerMode, setRamDisk, setImageFilePath,\
    setImageFilePrefix, setImageFileNumber, setImageFileType, setPhotonEnergy,\
    setMXparameter, startAcquisition, stopAcquisition  = list(range(16))
    
    def __init__(self, type, data=None):
        self.type = type
        self.data = data


class PilatusThread(QThread):

    # A thread is started by calling QThread.start() never by calling run() directly!
    #def __init__(self, mainwindowPassing, deviceserver, cmd_q=Queue.Queue(), reply_q=Queue.Queue(), parent = None):
    def __init__(self, deviceserver, cmd_q=queue.Queue(), reply_q=queue.Queue(), parent = None, simulation = False):
        QThread.__init__(self, parent)
        #self.MainWindow = mainwindowPassing
        print("Pilatus thread: Starting thread")
        self.cmd_q = cmd_q
        self.reply_q = reply_q
        self.alive = True
        self.simulationMode = simulation
        self.debugMode = 0
        
        self.handlers = {
            PilatusClientCommand.setExposureTime: self.setExposureTime,
            PilatusClientCommand.setExposurePeriod: self.setExposurePeriod,
            PilatusClientCommand.setNumberOfFrames: self.setNumberOfFrames,
            PilatusClientCommand.setNumberOfExposuresPerFrame: self.setNumberOfExposuresPerFrame,
            PilatusClientCommand.setDelayTime: self.setDelayTime,
            PilatusClientCommand.setShutterControl: self.setShutterControl,
            PilatusClientCommand.setTriggerMode: self.setTriggerMode,
            PilatusClientCommand.setRamDisk: self.setRamDisk,
            PilatusClientCommand.setImageFilePath: self.setImageFilePath,
            PilatusClientCommand.setImageFilePrefix: self.setImageFilePrefix,
            PilatusClientCommand.setImageFileNumber: self.setImageFileNumber,
            PilatusClientCommand.setImageFileType: self.setImageFileType,
            PilatusClientCommand.setPhotonEnergy: self.setPhotonEnergy,
            PilatusClientCommand.setMXparameter: self.setMXparameter,
            PilatusClientCommand.startAcquisition: self.startAcquisition,
            PilatusClientCommand.stopAcquisition: self.stopAcquisition,
        }       
        self.statePilatus = ""
        self.statusPilatus = ""
        self.exposureTime = 0
        self.exposurePeriod = 0
        self.numberOfFrames = 0
        self.numberOfExposuresPerFrame = 0
        self.delayTime = 0
        self.shutterControl = 0
        self.triggerMode = 0
        self.mxParameters = 0
        self.ramDisk = False
        self.imageFilePath = ""
        self.imageFilePrefix = ""
        self.imageFileNumber = 0
        self.imageFileType = 0
        self.lastImageFileName = ""
        self.photonEnergy = 0
        self.thresholdEnergy = 0
        self.gain = 0
        
        if self.simulationMode:
            print("Pilatus in simulation mode")
            self.proxyPilatus = SimulationDevice()
            self.statePilatus = "ON"
            self.statusPilatus = "Pilatus is in simulation mode"
            self.proxyPilatus.write_attribute("ExposureTime",0.09)
            self.proxyPilatus.write_attribute("ExposurePeriod",0.1)
            self.proxyPilatus.write_attribute("NbFrames",1)
            self.proxyPilatus.write_attribute("NbExposures",1)
            self.proxyPilatus.write_attribute("DelayTime",0.05)
            self.proxyPilatus.write_attribute("ShutterEnable",False)
            self.proxyPilatus.write_attribute("TriggerMode",2)
            #self.proxyPilatus.write_attribute("MXparameters","")
            self.proxyPilatus.write_attribute("UseRamDisk",True)
            self.proxyPilatus.write_attribute("FileDir","/dev/null")
            self.proxyPilatus.write_attribute("FilePrefix","simulationFile")
            self.proxyPilatus.write_attribute("FileStartNum",1)
            self.proxyPilatus.write_attribute("FilePostfix",".cbf")
            self.proxyPilatus.write_attribute("LastImageTaken","foo")
            self.proxyPilatus.write_attribute("Energy",12000)
            self.proxyPilatus.write_attribute("Threshold",6000)
            self.proxyPilatus.write_attribute("Gain",0)
        else:
            try:
                self.proxyPilatus = DeviceProxy(deviceserver)
                self.proxyPilatus.write_attribute("FilePostfix",".cbf")
                self.alive = True
            except:
                pass

    def stop(self):
        print("Pilatus thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own

    def run(self):
        print("Pilatus thread: started")
        
        while self.alive:
            #QtGui.QApplication.processEvents()
            time.sleep(0.5)
            self.readAttributes()
            try:
                # Queue.get with timeout to allow checking self.alive
                cmd = self.cmd_q.get(True, 0.5)
                self.handlers[cmd.type](cmd.data)
            except queue.Empty as e:
                continue
            
        # exit position of run function of thread. if exiting == true we end up here
        self.valid = 0
        self.status = "OFFLINE"
        
        print("Pilatus Thread: Thread for pilatus died")

    def join(self, timeout=None):
        print("Pilatus thread: join method")
        self.alive = False

    def readAttributes(self):
        
        try:
            self.statePilatus = str(self.proxyPilatus.state())
        except:
            print(sys.exc_info())
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])
            return
        if self.statePilatus == "FAULT":
            self.proxyPilatus.command_inout("Init")
            time.sleep(1.5)
        try:
            self.statusPilatus = str(self.proxyPilatus.status())
        except:
            return
        try:
            self.exposureTime = self.proxyPilatus.read_attribute("ExposureTime").value
        except:
            return
        try:
            self.exposurePeriod = self.proxyPilatus.read_attribute("ExposurePeriod").value
        except:
            return
        try:
            self.numberOfFrames = self.proxyPilatus.read_attribute("NbFrames").value
        except:
            return
        try:
            self.numberOfExposuresPerFrame = self.proxyPilatus.read_attribute("NbExposures").value
        except:
            return
        try:
            self.delayTime = self.proxyPilatus.read_attribute("DelayTime").value
        except:
            return
        try:
            self.shutterControl = self.proxyPilatus.read_attribute("ShutterEnable").value
        except:
            return
        try:
            self.triggerMode = self.proxyPilatus.read_attribute("TriggerMode").value
        except:
            return
        try:
            self.mxParameters = self.proxyPilatus.read_attribute("MXparameters").value
        except:
            return
        try:
            self.ramDisk = self.proxyPilatus.read_attribute("UseRamDisk").value
        except:
            return
        try:
            self.imageFilePath = self.proxyPilatus.read_attribute("FileDir").value
        except:
            return
        try:
            self.imageFilePrefix = self.proxyPilatus.read_attribute("FilePrefix").value
        except:
            return
        try:
            self.imageFileNumber = self.proxyPilatus.read_attribute("FileStartNum").value
        except:
            return
        try:
            self.imageFileType = self.proxyPilatus.read_attribute("FilePostfix").value
        except:
            return
        try:
            self.lastImageFileName = self.proxyPilatus.read_attribute("LastImageTaken").value
        except:
            return
        try:
            self.photonEnergy = self.proxyPilatus.read_attribute("Energy").value
        except:
            return
        try:
            self.thresholdEnergy = self.proxyPilatus.read_attribute("Threshold").value
        except:
            return
        try:
            self.gain = self.proxyPilatus.read_attribute("Gain").value
        except:
            return

    def setExposureTime(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Pilatus thread: setExposureTime(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("ExposureTime",arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
    

    def setExposurePeriod(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Pilatus thread: setExposurePeriod(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("ExposurePeriod", arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
    
    def setNumberOfFrames(self, arg):
        arg = int(arg)
        if self.debugMode:
            print("Pilatus thread: setNumberOfFrames(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("NbFrames", arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setNumberOfExposuresPerFrame(self, arg):
        arg = int(arg)
        if self.debugMode:
            print("Pilatus thread: setNumberOfExposuresPerFrame(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("NbExposures", arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setDelayTime(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Pilatus thread: setDelayTime(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("DelayTime", arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setShutterControl(self, arg):
        arg = bool(arg)
        if self.debugMode:
            print("Pilatus thread: setShutterControl(), arg:", arg.data)
        try:
            self.proxyPilatus.write_attribute("ShutterEnable", arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setTriggerMode(self, arg):
        arg = int(arg)
        if self.debugMode:
            print("Pilatus thread: setTriggerMode(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("TriggerMode", arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        
    def setRamDisk(self, arg):
        arg = bool(arg)
        if self.debugMode:
            print("Pilatus thread: setRamDisk(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("UseRamDisk", arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setImageFilePath(self, arg):
        arg = str(arg)
        if self.debugMode:
            print("Pilatus thread: setImageFilePath(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("FileDir", arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setImageFilePrefix(self, arg):
        arg = str(arg)
        if self.debugMode:
            print("Pilatus thread: setImageFilePrefix(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("FilePrefix", arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setImageFileNumber(self, arg):
        arg = int(arg)
        if self.debugMode:
            print("Pilatus thread: setImageFileNumber(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("FileStartNum", arg)
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setImageFileType(self,arg):
        arg = str(arg)
        if self.debugMode:
            print("Pilatus thread: setImageFileType(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("FilePostfix", arg)
            time.sleep(0.05)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setPhotonEnergy(self, arg):
        arg = int(arg)
        if self.debugMode:
            print("Pilatus thread: setPhotonEnergy(), arg:", arg)
        try:
            self.proxyPilatus.write_attribute("Energy", arg)
            time.sleep(0.05)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setMXparameter(self, arg):
        arg = str(arg)
        if self.debugMode:
            print("Pilatus thread: setMXparameter(), arg:", arg)
        try:
            self.proxyPilatus.command_inout("MXsettings", arg)
            time.sleep(0.05)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def startAcquisition(self, arg=None):
        if self.debugMode: print("Pilatus thread: Starting acquisition")
        try:
            self.proxyPilatus.command_inout("StartStandardAcq")
            self.statePilatus = str(self.proxyPilatus.state())
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def stopAcquisition(self, arg=None):
        if self.debugMode: print("Pilatus thread: Stopping acquisition")
        try:
            self.proxyPilatus.command_inout("StopAcq")
            self.statePilatus = str(self.proxyPilatus.state())
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

