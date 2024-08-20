# -*- coding: utf-8 -*-
import sys
import queue
import time
import inspect
from PyTango import DeviceProxy
from PyQt4.QtCore import SIGNAL, QThread
from simulationDevice import SimulationDevice


class EigerClientCommand(object):
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


class EigerThread(QThread):

    # A thread is started by calling QThread.start() never by calling run() directly!
    #def __init__(self, mainwindowPassing, deviceserver, cmd_q=Queue.Queue(), reply_q=Queue.Queue(), parent = None):
    def __init__(self, deviceserver, cmd_q=queue.Queue(), reply_q=queue.Queue(), parent = None, simulation = False):
        QThread.__init__(self, parent)
        #self.MainWindow = mainwindowPassing
        print("Eiger thread: Starting thread")
        self.cmd_q = cmd_q
        self.reply_q = reply_q
        self.alive = True
        self.simulationMode = simulation
        self.debugMode = 0
        
        self.handlers = {
            EigerClientCommand.setExposureTime: self.setExposureTime,
            EigerClientCommand.setExposurePeriod: self.setExposurePeriod,
            EigerClientCommand.setNumberOfFrames: self.setNumberOfFrames,
#            EigerClientCommand.setNumberOfExposuresPerFrame: self.setNumberOfExposuresPerFrame,
            EigerClientCommand.setDelayTime: self.setDelayTime,
#            EigerClientCommand.setShutterControl: self.setShutterControl,
            EigerClientCommand.setTriggerMode: self.setTriggerMode,
#            EigerClientCommand.setRamDisk: self.setRamDisk,
            EigerClientCommand.setImageFilePath: self.setImageFilePath,
            EigerClientCommand.setImageFilePrefix: self.setImageFilePrefix,
            EigerClientCommand.setImageFileNumber: self.setImageFileNumber,
 #           EigerClientCommand.setImageFileType: self.setImageFileType,
            EigerClientCommand.setPhotonEnergy: self.setPhotonEnergy,
 #           EigerClientCommand.setMXparameter: self.setMXparameter,
            EigerClientCommand.startAcquisition: self.startAcquisition,
            EigerClientCommand.stopAcquisition: self.stopAcquisition,
        }       
        self.stateEiger = ""
        self.statusEiger = ""
        self.exposureTime = 0
        self.exposurePeriod = 0
        self.numberOfFrames = 0
        self.numberOfExposuresPerFrame = 1
        self.delayTime = 0
        self.shutterControl = 0
        self.triggerMode = "ints"
        self.mxParameters = 0
        self.ramDisk = False
        self.imageFilePath = ""
        self.imageFilePrefix = ""
        self.imageFileNumber = 0
        self.imageFileType = 0
        self.imagesPerFile = 1000
        self.lastImageFileName = ""
        self.photonEnergy = 0
        self.thresholdEnergy = 0
        self.roiMode = "disabled"
        self.triggerModes = ["ints", "exte", "exts", "extg", "inte"]
        self.stateFilewriter = ""
        self.stateMonitor = ""
        self.monitorBufferSize = 0
        self.monitorDiscardNew = False
        
        if self.simulationMode:
            print("Eiger in simulation mode")
            self.proxyEiger = SimulationDevice()
            self.proxyFilewriter = SimulationDevice()
            self.proxyMonitor = SimulationDevice()
            self.stateEiger = "ON"
            self.statusEiger = "Eiger is in simulation mode"
            self.proxyEiger.write_attribute("State", "ON")
            self.proxyEiger.write_attribute("Status", "Eiger is in simulation mode")
            self.proxyEiger.write_attribute("Compression", "bslz4")
            self.proxyEiger.write_attribute("CountTime", 0.01)
            self.proxyEiger.write_attribute("FrameTime", 0.01)
            self.proxyEiger.write_attribute("Nimages", 1)
            self.proxyEiger.write_attribute("Ntrigger", 1)
            self.proxyEiger.write_attribute("TriggerMode", "exte")
            self.proxyEiger.write_attribute("TriggerStartDelay", 0.01)
            self.proxyEiger.write_attribute("RoiMode", "disabled")
            self.proxyFilewriter.write_attribute("State", "ON")
            self.proxyFilewriter.write_attribute("Mode", "enabled")
            self.proxyFilewriter.write_attribute("CompressionEnabled", True)
            self.proxyFilewriter.write_attribute("NamePattern", "foo")
            self.proxyFilewriter.write_attribute("NimagesPerFile", 1000)
            self.proxyFilewriter.write_attribute("ImageNrStart", 1)
            self.proxyMonitor.write_attribute("State", "ON")
            self.proxyMonitor.write_attribute("Mode", "enabled")
            self.proxyMonitor.write_attribute("BufferSize", 1)
            self.proxyMonitor.write_attribute("DiscardNew", False)
        else:
            try:
                self.proxyEiger = DeviceProxy(deviceserver[0])
                self.proxyFilewriter = DeviceProxy(deviceserver[1])
                self.proxyMonitor = DeviceProxy(deviceserver[2])
            except:
                pass

    def stop(self):
        print("Eiger thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own

    def run(self):
        print("Eiger thread: started")
        self.alive = True
        while self.alive:
            #QtGui.QApplication.processEvents()
            #self.msleep(500)
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
        print("Eiger thread: Thread for Eiger died")

    def join(self, timeout=None):
        print("Eiger thread: join method")
        self.alive = False

    def readAttributes(self):
        try:
            attributes = self.proxyEiger.read_attributes([
                "State",
                "Status",
                "Compression",
                "CountTime",
                "FrameTime",
                "Nimages",
                "Ntrigger",
                "TriggerMode",
                "TriggerStartDelay",
                "PhotonEnergy",
                "ThresholdEnergy",
                "RoiMode",
            ])
        except:
            self.stateEiger = "UNKNOWN"
            self.statusEiger = "UNKNOWN"
            attributes = []
            print(sys.exc_info(), inspect.currentframe())
        for attr in attributes:
            if attr.name == "State":
                self.stateEiger = str(attr.value)
            elif attr.name == "Status":
                self.statusEiger = attr.value
            elif attr.name == "Compression":
                compression = attr.value
            elif attr.name == "CountTime":
                self.exposureTime = attr.value
            elif attr.name == "FrameTime":
                self.exposurePeriod = attr.value
            elif attr.name == "Nimages":
                self.numberOfFrames = attr.value
            elif attr.name == "TriggerMode":
                self.triggerMode = attr.value
            elif attr.name == "TriggerStartDelay":
                self.delayTime = attr.value
            elif attr.name == "PhotonEnergy":
                self.photonEnergy = attr.value
            elif attr.name == "ThresholdEnergy":
                self.thresholdEnergy = attr.value
            elif attr.name == "Ntrigger":
                self.numberOfTriggers = attr.value
            elif attr.name == "RoiMode":
                self.roiMode = attr.value

        try:
            attributes = self.proxyFilewriter.read_attributes([
                "State",
                "Mode",
                "CompressionEnabled",
                "NamePattern",
                "NimagesPerFile",
                "ImageNrStart",
            ])
        except:
            self.stateFilewriter = "UNKNOWN"
            attributes = []
            print(sys.exc_info(), inspect.currentframe())
        for attr in attributes:
            if attr.name == "State":
                self.stateFilewriter = str(attr.value)
            elif attr.name == "Mode":
                filewriterMode = attr.value
            elif attr.name == "CompressionEnabled":
                compressionEnabled = attr.value
            elif attr.name == "NamePattern":
                self.imageFilePath = "/".join(attr.value.split("/")[:-1])
                self.imageFilePrefix = attr.value.split("/")[-1]
            elif attr.name == "NimagesPerFile":
                self.imagesPerFile = attr.value
            elif attr.name == "ImageNrStart":
                self.imageFileNumber = attr.value

        if self.stateEiger == "UNKNOWN" or self.stateFilewriter == "UNKNOWN":
            pass
        elif filewriterMode == "disabled":
            self.imageFileType = "none"
        elif compressionEnabled == False:
            self.imageFileType = "raw"
        else:
            self.imageFileType = compression

        try:
            attributes = self.proxyMonitor.read_attributes([
                "State",
                "BufferSize",
                "DiscardNew",
            ])
        except:
            self.stateMonitor = "UNKNOWN"
            attributes = []
            print(sys.exc_info(), inspect.currentframe())
        for attr in attributes:
            if attr.name == "State":
                self.stateMonitor = str(attr.value)
            elif attr.name == "BufferSize":
                self.monitorBufferSize = attr.value
            elif attr.name == "DiscardNew":
                self.monitorDiscardNew = attr.value

    def setExposureTime(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Eiger thread: setExposureTime(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("CountTime",arg)
            self.exposureTime = arg
            time.sleep(0.1)
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),sys.exc_info()[1])
    

    def setExposurePeriod(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Eiger thread: setExposurePeriod(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("FrameTime", arg)
            self.exposurePeriod = arg
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
    
    def setNumberOfFrames(self, arg):
        arg = int(arg)
        if self.debugMode:
            print("Eiger thread: setNumberOfFrames(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("Nimages", arg)
            self.numberOfFrames = arg
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setNumberOfTriggers(self, arg):
        arg = int(arg)
        if self.debugMode:
            print("Eiger thread: setNumberOfTriggers(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("Ntrigger", arg)
            self.numberOfTriggers = arg
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setDelayTime(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Eiger thread: setDelayTime(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("TriggerStartDelay", arg)
            self.delayTime = arg
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
 
    def setTriggerMode(self, arg):
        if not arg in self.triggerModes:
            arg = self.triggerModes[int(arg)]
        if self.debugMode:
            print("Eiger thread: setTriggerMode(), arg:", arg)
        try:
            labels = list(self.proxyEiger.get_attribute_config_ex("TriggerMode")[0].enum_labels)
            value = labels.index(arg)
            self.proxyEiger.write_attribute("TriggerMode", value)
            self.triggerMode = arg
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        
    def setImageFilePath(self, arg):
        arg = str(arg)
        if self.debugMode:
            print("Eiger thread: setImageFilePath(), arg:", arg)
        try:
            pattern = self.proxyFilewriter.read_attribute("NamePattern").value
            pattern = pattern.split("/")
            pattern = arg.rstrip("/") + "/" + pattern[-1]
            self.proxyFilewriter.write_attribute("NamePattern", pattern)
            self.imageFilePath = arg
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setImageFilePrefix(self, arg):
        arg = str(arg)
        if self.debugMode:
            print("Eiger thread: setImageFilePrefix(), arg:", arg)
        try:
            pattern = self.proxyFilewriter.read_attribute("NamePattern").value
            pattern = pattern.split("/")
            pattern[-1] = arg
            arg = "/".join(pattern)
            self.proxyFilewriter.write_attribute("NamePattern", arg)
            self.imageFilePrefix = pattern[-1]
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setImageFileNumber(self, arg):
        arg = int(arg)
        if self.debugMode:
            print("Eiger thread: setImageFileNumber(), arg:", arg)
        try:
            self.proxyFilewriter.write_attribute("ImageNrStart", arg)
            self.imageFileNumber = arg
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setNumberOfImagesPerFile(self, arg):
        arg = int(arg)
        if self.debugMode:
            print("Eiger thread: setNumberOfImagesPerFile(), arg:", arg)
        try:
            self.proxyFilewriter.write_attribute("NimagesPerFile", arg)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setImageFileType(self, arg):
        arg = str(arg)
        if self.debugMode:
            print("Eiger thread: setImageFileType(), arg:", arg)
        if arg == "none":
            try:
                labels = list(self.proxyFilewriter.get_attribute_config_ex("Mode")[0].enum_labels)
                value = labels.index("disabled")
                self.proxyFilewriter.write_attribute("Mode", value)
            except:
                print(sys.exc_info(), inspect.currentframe())
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
        else:
            compression = True
            if arg == "raw":
                compression = False
            try:
                labels = list(self.proxyFilewriter.get_attribute_config_ex("Mode")[0].enum_labels)
                value = labels.index("enabled")
                self.proxyFilewriter.write_attribute("Mode", value)
                self.proxyFilewriter.write_attribute("CompressionEnabled", compression)
            except:
                print(sys.exc_info(), inspect.currentframe())
                self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
            if arg in ["lz4", "bslz4"]:
                try:
                    labels = list(self.proxyEiger.get_attribute_config_ex("Compression")[0].enum_labels)
                    value = labels.index(arg)
                except:
                    print(sys.exc_info(), inspect.currentframe())
                    self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
            if arg == "lz4":
                try:
                    self.proxyEiger.write_attribute("Compression", value)
                except:
                    print(sys.exc_info(), inspect.currentframe())
                    self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
            elif arg == "bslz4":
                try:
                    self.proxyEiger.write_attribute("Compression", value)
                except:
                    print(sys.exc_info(), inspect.currentframe())
                    self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setPhotonEnergy(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Eiger thread: setPhotonEnergy(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("PhotonEnergy", arg)
            self.photonEnergy = arg
            time.sleep(0.05)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setRoiMode(self, arg):
        if self.debugMode:
            print("Eiger thread: setPhotonEnergy(), arg:", arg)
        try:
            labels = list(self.proxyEiger.get_attribute_config_ex("RoiMode")[0].enum_labels)
            value = labels.index(arg)
            self.proxyEiger.write_attribute("RoiMode", value)
            self.roiMode = arg
            time.sleep(0.05)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setMonitorMode(self, arg):
        if self.debugMode:
            print("Eiger thread: setMonitorMode(), arg:", bool(arg))
        try:
            labels = list(self.proxyMonitor.get_attribute_config_ex("Mode")[0].enum_labels)
            value = labels.index(arg)
            self.proxyMonitor.write_attribute("Mode", value)
            time.sleep(0.05)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setMonitorBufferSize(self, arg):
        if self.debugMode:
            print("Eiger thread: setMonitorBufferSize(), arg:", int(arg))
        try:
            self.proxyMonitor.write_attribute("BufferSize", int(arg))
            time.sleep(0.05)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setMonitorDiscardNew(self, arg):
        if self.debugMode:
            print("Eiger thread: setMonitorDiscardNew(), arg:", bool(arg))
        try:
            self.proxyMonitor.write_attribute("DiscardNew", bool(arg))
            time.sleep(0.05)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def setMetadataStartAngle(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Eiger thread: setMetadataStartAngle(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("OmegaStart", arg)
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
    
    def setMetadataAngleIncrement(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Eiger thread: setMetadataAngleIncrement(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("OmegaIncrement", arg)
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
    
    def setMetadataBeamOriginX(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Eiger thread: setMetadataBeamOriginX(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("BeamCenterX", arg)
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
    
    def setMetadataBeamOriginY(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Eiger thread: setMetadataBeamOriginY(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("BeamCenterY", arg)
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
    
    def setMetadataDetectorDistance(self, arg):
        arg = float(arg)
        if self.debugMode:
            print("Eiger thread: setMetadataDetectorDistance(), arg:", arg)
        try:
            self.proxyEiger.write_attribute("DetectorDistance", arg)
            time.sleep(0.1)
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])
    
    def startAcquisition(self, arg=None):
        if self.debugMode: print("Eiger thread: Starting acquisition")
        try:
            self.proxyEiger.command_inout("Arm")
            self.stateEiger = str(self.proxyEiger.state())
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def stopAcquisition(self, arg=None):
        if self.debugMode: print("Eiger thread: Stopping acquisition")
        try:
            self.proxyEiger.command_inout("Abort")
            self.proxyEiger.command_inout("Disarm")
            self.stateEiger = str(self.proxyEiger.state())
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])

    def clearMonitorBuffer(self, arg=None):
        if self.debugMode: print("Eiger thread: Clearing monitor buffer")
        try:
            self.proxyMonitor.command_inout("Clear")
        except:
            print(sys.exc_info(), inspect.currentframe())
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), sys.exc_info()[1])



