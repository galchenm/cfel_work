# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
try:    
    from PyTango import DeviceProxy
except:
    pass
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL, QThread
import configparser
import os
import sys
import time
import numpy
import datetime
from simulationDevice import SimulationDevice
import urllib.request, urllib.error, urllib.parse

class PetraThread(QThread):           
    def __init__(self, petraservers,directBeamTransmission,simulation = False):
            QThread.__init__(self) 
            
            print("Petra thread: Starting thread")
            

            self.petraservers = petraservers
            
            self.directBeamTransmission = directBeamTransmission
            self.currentFilter1Position = 0
            self.currentFilter2Position = 0
            self.currentFilter3Position = 0
            self.currentFilter1Thickness = 0.
            self.currentFilter2Thickness = 0.
            self.currentFilter3Thickness = 0.
            self.currentFilterTransmission = 1.
            self.filterThicknessDict = dict()
            self.filterThicknessList = []
            self.filter1ThicknessList = []
            self.filter2ThicknessList = []
            self.filter3ThicknessList = []
            self.prevTransmission = 1
            self.devPathShutter = "p11/shutter/1"
            self.devPathGlobal = "PETRA/globals/keyword"
            self.devPathMono = "p11/dcmener/oh.01"
            self.devPathVacuum = "p11/vacuum/1"
            #self.devPathICS = "p11/ics/1"
            self.devPathFilter1Z = "p11/piezomotor/eh.1.10"
            self.devPathFilter2Z = "p11/piezomotor/eh.1.12"
            self.devPathFilter3Z = "p11/piezomotor/eh.1.14"
            self.exiting = False # custom variable that is used to stop the thread
            self.connected = 1
            
            self.simulationMode = simulation
            self.updatetime = 2 #Seconds
            self.currPetraCurrent = 100
            self.currPetraEnergy = 12000
            self.currNumBunches = 0
            self.stateVacuum = "OFF"
            self.statusShutter = "OK"
            self.statusShutterFS = 0
            self.statusShutterBS0 = 0
            self.statusShutterBS1 = 0
            self.statusShutterABS0 = 0
            self.currentMonoEnergy = 12000
            self.createServers()
            self.getStatus()
            self.formerStatusBS0 = self.statusShutterBS0
            self.formerStatusBS1 = self.statusShutterBS1

    def createServers(self):
        if self.simulationMode:
            print("Petra thread in simulation mode")
            self.devShutter = SimulationDevice()
            self.devFastShutter = SimulationDevice()
            self.devGlobal = SimulationDevice()
            self.devMono = SimulationDevice()
            self.devVacuum = SimulationDevice()
        
            self.devGlobal.write_attribute("BeamCurrent",100)
            self.devMono.write_attribute("VelocityUnits", 12000)
            self.devMono.write_attribute("Position", 12000)
            time.sleep(0.01)
            self.bs0StatusProxy = SimulationDevice()
            self.bs1StatusProxy = SimulationDevice()
        
            self.filterProxy = SimulationDevice()
            self.devFilter1Z = SimulationDevice()
            self.devFilter2Z = SimulationDevice()
            self.devFilter3Z = SimulationDevice()
            self.currentFilter1Position = 0
            self.currentFilter2Position = 0
            self.currentFilter3Position = 0
            self.currentFilter1Thickness = 0
            self.currentFilter2Thickness = 0
            self.currentFilter3Thickness = 0
            self.currentFilterTransmission = 1
            self.currentFilterPosition = 0
            self.filterThicknessList = ["0 um"]
            self.stateFilter = "ON"
            
            self.statusShutterBS0 = 1
            self.statusShutterBS1 = 1
            self.statusShutterABS0 = 1
            
        else:
            self.bs0StatusProxy = None
            self.bs1StatusProxy = None
            self.filterProxy = None
            self.devGlobal = None
            self.devMono = None
            self.devVacuum = None
            devicesAlive = False
            while not devicesAlive:
                if self.exiting: break
#                 self.bs0StatusProxy = DeviceProxy(self.petraservers[0])
#                 self.bs1StatusProxy = DeviceProxy(self.petraservers[1])
                self.bs0StatusProxy = DeviceProxy("hasylab/piconditions/bs11_0_geschlossen")
                self.bs1StatusProxy = DeviceProxy("hasylab/piconditions/bs11_1_geschlossen")
                self.devFastShutter = DeviceProxy(self.petraservers[2])
                self.filterProxy = DeviceProxy(self.petraservers[3])
                self.devGlobal = DeviceProxy(self.devPathGlobal)
                self.devMono = DeviceProxy(self.devPathMono)
                self.devVacuum = DeviceProxy(self.devPathVacuum)
                try:
                    properties = self.filterProxy.get_property(["Filter1ZMotor", "Filter2ZMotor", "Filter3ZMotor"])
                    self.devPathFilter1Z = str(properties["Filter1ZMotor"][0])
                    self.devPathFilter2Z = str(properties["Filter2ZMotor"][0])
                    self.devPathFilter3Z = str(properties["Filter3ZMotor"][0])
                    self.devFilter1Z = DeviceProxy(self.devPathFilter1Z)
                    self.devFilter2Z = DeviceProxy(self.devPathFilter2Z)
                    self.devFilter3Z = DeviceProxy(self.devPathFilter3Z)
                    self.devFilter1Z.ping()
                    self.devFilter2Z.ping()
                    self.devFilter3Z.ping()
                    self.bs0StatusProxy.ping()
                    self.bs1StatusProxy.ping()
                    self.devFastShutter.ping()
                    self.filterProxy.ping()
                    self.devGlobal.ping()
                    self.devMono.ping()            
                    self.devVacuum.ping()
                except:
                    devicesAlive = False
                    print(sys.exc_info())
                    print("Error creating device proxies, retrying")
                    time.sleep(1)
                    continue
                else:
                    devicesAlive = True
                    print("Device proxies created")
                
            filter1ThicknessList = self.filterProxy.get_property("Filter1ThicknessList")["Filter1ThicknessList"]
            for f in filter1ThicknessList:
                self.filter1ThicknessList.append(f + " um")

            filter2ThicknessList = self.filterProxy.get_property("Filter2ThicknessList")["Filter2ThicknessList"]
            for f in filter2ThicknessList:
                self.filter2ThicknessList.append(f  + " um")

            filter3ThicknessList = self.filterProxy.get_property("Filter3ThicknessList")["Filter3ThicknessList"]
            for f in filter3ThicknessList:
                self.filter3ThicknessList.append(f  + " um")

            thicknessList = []
            for pos1, value1 in enumerate(filter1ThicknessList):
                for pos2, value2 in enumerate(filter2ThicknessList):
                    for pos3, value3 in enumerate(filter3ThicknessList):
                        thickness = int(value1) + int(value2) + int(value3)
                        self.filterThicknessDict[thickness] = [pos1, pos2, pos3]
                        if not thickness in thicknessList:
                            thicknessList.append(thickness)
            thicknessList.sort()
            self.filterThicknessList = [str(value) + " um" for value in thicknessList]

    def run(self):
        self.exiting = False
        print("Petra thread: started")
        while self.exiting == False:
        
            self.getStatus()
            if(self.statusShutter == "MOVING"):
                if(self.formerStatusBS0 != self.statusShutterBS0 and self.formerStatusBS1 != self.statusShutterBS1):
                    self.statusShutter = "OK"
            elif(self.statusShutterABS0 + self.statusShutterBS0 + self.statusShutterBS1 == 3):
                self.statusShutter = "OK"
            else:
                self.statusShutter = "FAULT"
            self.currentFilter1Position = self.filterProxy.read_attribute("Filter1Position").value
            self.currentFilter2Position = self.filterProxy.read_attribute("Filter2Position").value
            self.currentFilter3Position = self.filterProxy.read_attribute("Filter3Position").value
            self.currentFilter1Thickness = self.filterProxy.read_attribute("Filter1Thickness").value
            self.currentFilter2Thickness = self.filterProxy.read_attribute("Filter2Thickness").value
            self.currentFilter3Thickness = self.filterProxy.read_attribute("Filter3Thickness").value
            self.currentFilterTransmission = self.filterProxy.read_attribute("CurrentTransmission").value
            self.stateFilter = str(self.filterProxy.state())
            thickness = int(self.currentFilter1Thickness) + int(self.currentFilter2Thickness) + int(self.currentFilter3Thickness)
            try:
                self.currentFilterPosition = self.filterThicknessList.index(str(thickness) + " um")
            except:
                self.currentFilterPosition = -1
            time.sleep(self.updatetime)
        print("Thread for PETRA died")


    def stop(self):
        print("Stopping thread")
        self.exiting = True
        self.wait() # waits until run stops on his own  
        self.connected = 0


    def getStatus(self):
        if self.connected:
            try:
                #shutters
                if self.bs0StatusProxy.read_attribute("displayState").value[0] == 3:
                    self.statusShutterBS0 = 1
                else: 
                    self.statusShutterBS0 = 0
                if self.bs1StatusProxy.read_attribute("displayState").value[0] == 3:
                    self.statusShutterBS1 = 1
                else: 
                    self.statusShutterBS1 = 0
            except:
                pass
            #PETRA
            try:
                self.currPetraCurrent = self.devGlobal.read_attribute("BeamCurrent").value
                self.currPetraEnergy = self.devGlobal.read_attribute("Energy").value
                #self.currNumBunches = self.devGlobal.read_attribute("NumberOfBunches").value
                if self.currPetraCurrent >= 50:
                    self.statusGlobal = 1
                elif self.currPetraCurrent is None:
                    self.currPetraCurrent = 0.0
                    self.statusGlobal = 0    
                else:
                    self.statusGlobal = 0    
            except:
                print("Error reading PETRA globals, recreating device proxies", sys.exc_info())
            #Mono
            try:
                self.currentMonoEnergy = float(self.devMono.read_attribute("Position").value)
                if self.currentMonoEnergy < 0.1:
                    self.currentMonoEnergy = 12000
                
            except:
                print("Error reading Mono, recreating device proxies", sys.exc_info())
                self.createServers()
            try:
                self.stateVacuum = str(self.devVacuum.state())
            except:
                print("Error reading vacuum, recreating device proxies", sys.exc_info())

            #FastShutter
            try:
                self.statusShutterFS = self.devFastShutter.read_attribute("Value").value
            except:
                print("Error reading fastshutter, recreating device proxies", sys.exc_info())


    def fetch_url(self,url,timeout=3,retries=10):
        try:
            result=urllib.request.urlopen(url,None,timeout).readlines()
        except:
            print("PetraThread: Error reading URL", url)
            print(sys.exc_info())
            

    def closeBS0(self):
        if not self.simulationMode:
            self.statusShutter = "MOVING"
            self.formerStatusBS0 = self.statusShutterBS0
            self.fetch_url("https://ics.desy.de//tineinterface/?action=write&deviceName=closeABS_BS11_0")
            time.sleep(3)
        else:
            self.bs0StatusProxy.write_attribute("displayState",1) #CLOSED
            

    def closeBS1(self):
        if not self.simulationMode:
            print("Closing BS1")
            self.statusShutter = "MOVING"
            self.formerStatusBS1 = self.statusShutterBS1
            self.fetch_url("https://ics.desy.de//tineinterface/?action=write&deviceName=closeBS11_1")
            time.sleep(3)
        else:
            self.bs1StatusProxy.write_attribute("displayState",1) #CLOSED
            
    def openBS0(self):
        if not self.simulationMode:
            print("Opening BS0")
            self.statusShutter = "MOVING"
            self.formerStatusBS0 = self.statusShutterBS0
            self.fetch_url("https://ics.desy.de//tineinterface/?action=write&deviceName=openABS_BS11_0")
            time.sleep(3)
        else:
            self.bs0StatusProxy.write_attribute("displayState",3) #OPEN
        
    def openBS1(self):
        if not self.simulationMode:
            print("Opening BS1")
            self.statusShutter = "MOVING"
            self.formerStatusBS1 = self.statusShutterBS1
            self.fetch_url("https://ics.desy.de//tineinterface/?action=write&deviceName=openBS11_1")
            time.sleep(3)
        else:
            self.bs1StatusProxy.write_attribute("displayState",3) #OPEN
            
    def breakInterlockOH(self):
        if not self.simulationMode:
            print("Opening OH")
            self.fetch_url("https://ics.desy.de//tineinterface/?action=write&deviceName=G11_1_AbrkIntrlk")

    def breakInterlockEH(self):
        if not self.simulationMode:
            print("Opening EH")
            self.fetch_url("https://ics.desy.de//tineinterface/?action=write&deviceName=G11_2_AbrkIntrlk")

    def setFilter1(self,position):
        try:
            self.filterProxy.write_attribute("Filter1Position", int(position))
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        time.sleep(0.2)
        self.stateFilter = str(self.filterProxy.state())

    def setFilter2(self,position):
        try:
            self.filterProxy.write_attribute("Filter2Position", int(position))
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        time.sleep(0.2)
        self.stateFilter = str(self.filterProxy.state())
        
    def setFilter3(self,position):
        try:
            self.filterProxy.write_attribute("Filter3Position", int(position))
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        time.sleep(0.2)
        self.stateFilter = str(self.filterProxy.state())
        
    def setFilters(self, positions):
        try:
            self.filterProxy.write_attribute("Filter1Position", positions[0])
            self.filterProxy.write_attribute("Filter2Position", positions[1])
            self.filterProxy.write_attribute("Filter3Position", positions[2])
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        time.sleep(0.2)
        self.stateFilter = str(self.filterProxy.state())
        
    def setFilterTransmission(self,transmission): #in percent
        try:
            self.filterProxy.write_attribute("SelectTransmission", float(transmission/100.))
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        time.sleep(0.2)
        self.stateFilter = str(self.filterProxy.state())
        return self.filterProxy.read_attribute("SelectTransmission").w_value

    def stopFilters(self):
        try:
            self.devFilter1Z.command_inout("AbortMove")
            self.devFilter2Z.command_inout("AbortMove")
            self.devFilter3Z.command_inout("AbortMove")
            self.devFilter1Z.write_attribute("PIDactive", 1)
            self.devFilter2Z.write_attribute("PIDactive", 1)
            self.devFilter3Z.write_attribute("PIDactive", 1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        self.stateFilter = str(self.filterProxy.state())

    def getDesiredFilterTransmission(self):
        return self.filterProxy.read_attribute("SelectTransmission").w_value * 100.0
    
    def setDirectBeamTransmission(self):
        try:
            self.prevTransmission = self.filterProxy.read_attribute("CurrentTransmission").value
            print("setting transmission to ",float(self.directBeamTransmission))
            self.filterProxy.write_attribute("SelectTransmission", float(self.directBeamTransmission))
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        time.sleep(0.2)
        self.stateFilter = str(self.filterProxy.state())
        while self.stateFilter == "MOVING":
            pass
        print("Setting direct beam transmission finished")
        
    def unsetDirectBeamTransmission(self):
        try:
            print("resetting transmission to ",float(self.prevTransmission))
            self.filterProxy.write_attribute("SelectTransmission", float(self.prevTransmission))
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
        time.sleep(0.2)
        self.stateFilter = str(self.filterProxy.state())
        while self.stateFilter == "MOVING":
            pass
        print("Resetting transmission finished")
        
        
if __name__ == "__main__":
    myPETRA = PetraThread()
