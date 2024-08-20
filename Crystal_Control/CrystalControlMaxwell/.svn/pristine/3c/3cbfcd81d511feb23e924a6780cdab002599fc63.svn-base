#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyTango import DeviceProxy, DevState
from PyQt4.QtCore import SIGNAL, QThread
import sys

class RobotThread(QThread):
    def __init__(self, robotserver, parent):
        QThread.__init__(self)
        print("Robot thread: Starting thread")
        try:
            self.dev = DeviceProxy(robotserver)
            #self.dev.ping()
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Robot thread: started")
            print("Robot thread: started")
            self.connected = True
        except:
            print(sys.exc_info())
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Robot server not running")
            print("Robot server not running")
            self.connected = False

        self.alive = False
        self.action = None
        self.mounting = False
        self.demounting = False
        self.myparent = parent

        self.tangostate = "UNKNOWN"
        self.statusInterlock = False
        self.statusGripper = False
        self.sampleInGripper = False
        self.statusCollisionProtection = False
        self.statusHomePosition = False
        self.statusSampleMounted = False
        self.readRobotSpeed = ""
        self.statusCryojet = True
        self.statusArmPowered = False
        self.statusGonio = False
        self.statusGuillotine = False
        self.statusPiezos = False
        self.deiceSampleInterval = 0
        self.deiceTimeInterval = 0

        self.robotCenteringX = 0
        self.robotCenteringY = 0
        self.robotGoniometerX = 0
        self.robotGoniometerY = 0
        self.robotGoniometerZ = 0
        self.robotMicroscopeY = 0
        self.robotMicroscopeZ = 0


    def stop(self):
        print("Robot thread: Stopping thread")
        self.alive = False
#         self.wait() # waits until run stops on his own

    def run(self):
        if not self.connected:
            return
        self.alive = True
        while self.alive:
            if self.action is not None:
                self.action()
                self.action = None
            self.readAttributes()
            self.msleep(1000)
        print("Robot thread: Thread for Robot died")

    def readAttributes(self):
        try: 
            self.statusInterlock = self.dev.read_attribute("ConditionInterlockSet").value
            self.statusArmPowered = self.dev.read_attribute("RobotPowered").value
            self.statusEmergencyStop = self.dev.read_attribute("RobotEmergencyStopClear").value
            self.statusCollisionProtection = self.dev.read_attribute("ConditionCollisionProtectionClear").value
            self.statusSampleMounted = self.dev.read_attribute("RobotCurrentSample").value
            #self.readRobotSpeed = self.dev.read_attribute("RobotSpeed").value
            self.tangostate = str(self.dev.state())
            self.statusCryojet = self.dev.read_attribute("ConditionCryojetOut").value
            self.statusGonio = self.dev.read_attribute("ConditionGoniometerMountPosition").value
            self.statusGuillotine = self.dev.read_attribute("ConditionGuillotineClosed").value
            self.statusScreen = self.dev.read_attribute("ConditionScreenOut").value
            self.statusCollimator = self.dev.read_attribute("ConditionCollimatorOut").value
            self.deiceSampleInterval = self.dev.read_attribute("GripperDeiceSampleInterval").value
            self.deiceTimeInterval = self.dev.read_attribute("GripperDeiceTimeInterval").value
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "robot thread error " + str(sys.exc_info()[0]))
        self.emit(SIGNAL("update()"))

    def getSample(self, sampleNumber):
        try:
            self.dev.command_inout("MountSample", sampleNumber)
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "robot thread error " + str(sys.exc_info()[0]))

    def demountSample(self):
        self.dev.command_inout("DemountSample")
        
    def washSample(self):
        self.dev.command_inout("WashSample")
        
    def deiceGripper(self):
        self.dev.command_inout("DeiceGripper")
        
    def setDeiceSampleInterval(self, sampleInterval):
        self.dev.write_attribute("GripperDeiceSampleInterval", sampleInterval)
        
    def setDeiceTimeInterval(self, timeInterval):
        self.dev.write_attribute("GripperDeiceTimeInterval", timeInterval)
        
    def coolGripper(self):
        self.dev.command_inout("CoolGripper")
        
    def moveHome(self):
        self.dev.command_inout("HomePosition")
        
    def setSpeed(self, speed):
        self.dev.write_attribute("RobotSpeed", speed)
            
    def openGripper(self):
        self.dev.write_attribute("GripperOpen", 1)

    def closeGripper(self):
        self.dev.write_attribute("GripperOpen", 0)
        
    def eStop(self):
        self.dev.command_inout("Stop")

    def setMountPosition(self):
        try:
            self.robotCenteringX = self.myparent.goniometerThread.proxyFlexureX.read_attribute("Position").w_value
            self.robotCenteringY = self.myparent.goniometerThread.proxyFlexureY.read_attribute("Position").w_value
            self.robotGoniometerX = self.myparent.goniometerThread.proxyKohzuGoniometerX.read_attribute("Position").value
            self.robotGoniometerY = self.myparent.goniometerThread.proxyKohzuGoniometerY.read_attribute("Position").value
            self.robotGoniometerZ = self.myparent.goniometerThread.proxyKohzuGoniometerZ.read_attribute("Position").value
            self.robotMicroscopeY = self.myparent.goniometerThread.proxyKohzuMicroscopeY.read_attribute("Position").value
            self.robotMicroscopeZ = self.myparent.goniometerThread.proxyKohzuMicroscopeZ.read_attribute("Position").value
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Mount action failed: " + str(sys.exc_info()[0]))

        while(self.myparent.goniometerThread.proxyGoniometer.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyFlexureX.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyFlexureY.state() == DevState.MOVING or
                self.myparent.piezoThread.proxyPiezoPinholeZ.state() == DevState.MOVING or
                self.myparent.piezoThread.proxyPiezoScreenZ.state() == DevState.MOVING or
                self.myparent.piezoThread.proxyPiezoCollimatorZ.state() == DevState.MOVING or
                self.myparent.piezoThread.proxyPiezoBeamstopX.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerX.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerY.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerZ.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuMicroscopeY.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuMicroscopeZ.state() == DevState.MOVING):
            self.readAttributes()
            self.msleep(500)

        self.readAttributes()
        self.myparent.goniometerThread.setAngle(0)
        self.myparent.goniometerThread.setPositionFlexureX(0)
        self.myparent.goniometerThread.setPositionFlexureY(0)
        self.myparent.setKohzuGoniometerX(0)
        self.myparent.setKohzuGoniometerY(0)
        self.myparent.setKohzuGoniometerZ(0)
        self.myparent.setKohzuMicroscopeY(0)
        self.myparent.setKohzuMicroscopeZ(0)
        self.myparent.piezoThread.collimatorOut()
        self.myparent.waitingForCollimatorOut = True
        self.myparent.piezoThread.screenOut()
        self.myparent.waitingForScreenOut = True
        self.myparent.piezoThread.moveBeamStopOut()
        self.myparent.goniometerThread.moveContrastScreenOut()
        self.myparent.cryoThread.retract()

        while(self.myparent.goniometerThread.proxyGoniometer.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyFlexureX.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyFlexureY.state() == DevState.MOVING or
                self.myparent.piezoThread.proxyPiezoPinholeZ.state() == DevState.MOVING or
                self.myparent.piezoThread.proxyPiezoScreenZ.state() == DevState.MOVING or
                self.myparent.piezoThread.proxyPiezoCollimatorZ.state() == DevState.MOVING or
                self.myparent.piezoThread.proxyPiezoBeamstopX.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerX.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerY.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerZ.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuMicroscopeY.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuMicroscopeZ.state() == DevState.MOVING):
            self.readAttributes()
            self.msleep(500)
            #print "setMountPosition: devices are still moving"

    def resetPosition(self, demount=False):
        while(self.myparent.goniometerThread.proxyFlexureX.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyFlexureY.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerX.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerY.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerZ.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuMicroscopeY.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuMicroscopeZ.state() == DevState.MOVING):
            self.readAttributes()
            self.msleep(500)

        self.readAttributes()
        self.myparent.goniometerThread.setPositionFlexureX(self.robotCenteringX)
        self.myparent.goniometerThread.setPositionFlexureY(self.robotCenteringY)
        self.myparent.setKohzuGoniometerX(self.robotGoniometerX)
        self.myparent.setKohzuGoniometerY(self.robotGoniometerY)
        self.myparent.setKohzuGoniometerZ(self.robotGoniometerZ)
        self.myparent.setKohzuMicroscopeY(self.robotMicroscopeY)
        self.myparent.setKohzuMicroscopeZ(self.robotMicroscopeZ)
        self.myparent.goniometerThread.moveContrastScreenIn()
        self.myparent.cryoThread.extend()

        while(self.myparent.goniometerThread.proxyFlexureX.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyFlexureY.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerX.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerY.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuGoniometerZ.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuMicroscopeY.state() == DevState.MOVING or
                self.myparent.goniometerThread.proxyKohzuMicroscopeZ.state() == DevState.MOVING):
            self.readAttributes()
            self.msleep(500)

    def startMount(self, sampleNumber):
        if self.action is None:
            self.action = lambda: self.mountAction(sampleNumber)

    def mountAction(self, sampleNumber):
        self.mounting = True
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Mount action started: moving crystallography in mount position...")
        self.setMountPosition()
        self.msleep(200)
        self.readAttributes()
        while(self.tangostate == "MOVING"):
            self.msleep(1000)
            self.readAttributes()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Mounting sample " + str(int(sampleNumber/16)) + " from Puck " + str(sampleNumber%16+1))
        self.getSample(sampleNumber)
        self.msleep(1000)
        self.readAttributes()
        while(self.tangostate == "MOVING"):
            self.msleep(1000)
            self.readAttributes()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "mounted" + str(sampleNumber))
        while(self.myparent.goniometerThread.proxyFlexureX.is_locked()):
            self.msleep(500)
            self.readAttributes()
        self.msleep(100)
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Devices unlocked, resetting position")
        self.readAttributes()
        if self.tangostate != "INIT":
            self.resetPosition()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Mount action finished")
        self.mounting = False

    def startDemount(self):
        if self.action is None:
            self.action = self.demountAction

    def demountAction(self):
        self.demounting = True
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Demount action started: moving crystallography in mount position...")
        self.setMountPosition()
        self.msleep(200)
        self.readAttributes()
        while(self.tangostate == "MOVING"):
            self.msleep(1000)
            self.readAttributes()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Demounting sample")
        self.demountSample()
        self.msleep(1000)
        self.readAttributes()
        while(self.tangostate == "MOVING"):
            self.msleep(1000)
            self.readAttributes()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "demounted")
        while(self.myparent.goniometerThread.proxyFlexureX.is_locked()):
            self.msleep(500)
            self.readAttributes()
        self.msleep(100)
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Devices unlocked, resetting position")
        self.readAttributes()
        if self.tangostate != "INIT":
            self.resetPosition()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Demount action finished")
        self.demounting = False

    def startWashing(self):
        if self.action is None:
            self.action = self.washAction

    def washAction(self):
        self.demounting = True
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Wash action started: moving crystallography in mount position...")
        self.setMountPosition()
        self.msleep(200)
        self.readAttributes()
        while(self.tangostate == "MOVING"):
            self.msleep(1000)
            self.readAttributes()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Washing sample")
        self.washSample()
        self.msleep(1000)
        self.readAttributes()
        while(self.tangostate == "MOVING"):
            self.msleep(1000)
            self.readAttributes()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "mounted sample")
        while(self.myparent.goniometerThread.proxyFlexureX.is_locked()):
            self.msleep(500)
            self.readAttributes()
        self.msleep(1000)
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Devices unlocked, resetting position")
        self.readAttributes()
        if self.tangostate != "INIT":
            self.resetPosition()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), "Wash action finished")
        self.demounting = False

