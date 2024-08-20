from PyTango import DeviceProxy
from PyQt4 import QtCore, QtGui
import time
from PyQt4.QtCore import SIGNAL, QThread
import queue
from simulationDevice import SimulationDevice


class CryoThread(QThread):

    tangostate = ""
    runMode = ""
    phase = ""
    gasTemp = 300.0
    devStatus = ""
    shutterOpen = None
    cryoRetracted = None

    def __init__(self, servers, simulation = False):
        QThread.__init__(self)
        
        print("Cryo thread: Starting thread")
        
        self.simulationMode = simulation
        if(self.simulationMode):
            self.devCryo = SimulationDevice()
            self.devCryo.write_attribute("GasTemp", 80.0)
            self.devCryo.write_attribute("RunMode", "Run")
            self.devCryo.write_attribute("Phase", "Hold")
            self.devAnnealer = SimulationDevice()
            self.devAnnealer.write_attribute("Value", False)
            self.devRetractor = SimulationDevice()
            self.devRetractor.write_attribute("Value", False)
            self.alive = True
            self.connected = 1
        else:
            try:
                self.devCryo = DeviceProxy(servers[0])
                self.devCryo.ping()
                self.devAnnealer = DeviceProxy(servers[1])
                self.devAnnealer.ping()
                self.devRetractor = DeviceProxy(servers[2])
                self.devRetractor.ping()
                self.alive = True
                print("Cryo thread: started")
                self.connected = 1
            except:
                print("Cryo server not running")
                self.alive = False
                self.connected = 0

    def stop(self):
        print("Cryo thread: Stopping thread")
        self.alive = False
       # self.wait() # waits until run stops on his own

    def run(self):
        while self.alive:
            self.readAttributes()
            time.sleep(1)
        print("Cryo thread: Thread for cryo died")

    def readAttributes(self):
        try:
            self.shutterOpen = not self.devAnnealer.read_attribute("Value").value
        except:
            self.shutterOpen = None
        try:
            self.cryoRetracted = bool(self.devRetractor.read_attribute("Value").value)
        except:
            self.cryoRetracted = None
        try: 
            self.gasTemp = self.devCryo.read_attribute("GasTemp").value
            self.tangostate = str(self.devCryo.state())
            if self.shutterOpen == False:
                self.devStatus = "annealing"
            elif self.tangostate == "RUNNING":
                self.devStatus = self.devCryo.read_attribute("Phase").value
            elif self.tangostate == "ON" or self.tangostate == "INIT":
                self.devStatus = self.devCryo.read_attribute("RunMode").value
            elif self.tangostate == "FAULT":
                self.devStatus = self.devCryo.status()
        except:
            self.tangostate == "FAULT"
            self.devStatus = "not connected"

    def extend(self):
        try:
            self.devAnnealer.write_attribute("Value", False)
        except:
            pass
        try:
            self.devRetractor.write_attribute("Value", 0)
        except:
            pass

    def retract(self):
        try:
            self.devRetractor.write_attribute("Value", 1)
        except:
            pass

    def anneal(self, interval):
        try:
            self.devAnnealer.command_inout("Anneal", interval)
        except:
            pass

