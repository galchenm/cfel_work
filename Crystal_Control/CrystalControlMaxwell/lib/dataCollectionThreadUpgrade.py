# -*- coding: utf-8 -*-
import sys
import time
import http.client
from PyTango import DeviceProxy, DevState
#from PyTango import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import SIGNAL, QThread, QTimer
from PyQt4.QtGui import qRgb
import queue
import math
from goniometerThread import ClientCommand
import h5py
import os
import numpy
from serialCrystallographyThread import GridScanThread
from liveViewThread import LiveView
#import cbfimage
import filesystem
from scipy import ndimage
import triggerUtils

class DataCollector(QThread):
    ERR_NO_ERROR = 0
    ERR_CANCELLED = 1
    ERR_TYPE_MISMATCH = 2
    ERR_VALUE_OUT_OF_RANGE = 3
    ERR_TIMEOUT = 4
    ERR_ALREADY_RUNNING = 8
    ERR_INTERLOCK_NOT_SET = 9
    ERR_MISALIGNED_BEAMSTOP = 10
    ERR_PIEZOMOTOR_OFFLINE = 11
    ERR_WAIT_CONDITION_TIMEOUT = 12
        
    ERR_MSGS = [
        "Success.",
        "Canceled.",
        "Wrong parameter type.",
        "Parameter value out of range.",
        "Timeout during start up procedure.",
        "",
        "",
        "",
        "Data collection is already running.",
        "Interlock is not set.",
        "Beamstop is not aligned. \n Direct beam on detector! Please contact beamline personnel.",
    ]

    WAIT_CONDITIONS_TIMEOUT = 1000 #*interval
    WAIT_CONDITIONS_INTERVAL = 200 #ms
    WAIT_CONDITIONS_TIMEOUT_NEXTSCANPOINT = 1000 #*interval
    WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT = 100 #ms

    DETECTORTOWER_TOLERANCE = 1.0 #mm
    DETECTOR_ENERGY_TOLERANCE = 500.0 #eV
    GONIOMETER_DEFAULT_SPEED = 130.0 #deg/s

    INFO_TXT = \
        "run type:            regular\n" + \
        "run name:            {name:s}\n" + \
        "start angle:         {startangle:.2f}deg\n" + \
        "frames:              {frames:d}\n" + \
        "degrees/frame:       {degreesperframe:.2f}deg\n" + \
        "exposure time:       {exposuretime:.3f}ms\n" + \
        "energy:              {energy:.3f}keV\n" + \
        "wavelength:          {wavelength:.3f}A\n" + \
        "detector distance:   {detectordistance:.2f}mm\n" + \
        "resolution:          {resolution:.2f}A\n" + \
        "aperture:            {pinholeDiameter:d}um\n" + \
        "focus:               {focus:s}\n" + \
        "filter transmission: {filterTransmission:.3f}%\n" + \
        "filter thickness:    {filterThickness:d}um\n" + \
        "ring current:        {beamCurrent:.3f}mA\n" + \
        "\n" + \
        "For exact flux reading, please consult the staff." + \
        "Typical flux of P11 at 12 keV with 100 mA ring current " + \
        "(beam area is defined by selected pinhole in flat beam, in " + \
        "focused mode typically pinhole of 200 um is used and beam " + \
        "areas is defined by focusing state):\n" + \
        "\n" + \
        "Focus       Beam area (um)  Flux (ph/s)\n" + \
        "Flat        200 x 200       2e12\n" + \
        "Flat        100 x 100       5e11\n" + \
        "Flat          50 x 50       1.25e11\n" + \
        "Flat          20 x 20       2e10\n" + \
        "Focused     200 x 200       4.4e12\n" + \
        "Focused     100 x 100       9.9e12\n" + \
        "Focused       50 x 50       9.9e12\n" + \
        "Focused       20 x 20       9.9e12\n" + \
        "Focused         9 x 4       8.7e12\n"

    # A thread is started by calling QThread.start() never by calling run() directly!
    def __init__(self, detectorTowerThread, goniometerThread, petraThread, piezoThread, eigerThread, liveViewThread, path, parent = None, simulation = False):
        QThread.__init__(self, parent)
        #self.MainWindow = mainwindowPassing
        print("Data collection thread: Starting thread")
        self.myparent = parent
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Preparing data collection...")
        self.alive = True
        self.waitConditionActive = False
        self.dataCollectionActive = False
        self.remainingTime = 0.0
        self.parameters = {
            "filetype": ".cbf",
            "filenumber": 1,
            "startangle": 0.0,
            "frames": 0,
            "degreesperframe": 0.0,
            "exposuretime": 0.0,
            "exposureperiod": 0.0,
            "detectordistance": 0.0,
            "4mMode": False,
            "liveview": False,
            "pinhole": 0,
            "pinholeDiameter": 0,
            "filterTransmission": 1.0,
            "filterThickness": 0.0,
            "beamX": 1262,
            "beamY": 1242,
            "scanPoints": [],
            "sampleoutDistanceWhenBeamcheck": 0,
            "autostartXDS": False,
        }
        self.conditionsList = {
            "BS0open": False,
            "BS1open": False,
            "FSopen": False,
            "BeamstopInPosition": False,
            "DetectorInPosition": False,
            "DetectorThresholdSet": False,
            "GoniometerInPosition": False,
            "CollimatorInPosition": False,
            "ContrastScreenInPosition": False,
            "BeamstopDiodeOK": False,
            "ShieldDown": False,
            "CollectionStarted": False
            }
        
        self.debugMode = 0
        self.detectorTowerThread = detectorTowerThread
        self.goniometerThread = goniometerThread
        self.petraThread = petraThread
        self.piezoThread = piezoThread
        self.eigerThread = eigerThread        
        self.timerOnaxisImage = QTimer(self)
        self.timerOnaxisImage.timeout.connect(self.signalOnaxisImage)        
        self.liveViewThread = liveViewThread
        self.path = path
        self.err = self.ERR_NO_ERROR
        

    def stop(self):
        print("Data collector thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own


    def join(self, timeout=None):
        self.alive = False
        print("Data collector thread: join method")

    def prepareRun(self):
        self.alive = True
        self.starttime = time.time()
        print("Data collector thread: started")
        
        if not self.detectorTowerThread.statusInterlock: #FIXME
            self.err = self.ERR_INTERLOCK_NOT_SET
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"Data collection: Interlock is not set.")
        
        if not self.piezoThread.pinholeAboveMinimumZ:
            self.err = self.ERR_VALUE_OUT_OF_RANGE
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"Data collection: No pinhole selected.")
            return

        #set up everything
        self.signalOnaxisImage()
        self.remainingTime = self.parameters["frames"] * self.parameters["exposureperiod"]
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Preparing to start data collection")
        print("Checking wait conditions")

        ###MOveintoWaitConditions
        self.err = self.waitConditions()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Data collection preparations done")
        print("WAIT RETURNED", self.err)

        if(self.err == self.ERR_NO_ERROR):
            #start data collection
            self.writeInfo()
            if(self.parameters["degreesperframe"] == 0.0):
                raise Exception(self.ERR_VALUE_OUT_OF_RANGE,"degreesperframe out of range",self.parameters["degreesperframe"])
            self.setEigerParameters()
            self.goniometerThread.setSpeed(self.GONIOMETER_DEFAULT_SPEED)
            self.goniometerThread.setAngle(self.parameters["startangle"])
            time.sleep(0.25)
            while (self.goniometerThread.stateGoniometer == "MOVING"):
                if not self.alive: return
                time.sleep(0.1)
            self.conditionsList["GoniometerInPosition"] = True
            self.emit(SIGNAL("waitConditionsUpdate()"))
            if self.parameters["liveview"]:
                self.liveViewThread.start(self.path.get_path(
                        "/beamline/beamtime/raw/user/sample/rotational_number"))
            self.conditionsList["CollectionStarted"] = True
            self.conditionsList["FSopen"] = True
            self.emit(SIGNAL("waitConditionsUpdate()"))
            self.eigerThread.startAcquisition()
            time.sleep(0.5)
            self.speed = self.parameters["degreesperframe"] * (1.0 / (self.parameters["exposureperiod"]))
            self.stopAngle = self.parameters["startangle"] + (self.parameters["frames"] + 1) * self.parameters["degreesperframe"]


    def run(self):
        self.prepareRun()
        if(self.err == self.ERR_NO_ERROR):
            self.goniometerThread.startAcquisitionRun(self.parameters["startangle"], self.stopAngle, self.speed)
        self.prepareExit()
            

    def prepareExit(self):
            
        if(self.err == self.ERR_NO_ERROR):
            
            self.dataCollectionActive = True
            if(self.parameters["degreesperframe"] != 0.0):
                self.timerOnaxisImage.start(45000.0/self.parameters["degreesperframe"])
            else:
                self.timerOnaxisImage.start(30000)
            
            #data collection running
            infoAdded = False
            path = self.path.get_path(
                    "/beamline/beamtime/raw/user/sample/" +
                    "rotational_number/sample_rotational_number_master.h5")
            while(True):
                if not infoAdded and os.path.isfile(path):
                    self.addH5Info()
                    infoAdded = True
                #end reached
                if(infoAdded and self.eigerThread.stateEiger == "ON"):
                    break
                #abort data collection
                if(self.eigerThread.stateEiger == "FAULT"):
                    self.eigerThread.stopAcquisition()
                    self.goniometerThread.stopMotion()
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Data collection error: Eiger is in FAULT state.")
                    break
                if(not self.alive):
                    self.eigerThread.stopAcquisition()
                    self.goniometerThread.stopMotion()
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Data collection aborted.")
                    break
                #wait
                self.msleep(250)
                self.remainingTime = self.goniometerThread.remainingMoveTime
                    
            #stop data collection
            self.goniometerThread.stopMotion()
            self.timerOnaxisImage.stop()
            while(not infoAdded and self.alive):
                if os.path.isfile(path):
                    self.addH5Info()
                    infoAdded = True
                else:
                    self.msleep(250)
            if self.parameters["autostartXDS"]:
                print("Starting full processing")
                self.startProcessing()
            self.generateTemplate()
            self.dataCollectionActive = False

        elif(self.err > self.ERR_CANCELLED):
            #error
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"Data collection error: "+ str(self.ERR_MSGS[self.err]))
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Data collection error: "+ str(self.ERR_MSGS[self.err]))
        self.detectorTowerThread.shieldUp()
        if self.parameters["liveview"]:
            self.liveViewThread.stop(3.0)
        print("Data collector thread: Thread for Data collector died")

        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Data collection finished.")
        self.alive = False


    def setParameters(self, data):
        if(type(data) != dict):
            return self.ERR_TYPE_MISMATCH
        for key in data:
            self.parameters[key] = data[key]

    def setParameter(self, key, data):
        self.parameters[key] = data

    def signalOnaxisImage(self):
        self.emit(SIGNAL("onaxisImage()"))
        
    def setEigerParameters(self):
        if self.parameters["4mMode"]:
            self.eigerThread.setRoiMode("4M")
        else:
            self.eigerThread.setRoiMode("disabled")
        self.eigerThread.setTriggerMode("exts")
        self.eigerThread.setExposureTime(self.parameters["exposuretime"])
        self.eigerThread.setExposurePeriod(self.parameters["exposuretime"])
        self.eigerThread.setImageFileType("bslz4")
        self.eigerThread.setNumberOfImagesPerFile(1000)
        self.eigerThread.setNumberOfFrames(self.parameters["frames"])
        self.eigerThread.setNumberOfTriggers(1)
        self.eigerThread.setDelayTime(0.004)
        self.eigerThread.setMetadataStartAngle(self.parameters["startangle"])
        self.eigerThread.setMetadataAngleIncrement(self.parameters["degreesperframe"])
        self.eigerThread.setMetadataBeamOriginX(self.parameters["beamX"])
        self.eigerThread.setMetadataBeamOriginY(self.parameters["beamY"])
        self.eigerThread.setMetadataDetectorDistance(self.parameters["detectordistance"] / 1000.0)
        self.eigerThread.setImageFileNumber(1)
        self.eigerThread.setImageFilePrefix(self.path.get_path(
                "sample_rotational_number"))
        self.eigerThread.setImageFilePath(self.path.get_path(
                "/beamtime/raw/user/sample/rotational_number/"))
        time.sleep(0.1)

    def waitConditions(self):
        if(not self.detectorTowerThread.statusInterlock):
            return self.ERR_INTERLOCK_NOT_SET
        if(self.waitConditionActive):
            return self.ERR_ALREADY_RUNNING
        self.waitConditionActive = True
        waitConditionTimeOut = 0
        while(True):
            if not self.alive: break
            #Shutter
            if(self.goniometerThread.statusFastShutter):
                print("Closing FS")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Closing FS")
                self.goniometerThread.closeShutter()
            #BS0
            if(not self.petraThread.statusShutterBS0):
                print("opening BS0")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Opening BS0")
                self.petraThread.openBS0()
            else:
                self.conditionsList["BS0open"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #BS1
            if(not self.petraThread.statusShutterBS1):
                self.petraThread.openBS1()
            else:
                self.conditionsList["BS1open"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Beamstop
            if (self.piezoThread.beamstopXInOut == "Out"):
                if (str(self.piezoThread.proxyPiezoBeamstopX.state()) == "ON"):
                    self.piezoThread.moveBeamStopIn()
            elif (self.piezoThread.beamstopXInOut == "In"):
                self.conditionsList["BeamstopInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #DetectorTower
            if(self.parameters["detectordistance"] > self.detectorTowerThread.currentPositionDetectorTowerServer + self.DETECTORTOWER_TOLERANCE or \
                    self.parameters["detectordistance"] < self.detectorTowerThread.currentPositionDetectorTowerServer - self.DETECTORTOWER_TOLERANCE):
                if(self.parameters["detectordistance"] < self.detectorTowerThread.minPositionDetectorTowerServer + 0.1):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Invalid detector distance (value out of range).")
                    return self.ERR_VALUE_OUT_OF_RANGE
                elif(self.parameters["detectordistance"] > self.detectorTowerThread.maxPositionDetectorTowerServer - 0.1):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Invalid detector distance (value out of range).")
                    return self.ERR_VALUE_OUT_OF_RANGE
                elif(self.detectorTowerThread.stateDetectorTower == "ON"):
                    print("Moving detector tower")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving detector tower.")
                    self.detectorTowerThread.setPositionDetectorTower(self.parameters["detectordistance"])
            else:
                self.conditionsList["DetectorInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Eiger
            if(self.petraThread.currentMonoEnergy > (self.eigerThread.photonEnergy + self.DETECTOR_ENERGY_TOLERANCE) or \
                self.petraThread.currentMonoEnergy < (self.eigerThread.photonEnergy - self.DETECTOR_ENERGY_TOLERANCE)):
                if(str(self.eigerThread.proxyEiger.state()) == "ON"):
                    print("Setting pilatus threshold")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Setting Eiger energy threshold.")
                    if self.petraThread.currentMonoEnergy > 5500:
                        self.eigerThread.setPhotonEnergy(self.petraThread.currentMonoEnergy)
                    else:
                        self.eigerThread.setPhotonEnergy(5500)
                    time.sleep(1.5)
                    conditions = False
                    self.conditionsList["DetectorThresholdSet"] = False
            elif (str(self.eigerThread.proxyEiger.state()) == "ON"):
                self.conditionsList["DetectorThresholdSet"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            elif(not str(self.eigerThread.proxyEiger.state()) == "ON"):
                self.conditionsList["DetectorThresholdSet"] = False
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Pinhole
            if(self.parameters["pinhole"] != self.piezoThread.currentPinholePosition):
                if(str(self.piezoThread.proxyPiezoPinholeZ.state()) == "ON"):
                    print("Setting pinhole")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Setting pinhole.")
                    self.piezoThread.setPinhole(self.parameters["pinhole"])
                conditions = False
            #Collimator
            if(not self.piezoThread.collimatorInPlace):
                if(str(self.piezoThread.proxyPiezoCollimatorZ.state()) == "ON"):
                    print("Moving collimator in")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving collimator in.")
                    self.piezoThread.collimatorIn()
            else:
                self.conditionsList["CollimatorInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #YAG/Diode #FIXME
           # if(self.piezoThread.currentYAGScreenPosition != "Out"):
           #     if(self.piezoThread.stateScreen == "ON"):
           #         self.piezoThread.screenOut()
           #     conditions = False
           # else:
            #ContrastScreen #FIXME
            if(self.goniometerThread.positionContrastscreen):
                self.goniometerThread.moveContrastScreenOut()
                
            else:
                self.conditionsList["ContrastScreenInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #BeamstopDiode
            if(not self.detectorTowerThread.interlockWasBroken):
                self.conditionsList["BeamstopDiodeOK"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            elif(self.conditionsList["BS1open"] and self.conditionsList["BS0open"]) and \
                    (not self.conditionsList["BeamstopDiodeOK"] and self.detectorTowerThread.shieldIsUp and \
                     self.conditionsList["BeamstopInPosition"]):
                print("Checking if beamstop OK")
                #Move the sample to safety first
                currentGonioY = self.goniometerThread.currentPositionKohzuGoniometerY
                self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY - self.parameters["sampleoutDistanceWhenBeamcheck"])
                time.sleep(0.2)
                while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                    time.sleep(0.1)
                if(not self.goniometerThread.statusFastShutter):
                    self.goniometerThread.openShutter()
                time.sleep(0.5)
                if(self.detectorTowerThread.diodeThresholdOK):
                    print("Beamstop OK")
                    self.goniometerThread.closeShutter()
                    self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY)
                    time.sleep(0.2)
                    self.detectorTowerThread.interlockWasBroken = False
                    self.conditionsList["BeamstopDiodeOK"] = True
                    self.emit(SIGNAL("waitConditionsUpdate()"))
                    while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                        time.sleep(0.1)
                else:
                    self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY)
                    time.sleep(0.2)
                    while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                        time.sleep(0.1)
                    return self.ERR_MISALIGNED_BEAMSTOP
            #Guillotine
            if(self.conditionsList["BeamstopDiodeOK"]):
                if(not self.detectorTowerThread.shieldIsDown):
                    self.detectorTowerThread.shieldDown()
                else:
                    self.conditionsList["ShieldDown"] = True
                    self.emit(SIGNAL("waitConditionsUpdate()"))
            #check end conditions
            if (self.conditionsList["BS0open"] and \
                self.conditionsList["BS1open"] and \
                self.conditionsList["BeamstopDiodeOK"] and \
                self.conditionsList["BeamstopInPosition"] and \
                self.conditionsList["DetectorInPosition"] and \
                self.conditionsList["CollimatorInPosition"] and \
                self.conditionsList["DetectorThresholdSet"] and \
                self.conditionsList["CollimatorInPosition"] and \
                self.conditionsList["ContrastScreenInPosition"] and \
                self.conditionsList["ShieldDown"]):
                self.waitConditionActive = False
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_NO_ERROR
                 
            #if(conditions):
            #    self.waitConditionActive = False
            #    self.emit(SIGNAL("waitConditionsUpdate()"))
            #    return self.ERR_NO_ERROR
            
            waitConditionTimeOut += 1
            if(waitConditionTimeOut >= self.WAIT_CONDITIONS_TIMEOUT):
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_WAIT_CONDITION_TIMEOUT
            if(not self.alive):
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_CANCELLED
            
            self.msleep(self.WAIT_CONDITIONS_INTERVAL)

        return self.ERR_CANCELLED

    def startProcessing(self):
        #creation will fail if beamtime folder, slurm reservation or
        #bl-fs mount on the compute nodes can not be found
        try:
            btHelper = triggerUtils.Trigger()
        except:
            print(sys.exc_info())
            return

        energy = self.petraThread.currentMonoEnergy / 1000.
        wavelength = 12.3984 / energy #in Angstrom
        res = wavelength / (2. * math.sin(0.5 * math.atan(
                (311. / 2.) / self.parameters["detectordistance"])))
        frames = self.parameters["frames"]
        imagepath = self.path.get_path(
                "/central/beamtime/raw/user/sample/rotational_number/" +
                "sample_rotational_number_master.h5")
        processpath = "/beamline/p11/current" + self.path.get_path(
                "/processed/user/sample/rotational_number/xdsapp")

        #create processing folder with 0o777
        self.path.get_path("/beamline/beamtime/processed/user/sample/" +
                "rotational_number/xdsapp", force=True)
        #add to datasets.txt for presenterd
        try:
            f = open(self.path.get_path(
                    "/beamline/beamtime/processed/datasets.txt"), "a")
            f.write(self.path.get_path(
                    "user/sample/rotational_number/xdsapp\n").lstrip("/"))
            f.close()
        except:
            print(sys.exc_info())

        #create call
        ssh = btHelper.get_ssh_command()
        sbatch = btHelper.get_sbatch_command(
            jobname_prefix = "xdsapp",
            job_dependency = "",
            logfile_path = processpath + "/xdsapp.log"
        )
        cmd = ("/asap3/petra3/gpfs/common/p11/processing/xdsapp_sbatch.sh " + \
                "{imagepath:s} {processpath:s} {res:f}").format(
            imagepath = imagepath,
            processpath = processpath,
            res = res
        )
        print(cmd)
        os.system("{ssh:s} \"{sbatch:s} --wrap \\\"{cmd:s}\\\"\"".format(
            ssh = ssh,
            sbatch = sbatch,
            cmd = cmd
        ))

    def writeInfo(self):
        path = self.path.get_path("/beamline/beamtime/raw/user/sample" +
                "/rotational_number", force=True)
        energy = self.petraThread.currentMonoEnergy/1000.
        wavelength = 12.3984/(energy) #in Angstrom
        resolution = wavelength/(2.*math.sin(0.5*math.atan((311./2.)/ self.parameters["detectordistance"])))
        output = self.INFO_TXT.format(
            name = self.path.get_path("sample_rotational_number"),
            startangle = self.parameters["startangle"],
            frames = self.parameters["frames"],
            degreesperframe = self.parameters["degreesperframe"],
            exposuretime = self.parameters["exposureperiod"] * 1000,
            energy = energy,
            wavelength = wavelength,
            detectordistance = self.parameters["detectordistance"],
            resolution = resolution,
            pinholeDiameter = int(self.parameters["pinholeDiameter"]),
            focus = self.parameters["focus"],
            filterTransmission = self.parameters["filterTransmission"]*100,
            filterThickness = int(self.parameters["filterThickness"]),
            beamCurrent = self.parameters["beamCurrent"]
        )
        try:
            f = open(path + "/info.txt", "w")
            f.write(output)
            f.close()
        except:
            print(sys.exc_info()[1])
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Unable to write info file.")

    def generateTemplate(self):
        cmd = "\"sleep 20; module load xdsapp/3.0.8; cd '{processpath:s}'; " + \
                "generate_XDS.INP '{imagepath:s}'\" >/dev/null 2>&1\n"
        processpath = self.path.get_path("/beamline/beamtime/processed" +
                "/user/sample/rotational_number/manual", force=True)
        imagepath = self.path.get_relative_path(
                "/beamline/beamtime/raw" +
                "/user/sample/rotational_number/",
                "/beamline/beamtime/processed" +
                "/user/sample/rotational_number/manual/")
        imagepath += self.path.get_path("sample_rotational_number_master.h5")
        os.system("ssh -n -f p11user@haspp11eval01 " +
                cmd.format(imagepath=imagepath, processpath=processpath))
       

    def addH5Info(self):
        imagepath = self.path.get_path(
                "/beamline/beamtime/raw/user/sample/rotational_number/" +
                "sample_rotational_number_master.h5")
        time.sleep(0.5)
        print("add h5 info")
        try:
            f = h5py.File(imagepath, "r+")
            #source and instrument
            g = f.create_group(u"entry/source")
            g.attrs[u"NX_class"] = numpy.array(u"NXsource", dtype="S")
            g.create_dataset(u"name", data=numpy.array(u"PETRA III, DESY", dtype="S"))
            g = f.get(u"entry/instrument")
            g.create_dataset(u"name", data=numpy.array(u"P11", dtype="S"))
            #attenuator
            g = f.create_group(u"entry/instrument/attenuator")
            g.attrs[u"NX_class"] = numpy.array(u"NXattenuator", dtype="S")
            ds = g.create_dataset(u"thickness", dtype="f8",
                    data=float(self.parameters["filterThickness"])/1000000)
            ds.attrs[u"units"] = numpy.array(u"m", dtype="S")
            ds = g.create_dataset(u"type", data=numpy.array(u"Aluminum", dtype="S"))
            ds = g.create_dataset(u"attenuator_transmission", dtype="f8",
                    data=float(self.parameters["filterTransmission"]))
            #fix rotation axis and detector orientation
            ds = f.get(u"entry/sample/transformations/omega")
            ds.attrs[u"vector"] = [1., 0., 0.]
            ds = f.get(u"entry/instrument/detector/module/fast_pixel_direction")
            ds.attrs[u"vector"] = [1., 0., 0.]
            ds = f.get(u"entry/instrument/detector/module/slow_pixel_direction")
            ds.attrs[u"vector"] = [0., 1., 0.]
            #delete phi angle info to avoid confusion
            nodes = [
                "entry/sample/goniometer/phi",
                "entry/sample/goniometer/phi_end",
                "entry/sample/goniometer/phi_range_average",
                "entry/sample/goniometer/phi_range_total"]
            for node in nodes:
                if node in f:
                    del f[node]
            f.close()
        except:
            print(sys.exc_info()[1])
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),
                    "Failed to insert info to H5 file.")

    def collectionTime(self, percent = False):
        return self.goniometerThread.remainingMoveTime(percent)


class ScreeningCollector(QThread):
    ERR_NO_ERROR = 0
    ERR_CANCELLED = 1
    ERR_TYPE_MISMATCH = 2
    ERR_VALUE_OUT_OF_RANGE = 3
    ERR_TIMEOUT = 4
    ERR_ALREADY_RUNNING = 8
    ERR_INTERLOCK_NOT_SET = 9
    ERR_MISALIGNED_BEAMSTOP = 10
    ERR_PIEZOMOTOR_OFFLINE = 11
    ERR_WAIT_CONDITION_TIMEOUT = 12
    
    ERR_MSGS = [
        "Success.",
        "Canceled.",
        "Wrong parameter type.",
        "Parameter value out of range.",
        "Timeout during start up procedure.",
        "",
        "",
        "",
        "Screening is already running.",
        "Interlock is not set.",
        "Beamstop is not aligned. \n Direct beam on detector! Please contact beamline personnel.",
    ]

    WAIT_CONDITIONS_TIMEOUT = 1000 #*interval
    WAIT_CONDITIONS_INTERVAL = 200 #ms
    WAIT_CONDITIONS_TIMEOUT_NEXTSCANPOINT = 1000 #*interval
    WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT = 100 #ms

    DETECTORTOWER_TOLERANCE = 1.0 #mm
    GONIOMETER_TURNBACK_TIME = 0.1 #s
    GONIOMETER_ANGLE_TOLERANCE = 0.05 #deg
    GONIOMETER_DEFAULT_SPEED = 130.0 #deg/s
    DETECTOR_ENERGY_TOLERANCE = 500.0 #eV
    TRAVEL_TIME = 1.5 #s

    INFO_TXT = \
        "run type:            screening\n" + \
        "run name:            {name:s}\n" + \
        "start angle:         {startangle:.2f}deg\n" + \
        "frames:              {frames:d}\n" + \
        "degrees/frame:       {degreesperframe:.2f}deg\n" + \
        "image interval:      {imageinterval:.2f}deg\n" + \
        "exposure time:       {exposuretime:.3f}ms\n" + \
        "energy:              {energy:.3f}keV\n" + \
        "wavelength:          {wavelength:.3f}A\n" + \
        "detector distance:   {detectordistance:.2f}mm\n" + \
        "resolution:          {resolution:.2f}A\n" + \
        "aperture:            {pinholeDiameter:d}um\n" + \
        "focus:               {focus:s}\n" + \
        "filter transmission: {filterTransmission:.3f}%\n" + \
        "filter thickness:    {filterThickness:d}um\n" + \
        "ring current:        {beamCurrent:.3f}mA\n" + \
        "\n" + \
        "For exact flux reading, please consult the staff." + \
        "Typical flux of P11 at 12 keV with 100 mA ring current " + \
        "(beam area is defined by selected pinhole in flat beam, in " + \
        "focused mode typically pinhole of 200 um is used and beam " + \
        "areas is defined by focusing state):\n" + \
        "\n" + \
        "Focus       Beam area (um)  Flux (ph/s)\n" + \
        "Flat        200 x 200       2e12\n" + \
        "Flat        100 x 100       5e11\n" + \
        "Flat          50 x 50       1.25e11\n" + \
        "Flat          20 x 20       2e10\n" + \
        "Focused     200 x 200       4.4e12\n" + \
        "Focused     100 x 100       9.9e12\n" + \
        "Focused       50 x 50       9.9e12\n" + \
        "Focused       20 x 20       9.9e12\n" + \
        "Focused         9 x 4       8.7e12\n"

    # A thread is started by calling QThread.start() never by calling run() directly!
    def __init__(self, detectorTowerThread, goniometerThread, petraThread, piezoThread, eigerThread, liveViewThread, path, parent = None, simulation = False):
        QThread.__init__(self, parent)
        #self.MainWindow = mainwindowPassing
        print("Screening thread: Starting thread")
        self.myparent = parent
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Preparing screening...")
        self.alive = True
        self.waitConditionActive = False
        self.dataCollectionActive = False
        self.remainingTime = 0.0
        self.parameters = { 
            "filetype": ".cbf",
            "filenumber": 0,
            "startangle": 0.0,
            "angles": [0],
            "frames": 1,
            "degreesperframe": 0.0,
            "exposuretime": 0.0,
            "exposureperiod": 0.0,
            "detectordistance": 0.0,
            "4mMode": False,
            "liveview": False,
            "pinhole": 0,
            "pinholeDiameter": 0,
            "filterTransmission": 1.0,
            "filterThickness": 0.0,
            "beamX": 1262,
            "beamY": 1242,
            "scanPoints": [],
            "sampleoutDistanceWhenBeamcheck": 0,
            "autostartMosflm": False,
        }
        self.conditionsList = {
            "BS0open": False,
            "BS1open": False,
            "FSopen": False,
            "BeamstopInPosition": False,
            "DetectorInPosition": False,
            "DetectorThresholdSet": False,
            "GoniometerInPosition": False,
            "CollimatorInPosition": False,
            "ContrastScreenInPosition": False,
            "BeamstopDiodeOK": False,
            "ShieldDown": False,
            "CollectionStarted": False ,
            }
        
        self.debugMode = 0
        self.detectorTowerThread = detectorTowerThread
        self.goniometerThread = goniometerThread
        self.petraThread = petraThread
        self.piezoThread = piezoThread
        self.eigerThread = eigerThread
        self.liveViewThread = liveViewThread
        self.path = path
        self.starttime = time.time()
        self.err = self.ERR_NO_ERROR

    def stop(self):
        print("Screening thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own

    def join(self, timeout=None):
        print("Screening thread: join method")
        self.alive = False

    def run(self):
        self.alive = True
        self.starttime = time.time()
        print("Screening thread: started")
        if not self.detectorTowerThread.statusInterlock: #FIXME
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"Screening: Interlock is not set.")
        if not self.piezoThread.pinholeAboveMinimumZ:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"Screening: No pinhole selected.")
            return
        #set up everything
        self.remainingTime = len(self.parameters["angles"]) * (self.TRAVEL_TIME + (0.001 * self.parameters["exposureperiod"]))
        self.totalTime = self.remainingTime
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Preparing to start screening")
        print("Checking wait conditions")
        if self.parameters["liveview"] and not self.liveViewThread.alive:
            self.liveViewThread.start(self.path.get_path(
                "/beamline/beamtime/raw/user/sample/screening_number"),
                stream=True)
        err = self.waitConditions()
        self.liveViewThread.stop()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Screening preparations done")
        print("WAIT RETURNED", err)
        if(err == self.ERR_NO_ERROR):
            self.setEigerParameters()
            if self.parameters["liveview"] and not self.liveViewThread.alive:
                self.liveViewThread.start(self.path.get_path(
                    "/beamline/beamtime/raw/user/sample/screening_number"),
                    stream=True)
            self.writeInfo()
            #start data collection
            if(self.parameters["degreesperframe"] != 0.0):
                speed = self.parameters["degreesperframe"] * (1.0 / (self.parameters["exposureperiod"]))
                stopAngle = self.parameters["startangle"] + self.parameters["frames"] * self.parameters["degreesperframe"] + speed * self.GONIOMETER_TURNBACK_TIME
            else:
                raise Exception(self.ERR_VALUE_OUT_OF_RANGE,"degreesperframe out of range",self.parameters["degreesperframe"])
            self.eigerThread.startAcquisition()
            self.xdsStarted = False
            self.conditionsList["CollectionStarted"] = True
            self.dataCollectionActive = True
            infoAdded = False
            path = self.path.get_path(
                    "/beamline/beamtime/raw/user/sample/" +
                    "screening_number/sample_screening_number_master.h5")
            for angle in self.parameters["angles"]:
                if not self.alive: break
                print("Now at Phi %8.3f"%angle)
                self.conditionsList["FSopen"] = False
                self.conditionsList["GoniometerInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
                self.signalOnaxisScreeningImage(angle)   
                self.conditionsList["FSopen"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
                time.sleep(0.25)
                print("Moving gonio to",angle+self.parameters["degreesperframe"]+speed*self.GONIOMETER_TURNBACK_TIME)
                self.goniometerThread.startAcquisitionRun(angle, angle+self.parameters["degreesperframe"], speed)
                self.remainingTime -= self.TRAVEL_TIME + 0.001 * self.parameters["exposureperiod"]
                time.sleep(0.25)            
                #data collection running
                while(True):
                    if not infoAdded and os.path.isfile(path):
                        self.addH5Info()
                        infoAdded = True
                    if (self.goniometerThread.stateGoniometer == "MOVING"):
                        time.sleep(0.1)
                        continue
                    #end reached
                    elif (self.goniometerThread.stateGoniometer == "ON"):
                        break
                    if(self.eigerThread.stateEiger == "ON"):
                        break
                    #abort data collection
                    if(self.eigerThread.stateEiger == "FAULT"):
                        self.eigerThread.stopAcquisition()
                        self.goniometerThread.stopMotion()
                        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Screening error: Pilatus is in FAULT state.")
                        break
                    if not self.alive:
                        self.eigerThread.stopAcquisition()
                        self.goniometerThread.stopMotion()
                        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Screening aborted.")
                        break
                    self.msleep(100)
            while(not infoAdded and self.alive):
                if os.path.isfile(path):
                    self.addH5Info()
                    infoAdded = True
                else:
                    self.msleep(250)

            #stop data collection
            self.dataCollectionActive = False
        elif(err > self.ERR_CANCELLED):
            #error
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"Screening error: "+ str(self.ERR_MSGS[err]))
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Screening error: "+ str(self.ERR_MSGS[err]))
        self.detectorTowerThread.shieldUp()
        if self.parameters["liveview"]:
            self.liveViewThread.stop(3.0)
        if self.parameters["autostartMosflm"]:
            self.startProcessing()
        self.msleep(500)
        print("Screening thread: Thread for screening died")
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Screening finished.")
        self.alive = False

    def setParameters(self, data):
        if(type(data) != dict):
            return self.ERR_TYPE_MISMATCH
        for key in data:
            self.parameters[key] = data[key]

    def setParameter(self, key, data):
        self.parameters[key] = data

    def signalOnaxisScreeningImage(self,angle):
        self.emit(SIGNAL("onaxisScreeningImage(int)"),angle)

    def setEigerParameters(self):
        if len(self.parameters["angles"]) > 1:
            angleInc = self.parameters["angles"][1] - self.parameters["angles"][0]
        else:
            angleInc = self.parameters["degreesperframe"]
        if self.parameters["4mMode"]:
            self.eigerThread.setRoiMode("4M")
        else:
            self.eigerThread.setRoiMode("disabled")
        self.eigerThread.setTriggerMode("exts")
        self.eigerThread.setExposureTime(self.parameters["exposuretime"])
        self.eigerThread.setExposurePeriod(self.parameters["exposuretime"])
        self.eigerThread.setImageFileType("bslz4")
        self.eigerThread.setNumberOfImagesPerFile(1000)
        self.eigerThread.setNumberOfFrames(1)
        self.eigerThread.setNumberOfTriggers(len(self.parameters["angles"]))
        self.eigerThread.setDelayTime(0.004)
        self.eigerThread.setMetadataStartAngle(self.parameters["startangle"])
        self.eigerThread.setMetadataAngleIncrement(angleInc)
        self.eigerThread.setMetadataBeamOriginX(self.parameters["beamX"])
        self.eigerThread.setMetadataBeamOriginY(self.parameters["beamY"])
        self.eigerThread.setMetadataDetectorDistance(self.parameters["detectordistance"] / 1000.0)
        self.eigerThread.setImageFileNumber(1)
        self.eigerThread.setImageFilePrefix(self.path.get_path(
                "sample_screening_number"))
        self.eigerThread.setImageFilePath(self.path.get_path(
                "/beamtime/raw/user/sample/screening_number/"))
        time.sleep(0.1)

    def moveToNextScanPoint(self,point):
        nextPointX = point[0]
        #nextPointY = point[1]
        nextPointFlexureX = point[1]
        nextPointFlexureY = point[2]
        #self.goniometerThread.setPositionFlexureY(nextPointY)
        self.goniometerThread.setPositionFlexureX(nextPointFlexureX)
        self.goniometerThread.setPositionFlexureY(nextPointFlexureY)
        self.goniometerThread.setPositionKohzuGoniometerY(nextPointX)
        
        time.sleep(0.5)
        if(self.waitConditionActive):
            return self.ERR_ALREADY_RUNNING
        self.waitConditionActive = True
        waitConditionTimeOut = 0
        
        while(True):
            conditions = True
            #Shutter
            #if(self.goniometerThread.stateKohzuGoniometerY == "MOVING" or self.goniometerThread.stateKohzuGoniometerZ == "MOVING"):
            if(self.goniometerThread.stateFlexureX == "MOVING" or self.goniometerThread.stateFlexureY == "MOVING" or self.goniometerThread.stateKohzuGoniometerY == "MOVING"):
                conditions = False
 
            #check end conditions
            if(conditions):
                self.waitConditionActive = False
                return self.ERR_NO_ERROR
            waitConditionTimeOut += 1
            if(waitConditionTimeOut >= self.WAIT_CONDITIONS_TIMEOUT_NEXTSCANPOINT):
                return self.ERR_WAIT_CONDITION_TIMEOUT_NEXTSCANPOINT
            if(not self.alive):
                return self.ERR_CANCELLED
            self.msleep(self.WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT)

    def waitConditions(self):
        if(not self.detectorTowerThread.statusInterlock): #FIXME
            return self.ERR_INTERLOCK_NOT_SET
        
        if(self.waitConditionActive):
            return self.ERR_ALREADY_RUNNING
        self.waitConditionActive = True
        waitConditionTimeOut = 0
        while(True):
            if not self.alive: break
            conditions = True
            #Shutter
            if(self.goniometerThread.statusFastShutter):
                print("Closing FS")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Closing FS")
                self.goniometerThread.closeShutter()
                conditions = False
            #BS0
            #if 0:
            if(not self.petraThread.statusShutterBS0):
                print("opening BS0")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Opening BS0")
                self.petraThread.openBS0()
                conditions = False
            else:
                self.conditionsList["BS0open"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #BS1
            if(not self.petraThread.statusShutterBS1):
            #if 0: 
                self.petraThread.openBS1()
                conditions = False
            else:
                self.conditionsList["BS1open"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Beamstop
            if (self.piezoThread.beamstopXInOut == "Out"):
                if (str(self.piezoThread.proxyPiezoBeamstopX.state()) == "ON"):
                    self.piezoThread.moveBeamStopIn()
            elif (self.piezoThread.beamstopXInOut == "In"):
                self.conditionsList["BeamstopInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #DetectorTower
            if(self.parameters["detectordistance"] > self.detectorTowerThread.currentPositionDetectorTowerServer + self.DETECTORTOWER_TOLERANCE or \
                    self.parameters["detectordistance"] < self.detectorTowerThread.currentPositionDetectorTowerServer - self.DETECTORTOWER_TOLERANCE):
                if(self.parameters["detectordistance"] < self.detectorTowerThread.minPositionDetectorTowerServer + 0.1):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Invalid detector distance (value out of range).")
                    return self.ERR_VALUE_OUT_OF_RANGE
                elif(self.parameters["detectordistance"] > self.detectorTowerThread.maxPositionDetectorTowerServer - 0.1):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Invalid detector distance (value out of range).")
                    return self.ERR_VALUE_OUT_OF_RANGE
                elif(self.detectorTowerThread.stateDetectorTower == "ON"):
                    print("Moving detector tower")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving detector tower.")
                    self.detectorTowerThread.setPositionDetectorTower(self.parameters["detectordistance"])
                conditions = False
            else:
                self.conditionsList["DetectorInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Eiger
            if(self.petraThread.currentMonoEnergy > (self.eigerThread.photonEnergy + self.DETECTOR_ENERGY_TOLERANCE) or \
                self.petraThread.currentMonoEnergy < (self.eigerThread.photonEnergy - self.DETECTOR_ENERGY_TOLERANCE)):
                if(str(self.eigerThread.proxyEiger.state()) == "ON"):
                    print("Setting Eiger threshold")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Setting Eiger energy threshold.")
                    if self.petraThread.currentMonoEnergy > 5500:
                        self.eigerThread.setPhotonEnergy(self.petraThread.currentMonoEnergy)
                    else:
                        self.eigerThread.setPhotonEnergy(5500)
                    time.sleep(1.5)
                    conditions = False
                    self.conditionsList["DetectorThresholdSet"] = False
            elif (str(self.eigerThread.proxyEiger.state()) == "ON"):
                self.conditionsList["DetectorThresholdSet"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            elif (not (str(self.eigerThread.proxyEiger.state()) == "ON")):
                conditions = False
                self.conditionsList["DetectorThresholdSet"] = False
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Pinhole
            if(self.parameters["pinhole"] != self.piezoThread.currentPinholePosition):
                if(str(self.piezoThread.proxyPiezoPinholeZ.state()) == "ON"):
                    print("Setting pinhole")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Setting pinhole.")
                    self.piezoThread.setPinhole(self.parameters["pinhole"])
                conditions = False
            #Collimator
            if(not self.piezoThread.collimatorInPlace):
                if(str(self.piezoThread.proxyPiezoCollimatorZ.state()) == "ON"):
                    print("Moving collimator in")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving collimator in.")
                    self.piezoThread.collimatorIn()
                conditions = False
            else:
                self.conditionsList["CollimatorInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #YAG/Diode #FIXME
           # if(self.piezoThread.currentYAGScreenPosition != "Out"):
           #     if(self.piezoThread.stateScreen == "ON"):
           #         self.piezoThread.screenOut()
           #     conditions = False
           # else:
                
            #ContrastScreen #FIXME
            if(self.goniometerThread.positionContrastscreen):
                self.goniometerThread.moveContrastScreenOut()
                conditions = False
            else:
                self.conditionsList["ContrastScreenInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #BeamstopDiode
            if(not self.detectorTowerThread.interlockWasBroken):
                self.conditionsList["BeamstopDiodeOK"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            elif(self.conditionsList["BS1open"] and self.conditionsList["BS0open"]) and \
                    (not self.conditionsList["BeamstopDiodeOK"] and self.detectorTowerThread.shieldIsUp and \
                     self.conditionsList["BeamstopInPosition"]):
                print("Checking if beamstop OK")
                #Move the sample to safety first
                currentGonioY = self.goniometerThread.currentPositionKohzuGoniometerY
                self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY - self.parameters["sampleoutDistanceWhenBeamcheck"])
                time.sleep(0.2)
                while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                    time.sleep(0.1)
                if(not self.goniometerThread.statusFastShutter):
                    self.goniometerThread.openShutter()
                time.sleep(0.5)
                if(self.detectorTowerThread.diodeThresholdOK):
                    print("Beamstop OK")
                    self.goniometerThread.closeShutter()
                    self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY)
                    time.sleep(0.2)
                    self.detectorTowerThread.interlockWasBroken = False
                    self.conditionsList["BeamstopDiodeOK"] = True
                    self.emit(SIGNAL("waitConditionsUpdate()"))
                    while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                        time.sleep(0.1)
                else:
                    self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY)
                    time.sleep(0.2)
                    while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                        time.sleep(0.1)
                    return self.ERR_MISALIGNED_BEAMSTOP
            #Guillotine
            if(self.conditionsList["BeamstopDiodeOK"]):
                if(not self.detectorTowerThread.shieldIsDown):
                    self.detectorTowerThread.shieldDown()
                else:
                    self.conditionsList["ShieldDown"] = True
                    self.emit(SIGNAL("waitConditionsUpdate()"))
            #check end conditions
            if (self.conditionsList["BS0open"] and \
                self.conditionsList["BS1open"] and \
                self.conditionsList["BeamstopDiodeOK"] and \
                self.conditionsList["BeamstopInPosition"] and \
                self.conditionsList["DetectorInPosition"] and \
                self.conditionsList["CollimatorInPosition"] and \
                self.conditionsList["DetectorThresholdSet"] and \
                self.conditionsList["CollimatorInPosition"] and \
                self.conditionsList["ContrastScreenInPosition"] and \
                self.conditionsList["ShieldDown"]):
                self.waitConditionActive = False
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_NO_ERROR
                 
            #if(conditions):
            #    self.waitConditionActive = False
            #    self.emit(SIGNAL("waitConditionsUpdate()"))
            #    return self.ERR_NO_ERROR
            waitConditionTimeOut += 1
            if(waitConditionTimeOut >= self.WAIT_CONDITIONS_TIMEOUT):
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_WAIT_CONDITION_TIMEOUT
            if(not self.alive):
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_CANCELLED
            
            self.msleep(self.WAIT_CONDITIONS_INTERVAL)

    def startProcessing(self):
        #creation will fail if beamtime folder, slurm reservation or
        #bl-fs mount on the compute nodes can not be found
        try:
            btHelper = triggerUtils.Trigger()
        except:
            print(sys.exc_info())
            return

        energy = self.petraThread.currentMonoEnergy / 1000.
        wavelength = 12.3984 / energy #in Angstrom
        res = wavelength / (2. * math.sin(0.5 * math.atan(
                (311. / 2.) / self.parameters["detectordistance"])))
        frames = len(self.parameters["angles"])
        imagepath = self.path.get_path(
                "/central/beamtime/raw/user/sample/screening_number/")
        filename = self.path.get_path("sample_screening_number_master.h5")
        processpath = "/beamline/p11/current" + self.path.get_path(
                "/processed/user/sample/screening_number/mosflm")

        #create processing folder with 0o777
        self.path.get_path("/beamline/beamtime/processed/user/sample/" +
                "screening_number/mosflm", force=True)
        #add to datasets.txt for presenterd
        try:
            f = open(self.path.get_path(
                    "/beamline/beamtime/processed/datasets.txt"), "a")
            f.write(self.path.get_path(
                    "user/sample/screening_number/mosflm\n").lstrip("/"))
            f.close()
        except:
            print(sys.exc_info())

        #create call
        ssh = btHelper.get_ssh_command()
        sbatch = btHelper.get_sbatch_command(
            jobname_prefix = "mosflm",
            job_dependency = "",
            logfile_path = processpath + "/mosflm.log"
        )
        cmd = ("/asap3/petra3/gpfs/common/p11/processing/mosflm_sbatch.sh " + \
                 "{imagepath:s} {filename:s} {processpath:s} {frames:d} {res:f}").format(
            imagepath = imagepath,
            filename = filename,
            processpath = processpath,
            frames = frames,
            res = res
        )
        print(cmd)
        os.system("{ssh:s} \"{sbatch:s} --wrap \\\"{cmd:s}\\\"\"".format(
            ssh = ssh,
            sbatch = sbatch,
            cmd = cmd
        ))

    def writeInfo(self):
        path = self.path.get_path("/beamline/beamtime/raw/user/sample" +
                "/screening_number", force=True)
        energy = self.petraThread.currentMonoEnergy/1000.
        wavelength = 12.3984/(energy) #in Angstrom
        resolution = wavelength/(2.*math.sin(0.5*math.atan((311./2.)/ self.parameters["detectordistance"])))
        frames = len(self.parameters["angles"])
        imageinterval = 0
        if frames > 1:
            imageinterval = self.parameters["angles"][1] - self.parameters["startangle"]
        output = self.INFO_TXT.format(
            name = self.path.get_path("sample_screening_number"),
            startangle = self.parameters["startangle"],
            frames = frames,
            degreesperframe = self.parameters["degreesperframe"],
            imageinterval = imageinterval,
            exposuretime = self.parameters["exposureperiod"] * 1000,
            energy = energy,
            wavelength = wavelength,
            detectordistance = self.parameters["detectordistance"],
            resolution = resolution,
            pinholeDiameter = int(self.parameters["pinholeDiameter"]),
            focus = self.parameters["focus"],
            filterTransmission = self.parameters["filterTransmission"]*100,
            filterThickness = int(self.parameters["filterThickness"]),
            beamCurrent = self.parameters["beamCurrent"]
        )
        try:
            f = open(path + "/info.txt", "w")
            f.write(output)
            f.close()
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Unable to write info file.")

    def addH5Info(self):
        imagepath = self.path.get_path(
                "/beamline/beamtime/raw/user/sample/screening_number/" +
                "sample_screening_number_master.h5")
        time.sleep(0.5)
        print("add h5 info")
        try:
            f = h5py.File(imagepath, "r+")
            #source and instrument
            g = f.create_group(u"entry/source")
            g.attrs[u"NX_class"] = numpy.array(u"NXsource", dtype="S")
            g.create_dataset(u"name", data=numpy.array(u"PETRA III, DESY", dtype="S"))
            g = f.get(u"entry/instrument")
            g.create_dataset(u"name", data=numpy.array(u"P11", dtype="S"))
            #attenuator
            g = f.create_group(u"entry/instrument/attenuator")
            g.attrs[u"NX_class"] = numpy.array(u"NXattenuator", dtype="S")
            ds = g.create_dataset(u"thickness", dtype="f8",
                    data=float(self.parameters["filterThickness"])/1000000)
            ds.attrs[u"units"] = numpy.array(u"m", dtype="S")
            ds = g.create_dataset(u"type", data=numpy.array(u"Aluminum", dtype="S"))
            ds = g.create_dataset(u"attenuator_transmission", dtype="f8",
                    data=float(self.parameters["filterTransmission"]))
            #delete existing angle info
            nodes = [
                "entry/sample/goniometer/omega",
                "entry/sample/goniometer/omega_end",
                "entry/sample/goniometer/omega_range_average",
                "entry/sample/goniometer/omega_range_total",
                "entry/sample/goniometer/phi",
                "entry/sample/goniometer/phi_end",
                "entry/sample/goniometer/phi_range_average",
                "entry/sample/goniometer/phi_range_total",
                "entry/sample/transformations/omega",
                "entry/sample/transformations/omega_end",
                "entry/sample/transformations/omega_range_average",
                "entry/sample/transformations/omega_range_total"]
            for node in nodes:
                if node in f:
                    del f[node]
            # fix detector orientation
            ds = f.get(u"entry/instrument/detector/module/fast_pixel_direction")
            ds.attrs[u"vector"] = [1., 0., 0.]
            ds = f.get(u"entry/instrument/detector/module/slow_pixel_direction")
            ds.attrs[u"vector"] = [0., 1., 0.]
            #correct angles
            angles = []
            angles_end = []
            for angle in self.parameters["angles"]:
                angles.append(float(angle))
                angles_end.append(float(angle +
                        self.parameters["degreesperframe"]))
            g = f.get("entry/sample/goniometer")
            o = g.create_dataset(u"omega", dtype="f8",
                    data=angles)
            o.attrs["vector"] = [1., 0., 0.]
            g.create_dataset(u"omega_end", dtype="f8",
                    data=angles_end)
            g.create_dataset(u"omega_range_average", dtype="f8",
                    data=float(self.parameters["degreesperframe"]))
            g = f.get("entry/sample/transformations")
            o = g.create_dataset(u"omega", dtype="f8",
                    data=angles)
            o.attrs["vector"] = [1., 0., 0.]
            g.create_dataset(u"omega_end", dtype="f8",
                    data=angles_end)
            g.create_dataset(u"omega_range_average", dtype="f8",
                    data=float(self.parameters["degreesperframe"]))
            f.close()
        except:
            print(sys.exc_info()[1])
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),
                    "Failed to insert info to H5 file.")

    def collectionTime(self, percent = False):
        if percent:
            return 100 * (1 - (self.remainingTime / self.totalTime)) 
        else:
            return self.remainingTime

#fly scane
class GridScreeningCollector(QThread):

    ERR_NO_ERROR = 0
    ERR_CANCELLED = 1
    ERR_TYPE_MISMATCH = 2
    ERR_VALUE_OUT_OF_RANGE = 3
    ERR_TIMEOUT = 4
    ERR_ALREADY_RUNNING = 8
    ERR_INTERLOCK_NOT_SET = 9
    ERR_MISALIGNED_BEAMSTOP = 10
    ERR_PIEZOMOTOR_OFFLINE = 11
    ERR_WAIT_CONDITION_TIMEOUT = 12
    
    ERR_MSGS = [
        "Success.",
        "Canceled.",
        "Wrong parameter type.",
        "Parameter value out of range.",
        "Timeout during start up procedure.",
        "",
        "",
        "",
        "Grid screening is already running.",
        "Interlock is not set.",
        "Beamstop is not aligned. \n Direct beam on detector! Please contact beamline personnel.",
    ]

    WAIT_CONDITIONS_TIMEOUT = 1000 #*interval
    WAIT_CONDITIONS_INTERVAL = 200 #ms
    WAIT_CONDITIONS_TIMEOUT_NEXTSCANPOINT = 1000 #*interval
    WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT = 100 #ms

    DETECTORTOWER_TOLERANCE = 1.0 #mm
    GONIOMETER_TURNBACK_TIME = 0.1 #s
    GONIOMETER_ANGLE_TOLERANCE = 0.05 #deg
    GONIOMETER_DEFAULT_SPEED = 90.0 #deg/s
    DETECTOR_ENERGY_TOLERANCE = 500.0 #eV

    INFO_TXT = \
        "run type:            grid\n" + \
        "run name:            {name:s}\n" + \
        "grid:                {columns:d}x{rows:d}\n" + \
        "angle:               {angle:.2f}deg\n" + \
        "frames:              {frames:d}\n" + \
        "exposure time:       {exposuretime:.3f}ms\n" + \
        "energy:              {energy:.3f}keV\n" + \
        "wavelength:          {wavelength:.3f}A\n" + \
        "detector distance:   {detectordistance:.2f}mm\n" + \
        "resolution:          {resolution:.2f}A\n" + \
        "aperture:            {pinholeDiameter:d}um\n" + \
        "focus:               {focus:s}\n" + \
        "filter transmission: {filterTransmission:.3f}%\n" + \
        "filter thickness:    {filterThickness:d}um\n" + \
        "ring current:        {beamCurrent:.3f}mA\n" + \
        "\n" + \
        "For exact flux reading, please consult the staff." + \
        "Typical flux of P11 at 12 keV with 100 mA ring current " + \
        "(beam area is defined by selected pinhole in flat beam, in " + \
        "focused mode typically pinhole of 200 um is used and beam " + \
        "areas is defined by focusing state):\n" + \
        "\n" + \
        "Focus       Beam area (um)  Flux (ph/s)\n" + \
        "Flat        200 x 200       2e12\n" + \
        "Flat        100 x 100       5e11\n" + \
        "Flat          50 x 50       1.25e11\n" + \
        "Flat          20 x 20       2e10\n" + \
        "Focused     200 x 200       4.4e12\n" + \
        "Focused     100 x 100       9.9e12\n" + \
        "Focused       50 x 50       9.9e12\n" + \
        "Focused       20 x 20       9.9e12\n" + \
        "Focused         9 x 4       8.7e12\n"

    # A thread is started by calling QThread.start() never by calling run() directly!
    def __init__(self, detectorTowerThread, goniometerThread, petraThread, piezoThread, eigerThread, raster, liveViewThread, path, parent = None, simulation = False):
        QThread.__init__(self, parent)
        #self.MainWindow = mainwindowPassing
        print("ISMO collection thread: Starting thread")
        self.myparent = parent
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Preparing ISMO collection...")
        self.alive = True
        self.waitConditionActive = False
        self.dataCollectionActive = False
        self.remainingTime = 0.0
        self.parameters = { 
            "filetype": ".cbf",
            "filenumber": 0,
            "exposuretime": 0.0,
            "exposureperiod": 0.0,
            "detectordistance": 0.0,
            "rows": 0,
            "columns": 0,
            "4mMode": False,
            "liveview": False,
            "pinhole": 0,
            "pinholeDiameter": 0,
            "filterTransmission": 1.0,
            "filterThickness": 0.0,
            "beamX": 1261,
            "beamY": 1269,
            "scanType": 0,
            "scanPoints": [],
            "sampleoutDistanceWhenBeamcheck": 0,
        }
        self.conditionsList = {
            "BS0open": False,
            "BS1open": False,
            "FSopen": False,
            "BeamstopInPosition": False,
            "DetectorInPosition": False,
            "DetectorThresholdSet": False,
            "GoniometerInPosition": False,
            "CollimatorInPosition": False,
            "ContrastScreenInPosition": False,
            "BeamstopDiodeOK": False,
            "ShieldDown": False,
            "CollectionStarted": False ,
            }
        
        self.debugMode = 0
        self.detectorTowerThread = detectorTowerThread
        self.goniometerThread = goniometerThread
        self.petraThread = petraThread
        self.piezoThread = piezoThread
        self.eigerThread = eigerThread        
        self.raster = raster        
        self.liveViewThread = liveViewThread
        self.path = path
        self.centreAngle = 0
        self.timePerSample = 0
        self.degreesPerFrame = 0
        self.starttime = time.time()
        self.numOfSamples = 0
        self.delay = 0.05


    def stop(self):
        print("ISMO collector thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own


    def join(self, timeout=None):
        print("ISMO collector thread: join method")
        self.alive = False


    def run(self):
        self.alive = True
        print("GridScreeningCollector: started")
        if not self.piezoThread.pinholeAboveMinimumZ:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"GridScreeningCollector: No pinhole selected.")
            self.alive = False
            return
        if not self.detectorTowerThread.statusInterlock: #FIXME
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"GridScreeningCollector: Interlock is not set.")
            self.alive = False
            return

        #set up everything
        self.flexureXposition = self.goniometerThread.currentPositionFlexureX
        self.flexureYposition = self.goniometerThread.currentPositionFlexureY
        self.kohzuYposition = self.goniometerThread.currentPositionKohzuGoniometerY
        try:
            convX = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Conversion").value
            aX = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Acceleration").value
            vMaxX = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("SlewRate").value
            aFlexY = self.goniometerThread.proxyFlexureY.read_attribute("Acceleration").value
            vMaxFlexY = self.goniometerThread.proxyFlexureY.read_attribute("Velocity").value
            aFlexX = self.goniometerThread.proxyFlexureX.read_attribute("Acceleration").value
            vMaxFlexX = self.goniometerThread.proxyFlexureX.read_attribute("Velocity").value
        except:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"GridScreeningCollector: Failed to read flexure values.")
            self.alive = False
            return
        angle = self.goniometerThread.currentAngle
        aX /= float(convX)
        vMaxX /= float(convX)
        aY = abs(math.cos(math.radians(angle)) * aFlexY) + abs(math.sin(math.radians(angle)) * aFlexX)
        vMaxY = abs(math.cos(math.radians(angle)) * vMaxFlexY) + abs(math.sin(math.radians(angle)) * vMaxFlexX)
        sX = self.raster.raster.stepsizeHorizontal
        tExp = max(self.parameters["exposuretime"], sX / vMaxX, 0.0075)
        if tExp != self.parameters["exposuretime"]:
            self.emit(SIGNAL("exposureTimeChanged(PyQt_PyObject)"), tExp * 1000.)
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), "GridScreeningCollector: Using minimal exposure time of %.03f s."%tExp)
            self.parameters["exposuretime"] = tExp
            self.parameters["exposureperiod"] = tExp
        vAcqX = math.cos(math.radians(self.raster.raster.angle)) * sX / tExp
        tAccX = vAcqX / aX
        sAccX = 0.5 * aX * tAccX * tAccX
        vAcqY = abs(math.sin(math.radians(self.raster.raster.angle))) * sX / tExp
        tAccY = vAcqY / aY
        sAccY = abs((0.5 * aY * tAccY * tAccY) + ((tAccX - tAccY) * vAcqY))
        if math.tan(math.radians(self.raster.raster.angle)) > 0:
            sAccY *= -1
        self.delay = tAccX
        self.numOfSamples = len(self.parameters["scanPoints"])
        positions = self.raster.raster.getScanRows()
        if not positions:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"GridScreeningCollector: Grid not set.")
            return
        distance = positions[0][-1].x() - positions[0][0].x() + sX
        self.remainingTime = len(positions) * ((distance / vAcqX) + 2 * tAccX + (distance / vMaxX) + 0.5)
        self.totalTime = self.remainingTime
        self.starttime = time.time()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Preparing to start GridScreeningCollector")
        err = self.waitConditions()
        
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"GridScreeningCollector preparations done")
        if(err == self.ERR_NO_ERROR):
            self.setEigerParameters(len(positions[0]), len(positions))
            if self.parameters["liveview"]:
                self.liveViewThread.start(self.path.get_path(
                    "/beamline/beamtime/raw/user/sample/grid_number"),
                    stream=True)
            self.eigerThread.startAcquisition()
            infoAdded = False
            path = self.path.get_path(
                    "/beamline/beamtime/raw/user/sample/" +
                    "grid_number/sample_grid_number_master.h5")
            self.writeInfo()
            #start data collection
            self.dataCollectionActive = True
            self.conditionsList["GoniometerInPosition"] = True
            self.conditionsList["CollectionStarted"] = True
            self.emit(SIGNAL("waitConditionsUpdate()"))
            #data collection running
            for row in positions:
                print("Move to next row at time", time.time())
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving to next row.")

                err = self.moveToNextRow(row[0].x() - sAccX, row[0].y() - sAccY, vMaxX, vMaxFlexX, vMaxFlexY, vAcqX, vAcqY, convX)
                if(err != self.ERR_NO_ERROR):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"GridScreeningCollector error: piezomotor doesnt work properly")
                    self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), "Error: piezomotor doesnt work properly")
                    raise Exception(self.ERR_PIEZOMOTOR_OFFLINE,"Error: piezomotor doesnt work properly")
                self.buildHeatmap()
                self.remainingTime -= (distance / vMaxX) + 0.3
                angle = round(self.goniometerThread.currentAngle, 1)
                deltaX = (row[-1].y()+sAccY)*math.sin(math.radians(angle))
                deltaY = (row[-1].y()+sAccY)*math.cos(math.radians(angle))
                flexureXposition = self.goniometerThread.proxyFlexureX.read_attribute("Position").w_value
                flexureYposition = self.goniometerThread.proxyFlexureY.read_attribute("Position").w_value
                kohzuYposition = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Position").w_value
                self.goniometerThread.setPositionFlexureX(self.flexureXposition+deltaX)
                self.goniometerThread.setPositionFlexureY(self.flexureYposition+deltaY)
                self.goniometerThread.setPositionKohzuGoniometerY(self.kohzuYposition+row[-1].x()+sAccX) 
                time.sleep(self.delay)
                self.goniometerThread.openShutter()
                while((self.goniometerThread.proxyFlexureX.state() == DevState.MOVING or
                        self.goniometerThread.proxyFlexureY.state() == DevState.MOVING or
                        self.goniometerThread.proxyKohzuGoniometerY.state() == DevState.MOVING)
                        and self.alive):
                    self.msleep(self.WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT)
                self.remainingTime -= (distance / vAcqX) + 2 * tAccX + 0.2
                self.goniometerThread.closeShutter()
                #modify h5 master
                if not infoAdded and os.path.isfile(path):
                    self.addH5Info()
                    infoAdded = True
                    self.startProcessing()
                #abort data collection
                if(self.eigerThread.stateEiger == "FAULT"):
                    self.eigerThread.stopAcquisition()
                    self.goniometerThread.stopMotion()
                    self.dataCollectionActive = False
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"GridScreeningCollector error: Pilatus is in FAULT state.")
                    break
                if(not self.alive):
                    self.eigerThread.stopAcquisition()
                    self.goniometerThread.stopMotion()
                    self.dataCollectionActive = False
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"GridScreeningCollector aborted.")
                    break
            #stop data collection
            while(not infoAdded and self.alive):
                if not infoAdded and os.path.isfile(path):
                    self.addH5Info()
                    infoAdded = True
                    self.startProcessing()
                else:
                    self.msleep(250)
            #if it does not take too long, finish the heatmap
            loopCount = 0
            while self.numOfSamples > self.buildHeatmap() and \
                    self.alive and loopCount <= 20:
                self.msleep(500)
                loopCount += 1
            self.dataCollectionActive = False
        elif(err > self.ERR_CANCELLED):
            #error
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"GridScreeningCollector error: "+ str(self.ERR_MSGS[err]))
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"GridScreeningCollector error: "+ str(self.ERR_MSGS[err]))
        self.detectorTowerThread.shieldUp()
        self.goniometerThread.stopKohzuGoniometerY()
        self.goniometerThread.proxyKohzuGoniometerY.write_attribute("SlewRate", vMaxX*convX)
        self.goniometerThread.stopFlexure()
        self.goniometerThread.proxyFlexureX.write_attribute("Velocity", vMaxFlexX)
        self.goniometerThread.proxyFlexureY.write_attribute("Velocity", vMaxFlexY)
        if self.parameters["liveview"]:
            self.liveViewThread.stop(3.0)
        print("GridScreeningCollector thread: Thread for GridScreeningCollector died")
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"GridScreeningCollector finished.")
        self.alive = False

    def setParameters(self, data):
        if(type(data) != dict):
            return self.ERR_TYPE_MISMATCH
        for key in data:
            self.parameters[key] = data[key]

    def setParameter(self, key, data):
        self.parameters[key] = data

    def signalOnaxisImage(self):
        self.emit(SIGNAL("onaxisImage()"))

    def signalOnaxisImage_Point(self):
        self.emit(SIGNAL("onaxisImage_ISMO()"))

    def setEigerParameters(self, columns, rows):
        if self.parameters["4mMode"]:
            self.eigerThread.setRoiMode("4M")
        else:
            self.eigerThread.setRoiMode("disabled")
        self.eigerThread.setTriggerMode("exts")
        self.eigerThread.setExposureTime(self.parameters["exposuretime"])
        self.eigerThread.setExposurePeriod(self.parameters["exposuretime"])
        self.eigerThread.setImageFileType("bslz4")
        self.eigerThread.setNumberOfImagesPerFile(columns)
        self.eigerThread.setNumberOfFrames(columns)
        self.eigerThread.setNumberOfTriggers(rows)
        self.eigerThread.setDelayTime(0.004)
        self.eigerThread.setMetadataStartAngle(round(self.goniometerThread.currentAngle, 1))
        self.eigerThread.setMetadataAngleIncrement(0.0)
        self.eigerThread.setMetadataBeamOriginX(self.parameters["beamX"])
        self.eigerThread.setMetadataBeamOriginY(self.parameters["beamY"])
        self.eigerThread.setMetadataDetectorDistance(self.parameters["detectordistance"] / 1000.0)
        self.eigerThread.setImageFileNumber(1)
        self.eigerThread.setImageFilePrefix(self.path.get_path(
                "sample_grid_number"))
        self.eigerThread.setImageFilePath(self.path.get_path(
                "/beamtime/raw/user/sample/grid_number/"))
        time.sleep(0.1)

    def moveToNextRow(self, x, y, vMaxX, vMaxFlexX, vMaxFlexY, vAcqX, vAcqY, convX):
        err = self.ERR_NO_ERROR
        while((self.goniometerThread.proxyFlexureX.state() == DevState.MOVING or \
                self.goniometerThread.proxyFlexureY.state() == DevState.MOVING or \
                self.goniometerThread.proxyKohzuGoniometerY.state() == DevState.MOVING) and self.alive):
            self.msleep(self.WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT)
        try:
            self.goniometerThread.proxyKohzuGoniometerY.write_attribute("SlewRate", vMaxX*convX)
            self.goniometerThread.proxyFlexureX.write_attribute("Velocity", vMaxFlexX)
            self.goniometerThread.proxyFlexureY.write_attribute("Velocity", vMaxFlexY)
        except:
            print(sys.exc_info())
            err = self.ERR_PIEZOMOTOR_OFFLINE
        angle = round(self.goniometerThread.currentAngle, 1)
        deltaX = y*math.sin(math.radians(angle))
        deltaY = y*math.cos(math.radians(angle))
        self.goniometerThread.setPositionFlexureX(self.flexureXposition+deltaX)
        self.goniometerThread.setPositionFlexureY(self.flexureYposition+deltaY)
        self.goniometerThread.setPositionKohzuGoniometerY(self.kohzuYposition+x)
        self.msleep(self.WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT)
        while((self.goniometerThread.proxyFlexureX.state() == DevState.MOVING or \
                self.goniometerThread.proxyFlexureY.state() == DevState.MOVING or \
                self.goniometerThread.proxyKohzuGoniometerY.state() == DevState.MOVING) and self.alive):
            self.msleep(self.WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT)
        vFlexX = abs(vAcqY*math.sin(math.radians(angle)))
        vFlexY = abs(vAcqY*math.cos(math.radians(angle)))
        try:
            self.goniometerThread.proxyKohzuGoniometerY.write_attribute("SlewRate", vAcqX*convX)
            if abs(vFlexX) > 0.1:
                self.goniometerThread.proxyFlexureX.write_attribute("Velocity", vFlexX)
            if abs(vFlexY) > 0.1:
                self.goniometerThread.proxyFlexureY.write_attribute("Velocity", vFlexY)
        except:
            print(sys.exc_info())
            err = self.ERR_PIEZOMOTOR_OFFLINE
        return err

    def waitConditions(self):
        if(not self.detectorTowerThread.statusInterlock): #FIXME
            return self.ERR_INTERLOCK_NOT_SET
        
        if(self.waitConditionActive):
            return self.ERR_ALREADY_RUNNING
        self.waitConditionActive = True
        waitConditionTimeOut = 0
        while(True):
            conditions = True
            #Shutter
            if(self.goniometerThread.statusFastShutter):
                print("Closing FS")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Closing FS")
                self.goniometerThread.closeShutter()
                conditions = False
            #BS0
            if(not self.petraThread.statusShutterBS0):
                print("opening BS0")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Opening BS0")
                self.petraThread.openBS0()
                conditions = False
            else:
                self.conditionsList["BS0open"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #BS1
            if(not self.petraThread.statusShutterBS1): 
                self.petraThread.openBS1()
                conditions = False
            else:
                self.conditionsList["BS1open"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Beamstop
            if (self.piezoThread.beamstopXInOut == "Out"):
                if (self.piezoThread.stateProxyPiezoBeamstopX == "ON"):
                    self.piezoThread.moveBeamStopIn()
            elif (self.piezoThread.beamstopXInOut == "In"):
                self.conditionsList["BeamstopInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #DetectorTower
            if(self.parameters["detectordistance"] > self.detectorTowerThread.currentPositionDetectorTowerServer + self.DETECTORTOWER_TOLERANCE or \
                    self.parameters["detectordistance"] < self.detectorTowerThread.currentPositionDetectorTowerServer - self.DETECTORTOWER_TOLERANCE):
                if(self.parameters["detectordistance"] < self.detectorTowerThread.minPositionDetectorTowerServer + 0.1):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Invalid detector distance (value out of range).")
                    return self.ERR_VALUE_OUT_OF_RANGE
                elif(self.parameters["detectordistance"] > self.detectorTowerThread.maxPositionDetectorTowerServer - 0.1):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Invalid detector distance (value out of range).")
                    return self.ERR_VALUE_OUT_OF_RANGE
                elif(self.detectorTowerThread.stateDetectorTower == "ON"):
                    print("Moving detector tower")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving detector tower.")
                    self.detectorTowerThread.setPositionDetectorTower(self.parameters["detectordistance"])
                conditions = False
            else:
                self.conditionsList["DetectorInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Eiger
            if(self.petraThread.currentMonoEnergy > (self.eigerThread.photonEnergy + self.DETECTOR_ENERGY_TOLERANCE) or \
                self.petraThread.currentMonoEnergy < (self.eigerThread.photonEnergy - self.DETECTOR_ENERGY_TOLERANCE)):
                if(str(self.eigerThread.proxyEiger.state()) == "ON"):
                    print("Setting pilatus threshold")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Setting pilatus energy threshold.")
                    if self.petraThread.currentMonoEnergy > 5500:
                        self.eigerThread.setPhotonEnergy(self.petraThread.currentMonoEnergy)
                    else:
                        self.eigerThread.setPhotonEnergy(5500)
                    time.sleep(1.5)
                    conditions = False
                    self.conditionsList["DetectorThresholdSet"] = False
            elif (str(self.eigerThread.proxyEiger.state()) == "ON"):
                self.conditionsList["DetectorThresholdSet"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            elif (not (str(self.eigerThread.proxyEiger.state()) == "ON")):
                conditions = False
                self.conditionsList["DetectorThresholdSet"] = False
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Pinhole
            if(self.parameters["pinhole"] != self.piezoThread.currentPinholePosition):
                if(self.piezoThread.statePinhole == "ON"):
                    print("Setting pinhole")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Setting pinhole.")
                    self.piezoThread.setPinhole(self.parameters["pinhole"])
                conditions = False
            #Collimator
            if(not self.piezoThread.collimatorInPlace):
                if(self.piezoThread.stateCollimator == "ON"):
                    print("Moving collimator in")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving collimator in.")
                    self.piezoThread.collimatorIn()
                conditions = False
            else:
                self.conditionsList["CollimatorInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #YAG/Diode #FIXME
           # if(self.piezoThread.currentYAGScreenPosition != "Out"):
           #     if(self.piezoThread.stateScreen == "ON"):
           #         self.piezoThread.screenOut()
           #     conditions = False
           # else:
                
            #ContrastScreen #FIXME
            if(self.goniometerThread.positionContrastscreen):
                self.goniometerThread.moveContrastScreenOut()
                conditions = False
            else:
                self.conditionsList["ContrastScreenInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Filter
            #if(self.parameters["filter1"] != self.piezoThread.currentFilter1Position):
            #    if(self.piezoThread.stateFilter1 == "ON"):
            #        self.piezoThread.setFilter1(self.parameters["filter1"])
            #    conditions = False
            #if(self.parameters["filter2"] != self.piezoThread.currentFilter2Position):
            #    if(self.piezoThread.stateFilter2 == "ON"):
            #        self.piezoThread.setFilter2(self.parameters["filter2"])
            #    conditions = False
            #BeamstopDiode
            if(not self.detectorTowerThread.interlockWasBroken):
                self.conditionsList["BeamstopDiodeOK"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            elif(self.conditionsList["BS1open"] and self.conditionsList["BS0open"]) and \
                    (not self.conditionsList["BeamstopDiodeOK"] and self.detectorTowerThread.shieldIsUp and \
                     self.conditionsList["BeamstopInPosition"]):
                print("Checking if beamstop OK")
                #Move the sample to safety first
                currentGonioY = self.goniometerThread.currentPositionKohzuGoniometerY
                self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY - self.parameters["sampleoutDistanceWhenBeamcheck"])
                time.sleep(0.2)
                while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                    time.sleep(0.1)
                if(not self.goniometerThread.statusFastShutter):
                    self.goniometerThread.openShutter()
                time.sleep(0.5)
                if(self.detectorTowerThread.diodeThresholdOK):
                    print("Beamstop OK")
                    self.goniometerThread.closeShutter()
                    self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY)
                    time.sleep(0.2)
                    self.detectorTowerThread.interlockWasBroken = False
                    self.conditionsList["BeamstopDiodeOK"] = True
                    self.emit(SIGNAL("waitConditionsUpdate()"))
                    while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                        time.sleep(0.1)
                else:
                    self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY)
                    time.sleep(0.2)
                    while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                        time.sleep(0.1)
                    return self.ERR_MISALIGNED_BEAMSTOP
            #Guillotine
            if(self.conditionsList["BeamstopDiodeOK"]):
                if(not self.detectorTowerThread.shieldIsDown):
                    self.detectorTowerThread.shieldDown()
                else:
                    self.conditionsList["ShieldDown"] = True
                    self.emit(SIGNAL("waitConditionsUpdate()"))
            #check end conditions
            if (self.conditionsList["BS0open"] and \
                self.conditionsList["BS1open"] and \
                self.conditionsList["BeamstopInPosition"] and \
                self.conditionsList["BeamstopDiodeOK"] and \
                self.conditionsList["DetectorInPosition"] and \
                self.conditionsList["DetectorThresholdSet"] and \
                self.conditionsList["CollimatorInPosition"] and \
                self.conditionsList["ContrastScreenInPosition"] and \
                self.conditionsList["ShieldDown"]):
                self.waitConditionActive = False
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_NO_ERROR
                 
            #if(conditions):
            #    self.waitConditionActive = False
            #    self.emit(SIGNAL("waitConditionsUpdate()"))
            #    return self.ERR_NO_ERROR
            waitConditionTimeOut += 1
            if(waitConditionTimeOut >= self.WAIT_CONDITIONS_TIMEOUT):
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_WAIT_CONDITION_TIMEOUT
            if(not self.alive):
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_CANCELLED
            
            self.msleep(self.WAIT_CONDITIONS_INTERVAL)

    def buildHeatmap(self):
        colours = []
        score = {}
        score_max = 0
        score_min = sys.maxsize
        filename = self.path.get_path(
                "/beamline/beamtime/processed/user/sample/" +
                "grid_number/dozor/dozor.log")
        # read and parse scores from file
        try:
            with open(filename, "r") as f:
                for line in f:
                    # skip labels 
                    if line[1] in ['N', 'm', '-']:
                        continue
                    line = line.replace("|", "").strip()
                    while line.find("  ") >= 0:
                        line = line.replace("  ", " ")
                    values = line.split()
                    score[int(values[0]) - 1] = float(values[2])
                    if float(values[2]) > score_max:
                        score_max = float(values[2])
                    if float(values[2]) < score_min:
                        score_min = float(values[2])
                    if not self.alive:
                        return 0
        except:
            return 0
        # normalise scores and build heatmap
        score_dynamic = max(float(score_max - score_min), 1.0)
        for i in range(len(self.raster.raster.positions)):
            if not self.alive:
                return 0
            if i in score:
                score_current = 2 * (score[i] - score_min) / score_dynamic
                if score_current <= 1:
                    colours.append(qRgb(255 - 255 * score_current,
                            255 - 255 * score_current,
                            255 - 255 * score_current))    
                else:
                    colours.append(qRgb(255 * (score_current - 1), 0, 0))
            else:
                colours.append(qRgb(0, 255, 0))
        self.raster.raster.setColours(colours)
        self.raster.raster.positionsValid = False
        return len(score)

    def startProcessing(self):
        #creation will fail if beamtime folder, slurm reservation or
        #bl-fs mount on the compute nodes can not be found
        try:
            btHelper = triggerUtils.Trigger()
        except:
            print(sys.exc_info())
            return

        imagepath = self.path.get_path(
                "/central/beamtime/raw/user/sample/grid_number/" +
                "sample_grid_number_master.h5")
        processpath = "/beamline/p11/current" + self.path.get_path(
                "/processed/user/sample/grid_number/dozor")
        #create processing folder with 0o777
        self.path.get_path("/beamline/beamtime/processed/user/sample/" +
                "grid_number/dozor", force=True)

        #create call
        ssh = btHelper.get_ssh_command()
        sbatch = btHelper.get_sbatch_command(
            jobname_prefix = "dozor",
            job_dependency = "",
            logfile_path = processpath + "/dozor.log"
        )
        cmd = ("/asap3/petra3/gpfs/common/p11/processing/dozor_sbatch.sh " + \
                "{imagepath:s}").format(imagepath = imagepath)
        print(cmd)
        os.system("{ssh:s} \"{sbatch:s} --wrap \\\"{cmd:s}\\\"\"".format(
            ssh = ssh,
            sbatch = sbatch,
            cmd = cmd
        ))

    def addH5Info(self):
        imagepath = self.path.get_path(
                "/central/beamtime/raw/user/sample/grid_number/" +
                "sample_grid_number_master.h5"),
        time.sleep(0.5)
        print("add h5 info")
        try:
            f = h5py.File(imagepath, "r+")
            #source and instrument
            g = f.create_group(u"entry/source")
            g.attrs[u"NX_class"] = numpy.array(u"NXsource", dtype="S")
            g.create_dataset(u"name", data=numpy.array(u"PETRA III, DESY", dtype="S"))
            g = f.get(u"entry/instrument")
            g.create_dataset(u"name", data=numpy.array(u"P11", dtype="S"))
            #attenuator
            g = f.create_group(u"entry/instrument/attenuator")
            g.attrs[u"NX_class"] = numpy.array(u"NXattenuator", dtype="S")
            ds = g.create_dataset(u"thickness", dtype="f8",
                    data=float(self.parameters["filterThickness"])/1000000)
            ds.attrs[u"units"] = data=numpy.array(u"m", dtype="S")
            ds = g.create_dataset(u"type", data=numpy.array(u"Aluminum", dtype="S"))
            ds = g.create_dataset(u"attenuator_transmission", dtype="f8",
                    data=float(self.parameters["filterTransmission"]))
            # fix rotation axis and detector orientation
            ds = f.get(u"entry/sample/transformations/omega")
            ds.attrs[u"vector"] = [1., 0., 0.]
            ds = f.get(u"entry/instrument/detector/module/fast_pixel_direction")
            ds.attrs[u"vector"] = [1., 0., 0.]
            ds = f.get(u"entry/instrument/detector/module/slow_pixel_direction")
            ds.attrs[u"vector"] = [0., 1., 0.]
            #delete phi angle info to avoid confusion
            nodes = [
                "entry/sample/goniometer/phi",
                "entry/sample/goniometer/phi_end",
                "entry/sample/goniometer/phi_range_average",
                "entry/sample/goniometer/phi_range_total"]
            for node in nodes:
                if node in f:
                    del f[node]
            f.close()
        except:
            print(sys.exc_info()[1])
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),
                    "Failed to insert info to H5 file.")

    def writeInfo(self):
        path = self.path.get_path("/beamline/beamtime/raw/user/sample" +
                "/grid_number", force=True)
        energy = self.petraThread.currentMonoEnergy/1000.
        wavelength = 12.3984/(energy) #in Angstrom
        resolution = wavelength/(2.*math.sin(0.5*math.atan((311./2.)/ self.parameters["detectordistance"])))
        frames = len(self.parameters["scanPoints"])
        output = self.INFO_TXT.format(
            name = self.path.get_path("sample_grid_number"),
            rows = self.parameters["rows"],
            columns = self.parameters["columns"],
            angle = self.goniometerThread.currentAngle,
            frames = frames,
            exposuretime = self.parameters["exposureperiod"] * 1000,
            energy = energy,
            wavelength = wavelength,
            detectordistance = self.parameters["detectordistance"],
            resolution = resolution,
            pinholeDiameter = int(self.parameters["pinholeDiameter"]),
            focus = self.parameters["focus"],
            filterTransmission = self.parameters["filterTransmission"]*100,
            filterThickness = int(self.parameters["filterThickness"]),
            beamCurrent = self.parameters["beamCurrent"]
        )
        try:
            f = open(path + "/info.txt", "w")
            f.write(output)
            f.close()
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Unable to write info file.")

    def collectionTime(self, percent = False):
        if percent:
            return ((self.totalTime - self.remainingTime) / self.totalTime) * 100
        return self.remainingTime

#step scan
class ISMOCollector(QThread):

    ERR_NO_ERROR = 0
    ERR_CANCELLED = 1
    ERR_TYPE_MISMATCH = 2
    ERR_VALUE_OUT_OF_RANGE = 3
    ERR_TIMEOUT = 4
    ERR_ALREADY_RUNNING = 8
    ERR_INTERLOCK_NOT_SET = 9
    ERR_MISALIGNED_BEAMSTOP = 10
    ERR_PIEZOMOTOR_OFFLINE = 11
    ERR_WAIT_CONDITION_TIMEOUT = 12
    
    ERR_MSGS = [
        "Success.",
        "Canceled.",
        "Wrong parameter type.",
        "Parameter value out of range.",
        "Timeout during start up procedure.",
        "",
        "",
        "",
        "ISMO collection is already running.",
        "Interlock is not set.",
        "Beamstop is not aligned. \n Direct beam on detector! Please contact beamline personnel.",
    ]

    WAIT_CONDITIONS_TIMEOUT = 1000 #*interval
    WAIT_CONDITIONS_INTERVAL = 200 #ms
    WAIT_CONDITIONS_TIMEOUT_NEXTSCANPOINT = 1000 #*interval
    WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT = 100 #ms

    DETECTORTOWER_TOLERANCE = 1.0 #mm
    GONIOMETER_TURNBACK_TIME = 0.1 #s
    GONIOMETER_ANGLE_TOLERANCE = 0.05 #deg
    GONIOMETER_DEFAULT_SPEED = 90.0 #deg/s
    DETECTOR_ENERGY_TOLERANCE = 500.0 #eV

    INFO_TXT = \
        "run type:            ISMO\n" + \
        "run name:            {name:s}\n" + \
        "grid:                {columns:d}x{rows:d}\n" + \
        "angle:               {angle:.2f}deg\n" + \
        "positions:           {frames:d}\n" + \
        "frames/position:     {framesperposition:d}\n" + \
        "degrees/frame:       {degreesperframe:.2f}deg\n" + \
        "exposure time:       {exposuretime:.3f}ms\n" + \
        "energy:              {energy:.3f}keV\n" + \
        "wavelength:          {wavelength:.3f}A\n" + \
        "detector distance:   {detectordistance:.2f}mm\n" + \
        "resolution:          {resolution:.2f}A\n" + \
        "aperture:            {pinholeDiameter:d}um\n" + \
        "focus:               {focus:s}\n" + \
        "filter transmission: {filterTransmission:.3f}%\n" + \
        "filter thickness:    {filterThickness:d}um\n" + \
        "ring current:        {beamCurrent:.3f}mA\n" + \
        "\n" + \
        "For exact flux reading, please consult the staff." + \
        "Typical flux of P11 at 12 keV with 100 mA ring current " + \
        "(beam area is defined by selected pinhole in flat beam, in " + \
        "focused mode typically pinhole of 200 um is used and beam " + \
        "areas is defined by focusing state):\n" + \
        "\n" + \
        "Focus       Beam area (um)  Flux (ph/s)\n" + \
        "Flat        200 x 200       2e12\n" + \
        "Flat        100 x 100       5e11\n" + \
        "Flat          50 x 50       1.25e11\n" + \
        "Flat          20 x 20       2e10\n" + \
        "Focused     200 x 200       4.4e12\n" + \
        "Focused     100 x 100       9.9e12\n" + \
        "Focused       50 x 50       9.9e12\n" + \
        "Focused       20 x 20       9.9e12\n" + \
        "Focused         9 x 4       8.7e12\n"

    # A thread is started by calling QThread.start() never by calling run() directly!
    def __init__(self, detectorTowerThread, goniometerThread, petraThread, piezoThread, eigerThread, liveViewThread, path, parent = None, simulation = False):
        QThread.__init__(self, parent)
        #self.MainWindow = mainwindowPassing
        print("ISMO collection thread: Starting thread")
        self.myparent = parent
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Preparing ISMO collection...")
        self.alive = True
        self.waitConditionActive = False
        self.dataCollectionActive = False
        self.remainingTime = 0.0
        self.parameters = { 
            "filenumber": 0,
            "oscillationrange": 0.0,
            "framesperposition": 0,
            "rows": 0,
            "columns": 0,
            "exposuretime": 0.0,
            "exposureperiod": 0.0,
            "detectordistance": 0.0,
            "4mMode": False,
            "liveview": False,
            "pinhole": 0,
            "pinholeDiameter": 0,
            "filterTransmission": 1.0,
            "filterThickness": 0.0,
            "beamX": 1262,
            "beamY": 1242,
            "scanPoints": [],
            "sampleoutDistanceWhenBeamcheck": 0,
        }
        self.conditionsList = {
            "BS0open": False,
            "BS1open": False,
            "FSopen": False,
            "BeamstopInPosition": False,
            "DetectorInPosition": False,
            "DetectorThresholdSet": False,
            "GoniometerInPosition": False,
            "CollimatorInPosition": False,
            "ContrastScreenInPosition": False,
            "BeamstopDiodeOK": False,
            "ShieldDown": False,
            "CollectionStarted": False ,
            }
        
        self.debugMode = 0
        self.detectorTowerThread = detectorTowerThread
        self.goniometerThread = goniometerThread
        self.petraThread = petraThread
        self.piezoThread = piezoThread
        self.eigerThread = eigerThread
        self.liveViewThread = liveViewThread
        self.path = path
        self.centreAngle = 0
        self.timePerSample = 0
        self.degreesPerFrame = 0
        self.starttime = time.time()
        self.numOfSamples = 0
        self.sampleNumber = 0

    def stop(self):
        print("ISMO collector thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own

    def join(self, timeout=None):
        print("ISMO collector thread: join method")
        self.alive = False

    def run(self):
        self.alive = True
        self.starttime = time.time()
        print("ISMO collector thread: started")
        if not self.detectorTowerThread.statusInterlock: #FIXME
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"ISMO collection: Interlock is not set.")
        if not self.piezoThread.pinholeAboveMinimumZ:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"ISMO collection: No pinhole selected.")
            return
        #set up everything
        self.remainingTime = ((self.parameters["framesperposition"]*self.parameters["exposureperiod"]/1000)+3.5) * len(self.parameters["scanPoints"])
        self.totalTime = self.remainingTime
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Preparing to start ISMO collection")
        print("Checking wait conditions")
        err = self.waitConditions()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"ISMO collection preparations done")
        print("WAIT RETURNED", err)
        if(err == self.ERR_NO_ERROR):
            #start data collection
            self.centreAngle = self.goniometerThread.currentAngle
            if(self.parameters["framesperposition"] == 0):
                raise Exception(self.ERR_VALUE_OUT_OF_RANGE,"framesperposition",self.parameters["framesperposition"])
            if(self.parameters["oscillationrange"] != 0.0):
                self.startAngle = self.centreAngle + self.parameters["oscillationrange"]
                self.stopAngle = self.centreAngle - self.parameters["oscillationrange"]
                self.degreesPerFrame = abs((self.stopAngle-self.startAngle))/float(self.parameters["framesperposition"])*0.9
                self.acqSpeed = self.degreesPerFrame * (1.0 / (self.parameters["exposureperiod"]))
                self.timePerSample = float(self.parameters["oscillationrange"]) / self.acqSpeed
                self.goniometerThread.setSpeed(self.GONIOMETER_DEFAULT_SPEED)
                self.goniometerThread.setAngle(self.startAngle)
            self.setEigerParameters()
            if self.parameters["liveview"]:
                self.liveViewThread.start(self.path.get_path(
                    "/beamline/beamtime/raw/user/sample/ismo_number"),
                    stream=True)
            self.eigerThread.startAcquisition()
            infoAdded = False
            path = self.path.get_path(
                    "/beamline/beamtime/raw/user/sample/" +
                    "ismo_number/sample_ismo_number_master.h5")
            self.writeInfo()
            time.sleep(0.25)
            while (str(self.goniometerThread.proxyGoniometer.state()) == "MOVING"):
                time.sleep(0.1)
            self.conditionsList["GoniometerInPosition"] = True
            self.emit(SIGNAL("waitConditionsUpdate()"))
            # used for progress update
            self.numOfSamples = len(self.parameters["scanPoints"])
            self.sampleNumber = 0
            print("ISMO collector: num of samples", self.numOfSamples)
            self.dataCollectionActive = True
            self.conditionsList["CollectionStarted"] = True
            self.emit(SIGNAL("waitConditionsUpdate()"))
            #data collection running
            for scanpoint in range(len(self.parameters["scanPoints"])):
                self.sampleNumber += 1
                print("Move to next point at time", time.time())
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving to scanpoint #"+str(scanpoint + 1) + " at %8.3f"%self.parameters["scanPoints"][scanpoint][0] + ", %8.3f"%self.parameters["scanPoints"][scanpoint][1])
                err = self.moveToNextScanPoint(self.parameters["scanPoints"][scanpoint])
                print("Move to next point done at time", time.time())
                self.signalOnaxisImage_Point()
                if(err != self.ERR_NO_ERROR):
                    print("ISMO: SCAN MOTOR ERROR")
                    raise Exception(self.ERR_PIEZOMOTOR_OFFLINE,"Error: piezomotor doesnt work properly")
                    self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),self.ERR_PIEZOMOTOR_OFFLINE+ "Error: piezomotor doesnt work properly")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"ISMO collection error: piezomotor doesnt work properly")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Starting rotation")
                print("ISMO starttime at",time.time())
                if self.parameters["oscillationrange"] == 0.0:
                    self.msleep(150)
                    self.goniometerThread.openShutter()
                    self.msleep(5 + int(self.parameters["framesperposition"] * self.parameters["exposureperiod"]))
                    self.goniometerThread.closeShutter()
                elif self.sampleNumber % 2 == 0:  # even number
                    self.goniometerThread.startAcquisitionRun(self.startAngle, self.stopAngle, self.acqSpeed)
                    self.msleep(400)
                else:
                    self.goniometerThread.startAcquisitionRun(self.stopAngle, self.startAngle, self.acqSpeed)
                    self.msleep(400)
                startTime = time.time()
                while (self.goniometerThread.stateGoniometer == "MOVING" and self.alive):
                    self.msleep(100)
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"ISMO Collection finished. Preparing for next scan position.")
                print("done at",time.time())
                self.remainingTime -= (self.parameters["framesperposition"]*self.parameters["exposureperiod"]/1000)+3.5
                #abort data collection
                if(self.eigerThread.stateEiger == "FAULT"):
                    self.eigerThread.stopAcquisition()
                    self.goniometerThread.stopMotion()
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"ISMO collection error: Eiger is in FAULT state.")
                    break
                if(not self.alive):
                    self.eigerThread.stopAcquisition()
                    self.goniometerThread.stopMotion()
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"ISMO collection aborted.")
                    break
                #wait

            #end reached
            self.dataCollectionActive = False
        elif(err > self.ERR_CANCELLED):
            #error
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"ISMO collection error: "+ str(self.ERR_MSGS[err]))
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"ISMO collection error: "+ str(self.ERR_MSGS[err]))
        self.goniometerThread.setSpeed(self.GONIOMETER_DEFAULT_SPEED)
        self.goniometerThread.setAngle(self.centreAngle)
        self.detectorTowerThread.shieldUp()
        if self.parameters["liveview"]:
            self.liveViewThread.stop()
        print("ISMO collector thread: Thread for ISMO collector died")
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"ISMO collection finished.")
        self.alive = False

    def setParameters(self, data):
        if(type(data) != dict):
            return self.ERR_TYPE_MISMATCH
        for key in data:
            self.parameters[key] = data[key]

    def setParameter(self, key, data):
        self.parameters[key] = data

    def signalOnaxisImage(self):
        self.emit(SIGNAL("onaxisImage()"))

    def signalOnaxisImage_Point(self):
        self.emit(SIGNAL("onaxisImage_ISMO()"))

    def setEigerParameters(self):
        imagesperfile = self.parameters["framesperposition"] * self.parameters["columns"]
        while imagesperfile > 1000:
            imagesperfile /= 2
        if self.parameters["4mMode"]:
            self.eigerThread.setRoiMode("4M")
        else:
            self.eigerThread.setRoiMode("disabled")
        self.eigerThread.setTriggerMode("exts")
        self.eigerThread.setExposureTime(self.parameters["exposuretime"])
        self.eigerThread.setExposurePeriod(self.parameters["exposuretime"])
        self.eigerThread.setImageFileType("bslz4")
        self.eigerThread.setNumberOfImagesPerFile(imagesperfile)
        self.eigerThread.setNumberOfFrames(self.parameters["framesperposition"])
        self.eigerThread.setNumberOfTriggers(self.parameters["rows"] * self.parameters["columns"])
        self.eigerThread.setDelayTime(0.004)
        self.eigerThread.setMetadataStartAngle(round(self.goniometerThread.currentAngle, 1))
        self.eigerThread.setMetadataAngleIncrement(0.0)
        self.eigerThread.setMetadataBeamOriginX(self.parameters["beamX"])
        self.eigerThread.setMetadataBeamOriginY(self.parameters["beamY"])
        self.eigerThread.setMetadataDetectorDistance(self.parameters["detectordistance"] / 1000.0)
        self.eigerThread.setImageFileNumber(1)
        self.eigerThread.setImageFilePrefix(self.path.get_path(
                "sample_ismo_number"))
        self.eigerThread.setImageFilePath(self.path.get_path(
                "/beamtime/raw/user/sample/ismo_number/"))
        time.sleep(0.1)


    def moveToNextScanPoint(self,point):
        nextPointX = point[0]
        #nextPointY = point[1]
        nextPointFlexureX = point[1]
        nextPointFlexureY = point[2]
        #self.goniometerThread.setPositionFlexureY(nextPointY)
        self.goniometerThread.setPositionFlexureX(nextPointFlexureX)
        self.goniometerThread.setPositionFlexureY(nextPointFlexureY)
        self.goniometerThread.setPositionKohzuGoniometerY(nextPointX)
        
        time.sleep(0.5)
        if(self.waitConditionActive):
            return self.ERR_ALREADY_RUNNING
        self.waitConditionActive = True
        waitConditionTimeOut = 0
        
        while(True):
            conditions = True
            #Shutter
            #if(self.goniometerThread.stateKohzuGoniometerY == "MOVING" or self.goniometerThread.stateKohzuGoniometerZ == "MOVING"):
            if(self.goniometerThread.stateFlexureX == "MOVING" or self.goniometerThread.stateFlexureY == "MOVING" or self.goniometerThread.stateKohzuGoniometerY == "MOVING"):
                conditions = False
 
            #check end conditions
            if(conditions):
                self.waitConditionActive = False
                return self.ERR_NO_ERROR
            waitConditionTimeOut += 1
            if(waitConditionTimeOut >= self.WAIT_CONDITIONS_TIMEOUT_NEXTSCANPOINT):
                return self.ERR_WAIT_CONDITION_TIMEOUT_NEXTSCANPOINT
            if(not self.alive):
                return self.ERR_CANCELLED
            self.msleep(self.WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT)

    def waitConditions(self):
        if(not self.detectorTowerThread.statusInterlock): #FIXME
            return self.ERR_INTERLOCK_NOT_SET
        if(self.waitConditionActive):
            return self.ERR_ALREADY_RUNNING
        self.waitConditionActive = True
        waitConditionTimeOut = 0
        while(True):
            conditions = True
            #Shutter
            if(self.goniometerThread.statusFastShutter):
                print("Closing FS")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Closing FS")
                self.goniometerThread.closeShutter()
                conditions = False
            #BS0
            if(not self.petraThread.statusShutterBS0):
                print("opening BS0")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Opening BS0")
                self.petraThread.openBS0()
                conditions = False
            else:
                self.conditionsList["BS0open"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #BS1
            if(not self.petraThread.statusShutterBS1): 
                self.petraThread.openBS1()
                conditions = False
            else:
                self.conditionsList["BS1open"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Beamstop
            if (self.piezoThread.beamstopXInOut == "Out"):
                if (self.piezoThread.stateProxyPiezoBeamstopX == "ON"):
                    self.piezoThread.moveBeamStopIn()
            elif (self.piezoThread.beamstopXInOut == "In"):
                self.conditionsList["BeamstopInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #DetectorTower
            if(self.parameters["detectordistance"] > self.detectorTowerThread.currentPositionDetectorTowerServer + self.DETECTORTOWER_TOLERANCE or \
                    self.parameters["detectordistance"] < self.detectorTowerThread.currentPositionDetectorTowerServer - self.DETECTORTOWER_TOLERANCE):
                if(self.parameters["detectordistance"] < self.detectorTowerThread.minPositionDetectorTowerServer + 0.1):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Invalid detector distance (value out of range).")
                    return self.ERR_VALUE_OUT_OF_RANGE
                elif(self.parameters["detectordistance"] > self.detectorTowerThread.maxPositionDetectorTowerServer - 0.1):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Invalid detector distance (value out of range).")
                    return self.ERR_VALUE_OUT_OF_RANGE
                elif(self.detectorTowerThread.stateDetectorTower == "ON"):
                    print("Moving detector tower")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving detector tower.")
                    self.detectorTowerThread.setPositionDetectorTower(self.parameters["detectordistance"])
                conditions = False
            else:
                self.conditionsList["DetectorInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Eiger
            if(self.petraThread.currentMonoEnergy > (self.eigerThread.photonEnergy + self.DETECTOR_ENERGY_TOLERANCE) or \
                self.petraThread.currentMonoEnergy < (self.eigerThread.photonEnergy - self.DETECTOR_ENERGY_TOLERANCE)):
                if(str(self.eigerThread.proxyEiger.state()) == "ON"):
                    print("Setting pilatus threshold")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Setting pilatus energy threshold.")
                    if self.petraThread.currentMonoEnergy > 5500:
                        self.eigerThread.setPhotonEnergy(self.petraThread.currentMonoEnergy)
                    else:
                        self.eigerThread.setPhotonEnergy(5500)
                    time.sleep(1.5)
                    conditions = False
                    self.conditionsList["DetectorThresholdSet"] = False
            elif (str(self.eigerThread.proxyEiger.state()) == "ON"):
                self.conditionsList["DetectorThresholdSet"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            elif (not (str(self.eigerThread.proxyEiger.state()) == "ON")):
                conditions = False
                self.conditionsList["DetectorThresholdSet"] = False
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Pinhole
            if(self.parameters["pinhole"] != self.piezoThread.currentPinholePosition):
                if(self.piezoThread.statePinhole == "ON"):
                    print("Setting pinhole")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Setting pinhole.")
                    self.piezoThread.setPinhole(self.parameters["pinhole"])
                conditions = False
            #Collimator
            if(not self.piezoThread.collimatorInPlace):
                if(self.piezoThread.stateCollimator == "ON"):
                    print("Moving collimator in")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving collimator in.")
                    self.piezoThread.collimatorIn()
                conditions = False
            else:
                self.conditionsList["CollimatorInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #YAG/Diode #FIXME
           # if(self.piezoThread.currentYAGScreenPosition != "Out"):
           #     if(self.piezoThread.stateScreen == "ON"):
           #         self.piezoThread.screenOut()
           #     conditions = False
           # else:
            #ContrastScreen #FIXME
            if(self.goniometerThread.positionContrastscreen):
                self.goniometerThread.moveContrastScreenOut()
                conditions = False
            else:
                self.conditionsList["ContrastScreenInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Filter
            #if(self.parameters["filter1"] != self.piezoThread.currentFilter1Position):
            #    if(self.piezoThread.stateFilter1 == "ON"):
            #        self.piezoThread.setFilter1(self.parameters["filter1"])
            #    conditions = False
            #if(self.parameters["filter2"] != self.piezoThread.currentFilter2Position):
            #    if(self.piezoThread.stateFilter2 == "ON"):
            #        self.piezoThread.setFilter2(self.parameters["filter2"])
            #    conditions = False
            #BeamstopDiode
            if(not self.detectorTowerThread.interlockWasBroken):
                self.conditionsList["BeamstopDiodeOK"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            elif(self.conditionsList["BS1open"] and self.conditionsList["BS0open"]) and \
                    (not self.conditionsList["BeamstopDiodeOK"] and self.detectorTowerThread.shieldIsUp and \
                     self.conditionsList["BeamstopInPosition"]):
                print("Checking if beamstop OK")
                #Move the sample to safety first
                currentGonioY = self.goniometerThread.currentPositionKohzuGoniometerY
                self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY - self.parameters["sampleoutDistanceWhenBeamcheck"])
                time.sleep(0.2)
                while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                    time.sleep(0.1)
                if(not self.goniometerThread.statusFastShutter):
                    self.goniometerThread.openShutter()
                time.sleep(0.5)
                if(self.detectorTowerThread.diodeThresholdOK):
                    print("Beamstop OK")
                    self.goniometerThread.closeShutter()
                    self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY)
                    time.sleep(0.2)
                    self.detectorTowerThread.interlockWasBroken = False
                    self.conditionsList["BeamstopDiodeOK"] = True
                    self.emit(SIGNAL("waitConditionsUpdate()"))
                    while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                        time.sleep(0.1)
                else:
                    self.goniometerThread.setPositionKohzuGoniometerY(currentGonioY)
                    time.sleep(0.2)
                    while str(self.goniometerThread.proxyKohzuGoniometerY.state()) != "ON":
                        time.sleep(0.1)
                    return self.ERR_MISALIGNED_BEAMSTOP
            #Guillotine
            if(self.conditionsList["BeamstopDiodeOK"]):
                if(not self.detectorTowerThread.shieldIsDown):
                    self.detectorTowerThread.shieldDown()
                else:
                    self.conditionsList["ShieldDown"] = True
                    self.emit(SIGNAL("waitConditionsUpdate()"))
            #check end conditions
            if (self.conditionsList["BS0open"] and \
                self.conditionsList["BS1open"] and \
                self.conditionsList["BeamstopInPosition"] and \
                self.conditionsList["BeamstopDiodeOK"] and \
                self.conditionsList["DetectorInPosition"] and \
                self.conditionsList["DetectorThresholdSet"] and \
                self.conditionsList["CollimatorInPosition"] and \
                self.conditionsList["ContrastScreenInPosition"] and \
                self.conditionsList["ShieldDown"]):
                self.waitConditionActive = False
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_NO_ERROR
            #if(conditions):
            #    self.waitConditionActive = False
            #    self.emit(SIGNAL("waitConditionsUpdate()"))
            #    return self.ERR_NO_ERROR
            waitConditionTimeOut += 1
            if(waitConditionTimeOut >= self.WAIT_CONDITIONS_TIMEOUT):
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_WAIT_CONDITION_TIMEOUT
            if(not self.alive):
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_CANCELLED
            
            self.msleep(self.WAIT_CONDITIONS_INTERVAL)

    def addH5Info(self):
        imagepath = self.path.get_path(
                "/central/beamtime/raw/user/sample/ismo_number/" +
                "sample_ismo_number_master.h5"),
        time.sleep(0.5)
        print("add h5 info")
        try:
            f = h5py.File(imagepath, "r+")
            #source and instrument
            g = f.create_group(u"entry/source")
            g.attrs[u"NX_class"] = numpy.array(u"NXsource", dtype="S")
            g.create_dataset(u"name", data=numpy.array(u"PETRA III, DESY", dtype="S"))
            g = f.get(u"entry/instrument")
            g.create_dataset(u"name", data=numpy.array(u"P11", dtype="S"))
            #attenuator
            g = f.create_group(u"entry/instrument/attenuator")
            g.attrs[u"NX_class"] = numpy.array(u"NXattenuator", dtype="S")
            ds = g.create_dataset(u"thickness", dtype="f8",
                    data=float(self.parameters["filterThickness"])/1000000)
            ds.attrs[u"units"] = data=numpy.array(u"m", dtype="S")
            ds = g.create_dataset(u"type", data=numpy.array(u"Aluminum", dtype="S"))
            ds = g.create_dataset(u"attenuator_transmission", dtype="f8",
                    data=float(self.parameters["filterTransmission"]))
            #fix rotation axis and detector orientation
            ds = f.get(u"entry/sample/transformations/omega")
            ds.attrs[u"vector"] = [1., 0., 0.]
            ds = f.get(u"entry/instrument/detector/module/fast_pixel_direction")
            ds.attrs[u"vector"] = [1., 0., 0.]
            ds = f.get(u"entry/instrument/detector/module/slow_pixel_direction")
            ds.attrs[u"vector"] = [0., 1., 0.]
            #delete phi angle info to avoid confusion
            nodes = [
                "entry/sample/goniometer/phi",
                "entry/sample/goniometer/phi_end",
                "entry/sample/goniometer/phi_range_average",
                "entry/sample/goniometer/phi_range_total"]
            for node in nodes:
                if node in f:
                    del f[node]
            f.close()
        except:
            print(sys.exc_info()[1])
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),
                    "Failed to insert info to H5 file.")

    def writeInfo(self):
        path = self.path.get_path("/beamline/beamtime/raw/user/sample" +
                "/ismo_number", force=True)
        energy = self.petraThread.currentMonoEnergy/1000.
        wavelength = 12.3984/(energy) #in Angstrom
        resolution = wavelength/(2.*math.sin(0.5*math.atan((311./2.)/ self.parameters["detectordistance"])))
        frames = len(self.parameters["scanPoints"])
        output = self.INFO_TXT.format(
            name = self.path.get_path("sample_ismo_number"),
            rows = self.parameters["rows"],
            columns = self.parameters["columns"],
            angle = self.goniometerThread.currentAngle,
            frames = frames,
            framesperposition=self.parameters["framesperposition"],
            degreesperframe=self.degreesPerFrame,
            exposuretime = self.parameters["exposureperiod"] * 1000,
            energy = energy,
            wavelength = wavelength,
            detectordistance = self.parameters["detectordistance"],
            resolution = resolution,
            pinholeDiameter = int(self.parameters["pinholeDiameter"]),
            focus = self.parameters["focus"],
            filterTransmission = self.parameters["filterTransmission"]*100,
            filterThickness = int(self.parameters["filterThickness"]),
            beamCurrent = self.parameters["beamCurrent"]
        )
        try:
            f = open(path + "/info.txt", "w")
            f.write(output)
            f.close()
        except:
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Unable to write info file.")

    def collectionTime(self, percent = False):
        if percent:
            return ((self.totalTime - self.remainingTime) / self.totalTime) * 100
        return self.remainingTime


class SerialCollector(QThread):

    ERR_NO_ERROR = 0
    ERR_CANCELLED = 1
    ERR_TYPE_MISMATCH = 2
    ERR_VALUE_OUT_OF_RANGE = 3
    ERR_TIMEOUT = 4
    ERR_ALREADY_RUNNING = 8
    ERR_INTERLOCK_NOT_SET = 9
    ERR_MISALIGNED_BEAMSTOP = 10
    ERR_PIEZOMOTOR_OFFLINE = 11
    ERR_WAIT_CONDITION_TIMEOUT = 12
    
    ERR_MSGS = [ \
        "Success.", \
        "Canceled.", \
        "Wrong parameter type.", \
        "Parameter value out of range.", \
        "Timeout during start up procedure.", \
        "", \
        "", \
        "", \
        "Serial collection is already running.", \
        "Interlock is not set.", \
        "Beamstop is not aligned. \n Direct beam on detector! Please contact beamline personnel.", \
    ]

    WAIT_CONDITIONS_TIMEOUT = 1000 #*interval
    WAIT_CONDITIONS_INTERVAL = 200 #ms
    WAIT_CONDITIONS_TIMEOUT_NEXTSCANPOINT = 1000 #*interval
    WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT = 100 #ms

    DETECTORTOWER_TOLERANCE = 1.0 #mm
    PILATUS_ENERGY_TOLERANCE = 500.0 #eV
    serialMoveThread = None

    # A thread is started by calling QThread.start() never by calling run() directly!
    def __init__(self, detectorTowerThread, goniometerThread, petraThread, piezoThread, pilatusThread, liveViewThread, filesystem, parent = None, simulation = False):
        QThread.__init__(self, parent)
        #self.MainWindow = mainwindowPassing
        print("Serial collection thread: Starting thread")
        self.myparent = parent
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Preparing serial collection...")
        self.alive = True
        self.waitConditionActive = False
        self.dataCollectionActive = False
        self.remainingTime = 0.0
        self.parameters = { 
            "filetype": ".cbf", \
            "filenumber": 0, \
            "frames": 0, \
            "exposuretime": 0.0, \
            "exposureperiod": 0.0, \
            "detectordistance": 0.0, \
            "liveview": False, \
            "pinhole": 0, \
            "pinholeDiameter": 0, \
            "filterTransmission": 1.0, \
            "filterThickness": 0.0, \
            "beamX": 1262, \
            "beamY": 1242, \
            "scanPoints": [], \
            "sampleoutDistanceWhenBeamcheck": 0, \
            "scantype": 0, \
            "scanvelocity": None, \
        }
        self.conditionsList = { \
            "BS0open": False, \
            "BS1open": False, \
            "FSopen": False, \
            "BeamstopInPosition": False, \
            "DetectorInPosition": False, \
            "DetectorThresholdSet": False, \
            "GoniometerInPosition": False, \
            "CollimatorInPosition": False, \
            "ContrastScreenInPosition": False, \
            "BeamstopDiodeOK": False, \
            "ShieldDown": False, \
            "CollectionStarted": False , \
            }
        
        self.debugMode = 0
        self.detectorTowerThread = detectorTowerThread
        self.goniometerThread = goniometerThread
        self.petraThread = petraThread
        self.piezoThread = piezoThread
        self.pilatusThread = pilatusThread
        self.liveViewThread = liveViewThread
        self.filesystem = filesystem
        self.centreAngle = 0
        self.timePerSample = 0
        self.degreesPerFrame = 0
        self.starttime = time.time()
        self.remainingTime = 0
        self.progress = 0


    def stop(self):
        print("Serial collector thread: Stopping thread")
        self.alive = False
        self.wait() # waits until run stops on his own


    def join(self, timeout=None):
        print("Serial collector thread: join method")
        self.alive = False


    def run(self):
        self.alive = True
        
        print("Serial collector thread: started")
        if(self.parameters["frames"] == 0.0):
                raise Exception(self.ERR_VALUE_OUT_OF_RANGE,"frames",self.parameters["frames"])
        
        self.setPilatusParameters()
        
        if not self.detectorTowerThread.statusInterlock: #FIXME
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"Serial collection: Interlock is not set.")
            return
        
        if not self.piezoThread.pinholeAboveMinimumZ:
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"Serial collection: No pinhole selected.")
            return
        
        #set up everything
        self.totalTime = self.parameters["frames"] * self.parameters["exposureperiod"]/1000.
        self.remainingTime = self.totalTime
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Preparing to start Serial collection")
        
        print("Checking wait conditions")
        err = self.waitConditions()
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Serial collection preparations done")
        while self.alive and (self.goniometerThread.stateKohzuGoniometerY == "MOVING" or self.goniometerThread.stateKohzuGoniometerZ == "MOVING"):            
            time.sleep(0.01)
        self.goniometerThread.setPositionKohzuGoniometerY(self.parameters["scanPoints"][0][0])
        self.goniometerThread.setPositionKohzuGoniometerZ(self.parameters["scanPoints"][0][1])
        while self.alive and (self.goniometerThread.stateKohzuGoniometerY == "MOVING" or self.goniometerThread.stateKohzuGoniometerZ == "MOVING"):            
            time.sleep(0.01)

        print("WAIT RETURNED", err)
        if(err == self.ERR_NO_ERROR):
            #start data collection
            if self.parameters["scantype"] == 0:
                pass
            if self.parameters["scantype"] == 1:
                print("Serial collector: starting line scan thread")
                self.serialMoveThread = GridScanThread(self.goniometerThread,self.parameters["scanPoints"],self.parameters["scanvelocity"])
                self.serialMoveThread.start()
            if self.parameters["scantype"] == 2:
                print("Serial collector: starting grid scan thread")
                self.serialMoveThread = GridScanThread(self.goniometerThread,self.parameters["scanPoints"],self.parameters["scanvelocity"],scantype=self.parameters["scantype"])
                self.serialMoveThread.start()

            self.emit(SIGNAL("waitConditionsUpdate()"))
            if self.parameters["liveview"]:
                self.liveViewThread.start(self.filesystem.getPath(self.filesystem.FS_ROOT_LOCAL + self.filesystem.FS_SUB_RAW + self.filesystem.FS_TYPE_REGULAR))
            
            print("Serial collector: opening shutter")
            self.goniometerThread.openShutter()
            self.conditionsList["FSopen"] = True
            self.emit(SIGNAL("waitConditionsUpdate()"))
            print("Serial collector: starting acquisition")
            self.pilatusThread.startAcquisition()
            time.sleep(1.0)
            self.dataCollectionActive = True
            
            self.conditionsList["CollectionStarted"] = True
            self.emit(SIGNAL("waitConditionsUpdate()"))
            #data collection running
            self.starttime = time.time()
            while (self.pilatusThread.statePilatus == "RUNNING") and self.alive:
                elapsedTime = time.time()-self.starttime
                self.remainingTime = self.totalTime-elapsedTime
                self.progress = 100*(elapsedTime/self.totalTime)
                time.sleep(0.1)
            
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Collection finished.")
            print("Serial collection done at",time.time())
            #abort data collection
            if(self.pilatusThread.statePilatus == "FAULT"):
                self.pilatusThread.stopAcquisition()
                self.goniometerThread.stopMotion()
                self.goniometerThread.closeShutter()
                if self.serialMoveThread is not None: 
                    self.serialMoveThread.stop()
                    self.serialMoveThread.join()
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Serial collection error: Pilatus is in FAULT state.")
            if(not self.alive):
                print("Serial collector: alive is FALSE")
                self.pilatusThread.stopAcquisition()
                self.goniometerThread.stopMotion()
                self.goniometerThread.closeShutter()
                if self.serialMoveThread is not None: 
                    print("Serial collector: stopping move thread")
                    self.serialMoveThread.stop()
                    self.serialMoveThread.join()
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Serial collection aborted.")
            #stop data collection
            print("Serial collector: closing shutter")
            self.goniometerThread.closeShutter()
            if self.serialMoveThread is not None:
                print("Serial collector: stopping move thread") 
                self.serialMoveThread.stop()
                self.serialMoveThread.join()
            self.dataCollectionActive = False
        elif(err > self.ERR_CANCELLED):
            #error
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"Serial collection error: "+ str(self.ERR_MSGS[err]))
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Serial collection error: "+ str(self.ERR_MSGS[err]))
            self.goniometerThread.closeShutter()
            self.dataCollectionActive = False
            if self.serialMoveThread is not None: 
                print("Serial collector: stopping move thread")
                self.serialMoveThread.stop()
                self.serialMoveThread.join()
        self.detectorTowerThread.shieldUp()
        if self.parameters["liveview"]:
            self.liveViewThread.stop(3.0)
        print("Serial collector thread: Thread for Data collector died")
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Serial collection finished.")
        self.alive = False


    def setParameters(self, data):
        if(type(data) != dict):
            return self.ERR_TYPE_MISMATCH
        for key in data:
            self.parameters[key] = data[key]


    def setParameter(self, key, data):
        self.parameters[key] = data


    def signalOnaxisImage(self):
        self.emit(SIGNAL("onaxisImage()"))


    def setPilatusParameters(self):
        self.pilatusThread.setTriggerMode(0) #internal
        self.pilatusThread.setDelayTime(0.0)
        self.parameters["exposureperiod"] = self.parameters["exposuretime"] + 16
        if self.parameters["exposureperiod"] < 40:
            self.parameters["exposureperiod"] = 40
        self.pilatusThread.setExposureTime(self.parameters["exposuretime"]/1000.)
        self.pilatusThread.setExposurePeriod(self.parameters["exposureperiod"]/1000.)
        self.pilatusThread.setImageFileType(self.parameters["filetype"])
        self.pilatusThread.setNumberOfFrames(self.parameters["frames"])
        self.pilatusThread.setNumberOfExposuresPerFrame(1)
        #self.pilatusThread.setShutterControl(False)
        self.pilatusThread.setMXparameter("Wavelength %6.4f"%(12.3984/(self.petraThread.currentMonoEnergy/1000.0)))
        self.pilatusThread.setMXparameter("Filter_transmission %5.2f%%"%self.parameters["filterTransmission"])
        self.pilatusThread.setMXparameter("Filter_thickness %4d um Al"%self.parameters["filterThickness"])
        self.pilatusThread.setMXparameter("Pinhole %3d um"%self.parameters["pinholeDiameter"])
        self.pilatusThread.setMXparameter("Detector_distance %8.3fE-3"%self.parameters["detectordistance"])
        self.pilatusThread.setMXparameter("Beam_xy %d %d"%(self.parameters["beamX"], self.parameters["beamY"]))
        self.pilatusThread.setImageFileNumber(1)
        self.pilatusThread.setImageFilePrefix(self.filesystem.getFilename(self.filesystem.FS_TYPE_REGULAR, ""))
        self.pilatusThread.setImageFilePath(self.filesystem.getPath(self.filesystem.FS_ROOT_LOCAL + self.filesystem.FS_SUB_RAW + self.filesystem.FS_TYPE_REGULAR))
        time.sleep(0.1)
 

    def waitConditions(self):
        if(not self.detectorTowerThread.statusInterlock): #FIXME
            return self.ERR_INTERLOCK_NOT_SET
        
        if(self.waitConditionActive):
            return self.ERR_ALREADY_RUNNING
        self.waitConditionActive = True
        waitConditionTimeOut = 0
        while(True):
            conditions = True
            #Shutter
            if(self.goniometerThread.statusFastShutter):
                print("Closing FS")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Closing FS")
                self.goniometerThread.closeShutter()
                conditions = False
            #BS0
            if(not self.petraThread.statusShutterBS0):
                print("opening BS0")
                self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Opening BS0")
                self.petraThread.openBS0()
                conditions = False
            else:
                self.conditionsList["BS0open"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #BS1
            if(not self.petraThread.statusShutterBS1): 
                self.petraThread.openBS1()
                conditions = False
            else:
                self.conditionsList["BS1open"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Beamstop
            if (self.piezoThread.beamstopXInOut == "Out"):
                if (self.piezoThread.stateProxyPiezoBeamstopX == "ON"):
                    self.piezoThread.moveBeamStopIn()
            elif (self.piezoThread.beamstopXInOut == "In"):
                self.conditionsList["BeamstopInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #DetectorTower
            if(self.parameters["detectordistance"] > self.detectorTowerThread.currentPositionDetectorTowerServer + self.DETECTORTOWER_TOLERANCE or \
                    self.parameters["detectordistance"] < self.detectorTowerThread.currentPositionDetectorTowerServer - self.DETECTORTOWER_TOLERANCE):
                if(self.parameters["detectordistance"] < self.detectorTowerThread.minPositionDetectorTowerServer + 0.1):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Invalid detector distance (value out of range).")
                    return self.ERR_VALUE_OUT_OF_RANGE
                elif(self.parameters["detectordistance"] > self.detectorTowerThread.maxPositionDetectorTowerServer - 0.1):
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Invalid detector distance (value out of range).")
                    return self.ERR_VALUE_OUT_OF_RANGE
                elif(self.detectorTowerThread.stateDetectorTower == "ON"):
                    print("Moving detector tower")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving detector tower.")
                    self.detectorTowerThread.setPositionDetectorTower(self.parameters["detectordistance"])
                conditions = False
            else:
                self.conditionsList["DetectorInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Pilatus
            if(self.petraThread.currentMonoEnergy > (self.pilatusThread.photonEnergy + self.PILATUS_ENERGY_TOLERANCE) or \
                self.petraThread.currentMonoEnergy < (self.pilatusThread.photonEnergy - self.PILATUS_ENERGY_TOLERANCE)):
                if(self.pilatusThread.statePilatus == "ON"):
                    print("Setting pilatus threshold")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Setting pilatus energy threshold.")
                    if self.petraThread.currentMonoEnergy > 5500:
                        self.pilatusThread.setPhotonEnergy(self.petraThread.currentMonoEnergy)
                    else:
                        self.pilatusThread.setPhotonEnergy(5500)
                    time.sleep(1.5)
                    conditions = False
                    self.conditionsList["DetectorThresholdSet"] = False
            elif (self.pilatusThread.statePilatus == "ON"):
                self.conditionsList["DetectorThresholdSet"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            elif(not self.pilatusThread.statePilatus == "ON"):
                conditions = False
                self.conditionsList["DetectorThresholdSet"] = False
                self.emit(SIGNAL("waitConditionsUpdate()"))
            #Pinhole
            if(self.parameters["pinhole"] != self.piezoThread.currentPinholePosition):
                if(self.piezoThread.statePinhole == "ON"):
                    print("Setting pinhole")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Setting pinhole.")
                    self.piezoThread.setPinhole(self.parameters["pinhole"])
                conditions = False
            #Collimator
            if(not self.piezoThread.collimatorInPlace):
                if(self.piezoThread.stateCollimator == "ON"):
                    print("Moving collimator in")
                    self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Moving collimator in.")
                    self.piezoThread.collimatorIn()
                conditions = False
            else:
                self.conditionsList["CollimatorInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
                
            #ContrastScreen
            if(self.goniometerThread.positionContrastscreen):
                self.goniometerThread.moveContrastScreenOut()
                conditions = False
            else:
                self.conditionsList["ContrastScreenInPosition"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))

            if (self.conditionsList["BS1open"] and self.conditionsList["BS0open"]) and (not self.conditionsList["BeamstopDiodeOK"] and self.detectorTowerThread.shieldIsUp):
                
                if(not self.goniometerThread.statusFastShutter):
                    self.goniometerThread.openShutter()
                time.sleep(0.5)
                if(self.detectorTowerThread.diodeThresholdOK):
                    self.conditionsList["BeamstopDiodeOK"] = True
                    self.emit(SIGNAL("waitConditionsUpdate()"))
                    self.goniometerThread.closeShutter()
                    self.detectorTowerThread.shieldDown()
                else:
                    return self.ERR_MISALIGNED_BEAMSTOP
            
            if (self.conditionsList["BeamstopDiodeOK"] and self.detectorTowerThread.shieldIsDown):
                self.conditionsList["ShieldDown"] = True
                self.emit(SIGNAL("waitConditionsUpdate()"))
            
            #check end conditions
            if (self.conditionsList["BS0open"] and \
                self.conditionsList["BS1open"] and \
                self.conditionsList["BeamstopInPosition"] and \
                self.conditionsList["BeamstopDiodeOK"] and \
                self.conditionsList["DetectorInPosition"] and \
                self.conditionsList["DetectorThresholdSet"] and \
                self.conditionsList["CollimatorInPosition"] and \
                self.conditionsList["ContrastScreenInPosition"] and \
                self.conditionsList["ShieldDown"]):
                self.waitConditionActive = False
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_NO_ERROR
                 
            #if(conditions):
            #    self.waitConditionActive = False
            #    self.emit(SIGNAL("waitConditionsUpdate()"))
            #    return self.ERR_NO_ERROR
            waitConditionTimeOut += 1
            if(waitConditionTimeOut >= self.WAIT_CONDITIONS_TIMEOUT):
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_WAIT_CONDITION_TIMEOUT
            if(not self.alive):
                self.emit(SIGNAL("waitConditionsUpdate()"))
                return self.ERR_CANCELLED
            
            self.msleep(self.WAIT_CONDITIONS_INTERVAL)
