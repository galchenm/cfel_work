from PyQt4.QtCore import SIGNAL, QObject, QThread, Qt
from PyQt4.QtGui import QImage
from PyTango import DeviceProxy, DevState
from mjpgStream import MjpgStream


class VimbaCamera(QObject):

    def __init__(self, devicepath, pixelsperum, offsetX, offsetY, flipX, flipY):
        self.pixelsperum = pixelsperum
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.flipX = flipX
        self.flipY = flipY
        self.online = False
        self.gain = 0.0
        self.gainMin = 0.0
        self.gainMax = 0.0
        self.gainAuto = False
        self.exposure = 0.0
        self.exposureMin = 0.0
        self.exposureMax = 0.0
        self.exposureAuto = False
        self.width = 0
        self.widthMax = 0
        self.height = 0
        self.heightMax = 0
        self.frame = None
        self.event = None
        QObject.__init__(self)
        #init camera
        try:
            self.proxy = DeviceProxy(devicepath)
            self.proxy.write_attribute("ViewingMode", 4)
            self.proxy.write_attribute("TriggerSource", "FixedRate")
            self.proxy.write_attribute("AcquisitionFrameRateAbs", 10.)
            self.proxy.write_attribute("ExposureAutoMax", 200000)
            self.proxy.write_attribute("ExposureAuto", "Continuous")
            self.proxy.write_attribute("GainAuto", "Continuous")
            self.widthMax = self.proxy.read_attribute("WidthMax").value
            self.heightMax = self.proxy.read_attribute("HeightMax").value
            self.online = True
        except:
            print("failed to connect camera", devicepath)
            self.online = False
        self.updateValues()

    def start(self):
        try:
            if self.proxy.state() != DevState.RUNNING:
                self.proxy.command_inout("StartAcquisition")
            self.event = self.proxy.subscribe_event("ImageEnc", \
                    EventType.DATA_READY_EVENT, self.frameGrabbed, [], False)
        except:
            print("VimbaCamera.start():", sys.exc_info())

    def stop(self):
        try:
            if self.proxy.state() == DevState.RUNNING:
                self.proxy.command_inout("StopAcquisition")
            self.proxy.unsubscribe_event(self.event)
            self.event = None
        except:
            print("VimbaCamera.stop():", sys.exc_info())

    def frameGrabbed(self, event):
        try:
            event_type = event.event
            name = event.attr_name.lower()
            n = name.rfind("/")
            if n > 0:
                name = name[n+1:]
            if name == "imageenc" and event_type == "data_ready":
                value = self.connector.proxy.read_attribute("ImageEnc", extract_as=ExtractAs.ByteArray).value[1]
                self.frame = QImage.fromData(value)
                if self.frame is not None:
                    self.frame = self.frame.mirrored(self.flipX, self.flipY)
            self.emit(SIGNAL("newFrame()"))
        except:
            print("VimbaCamera.frameGrabbed():", sys.exc_info())

    def getFrame(self):
        return self.frame

    def updateValues(self):
        attrs = ["ExposureAuto", "ExposureAutoMin", "ExposureAutoMax",
            "ExposureTimeAbs", "GainAuto", "GainAutoMin", "GainAutoMax",
            "Gain", "Width", "Height"]
        try:
            results = self.proxy.read_attributes(attrs)
            self.online = True
        except:
            self.online = False
            results = []
            print("VimbaCamera.frameGrabbed(): failed to read from camera")
        for result in results:
            if result.name == "ExposureAuto":
                if result.value == "Continuous":
                    self.exposureAuto = True
                elif result.value == "Off":
                    self.exposureAuto = False
                else:
                    self.exposureAuto = None
            elif result.name == "ExposureAutoMin":
                self.exposureMin = result.value
            elif result.name == "ExposureAutoMax":
                self.exposureMax = result.value
            elif result.name == "ExposureTimeAbs":
                self.exposure = result.value
            elif result.name == "GainAuto":
                if result.value == "Continuous":
                    self.gainAuto = True
                elif result.value == "Off":
                    self.gainAuto = False
                else:
                    self.gainAuto = None
            elif result.name == "GainAutoMin":
                self.gainMin = result.value
            elif result.name == "GainAutoMax":
                self.gainMax = result.value
            elif result.name == "Gain":
                self.gain = result.value
            elif result.name == "Width":
                self.width = result.value
            elif result.name == "Height":
                self.height = Height.value

    def setCropSize(self, width=0, height=0):
        if width == 0 and height == 0:
            width = self.widthMax
            height = self.heightMax
        width = min(self.widthMax - 2 * abs(self.offsetX), width)
        height = min(self.heightMax - 2 * abs(self.offsetY), height)
        posX = max((self.widthMax - 2 * abs(self.offsetX) - width) / 2., 0)
        posY = max((self.heightMax - 2 * abs(self.offsetY) - height) / 2., 0)
        if self.offsetX > 0.0:
            posX += 2 * self.offsetX
        if self.offsetY > 0.0:
            posY += 2 * self.offsetY
        self.width = width
        self.height = height
        try:
            self.proxy.write_attribute("BinningHorizontal", 1)
            self.proxy.write_attribute("BinningVertical", 1)
            if int(posX) == 0:
                 self.proxy.write_attribute("OffestX", 0)
            if int(posY) == 0:
                 self.proxy.write_attribute("OffestX", 0)
            self.proxy.write_attribute("Width", int(width))
            self.proxy.write_attribute("height", int(height))
            if int(posX) > 0:
                 self.proxy.write_attribute("OffestX", int(posX))
            if int(posY) > 0:
                 self.proxy.write_attribute("OffestX", int(posY))
        except:
            print("VimbaCamera.setCropSize(): failed to write to camera")

    def getPixelsPerUm(self):
        return self.pixelsperum

    def setGain(self, value):
        try:
            self.proxy.write_attribute("Gain", value)
        except:
            print("VimbaCamera.setGain(): failed to write to camera")

    def setExposure(self, value):
        try:
            self.proxy.write_attribute("ExposureTimeAbs", value)
        except:
            print("VimbaCamera.setExposure(): failed to write to camera")

    def setAutoGain(self, value):
        if value:
            value = "Continuous"
        else:
            value = "Off"
        try:
            self.proxy.write_attribute("GainAuto", value)
        except:
            print("VimbaCamera.setAutoGain(): failed to write to camera")

    def setAutoExposure(self, value):
        if value:
            value = "Continuous"
        else:
            value = "Off"
        try:
            self.proxy.write_attribute("ExposureAuto", value)
        except:
            print("VimbaCamera.setAutoExposure(): failed to write to camera")

    def isRunning(self):
        return self.proxy.state() == DevState.RUNNING


class VideoCamera(QObject):

    def __init__(self, host, port, pixelsperum, offsetX, offsetY, flipX, flipY):
        self.camera = MjpgStream(host, port)
        self.pixelsperum = pixelsperum
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.flipX = flipX
        self.flipY = flipY
        self.online = False
        self.gain = 0.0
        self.gainMin = 0.0
        self.gainMax = 0.0
        self.gainAuto = False
        self.exposure = 0.0
        self.exposureMin = 0.0
        self.exposureMax = 0.0
        self.exposureAuto = False
        self.width = 0
        self.widthMax = 0
        self.height = 0
        self.heightMax = 0
        self.frame = None
        QObject.__init__(self)
        #init camera
        self.camera.sendCmd("FixedRate", MjpgStream.IN_CMD_AVT_FRAME_START_TRIGGER_MODE) # set to fixed rate
        self.camera.sendCmd(10000, MjpgStream.IN_CMD_AVT_FRAMERATE) # fixed rate in miliHz
        self.camera.sendCmd("Continuous", MjpgStream.IN_CMD_AVT_ACQUISITION_MODE) # acquisition mode continuous
        self.camera.sendCmd(0, MjpgStream.IN_CMD_AVT_ACQUISITION_START) # start acquisition
        self.camera.sendCmd(200000, MjpgStream.IN_CMD_AVT_EXPOSURE_AUTO_MAX) # auto exposure not longer than 200 ms
        self.camera.sendCmd("Auto", MjpgStream.IN_CMD_AVT_EXPOSURE_MODE) # auto exposure
        self.camera.sendCmd("Auto", MjpgStream.IN_CMD_AVT_GAIN_MODE) # auto gain
        data = self.camera.getControls()
        if data is not None:
            for info in data:
                if int(info["group"]) == MjpgStream.IN_CMD_GROUP_AVT_INFO:
                    if int(info["id"]) == MjpgStream.IN_CMD_AVT_SENSOR_HEIGHT[0]:
                        self.heightMax = int(info["value"])
                    elif int(info["id"]) == MjpgStream.IN_CMD_AVT_SENSOR_WIDTH[0]:
                        self.widthMax = int(info["value"])
                elif int(info["group"]) == MjpgStream.IN_CMD_GROUP_AVT_IMAGE_FORMAT:
                    if int(info["id"]) == MjpgStream.IN_CMD_AVT_HEIGHT[0]:
                        self.height = int(info["value"])
                    elif int(info["id"]) == MjpgStream.IN_CMD_AVT_WIDTH[0]:
                        self.width = int(info["value"])
        self.connect(self.camera, SIGNAL("newFrame()"), self.frameGrabbed)
        self.updateValues()

    def start(self):
        self.camera.start()

    def stop(self):
        if self.camera.isRunning():
            self.camera.stop()

    def frameGrabbed(self):
        self.frame = self.camera.getFrame()
        if self.frame is not None:
            self.frame = self.frame.mirrored(self.flipX, self.flipY)
        self.emit(SIGNAL("newFrame()"))

    def getFrame(self):
        return self.frame

    def updateValues(self):
        self.camera.sendCmd(MjpgStream.IN_CMD_GROUP_AVT_EXPOSURE, MjpgStream.IN_CMD_UPDATE_CONTROLS)
        self.camera.sendCmd(MjpgStream.IN_CMD_GROUP_AVT_GAIN, MjpgStream.IN_CMD_UPDATE_CONTROLS)
        data = self.camera.getControls()
        if data is not None:
            for info in data:
                if int(info["group"]) == MjpgStream.IN_CMD_GROUP_AVT_EXPOSURE:
                    if int(info["id"]) == MjpgStream.IN_CMD_AVT_EXPOSURE_VALUE[0]:
                        self.exposure = int(info["value"])
                        self.exposureMin = int(info["min"])
                        self.exposureMax = int(info["max"])
                    elif int(info["id"]) == MjpgStream.IN_CMD_AVT_EXPOSURE_MODE[0]:
                        self.exposureAuto = (info["menu"][info["value"]] == "Auto")
                elif int(info["group"]) == MjpgStream.IN_CMD_GROUP_AVT_GAIN:
                    if int(info["id"]) == MjpgStream.IN_CMD_AVT_GAIN_VALUE[0]:
                        self.gain = int(info["value"])
                        self.gainMin = int(info["min"])
                        self.gainMax = int(info["max"])
                    elif int(info["id"]) == MjpgStream.IN_CMD_AVT_GAIN_MODE[0]:
                        self.gainAuto = (info["menu"][info["value"]] == "Auto")
                elif int(info["group"]) == MjpgStream.IN_CMD_GROUP_AVT_IMAGE_FORMAT:
                    if int(info["id"]) == MjpgStream.IN_CMD_AVT_HEIGHT[0]:
                        self.height = int(info["value"])
                    elif int(info["id"]) == MjpgStream.IN_CMD_AVT_WIDTH[0]:
                        self.width = int(info["value"])
            self.online = True
        else:
            self.online = False

    def setCropSize(self, width=0, height=0):
        if width == 0 and height == 0:
            width = self.widthMax
            height = self.heightMax
        width = min(self.widthMax - 2 * abs(self.offsetX), width)
        height = min(self.heightMax - 2 * abs(self.offsetY), height)
        posX = max((self.widthMax - 2 * abs(self.offsetX) - width) / 2., 0)
        posY = max((self.heightMax - 2 * abs(self.offsetY) - height) / 2., 0)
        if self.offsetX > 0.0:
            posX += 2 * self.offsetX
        if self.offsetY > 0.0:
            posY += 2 * self.offsetY
        self.width = width
        self.height = height
        self.camera.sendCmd(1, MjpgStream.IN_CMD_AVT_BINNING_X)
        self.camera.msleep(10)
        self.camera.sendCmd(1, MjpgStream.IN_CMD_AVT_BINNING_Y)
        self.camera.msleep(10)
        if int(posX) == 0:
            self.camera.sendCmd(int(posX), MjpgStream.IN_CMD_AVT_REGION_X)
            self.camera.msleep(10)
        if int(posY) == 0:
            self.camera.sendCmd(int(posY), MjpgStream.IN_CMD_AVT_REGION_Y)
            self.camera.msleep(10)
        self.camera.sendCmd(int(width), MjpgStream.IN_CMD_AVT_WIDTH)
        self.camera.msleep(10)
        self.camera.sendCmd(int(height), MjpgStream.IN_CMD_AVT_HEIGHT)
        self.camera.msleep(10)
        if int(posX) > 0:
            self.camera.sendCmd(int(posX), MjpgStream.IN_CMD_AVT_REGION_X)
            self.camera.msleep(10)
        if int(posY) > 0:
            self.camera.sendCmd(int(posY), MjpgStream.IN_CMD_AVT_REGION_Y)

    def getPixelsPerUm(self):
        return self.pixelsperum

    def setGain(self, value):
        self.camera.sendCmd(value, MjpgStream.IN_CMD_AVT_GAIN_VALUE)

    def setExposure(self, value):
        self.camera.sendCmd(value, MjpgStream.IN_CMD_AVT_EXPOSURE_VALUE)

    def setAutoGain(self, value):
        if value:
            self.camera.sendCmd("Auto", MjpgStream.IN_CMD_AVT_GAIN_MODE)
        else:
            self.camera.sendCmd("Manual", MjpgStream.IN_CMD_AVT_GAIN_MODE)

    def setAutoExposure(self, value):
        if value:
            self.camera.sendCmd("Auto", MjpgStream.IN_CMD_AVT_EXPOSURE_MODE)
        else:
            self.camera.sendCmd("Manual", MjpgStream.IN_CMD_AVT_EXPOSURE_MODE)

    def isRunning(self):
        return self.camera.running


class SimulatedVideoCamera(QObject):

    def __init__(self):
        self.pixelsperum = 1.0
        self.online = True
        self.offsetX = 0
        self.offsetY = 0
        self.flipX = False
        self.flipY = False
        self.gain = 6.0
        self.gainMin = 0.0
        self.gainMax = 400.0
        self.gainAuto = False
        self.exposure = 10000.0
        self.exposureMin = 1.0
        self.exposureMax = 100000.0
        self.exposureAuto = False
        self.raw = QImage("img/fake_camera.png")
        self.frame = self.raw
        self.width = self.raw.width()
        self.widthMax = self.raw.width()
        self.height = self.raw.height()
        self.heightMax = self.raw.height()
        QObject.__init__(self)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def getFrame(self):
        return self.frame

    def updateValues(self):
        self.emit(SIGNAL("newFrame()"))

    def setCropSize(self, width=0, height=0):
        if width == 0 and height == 0:
            width = self.widthMax
            height = self.heightMax
        width = min(self.widthMax - 2 * abs(self.offsetX), width)
        height = min(self.heightMax - 2 * abs(self.offsetY), height)
        posX = max((self.widthMax - 2 * abs(self.offsetX) - width) / 2., 0)
        posY = max((self.heightMax - 2 * abs(self.offsetY) - height) / 2., 0)
        if self.offsetX > 0.0:
            posX += 2 * self.offsetX
        if self.offsetY > 0.0:
            posY += 2 * self.offsetY
        self.width = width
        self.height = height
        print(self.raw, self.frame)
        self.frame = self.raw.copy(int(posX), int(posY), int(width), int(height))

    def getPixelsPerUm(self):
        return self.pixelsperum

    def setGain(self, value):
        self.gain = min(value, self.gainMax)
        self.gain = max(self.gain, self.gainMin)

    def setExposure(self, value):
        self.exposure = min(value, self.exposureMax)
        self.exposure = max(self.exposure, self.exposureMin)

    def setAutoGain(self, value):
        self.gainAuto = bool(value)

    def setAutoExposure(self, value):
        self.exposureAuto = bool(value)

    def isRunning(self):
        return self.running


class VideoThread(QThread):

    def __init__(self, cameras, simulation = False):
        self.simulation = simulation
        self.pixelsperum = 1
        self.offsetX = 0
        self.offsetY = 0
        self.flipX = False
        self.flipY = False
        self.online = False
        self.gain = 0.0
        self.gainMin = 0.0
        self.gainMax = 0.0
        self.gainAuto = False
        self.exposure = 0.0
        self.exposureMin = 0.0
        self.exposureMax = 0.0
        self.exposureAuto = False
        self.width = 1
        self.height = 1
        self.frame = None
        self.running = False
        QThread.__init__(self)
        self.camera = None
        self.cameras = []
        if not simulation:
            for camera in cameras:
                self.cameras.append(VideoCamera(camera["host"], \
                        camera["port"], camera["pixelsperum"], \
                        camera["offsetX"], camera["offsetY"], \
                        camera["flipX"], camera["flipY"]))
            self.changeCamera(0)
        else:
            for camera in cameras:
                self.cameras.append(SimulatedVideoCamera())
            self.changeCamera(0)

    def changeCamera(self, n):
        if len(self.cameras) > n:
            if self.camera is not None:
                self.camera.stop()
                self.disconnect(self.camera, SIGNAL("newFrame()"), self.frameGrabbed)
            self.camera = self.cameras[n]
            self.camera.start()
            while not self.camera.isRunning():
                 self.msleep(10)
            self.connect(self.camera, SIGNAL("newFrame()"), self.frameGrabbed)
            self.offsetX = self.camera.offsetX
            self.offsetY = self.camera.offsetY
            self.flipX = self.camera.flipX
            self.flipY = self.camera.flipY

    def run(self):
        if not self.simulation:
            self.running = True
            while self.running:
                self.updateValues()
                self.sleep(1)

    def updateValues(self):
        self.camera.updateValues()
        self.gain = self.camera.gain
        self.gainMin = self.camera.gainMin
        self.gainMax = self.camera.gainMax
        self.gainAuto = self.camera.gainAuto
        self.exposure = self.camera.exposure
        self.exposureMin = self.camera.exposureMin
        self.exposureMax = self.camera.exposureMax
        self.exposureAuto = self.camera.exposureAuto
        self.online = self.camera.online
        self.emit(SIGNAL("updateValues()"))

    def stop(self):
        """Stops the streaming thread.
        
        """
        self.running = False
        self.wait() # waits until run stops on its own  

    def frameGrabbed(self):
        self.frame = self.camera.getFrame()
        if self.frame is not None and self.width and self.height:
            self.frame = self.frame.scaled(self.width, self.height)
        self.emit(SIGNAL("newFrame()"))

    def getFrame(self):
        return self.frame

    def setImageSize(self, width=0, height=0):
        """Sets the parameters on how frames are scaled. If width or height 
        are <=0, no scaling is done.
        
        Keyword arguments:
        width -- width to which the frames should be scaled (default 0)
        height -- height to which the frames should be scaled (default 0)
        
        """
        if(width > 0 and height > 0):
            self.width = width
            self.height = height
        else:
            self.width = 0
            self.height = 0

    def setCropSize(self, width=0, height=0):
        if self.simulation:
            return
        self.camera.setCropSize(width, height)

    def getPixelsPerUm(self):
        if self.simulation:
            return 1
        pixelsperum = self.camera.getPixelsPerUm()
        if(self.width > 0 and self.height > 0):
            pixelsperum /= (self.camera.width / float(self.width))
        return pixelsperum

    def setGain(self, value):
        if not self.simulation:
            self.camera.setGain(value)

    def setExposure(self, value):
        if not self.simulation:
            self.camera.setExposure(value)
            
    def setAutoGain(self, value):
        if not self.simulation:
            self.camera.setAutoGain(value)

    def setAutoExposure(self, value):
        if not self.simulation:
            self.camera.setAutoExposure(value)
