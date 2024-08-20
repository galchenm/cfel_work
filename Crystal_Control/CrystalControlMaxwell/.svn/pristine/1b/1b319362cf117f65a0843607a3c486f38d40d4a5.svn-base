# -*- coding: utf-8 -*-
from PyQt4.QtCore import SIGNAL, QThread
import time
from PyTango import DeviceProxy
from simulationDevice import SimulationDevice
import sys
class EnergyThread(QThread):

    # A thread is started by calling QThread.start() never by calling run() directly!
    def __init__(self, energyServer, simulation = False):
        QThread.__init__(self)
        #self.MainWindow = mainwindowPassing
        print("Energy thread: Starting thread")
        self.simulation = simulation
        self.state = "OFF"
        self.currentEnergy = 0
        self.currentEnergySet = 0
        self.controlVerticalCoating = False
        self.controlHorizontalCoating = False
        self.controlUndulatorHarmonic = False
        self.hysteresisMode = False
        self.beamSize = -1
        self.beamSizes = {-1: 200.0, 0: 200.0, 1: 200.0, 2: 100.0, 3: 50.0, 4: 20.0, 5: 9.0}
        self.beamSizeNames = {-1: "Unknown", 0: "Flat", 1: "200x200", 2: "100x100", 3: "50x50", 4: "20x20", 5: "4x9"}
        
        self.prevState = "OFF"
        if not self.simulation:
            self.energyProxy = DeviceProxy(energyServer)
        else:
            print("Energy thread in simulation mode")
            self.energyProxy = SimulationDevice()
            self.energyProxy.write_attribute("Energy",12000)
            self.energyProxy.write_attribute("ControlVerticalCoating",True)
            self.energyProxy.write_attribute("ControlHorizontalCoating",True)
            self.energyProxy.write_attribute("ControlUndulatorHarmonic",True)
            self.energyProxy.write_attribute("HysteresisMode",True)
    def stop(self):
        print("Energy thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own

    def join(self, timeout=None):
        print("Energy thread: join method")
        self.alive = False

    def run(self):
        self.alive = True
        while self.alive:
            if not self.simulation:
                try:
                    self.state = str(self.energyProxy.state())
                    self.currentEnergy = self.energyProxy.read_attribute("Energy").value
                    self.currentEnergySet = self.energyProxy.read_attribute("Energy").w_value
                    self.beamSize = self.energyProxy.read_attribute("BeamSize").value
                    #self.controlVerticalCoating = self.energyProxy.read_attribute("ControlVerticalCoating").value
                    #self.controlHorizontalCoating = self.energyProxy.read_attribute("ControlHorizontalCoating").value
                    #self.controlUndulatorHarmonic = self.energyProxy.read_attribute("ControlUndulatorHarmonic").value
                    #self.hysteresisMode = self.energyProxy.read_attribute("HysteresisMode").value
                    
                    if self.prevState == "ON" and self.state == "MOVING":
                        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Energy change started")
                    elif self.prevState == "MOVING" and self.state == "ON":
                        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Energy change finished")
                        
                    self.prevState = self.state
                except:
                    print(sys.exc_info())
            time.sleep(0.5)

    def setEnergy(self,energy):
        energy = float(energy)
        try:
            self.energyProxy.write_attribute("AutoBrake", True)
            if not self.state == "MOVING":
                self.energyProxy.write_attribute("Energy",energy)
        except:
             self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setControlVerticalCoating(self,arg):
        try:
            if not self.state == "MOVING":
                self.energyProxy.write_attribute("ControlVerticalCoating",arg)
        except:
             self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setControlHorizontalCoating(self,arg):
        try:
            if not self.state == "MOVING":
                self.energyProxy.write_attribute("ControlHorizontalCoating",arg)
        except:
             self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setControlUndulatorHarmonic(self,arg):
        try:
            if not self.state == "MOVING":
                self.energyProxy.write_attribute("ControlUndulatorHarmonic",arg)
        except:
             self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setHysteresisMode(self,arg):
        try:
            if not self.state == "MOVING":
                self.energyProxy.write_attribute("HysteresisMode",arg)
        except:
             self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

    def setBeamSize(self,arg):
        try:
            if not self.state == "MOVING":
                self.energyProxy.write_attribute("BeamSize",arg)
        except:
             self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])

