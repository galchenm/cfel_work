# -*- coding: utf-8 -*-
import sys
#from PyTango import DeviceProxy, DevState
from PyTango import *
from PyQt4 import QtCore, QtGui
import time
import string
import random
import os
from PyQt4.QtCore import SIGNAL, QThread
import random
import math
import queue
from simulationDevice import SimulationDevice

class ClientCommand(object):
    """ A command to the client thread.
        Each command type has its associated data:
    
        setSpeed               Float
        setAngle               Float
        stopMotion             None
        homeGoniometer         None
        setPositionFlexureX    Float
        setPositionFlexureY    Float
        setPositionKohzuX      Float
        setPositionKohzuY      Float
        setPositionKohzuZ      Float

    """
    setSpeed, setAngle, setAngleNoMod,stopMotion, homeGoniometer, setPositionFlexureX, \
    setPositionFlexureY, setPositionKohzuGoniometerX, setPositionKohzuGoniometerY, \
    setPositionKohzuGoniometerZ, setPositionKohzuMicroscopeY, setPositionKohzuMicroscopeZ, \
    openShutter, closeShutter = list(range(14))
    
    def __init__(self, type, data=None):
        self.type = type
        self.data = data


class GoniometerThread(QThread):

    GONIOMETER_TURNBACK_TIME = 0.3 #s
    GONIOMETER_ANGLE_TOLERANCE = 0.05 #deg
    GONIOMETER_DEFAULT_SPEED = 130.0 #deg/s

    TYPE_UNKNOWN = 0
    TYPE_OMS_MAX_V = 1
    TYPE_OMS_VME_58 = 2
    TYPE_GALIL_DMC = 3

    proxy = 0
    device = 0
    status = 0
    
    acquisitionInProgress = False 
    acquisitionTimeStart = 0.0
    acquisitionTimeTotal = 0.0 

    # A thread is started by calling QThread.start() never by calling run() directly!
    def __init__(self, deviceservers, cmd_q=queue.Queue(), reply_q=queue.Queue(), parent = None, simulation = False):
        QThread.__init__(self, parent)
        #self.MainWindow = mainwindowPassing
        print("Goniometer thread: Starting thread")
        self.cmd_q = cmd_q
        self.reply_q = reply_q
        self.alive = True
        self.simulationMode = simulation
        self.debugMode = 0
        self.motorTypeFlexureX = self.TYPE_UNKNOWN
        self.motorTypeFlexureY = self.TYPE_UNKNOWN
        self.currentPositionKohzuGoniometerX = 0.0
        self.currentPositionKohzuGoniometerY = 0.0
        self.currentPositionKohzuGoniometerZ = 0.0
        self.currentPositionKohzuMicroscopeY = 0.0
        self.currentPositionKohzuMicroscopeZ = 0.0
        self.velocityY = 0
        self.velocityZ = 0
        self.handlers = {
            ClientCommand.setSpeed: self.setSpeed,
            ClientCommand.setAngle: self.setAngle,
            ClientCommand.setAngleNoMod: self.setAngleNoMod,
            ClientCommand.stopMotion: self.stopMotion,
            ClientCommand.homeGoniometer: self.homeGoniometer,
            ClientCommand.setPositionFlexureX: self.setPositionFlexureX,
            ClientCommand.setPositionFlexureY: self.setPositionFlexureY,
            ClientCommand.setPositionKohzuGoniometerX: self.setPositionKohzuGoniometerX,
            ClientCommand.setPositionKohzuGoniometerY: self.setPositionKohzuGoniometerY,
            ClientCommand.setPositionKohzuGoniometerZ: self.setPositionKohzuGoniometerZ,
            ClientCommand.setPositionKohzuMicroscopeY: self.setPositionKohzuMicroscopeY,
            ClientCommand.setPositionKohzuMicroscopeZ: self.setPositionKohzuMicroscopeZ,
            ClientCommand.openShutter: self.openShutter,
            ClientCommand.closeShutter: self.closeShutter,
        }
        
        self.deviceservers = deviceservers
        
        if self.simulationMode:
            print("Goniometer in simulation mode")
            self.proxyGoniometer = SimulationDevice()
            self.proxyFlexureX = SimulationDevice()
            self.proxyFlexureY = SimulationDevice()
            self.proxyKohzuGoniometerX = SimulationDevice()
            self.proxyKohzuGoniometerY = SimulationDevice()
            self.proxyKohzuGoniometerZ = SimulationDevice()
            self.proxyKohzuMicroscopeY = SimulationDevice()
            self.proxyKohzuMicroscopeZ = SimulationDevice()
            self.proxyContrastscreen = SimulationDevice()
            self.proxyFlexureX.write_attribute("VelocityUnits",150)
            self.proxyFlexureY.write_attribute("VelocityUnits",150)
            self.proxyGoniometer.write_attribute("Velocity", 90)
            self.proxyGoniometer.write_attribute("PSOoutputStatus", 0)
            self.proxyKohzuGoniometerX.write_attribute("VelocityUnits",500)
            self.proxyKohzuGoniometerY.write_attribute("VelocityUnits",1000)
            self.proxyKohzuGoniometerZ.write_attribute("VelocityUnits",1000)
            self.proxyKohzuGoniometerY.write_attribute("Conversion",8)
            self.proxyKohzuGoniometerZ.write_attribute("Conversion",8)
            self.proxyKohzuGoniometerY.write_attribute("SlewRate",5000)
            self.proxyKohzuGoniometerZ.write_attribute("SlewRate",5000)
            self.proxyKohzuMicroscopeY.write_attribute("VelocityUnits",1000)
            self.proxyKohzuMicroscopeZ.write_attribute("VelocityUnits",1000)
            
            self.stateGoniometer = "ON"
            self.stateFlexureX = "ON"
            self.stateFlexureY = "ON"
            self.stateKohzuGoniometerX = "ON"
            self.stateKohzuGoniometerY = "ON"
            self.stateKohzuGoniometerZ = "ON"
            self.stateKohzuMicroscopeY = "ON"
            self.stateKohzuMicroscopeZ = "ON"

            self.positionContrastscreen = 0
            self.currentPositionFlexureX = 0.0
            self.maxPositionFlexureX = 1800
            self.minPositionFlexureX = -1800
            self.currentPositionFlexureY = 0.0
            self.maxPositionFlexureY = 1800
            self.minPositionFlexureY = -1800
            self.currentPositionKohzuGoniometerX = 0.0
            self.maxPositionKohzuGoniometerX = 10000
            self.minPositionKohzuGoniometerX = -10000
            self.currentPositionKohzuGoniometerY = 0.0
            self.maxPositionKohzuGoniometerY = 10000
            self.minPositionKohzuGoniometerY = -10000
            self.currentPositionKohzuGoniometerZ = 0.0
            self.maxPositionKohzuGoniometerZ = 10000
            self.minPositionKohzuGoniometerZ = -10000
            self.currentPositionKohzuMicroscopeY = 0.0
            self.maxPositionKohzuMicroscopeY = 10000
            self.minPositionKohzuMicroscopeY = -10000
            self.currentPositionKohzuMicroscopeZ = 0.0
            self.maxPositionKohzuMicroscopeZ = 10000
            self.minPositionKohzuMicroscopeZ = -10000
            self.currentAngle = 0.0        
            self.statusFastShutter = False
        else:
            print("Goniometer thread: started")
            #FlexureX
            try:
                self.proxyFlexureX = DeviceProxy(deviceservers[1])
                self.proxyFlexureX.ping()
            except:
                self.alive = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
                
                
            if(self.proxyFlexureX.info().dev_class == "OmsMaxV"):
                self.motorTypeFlexureX = self.TYPE_OMS_MAX_V
            elif(self.proxyFlexureX.info().dev_class == "GalilDMCMotor"):
                self.motorTypeFlexureX = self.TYPE_GALIL_DMC
            elif(self.proxyFlexureX.info().dev_class == "VirtualMotors"):
                self.motorTypeFlexureX = self.TYPE_GALIL_DMC  # should work like this
                
                
            #FlexureY
            try:
                self.proxyFlexureY = DeviceProxy(deviceservers[2])
                self.proxyFlexureY.ping()
            except:
                self.alive = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
            if(self.proxyFlexureY.info().dev_class == "OmsMaxV"):
                self.motorTypeFlexureY = self.TYPE_OMS_MAX_V
            elif(self.proxyFlexureY.info().dev_class == "GalilDMCMotor"):
                self.motorTypeFlexureY = self.TYPE_GALIL_DMC
            elif(self.proxyFlexureY.info().dev_class == "VirtualMotors"):
                self.motorTypeFlexureY = self.TYPE_GALIL_DMC  # should work like this
                
                
                
                
            try:
                self.proxyGoniometer = DeviceProxy(self.deviceservers[0])
                self.proxyGoniometer.ping()
                self.proxyKohzuGoniometerX = DeviceProxy(self.deviceservers[3])
                self.proxyKohzuGoniometerX.ping()
                self.proxyKohzuGoniometerY = DeviceProxy(self.deviceservers[4])
                self.proxyKohzuGoniometerY.ping()
                self.proxyKohzuGoniometerZ = DeviceProxy(self.deviceservers[5])
                self.proxyKohzuGoniometerZ.ping()
                self.proxyKohzuMicroscopeY = DeviceProxy(self.deviceservers[6])
                self.proxyKohzuMicroscopeY.ping()
                self.proxyKohzuMicroscopeZ = DeviceProxy(self.deviceservers[7])
                self.proxyKohzuMicroscopeZ.ping()
                self.proxyContrastscreen = DeviceProxy(self.deviceservers[9])
                self.proxyContrastscreen.ping()
            except:
                print(sys.exc_info())
                print("Deviceservers not running")
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
                self.alive = False
                self.connected = 0
                
            self.positionContrastscreen = self.proxyContrastscreen.read_attribute("Value").value
                

            try:
                if self.motorTypeFlexureX == self.TYPE_GALIL_DMC:
                    self.maxPositionFlexureX = self.proxyFlexureX.read_attribute("SoftCwLimit").value
                    self.minPositionFlexureX = self.proxyFlexureX.read_attribute("SoftCcwLimit").value
                else:
                    self.maxPositionFlexureX = self.proxyFlexureX.read_attribute("SoftLimitMaxUnits").value
                    self.minPositionFlexureX = self.proxyFlexureX.read_attribute("SoftLimitMinUnits").value
                if self.motorTypeFlexureY == self.TYPE_GALIL_DMC:
                    self.maxPositionFlexureY = self.proxyFlexureY.read_attribute("SoftCwLimit").value
                    self.minPositionFlexureY = self.proxyFlexureY.read_attribute("SoftCcwLimit").value
                else:
                    self.maxPositionFlexureY = self.proxyFlexureY.read_attribute("SoftLimitMaxUnits").value
                    self.minPositionFlexureY = self.proxyFlexureY.read_attribute("SoftLimitMinUnits").value
            except:
                self.alive = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

            self.currentAngle = 0.0
            self.statusFastShutter = False
            self.stateGoniometer = "ON"
            self.currentPositionKohzuGoniometerX = 0.0
            self.maxPositionKohzuGoniometerX = 10000
            self.minPositionKohzuGoniometerX = -10000
            self.currentPositionKohzuGoniometerY = 0.0
            self.maxPositionKohzuGoniometerY = 10000
            self.minPositionKohzuGoniometerY =-10000
            self.currentPositionKohzuGoniometerZ = 0.0
            self.maxPositionKohzuGoniometerZ = 10000
            self.minPositionKohzuGoniometerZ = -10000
            self.currentPositionKohzuMicroscopeY = 0.0
            self.maxPositionKohzuMicroscopeY = 10000
            self.minPositionKohzuMicroscopeY = -10000
            self.currentPositionKohzuMicroscopeZ = 0.0
            self.maxPositionKohzuMicroscopeZ = 10000
            self.minPositionKohzuMicroscopeZ = -10000

    def stop(self):
        print("Goniometer thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own

    def run(self):
        print("Goniometer thread: started")
        self.alive = True
        self.connected = 1
        while self.alive:
            self.readAttributes()
            try:
                # Queue.get with timeout to allow checking self.alive
                cmd = self.cmd_q.get(True, 0.005)
                self.handlers[cmd.type](cmd.data)
            except queue.Empty as e:
                continue
            
        # exit position of run function of thread. if exiting == true we end up here
        self.valid = 0
        self.status = "OFFLINE"
        self.connected = 0
        print("Goniometer thread: Thread for goniometer died")

    def join(self, timeout=None):
        print("Goniometer thread: join method")
        self.alive = False

    def readAttributes(self):
        try:
            self.stateGoniometer = str(self.proxyGoniometer.state())
            self.stateFlexureX = str(self.proxyFlexureX.state())
            self.stateFlexureY = str(self.proxyFlexureY.state())
            self.stateKohzuGoniometerX = str(self.proxyKohzuGoniometerX.state())
            self.stateKohzuGoniometerY = str(self.proxyKohzuGoniometerY.state())
            self.stateKohzuGoniometerZ = str(self.proxyKohzuGoniometerZ.state())
            self.stateKohzuMicroscopeY = str(self.proxyKohzuMicroscopeY.state())
            self.stateKohzuMicroscopeZ = str(self.proxyKohzuMicroscopeZ.state())
            self.statusFastShutter = bool(self.proxyGoniometer.read_attribute("PSOoutputStatus").value)
            self.speed = self.proxyGoniometer.read_attribute("Velocity").value
            self.currentAngle = self.proxyGoniometer.read_attribute("Position").value
            self.currentPositionFlexureX = self.proxyFlexureX.read_attribute("Position").value
            self.currentPositionFlexureY = self.proxyFlexureY.read_attribute("Position").value
            self.currentPositionKohzuGoniometerX = self.proxyKohzuGoniometerX.read_attribute("Position").value
            self.currentPositionKohzuGoniometerY = self.proxyKohzuGoniometerY.read_attribute("Position").value
            self.currentPositionKohzuGoniometerZ = self.proxyKohzuGoniometerZ.read_attribute("Position").value
            self.currentPositionKohzuMicroscopeY = self.proxyKohzuMicroscopeY.read_attribute("Position").value
            self.currentPositionKohzuMicroscopeZ = self.proxyKohzuMicroscopeZ.read_attribute("Position").value
            self.positionContrastscreen = self.proxyContrastscreen.read_attribute("Value").value            
            self.velocityY = self.proxyKohzuGoniometerY.read_attribute("SlewRate").value/self.proxyKohzuGoniometerY.read_attribute("Conversion").value
            self.velocityZ = self.proxyKohzuGoniometerZ.read_attribute("SlewRate").value/self.proxyKohzuGoniometerZ.read_attribute("Conversion").value
            self.statusFastShutter = bool(self.proxyGoniometer.read_attribute("PSOoutputStatus").value)
            self.speed = self.proxyGoniometer.read_attribute("Velocity").value
            self.currentAngle = self.proxyGoniometer.read_attribute("Position").value
            if(self.acquisitionInProgress and self.stateGoniometer != "MOVING"):
                if (time.time() - self.acquisitionTimeStart) > 0.5:
                    self.stopMotion()
            time.sleep(0.1)
        except:
            print(sys.exc_info())
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setSpeed(self, arg):
        speed = float(arg)
        if self.debugMode:
            print("Goniometer thread: setSpeed(), arg:", speed)
        try:
            self.proxyGoniometer.write_attribute("Velocity", speed)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setAngle(self, arg):
        angle = float(arg)
        if self.debugMode:
            print("Goniometer thread: setAngle(), arg:", angle)
        try:
            currentAngle = self.proxyGoniometer.read_attribute("Position").value
            if currentAngle < 0:
                currentAngle = abs(currentAngle)
                loadAngleNew = currentAngle % 360
                self.proxyGoniometer.command_inout("Calibrate", -loadAngleNew)
                self.proxyGoniometer.write_attribute("Position", angle)
            else:
                loadAngleNew = currentAngle % 360
                self.proxyGoniometer.command_inout("Calibrate", loadAngleNew)
                self.proxyGoniometer.write_attribute("Position", angle)
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setAngleNoMod(self, arg):
        angle = float(arg)
        if self.debugMode:
            print("Goniometer thread: setAngleNoMod(), arg:", angle)
        try:
            self.proxyGoniometer.write_attribute("Position", angle)
        except:
            #self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
            pass
        if self.simulationMode:
            self.proxyGoniometer.write_attribute("PSOoutputStatus", 1)

    def stopMotion(self, arg=None):
        if self.debugMode: print("Goniometer thread: Stopping goniometer")
        if self.acquisitionInProgress:
            self.acquisitionTimeStart = 0.0
            self.acquisitionTimeTotal = 0.0
            self.acquisitionInProgress = False
        try:
            self.proxyGoniometer.command_inout("AbortMove")
            self.proxyGoniometer.command_inout("PSOwindowOff")
            self.proxyGoniometer.command_inout("PSOcontrolOff")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        moving = True
        while moving:
            try:
                state = str(self.proxyGoniometer.state())
            except:
                moving = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
                break
            if state == "MOVING":
                moving = True
            else:
                moving = False
                
    def startAcquisitionRun(self, startAngle, stopAngle, speed):
        while (self.proxyGoniometer.state() == DevState.MOVING):
            time.sleep(0.1)
        time.sleep(0.1)
        self.setSpeed(self.GONIOMETER_DEFAULT_SPEED)
        time.sleep(0.15)
        self.setAngle(startAngle - speed * self.GONIOMETER_TURNBACK_TIME)
        time.sleep(0.1)
        while (self.proxyGoniometer.state() == DevState.MOVING):
            time.sleep(0.1)
        time.sleep(0.1)
        self.SetPSOcontrolArm(startAngle, stopAngle)  # Made as separate method of this class
        self.setSpeed(speed)
        time.sleep(0.1)
        self.setAngleNoMod(stopAngle + speed * self.GONIOMETER_TURNBACK_TIME)
        self.acquisitionTimeStart = time.time()
        self.acquisitionTimeTotal = (abs(stopAngle - startAngle) + 2 * speed * self.GONIOMETER_TURNBACK_TIME) / speed
        self.acquisitionInProgress = True

    def SetPSOcontrolArm(self, startAngle, stopAngle):
        """
        This Method sets the Tango Device Server "proxyGoniometer" into the PSOcontrolArm mode.
        For this mode, there is a  contact(pin) on controller, which will be set to High(Low)
        State, to trigger "start acquisition"("end acquisition") events of Detector-FastShutter.    
        """
        try:
            if startAngle <= stopAngle:
                self.proxyGoniometer.write_attribute("PSOwindowLowerBound", startAngle)
                self.proxyGoniometer.write_attribute("PSOwindowUpperBound", stopAngle)
            else:
                self.proxyGoniometer.write_attribute("PSOwindowLowerBound", stopAngle)
                self.proxyGoniometer.write_attribute("PSOwindowUpperBound", startAngle)
            self.proxyGoniometer.command_inout("PSOcontrolArm")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])



    def homeGoniometer(self, arg=None):
        if self.debugMode: print("Goniometer thread: Homing goniometer")
        try:
            self.proxyGoniometer.command_inout("StopUserTask1")
        except:
            pass
        time.sleep(0.5)
        try:
            self.proxyGoniometer.command_inout("StartUserTask1")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        else:
            self.currentAngle = 0

    def activateSerialCrystallographyMode(self):
        if self.debugMode: print("Goniometer thread: Activating serial crystallography mode")
        try:
            self.proxyGoniometer.write_attribute("SoftLimitCcw", -45)
            self.proxyGoniometer.write_attribute("SoftLimitCw", 20)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def deactivateSerialCrystallographyMode(self):
        if self.debugMode: print("Goniometer thread: Deactivating serial crystallography mode")
        try:
            self.proxyGoniometer.write_attribute("SoftLimitCcw", 0)
            self.proxyGoniometer.write_attribute("SoftLimitCw", 0)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def activateSerialCrystallographyManualMountPosition(self):
        if self.debugMode: print("Goniometer thread: Activating serial crystallography manual mount")
        try:
            self.proxyGoniometer.write_attribute("SoftLimitCcw", -135)
            self.proxyGoniometer.write_attribute("SoftLimitCw", 20)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def remainingMoveTime(self, percent = False):
        if self.acquisitionTimeStart == 0.0 or self.acquisitionTimeTotal == 0.0:
            return 0.0
        else:
            if percent:
                return 100 * (time.time() - self.acquisitionTimeStart) / self.acquisitionTimeTotal
            else:
                return self.acquisitionTimeTotal - (time.time() - self.acquisitionTimeStart)
        
    def setPositionFlexureX(self, arg):
        position = float(arg)
        if self.debugMode: print("Goniometer thread: setPositionFlexureX(), arg:", position)
        try:
            self.proxyFlexureX.write_attribute("Position", position)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        time.sleep(0.01)
        
    def setPositionFlexureXImmediately(self, arg):
        position = arg
        if self.debugMode: print("Goniometer thread: setPositionFlexureX(), arg:", arg)
        try:
            self.proxyFlexureX.write_attribute("Position", position)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setPositionFlexureY(self, arg):
        position = float(arg)
        if self.debugMode: print("Goniometer thread: setPositionFlexureY(), arg:", position)
        try:
            self.proxyFlexureY.write_attribute("Position", position)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        time.sleep(0.01)
        
    def setPositionFlexureYImmediately(self, arg):
        position = arg
        if self.debugMode: print("Goniometer thread: setPositionFlexureY(), arg:", arg)
        try:
            self.proxyFlexureY.write_attribute("Position",position)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def stopFlexure(self):
        if self.debugMode: print("Piezo thread: stopFlexure()")
        try:
            if self.motorTypeFlexureX == self.TYPE_GALIL_DMC:
                self.proxyFlexureX.command_inout("Stop")
            else:
                self.proxyFlexureX.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        try:
            if self.motorTypeFlexureY == self.TYPE_GALIL_DMC:
                self.proxyFlexureY.command_inout("Stop")
            else:
                self.proxyFlexureY.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setPositionKohzuGoniometerX(self, arg):
        position = float(arg)
        if self.debugMode: print("Goniometer thread: setPositionKohzuGoniometerX(), arg:", position)
        try:
            self.proxyKohzuGoniometerX.write_attribute("Position", position)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        time.sleep(0.01)

    def setPositionKohzuGoniometerY(self, arg):
        position = float(arg)
        if self.debugMode: print("Goniometer thread: setPositionKohzuGoniometerY(), arg:", position)
        try:
            self.proxyKohzuGoniometerY.write_attribute("Position", position)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        time.sleep(0.01)

    def setPositionKohzuGoniometerZ(self, arg):
        position = float(arg)
        if self.debugMode: print("Goniometer thread: setPositionKohzuGoniometerZ(), arg:", position)
        try:
            self.proxyKohzuGoniometerZ.write_attribute("Position", position)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        time.sleep(0.01)

    def setPositionKohzuMicroscopeY(self, arg):
        position = float(arg)
        if self.debugMode: print("Goniometer thread: setPositionKohzuMicroscopeY(), arg:", position)
        try:
            self.proxyKohzuMicroscopeY.write_attribute("Position", position)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        time.sleep(0.01)

    def setPositionKohzuMicroscopeZ(self, arg):
        position = float(arg)
        if self.debugMode: print("Goniometer thread: setPositionKohzuMicroscopeZ(), arg:", position)
        try:
            self.proxyKohzuMicroscopeZ.write_attribute("Position", position)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        time.sleep(0.01)

    def stopKohzuGoniometerY(self):
        try:
            self.proxyKohzuGoniometerY.command_inout("StopMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        moving = True
        while moving:
            try:
                state = str(self.proxyKohzuGoniometerY.state())
            except:
                moving = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
                break
            if state == "MOVING":
                moving = True
            else:
                moving = False

    def stopFlexureX(self):
        try:
            if self.motorTypeFlexureX == self.TYPE_GALIL_DMC:
                self.proxyFlexureX.command_inout("Stop")
            else:
                self.proxyFlexureX.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        moving = True
        while moving:
            try:
                stateX = str(self.proxyFlexureX.state())
            except:
                moving = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
                break
            if stateX == "MOVING":
                moving = True
            else:
                moving = False
    
    def stopFlexureY(self):
        try:
            if self.motorTypeFlexureY == self.TYPE_GALIL_DMC:
                self.proxyFlexureY.command_inout("Stop")
            else:
                self.proxyFlexureY.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        moving = True
        while moving:
            try:
                stateY = str(self.proxyFlexureY.state())
            except:
                moving = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
                break
            if stateY == "MOVING":
                moving = True
            else:
                moving = False

    def stopFlexures(self):
        try:
            if self.motorTypeFlexureX == self.TYPE_GALIL_DMC:
                self.proxyFlexureX.command_inout("Stop")
            else:
                self.proxyFlexureX.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        try:
            if self.motorTypeFlexureY == self.TYPE_GALIL_DMC:
                self.proxyFlexureY.command_inout("Stop")
            else:
                self.proxyFlexureY.command_inout("AbortMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        moving = True
        while moving:
            try:
                stateX = str(self.proxyFlexureX.state())
                stateY = str(self.proxyFlexureY.state())
            except:
                moving = False
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
                break
            if stateX == "MOVING" or stateY == "MOVING":
                moving = True
            else:
                moving = False
    
    def stopAllSteppers(self):
        try:
            self.proxyKohzuGoniometerX.command_inout("StopMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        try:
            self.proxyKohzuGoniometerY.command_inout("StopMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        try:
            self.proxyKohzuGoniometerZ.command_inout("StopMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        try:
            self.proxyKohzuMicroscopeY.command_inout("StopMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        try:
            self.proxyKohzuMicroscopeZ.command_inout("StopMove")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setRotationCenter(self):
        if abs(self.currentPositionKohzuGoniometerX) < 20. and \
                abs(self.currentPositionKohzuGoniometerZ) < 20.:
            try:
                self.proxyKohzuGoniometerX.command_inout("Calibrate", 0)
            except:
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
            try:
                self.proxyKohzuGoniometerZ.command_inout("Calibrate", 0)
            except:
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def openShutter(self, arg=None):
        try:
            self.proxyGoniometer.command_inout("PSOcontrolOn")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        if self.simulationMode:
            self.proxyGoniometer.write_attribute("PSOoutputStatus", 1)

    def closeShutter(self, arg=None):
        try:
            self.proxyGoniometer.command_inout("PSOcontrolOff")
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        if self.simulationMode:
            self.proxyGoniometer.write_attribute("PSOoutputStatus", 0)

    def setAutoShutter(self,arg):
        if self.debugMode:
            print("Goniometer thread: setAutoShutter(), arg:", arg)
        try:
            if arg:
                self.airbearing.write_attribute("AuxiliaryControlAtVelocity", 1)
            else:
                self.airbearing.write_attribute("AuxiliaryControlAtVelocity", 0)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        
    def moveContrastScreenIn(self):
        if self.debugMode:
            print("Goniometer thread: moveContrastScreenIn()")
        try:
            self.proxyContrastscreen.write_attribute("Value", 1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
    
    def moveContrastScreenOut(self):
        if self.debugMode:
            print("Goniometer thread: moveContrastScreenOut()")
        try:
            self.proxyContrastscreen.write_attribute("Value", 0)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
