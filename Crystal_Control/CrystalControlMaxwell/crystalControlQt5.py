#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# most imports are done in the main routine
print("Importing modules...")
import os
import sys
try:
	from PyQt4 import QtCore, QtGui
except:
	from PyQt5 import QtCore, QtGui, QtWidgets
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
print("...done")    
# To convert ui into python, one can run in src folder command: 
# pyuic4   lib/crystalControlGUI.ui -o lib/crystalControlGUI.py
# after running this command however, one needs to process manually
# paths in the resulting crystalControlGUI.py file. Namely, to remove ../ instances
# from the source code.
# it is 10 sec task using e.g. geany text editor Search/replace
# hopefully the new version of pyuic4 can handle relative path

 


#+class StartQT4(QtGui.QMainWindow):
class StartQT4(QtWidgets.QMainWindow):

    raster = None
    helix = None    
    draggingRaster = None
    lastDraggingRaster = None
    dragging = False
    rotating = False

    items = []
    item = None

    pixelsPerUm = 1.55
    lastPositionKohzuGoniometerY = 0
    lastPositionKohzuGoniometerZ = 0
    lastPositionFlexureY = 0
    lastPositionFlexureX = 0
    sampleWasMoving = False
    dataCollector = None
    currentPinhole = 0
    liveView = None
    path = None
    lineScanThread = None
    progressDialog = None    
    method = None   # string variable. data collection method 

    expTime = 0
    expPeriod = 0
    ismoScanEnabled = 0
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        parent.showMessage("\n\n   Setting up GUI")
        self.connect(self, QtCore.SIGNAL('triggered()'), self.closeEvent)
        self.pixmap = None
        self.raster = RasterItem()
        self.cursorPosition = "none"
        self.waitingForPilatusThreshold = False
        self.waitingForYagIn = False
        self.waitingForDiodeIn = False
        self.waitingForScreenOut = False
        self.waitingForCollimatorIn = False
        self.waitingForCollimatorOut = False
        self.filter1Transmission = 1.
        self.filter2Transmission = 1.
        self.ui = Ui_CrystalControlGUI()
        self.ui.setupUi(self)
        self.cameraOnline = False
        self.path = P11Path()
        self.currentFocus = 0
        self.currentPinhole = 0        
        self.threeClickMode = False
        self.currentSample = 0

        self.stdErrBar = self.ui.textEditDataCollectionLog.verticalScrollBar()
        self.connected = 0
        self.dataCollectionActive = 0
        self.pwhash = "eb0a191797624dd3a48fa681d3061212"
        self.pwhashSX = "d0843a1a4192e7ee7e64096057b8220a"
        self.pxhashISMO = "66f8faf35b245be3409a067bf6bf3fe2"
        self.expert = 0
        self.sxMode = 0
        self.settingsFile = os.path.realpath(os.path.dirname(sys.argv[0])) + '/' + "lastsettings.ini"
        self.configFile = os.path.realpath(os.path.dirname(sys.argv[0])) + '/' + "config.ini"
        self.persistentSettings = {}
        try:
           display_num = os.environ['DISPLAY'].split(':')[1]
        except:
           self.remote = False
        else:
           self.remote = display_num not in ['1.0', '1', 1]
        self.old_umask = os.umask(0o000)

        #--------General GUI widgets------------#
        QObject.connect(self.ui.toolBoxAlignment,QtCore.SIGNAL("currentChanged(int)"), self.tabChanged)
        QObject.connect(self.ui.toolBoxCollection,QtCore.SIGNAL("currentChanged(int)"), self.tabChanged)
        self.ui.actionQuit.triggered.connect(self.exitapp)
        self.ui.actionExpert_view.triggered.connect(self.expertView)
        QObject.connect(self.ui.pushButtonAutoCenterBeamstop,QtCore.SIGNAL("clicked()"), self.autoCenterBeamstop)
        self.ui.actionSAD_MAD.triggered.connect(self.startFluorescenceTool)
        
        QObject.connect(self.ui.pushButtonSaveLog,QtCore.SIGNAL("clicked()"), self.saveLog)
        QObject.connect(self.ui.pushButtonSetRotCenter, QtCore.SIGNAL("clicked()"), self.setRotationCenter)
        QObject.connect(self.ui.pushButtonStopAllSteppers, QtCore.SIGNAL("clicked()"), self.stopAllSteppers)

        QObject.connect(self.ui.pushButtonCenteringNClick,QtCore.SIGNAL("clicked()"), self.setMoveToBeam)
        QObject.connect(self.ui.pushButtonThreeClickMode,QtCore.SIGNAL("clicked()"), self.setThreeClickMode)
        QObject.connect(self.ui.pushButtonGridScanMode,QtCore.SIGNAL("clicked()"), self.setGridScanMode)
        self.ui.pushButtonGridScanMode.setHidden(True)
        
        #--------Widgets on Beam settings tab-----------#
        QObject.connect(self.ui.pushButtonCloseBS1,QtCore.SIGNAL("clicked()"), self.closeBS1)
        QObject.connect(self.ui.pushButtonOpenBS1,QtCore.SIGNAL("clicked()"), self.openBS1)
        QObject.connect(self.ui.pushButtonOpenShutter,QtCore.SIGNAL("clicked()"), self.openShutter)
        QObject.connect(self.ui.pushButtonCloseShutter,QtCore.SIGNAL("clicked()"), self.closeShutter)
        QObject.connect(self.ui.pushButtonYAGin,QtCore.SIGNAL("clicked()"), self.YAGIn)
        QObject.connect(self.ui.pushButtonDiodeIn,QtCore.SIGNAL("clicked()"), self.diodeIn)
        QObject.connect(self.ui.pushButtonScreenOut,QtCore.SIGNAL("clicked()"), self.screenOut)
        QObject.connect(self.ui.pushButtonScreenStop,QtCore.SIGNAL("clicked()"), self.screenStop)
        QObject.connect(self.ui.pushButtonSaveBeamPosition,QtCore.SIGNAL("clicked()"), self.saveBeamPosition)
        QObject.connect(self.ui.pushButtonSaveImage,QtCore.SIGNAL("clicked()"), self.saveCurrentImage)
        QObject.connect(self.ui.pushButtonCollimatorIn,QtCore.SIGNAL("clicked()"), self.collimatorIn)
        QObject.connect(self.ui.pushButtonCollimatorOut,QtCore.SIGNAL("clicked()"), self.collimatorOut)
        QObject.connect(self.ui.pushButtonCollimatorStop,QtCore.SIGNAL("clicked()"), self.collimatorStop)
        QObject.connect(self.ui.horizontalSliderFocus,QtCore.SIGNAL("sliderReleased()"), self.setYAGfocus)
        QObject.connect(self.ui.pushButtonAutoCenterPinholes, QtCore.SIGNAL("clicked()"), self.autoCenterPinhole)
        QObject.connect(self.ui.pushButtonSavePinholes, QtCore.SIGNAL("clicked()"), self.save_pinholes)
        QObject.connect(self.ui.pushButtonStopPinholes, QtCore.SIGNAL("clicked()"), self.stopPinhole)
        QObject.connect(self.ui.pushButtonStopFilters, QtCore.SIGNAL("clicked()"), self.stopFilters)
        QObject.connect(self.ui.pushButtonAutoCenterCollimator, QtCore.SIGNAL("clicked()"), self.autoCenterCollimator)
        QObject.connect(self.ui.pushButtonSaveCollimator, QtCore.SIGNAL("clicked()"), self.save_collimator)
        QObject.connect(self.ui.checkBoxCameraAutoExposure, QtCore.SIGNAL("stateChanged(int)"), self.setCameraAutoExposure)
        QObject.connect(self.ui.checkBoxCameraAutoGain, QtCore.SIGNAL("stateChanged(int)"), self.setCameraAutoGain)
                
            
        #----------Widgets on Sample alignment tab-------------#
        QObject.connect(self.ui.pushButtonExtendCryo,QtCore.SIGNAL("clicked()"), self.extendCryo)
        QObject.connect(self.ui.pushButtonRetractCryo,QtCore.SIGNAL("clicked()"), self.retractCryo)
        QObject.connect(self.ui.pushButtonContrastScreenIn,QtCore.SIGNAL("clicked()"), self.contrastScreenIn)
        QObject.connect(self.ui.pushButtonContrastScreenOut,QtCore.SIGNAL("clicked()"), self.contrastScreenOut)
        QObject.connect(self.ui.pushButtonIrisPlus,QtCore.SIGNAL("clicked()"), self.incInlineIris)
        QObject.connect(self.ui.pushButtonIrisMinus,QtCore.SIGNAL("clicked()"), self.decInlineIris)
        QObject.connect(self.ui.pushButtonSpotPlus,QtCore.SIGNAL("clicked()"), self.incInlineSpot)
        QObject.connect(self.ui.pushButtonSpotMinus,QtCore.SIGNAL("clicked()"), self.decInlineSpot)
        QObject.connect(self.ui.pushButtonAbs0,QtCore.SIGNAL("clicked()"), lambda angle=0:self.setGoniometerPosition(angle))
        QObject.connect(self.ui.pushButtonAbs90,QtCore.SIGNAL("clicked()"), lambda angle=90:self.setGoniometerPosition(angle))
        QObject.connect(self.ui.pushButtonAbs180,QtCore.SIGNAL("clicked()"), lambda angle=180:self.setGoniometerPosition(angle))
        QObject.connect(self.ui.pushButtonAbs270,QtCore.SIGNAL("clicked()"), lambda angle=270:self.setGoniometerPosition(angle))
        QObject.connect(self.ui.pushButtonAngleInc,QtCore.SIGNAL("clicked()"), self.incGoniometer)
        QObject.connect(self.ui.pushButtonAngleDec,QtCore.SIGNAL("clicked()"), self.decGoniometer)
        QObject.connect(self.ui.pushButtonStopGoniometer,QtCore.SIGNAL("clicked()"), self.stopGoniometer)
        QObject.connect(self.ui.pushButtonRecalibrateGonio,QtCore.SIGNAL("clicked()"), self.homeGoniometer)
        QObject.connect(self.ui.pushButtonFlexureDown,QtCore.SIGNAL("clicked()"), lambda direction="down":self.incrementFlexure(direction))
        QObject.connect(self.ui.pushButtonFlexureUp,QtCore.SIGNAL("clicked()"), lambda direction="up":self.incrementFlexure(direction))
        QObject.connect(self.ui.pushButtonStopFlexure,QtCore.SIGNAL("clicked()"), self.stopFlexure)
        QObject.connect(self.ui.pushButtonFocusPlus,QtCore.SIGNAL("clicked()"), self.focusPlus)
        QObject.connect(self.ui.pushButtonFocusMinus,QtCore.SIGNAL("clicked()"), self.focusMinus)
        QObject.connect(self.ui.pushButtonKohzuGoniometerLeft,QtCore.SIGNAL("clicked()"), lambda direction="left":self.incrementKohzuGoniometerY(direction))
        QObject.connect(self.ui.pushButtonKohzuGoniometerRight,QtCore.SIGNAL("clicked()"), lambda direction="right":self.incrementKohzuGoniometerY(direction))
        QObject.connect(self.ui.pushButtonManualMountPositionBreakInterlock,QtCore.SIGNAL("clicked()"), self.setManualMountPosition)
        QObject.connect(self.ui.comboBoxStepSize,QtCore.SIGNAL("activated(QString)"), self.setIncrementInterval)
        QObject.connect(self.ui.comboBoxStepSize,QtCore.SIGNAL("editTextChanged(QString)"), self.setIncrementInterval)
        QObject.connect(self.ui.comboBoxAnnealTime,QtCore.SIGNAL("activated(QString)"), self.setAnnealInterval)
        QObject.connect(self.ui.comboBoxAnnealTime,QtCore.SIGNAL("editTextChanged(QString)"), self.setAnnealInterval)
        QObject.connect(self.ui.pushButtonAnneal,QtCore.SIGNAL("clicked()"), self.anneal)

        #--------Widgets on Data collection tab-----------#
        QObject.connect(self.ui.pushButtonStartDataCollection,QtCore.SIGNAL("clicked()"), self.startDataCollection)
        self.ui.pushButtonStartDataCollection.setEnabled(True)
        QObject.connect(self.ui.doubleSpinBoxDetectorDistance,QtCore.SIGNAL("valueChanged(double)"), self.recalculateResolutionLimit)
        QObject.connect(self.ui.doubleSpinBoxResLimit,QtCore.SIGNAL("valueChanged(double)"), self.recalculateDetectorDistance)
        QObject.connect(self.ui.pushButtonStopDetectorTower,QtCore.SIGNAL("clicked()"), self.stopDetector)
        #self.ui.checkBoxTakeDirectBeamImage.setEnabled(False)        
        
        self.method = str(self.ui.toolBoxCollection.itemText(self.ui.toolBoxCollection.currentIndex()))
        self.windowsize = self.ui.graphicsView.size()
        self.scene = QtGui.QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.windowsize.width(), self.windowsize.height())
        self.ui.graphicsView.setTransformationAnchor(0)
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.setInteractive(True)
        self.ui.graphicsView.setMouseTracking(True)
        self.ui.graphicsView.wheelEvent = self.rotateWithMouseWheel
        self.ui.graphicsView.scene().installEventFilter(self)
        self.draggingIsActive = 0
        self.beamWidth = 200
        self.beamHeight = 200
        #self.raster.beamsize.setValue(self.beamWidth, self.beamHeight)
        #self.raster.stepsize.setValue(self.beamWidth, self.beamHeight)
        #self.raster.conversion.setValue(self.pixelsPerUm)

        self.item = QtGui.QGraphicsPixmapItem()  
        self.scene.addItem(self.item)        # it must 
        self.item.setZValue(-1)
        self.item.mousePressEvent = self.moveToBeam  # default behaviour must be set
        self.ui.pushButtonCenteringNClick.setChecked(True)
        self.ui.horizontalSliderFlexureXPosition.setEnabled(False)
        self.ui.verticalSliderFlexureYPosition.setEnabled(False)

        self.addPersistentSetting("file_name", "general", "str", \
            "self.ui.lineEditImagePrefix.text", \
            "self.ui.lineEditImagePrefix.setText")

        parent.showMessage("\n\n   Starting threads")
        self.initIllumination()
        self.initMethod_Std()
        self.initMethod_Screening()
        self.initMethod_Grid()
        self.initMethod_ISMO()
        self.initMethod_Helix()
        self.loadConfig()
        self.initCamera()
        if self.amarcord["enabled"]:
            self.initAmarcord()
        else:
            self.ui.lineEditPuckId.hide()
        self.initRobot()
        self.loadPersistentSettings()
        self.installEventFilter(self)
        self.setRunnumber()

        #A collection of timers used through the program
        self.updateTimer = QTimer(self) #This one updates GUI elements at a slow rate 
        self.updateTimer.timeout.connect(self.updateValues)
        self.updateTimer.start(100)
        
        self.updateTimerPositions = QTimer(self) #Fast update of GUI element showing motors positions 
        self.updateTimerPositions.timeout.connect(self.updateValuesPosition)
        self.updateTimerPositions.start(50)
        
        #self.updateTimerFlux = QTimer(self)  
        #self.updateTimerFlux.timeout.connect(self.updateFlux)
        
        self.updateTimerManualMountPosition = QTimer(self)
        self.updateTimerManualMountPosition.timeout.connect(self.checkManualMountStatus)
        
        self.updateTimerWaitForInterlockBreak = QTimer(self)
        self.updateTimerWaitForInterlockBreak.timeout.connect(self.waitForInterlockToBreak)

        self.updateTimerWaitForInterlockSet = QTimer(self)
        self.updateTimerWaitForInterlockSet.timeout.connect(self.waitForInterlockToSet)

        self.updateTimerDataCollectionProgress = QTimer(self)
        self.updateTimerDataCollectionProgress.timeout.connect(self.dataCollectionProgressUpdate)

        self.updateTimerOnaxisImages = QTimer(self)
        self.updateTimerOnaxisImages.timeout.connect(self.saveCurrentImage)
        
        self.ui.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.graphicsView.setDragMode(QtGui.QGraphicsView.NoDrag)
        self.ui.graphicsView.ensureVisible(0,0,self.ui.graphicsView.size().width(),self.ui.graphicsView.size().height(),0,0)
        
        self.setIncrementInterval("1 " + chr(181) + "m")
        self.setAnnealInterval("0.5 s")
        self.collectionParametersSet = False
        self.settingExposureParameters = False
        self.settingPilatusThreshold = False
        self.movingCollimatorIn = False
        self.movingShieldDown = False
        self.dataCollectionExposureParametersSet = False
        self.goniometerThreadInStartPosition = False
        self.movingGoniometerToStartPosition = False
        
        parent.showMessage("\n\n   Finished")
        parent.finish(self)
        
        self.rectDims = [50,50,200,200] #x,y, \ width,height

        self.rectCoordsUnrotated = [0,0,0,0,0,0,0,0]
        self.rectCoordsUnrotated[0] = self.rectDims[0]                 
        self.rectCoordsUnrotated[1] = self.rectDims[1]
        
        self.rectCoordsUnrotated[2] = self.rectDims[0]
        self.rectCoordsUnrotated[3] = self.rectDims[3]+self.rectDims[0]
        
        self.rectCoordsUnrotated[4] = self.rectDims[0]+self.rectDims[2]
        self.rectCoordsUnrotated[5] = self.rectDims[1]+self.rectDims[3]
        
        self.rectCoordsUnrotated[6] = self.rectDims[0]+self.rectDims[2]
        self.rectCoordsUnrotated[7] = self.rectDims[1]
        self.scanAreaPolygon = QtGui.QPolygon(4)
        self.scanAreaPolygon.setPoint(0, self.rectCoordsUnrotated[0],self.rectCoordsUnrotated[1])
        self.scanAreaPolygon.setPoint(1, self.rectCoordsUnrotated[2],self.rectCoordsUnrotated[3])
        self.scanAreaPolygon.setPoint(2, self.rectCoordsUnrotated[4],self.rectCoordsUnrotated[5])
        self.scanAreaPolygon.setPoint(3, self.rectCoordsUnrotated[6],self.rectCoordsUnrotated[7])
        
        rx = QtCore.QRegExp()
        rx.setPattern("[aA-zZ0-9][a-zA-Z0-9_,/]+")
        validator1 = QtGui.QRegExpValidator(rx, self.ui.lineEditImagePrefix)
        self.ui.lineEditImagePrefix.setValidator(validator1)

        rx = QtCore.QRegExp()
        rx.setPattern("[0-9]*[\.]*[0-9]*°")
        validator2 = QtGui.QRegExpValidator(rx, self.ui.comboBoxAngleIncrement)
        validator2.fixup = lambda input: input.rstrip('°') + '°'

        rx = QtCore.QRegExp()
        rx.setPattern("[0-9]*[\.]*[0-9]* µm")
        validator3 = QtGui.QRegExpValidator(rx, self.ui.comboBoxStepSize)
        validator3.fixup = lambda input: input.rstrip(' µm') + ' µm'
        self.ui.comboBoxStepSize.setValidator(validator3)

        #hide the break interlock button for remote users
        if self.remote:
            self.ui.pushButtonManualMountPositionBreakInterlock.hide()

        #hide expert tabs
        for tab in [self.ui.pageCenterOfRotation, self.ui.pageBeamAlignment, self.ui.pageAlignBeamShapers]:
            tab.hide()
            i = self.ui.toolBoxAlignment.indexOf(tab)
            self.ui.toolBoxAlignment.removeItem(i)
        self.ui.groupBoxScreen.hide()

        # temporarly remove Helical scan tab, until it really works
        self.ui.pageHelicalScan.hide()
        i = self.ui.toolBoxCollection.indexOf(self.ui.pageHelicalScan)
        self.ui.toolBoxCollection.removeItem(i)

        # temporarly remove grid scan tab, until it really works
        #self.ui.pageISMO.hide()
        #i = self.ui.toolBoxCollection.indexOf(self.ui.pageISMO)
        #self.ui.toolBoxCollection.removeItem(i)

        # hide the recalibrate button again for it's of uncertain use and breaking the layout
        self.ui.pushButtonRecalibrateGonio.hide()

        #PP
        # We have sometimes problem, that the state of motors is identified as "Not moving", however
        # it is just state of change of direction of motion During grid Scan, where the velocity must be at some point 0.
        # In this point, the updateValues function code for update of RasterPosition takes w_values, which 
        # times to times get already next value to move, instead of some value ov motionless state!
        
        # to prevent it, we use the self.sampleIsNotMovingCount counter and we consider 
        # the state as not moving, if counter reached some value (e.g. 5):        
        self.sampleIsNotMovingCount = 0
        # NOTE: IT IS MUCH BETTER TO MAKE STUFF RELATED TO IsNotMoving, IS ACORDING EVENT IS GENERATED
         

    #------- Start of general GUI behavior functions ---------#
    def closeEvent(self,event): # It is a kind of Destructor of the StartQT4 object instead of __del__
        self.exitapp()


    def exitapp(self):
        print("Exiting..")
        self.setBacklight(0)
        self.setIllumination(0)
        os.umask(self.old_umask)
        #time.sleep(1)
        self.savePersistentSettings()
        if self.connected:
            if self.sxMode:
                self.goniometerThread.deactivateSerialCrystallographyMode()
            self.goniometerThread.stop()

        QtGui.qApp.quit()
        sys.exit()
        

    def tabChanged(self,index):
        self.ui.pushButtonGridScanMode.setHidden(True)
        self.item.setEnabled(True) #mousePressEvent = self.moveToBeam # standard move To beam behaviour is switched on        
        if self.raster is not None: 
            self.ui.pushButtonClearGrid_ISMO.setEnabled(True)        
            self.ui.pushButtonClearGrid_Grid.setEnabled(True)        
        try:
            if (list(self.scene.items()).index(self.raster) > 0):
                self.scene.removeItem(self.raster)         
        except:
            pass

        if self.helix != None:        
            self.helix.hide() # default  - hide helix! for proper tab, it will be shown
        
        # default, but for certain tabs will be changed below
        self.ui.pushButtonCenteringNClick.setHidden(False)
        self.ui.pushButtonThreeClickMode.setHidden(False)        
                
        self.method = str(self.ui.toolBoxCollection.itemText(self.ui.toolBoxCollection.currentIndex()))
        if self.method == "Standard collection":
            self.setRunnumber()
        elif self.method == "Screening":
            self.setRunnumber_Screening()
        elif self.method == "Grid fly scan":
            self.setRunnumber_Grid()
            self.ui.pushButtonGridScanMode.setHidden(False)
            self.ui.pushButtonGridScanMode.setChecked(True)
            self.setGridScanMode()
            self.scene.addItem(self.raster)
        elif self.method == "Grid step scan":
            self.setRunnumber_ISMO()        
            self.ui.pushButtonGridScanMode.setHidden(False)            
            self.ui.pushButtonGridScanMode.setChecked(True)
            self.setGridScanMode()            
            self.scene.addItem(self.raster)
        elif self.method == "Helical scan": 
            #self.item.setEnabled(False) #mousePressEvent = None # standard move To beam behaviour is switched off
            if  self.helix == None: # create helix                
                self.helix = Helix(self.ui.graphicsView, self.goniometerThread, self.pixelsPerUm) #                
                self.helix.hide()
                #QObject.connect(self.helix, QtCore.SIGNAL("pointMouseReleaseEvent"), self.movePointToBeam)
            self.helix.setPixelsPerUm(self.pixelsPerUm) # it can be changed being alreadly initialised.
            
            # requests of group leaders: remain in the style of crystal control
            # on Tab change to Helical scan first nothing is to until an user press at least one of "Set" buttons.
            if (self.helix.p1.isSet or self.helix.p2.isSet):
                self.helix.show()
                
                
            # connect pressing buttons directly to methods of helix:
            # The Buttons could be probably included into helix object as Widget.            
            self.ui.setPoint1Button.clicked.connect(lambda: self.setPointForHelix(1))
            self.ui.unSetPoint1Button.clicked.connect(lambda: self.unSetPointForHelix(1))        

            
            self.ui.setPoint2Button.clicked.connect(lambda: self.setPointForHelix(2))        
            self.ui.unSetPoint2Button.clicked.connect(lambda: self.unSetPointForHelix(2))


            
            #self.ui.testButton.clicked.connect(self.test)
            self.ui.testButton.hide() # We will later use this button to test 
            # helical scan data collection using sardana macros 
            
            # ===============================================================================================
        
        
    def test(self):
        print("--- test ---")
        
        
                


    def expertView(self):
        if self.expert == 1:
            self.ui.actionExpert_view.setCheckable(False)
            self.ui.actionExpert_view.setChecked(False)
            for tab in [self.ui.pageCenterOfRotation, self.ui.pageBeamAlignment, self.ui.pageAlignBeamShapers]:
                tab.hide()
                i = self.ui.toolBoxAlignment.indexOf(tab)
                self.ui.toolBoxAlignment.removeItem(i)
            self.ui.groupBoxScreen.hide()
            self.expert = 0
        else:
            feedback = self.password()
            self.pw = hashlib.md5(feedback) 
            if self.pwhash == self.pw.hexdigest():
                self.expert = 1
                self.ui.actionExpert_view.setCheckable(True)
                self.ui.actionExpert_view.setChecked(True)
                for tab in [\
                        [self.ui.pageCenterOfRotation, "Center of rotation"],\
                        [self.ui.pageBeamAlignment, "Beam Alignment"],\
                        [self.ui.pageAlignBeamShapers, "Align beam shaping elements"]]:
                    self.ui.toolBoxAlignment.addItem(tab[0], tab[1])
                    tab[0].show()
                self.ui.groupBoxScreen.show()
                self.writeToLog("Correct password.")
            else:
                self.expert = 0
                self.ui.actionExpert_view.setCheckable(False)
                self.ui.actionExpert_view.setChecked(False)
                for tab in [self.ui.pageCenterOfRotation, self.ui.pageBeamAlignment, self.ui.pageAlignBeamShapers]:
                    tab.hide()
                    i = self.ui.toolBoxAlignment.indexOf(tab)
                    self.ui.toolBoxAlignment.removeItem(i)
                self.ui.groupBoxScreen.hide()
                self.writeToLog("Wrong password.")


    def password(self):
        diag = QtGui.QInputDialog
        s = None
        while s is None:
            s, ok = diag.getText(self, "Enable expert settings", "Password:", QtGui.QLineEdit.Password)
            if ok is False: # user pressed Cancel
                return ""
            if s == '':     # user entered nothing
                s = None
        return s.encode("utf-8")

    def eventFilter(self, obj, event):
        if((event.type() == QEvent.Leave) and (obj == self.scene)):
            self.setCursor(Qt.ArrowCursor)
        
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Return:
                w = self.focusWidget()
                if (self.connected):
                    if (w == self.ui.doubleSpinBoxSetAngle):
                        self.setGoniometerPositionReturnKey(self.ui.doubleSpinBoxSetAngle.value())
                    elif (w == self.ui.doubleSpinBoxFlexureXposition):
                        self.moveFlexureX(self.ui.doubleSpinBoxFlexureXposition.value())
                    elif (w == self.ui.doubleSpinBoxFlexureYposition):
                        self.moveFlexureY(self.ui.doubleSpinBoxFlexureYposition.value())
                    elif (w == self.ui.doubleSpinBoxKohzuGoniometerX):
                        self.setKohzuGoniometerX(self.ui.doubleSpinBoxKohzuGoniometerX.value())
                    elif (w == self.ui.doubleSpinBoxKohzuGoniometerY):
                        self.setKohzuGoniometerY(self.ui.doubleSpinBoxKohzuGoniometerY.value())
                    elif (w == self.ui.doubleSpinBoxKohzuGoniometerZ):
                        self.setKohzuGoniometerZ(self.ui.doubleSpinBoxKohzuGoniometerZ.value())
                    elif (w == self.ui.doubleSpinBoxKohzuMicroscopeY):
                        self.setKohzuMicroscopeY(self.ui.doubleSpinBoxKohzuMicroscopeY.value())
                    elif (w == self.ui.doubleSpinBoxKohzuMicroscopeZ):
                        self.setKohzuMicroscopeZ(self.ui.doubleSpinBoxKohzuMicroscopeZ.value())
                    elif (w == self.ui.spinBoxCameraExposureTime):
                        self.setCameraExpTime(self.ui.spinBoxCameraExposureTime.value())
                    elif (w == self.ui.spinBoxCameraGain):
                        self.setCameraGain(self.ui.spinBoxCameraGain.value())
                    elif (w == self.ui.lineEditImagePrefix):
                        self.setRunnumber()
                    elif (w == self.ui.doubleSpinBoxDetectorDistance):
                        self.setDetectorDistance(self.ui.doubleSpinBoxDetectorDistance.value())
                    elif (w == self.ui.doubleSpinBoxResLimit):
                        self.setResolutionLimit(self.ui.doubleSpinBoxResLimit.value())
                    elif (w == self.ui.doubleSpinBoxDesiredTransmission):
                        self.selectTransmission(self.ui.doubleSpinBoxDesiredTransmission.value())
                    elif (w == self.ui.doubleSpinBoxPinholePositionY):
                        self.setPinholePositionY()
                    elif (w == self.ui.doubleSpinBoxPinholePositionZ):
                        self.setPinholePositionZ()
                    elif (w == self.ui.doubleSpinBoxCollimatorPositionY):
                        self.setCollimatorPositionY()
                    elif (w == self.ui.doubleSpinBoxCollimatorPositionZ):
                        self.setCollimatorPositionZ()
        return QtGui.QMainWindow.eventFilter(self, obj, event)     

        
    def setMoveToBeam(self):                
        if (self.ui.pushButtonCenteringNClick.isChecked()):
            self.ui.pushButtonThreeClickMode.setChecked(False)        
            self.ui.pushButtonGridScanMode.setChecked(False)        
            self.item.mousePressEvent = self.moveToBeam
            
            #self.raster.mousePressEvent = self.moveToBeam # use other function of item instead of original raster function
            #self.raster.setEnabled(False) # does not work, because EventFilter works:
            self.raster.rasterEventFilter.remove()
        

    def setThreeClickMode(self):
        
        if (self.ui.pushButtonThreeClickMode.isChecked()):
            self.ui.pushButtonCenteringNClick.setChecked(False)        
            self.ui.pushButtonGridScanMode.setChecked(False)
            self.scene.setFocusItem(self.item)
            self.item.mousePressEvent = self.moveToBeam
            self.raster.rasterEventFilter.remove()        
        

    def setGridScanMode(self):
        time.sleep(0.1)
        if (self.ui.pushButtonGridScanMode.isChecked()):
            self.ui.pushButtonCenteringNClick.setChecked(False)        
            self.ui.pushButtonThreeClickMode.setChecked(False)            
            self.raster.rasterEventFilter.remove()
            self.raster.rasterEventFilter.install(self.scene)  
            self.setGridStepsizeX(self.ui.doubleSpinBoxStepsizeX_ISMO.value())
            self.setGridStepsizeY(self.ui.doubleSpinBoxStepsizeY_ISMO.value())
            self.setRasterBeamSize()
            self.raster.raster.setConversion(self.pixelsPerUm)
            self.raster.raster.setOffset(0,0)
            self.raster.updateRaster()
            self.ui.graphicsView.update()
            

    def setRasterBeamSize(self):    
        self.raster.raster.setBeamsize(self.beamWidth, self.beamHeight)
        self.raster.updateRaster()


    #------- Start of Config and Tango functions ---------#

    def saveBeamPosition(self):
        config = configparser.ConfigParser(dict_type=OrderedDict)
        config.read(self.settingsFile)
        config.set("Beam","beamPositionX",self.ui.doubleSpinBoxBeamPositionHorizontal.value())
        config.set("Beam","beamPositionY",self.ui.doubleSpinBoxBeamPositionVertical.value())
        config.set("Beam","beamWidth",self.beamWidth)
        config.set("Beam","beamHeight",self.beamHeight)
        with open(self.settingsFile, 'w') as configfile:
            config.write(configfile)
        self.writeToLog("Saved current beam position")

    def save_pinholes(self):
        config = configparser.ConfigParser(dict_type=OrderedDict)
        config.read(self.configFile)
        self.pinholePositionsY[self.currentPinhole] = self.piezoThread.currPinholeY
        self.pinholePositionsZ[self.currentPinhole] = self.piezoThread.currPinholeZ
        self.pinholes = numpy.column_stack((self.pinholePositionsY,self.pinholePositionsZ,self.pinholeList))
        self.piezoThread.pinholePositions = self.pinholes
        pinholeyposlist = ','.join(str(int(round(x,0))) for x in self.pinholePositionsY)
        pinholezposlist = ','.join(str(int(round(x,0))) for x in self.pinholePositionsZ)
        config.set("Pinholes","pinholeyposlist",pinholeyposlist)
        config.set("Pinholes","pinholezposlist",pinholezposlist)
        with open(self.configFile, 'w') as configfile:
            config.write(configfile)
        self.writeToLog("Saved pinhole settings")
        print("Saved pinhole settings to file")
        
    def save_collimator(self):
        config = configparser.ConfigParser(dict_type=OrderedDict)
        config.read(self.configFile)
        posy = int(self.piezoThread.currCollimatorY)
        posz = int(self.piezoThread.currCollimatorZ)
        self.piezoThread.collimatorInPositionY = posy
        self.piezoThread.collimatorInPositionZ = posz
        config.set("Collimator","collimatorinpositiony", str(posy))
        config.set("Collimator","collimatorinpositionZ", str(posz))
        with open(self.configFile, 'w') as configfile:
            config.write(configfile)
        self.writeToLog("Saved collimator settings")
        print("Saved collimator settings to file")

    def addPersistentSetting(self, name, group, type, getter, setter):
        if not group in self.persistentSettings:
            self.persistentSettings[group] = {}
        self.persistentSettings[group][name] = [type, getter, setter]

    def savePersistentSettings(self):
        self.writeToLog("Trying to open settings file")
        try:
            config = open(self.settingsFile, 'w')
        except:
            self.writeToLog("saving settings failed")
            return
        for group in sorted(list(self.persistentSettings.keys()), key=str.lower):
            config.write("["+str(group)+"]\n")
            for name in sorted(list(self.persistentSettings[group].keys()), key=str.lower):
                try:
                    config.write(str(name)+" = "+str(eval(self.persistentSettings[group][name][1]+"()"))+"\n")
                except:
                    self.writeToLog("failed to save setting "+str(group)+":"+str(name))
                    print("failed to save setting "+str(group)+":"+str(name), sys.exc_info())
            config.write("\n")
        config.close()
        self.writeToLog("settings saved")

    def loadPersistentSettings(self):
        if os.path.isfile(self.settingsFile):
            self.writeToLog("Trying to open settings file")
            config = configparser.ConfigParser()
            config.read(self.settingsFile)
            for group in sorted(list(self.persistentSettings.keys()), key=str.lower):
                if not config.has_section(group):
                    self.writeToLog("section not in settings file: "+str(group))
                    continue
                for name, value in config.items(group):
                    try:
                        if self.persistentSettings[group][name][0] == "bool":
                            v = value in ["True", "true", 1]
                            eval(self.persistentSettings[group][name][2])(v)
                        elif self.persistentSettings[group][name][0] == "int":
                            eval(self.persistentSettings[group][name][2])(int(value))
                        elif self.persistentSettings[group][name][0] == "float":
                            eval(self.persistentSettings[group][name][2])(float(value))
                        else:
                            eval(self.persistentSettings[group][name][2])(str(value))
                    except:
                        self.writeToLog("failed to load setting "+str(group)+":"+str(name))
            self.writeToLog("settings loaded")

    def loadConfig(self):
        self.writeToLog("Trying to open config file")
        if os.path.isfile(self.configFile):
            self.writeToLog("Loading config")
            config = configparser.ConfigParser(dict_type=OrderedDict)
            config.read(self.configFile)
            self.tangohost = config.get('Crystallography', 'tangohost')
            self.tangoport = config.get('Crystallography', 'tangoport')
            self.monoServer = config.get('Crystallography', 'monochromator')
            self.shutterServer = config.get('Crystallography', 'shutterserver')
            self.shutterstatusServer = config.get('Crystallography', 'shutterstatus')
            self.goniometerThreadserver = config.get('Crystallography', 'goniometerserver')
            self.flexureXserver = config.get('Crystallography', 'flexureXserver')
            self.flexureYserver = config.get('Crystallography', 'flexureYserver')
            self.kohzuGoniometerXserver = config.get('Crystallography', 'kohzuGoniometerXserver')
            self.kohzuGoniometerYserver = config.get('Crystallography', 'kohzuGoniometerYserver')
            self.kohzuGoniometerZserver = config.get('Crystallography', 'kohzuGoniometerZserver')
            self.kohzuMicroscopeYserver = config.get('Crystallography', 'kohzuMicroscopeYserver')
            self.kohzuMicroscopeZserver = config.get('Crystallography', 'kohzuMicroscopeZserver')
            self.detectortowerServer = config.get('Crystallography', 'detectorTowerServer')
            self.eigerThreadServer = config.get('Crystallography', 'eigerserver')
            self.eigerThreadFilewriter = config.get('Crystallography', 'eigerfilewriter')
            self.eigerThreadMonitor = config.get('Crystallography', 'eigermonitor')
            self.robotserver = config.get('Crystallography', 'robotserver')
            self.cryoserver = config.get('Crystallography', 'cryoserver')
            self.cryoshutter = config.get('Crystallography', 'cryoshutter')
            self.cryoretractorPort = config.get('Crystallography', 'cryoretractor')
            self.illuminationServer = config.get('Crystallography', 'illuminationserver')
            self.backlightport = config.get('Crystallography', 'backlightonoffport')
            self.inlineIlluminationServer = config.get('Crystallography', 'inlineIlluminationServer')
            self.inlineIrisServer = config.get('Crystallography', 'inlineIrisServer')
            self.inlineSpotServer = config.get('Crystallography', 'inlineSpotServer')
            self.contrastscreeninoutport = config.get('Crystallography', 'contrastscreeninoutport')
            self.detectorManualMountPosition = float(config.get('Crystallography', 'manualmountposition'))
            self.sampleoutDistanceWhenBeamcheck = float(config.get('Crystallography', 'sampleoutdistancewhenbeamcheck'))
            self.filterserver = config.get('Crystallography', 'filterserver')
            self.energyserver = config.get('Crystallography', 'energyserver')
            
            self.bs0statusserver = config.get('Crystallography', 'bs0status')
            self.bs1statusserver = config.get('Crystallography', 'bs1status')
            self.petraservers = [self.bs0statusserver, self.bs1statusserver, self.shutterstatusServer, self.filterserver]
            
            #self.contrastscreenyserver = config.get('Crystallography', 'contrastscreenyserver')
            #self.contrastscreenzserver = config.get('Crystallography', 'contrastscreenzserver')
	    
            self.defaultGoniospeed = float(config.get('Crystallography', 'goniospeed'))
            self.serverList = [self.goniometerThreadserver, self.flexureXserver, self.flexureYserver,
                               self.kohzuGoniometerXserver, self.kohzuGoniometerYserver, self.kohzuGoniometerZserver,
                               self.kohzuMicroscopeYserver,self.kohzuMicroscopeZserver, self.shutterServer, \
                               self.contrastscreeninoutport, self.shutterstatusServer]

            beamstopPiezoXserver = config.get('Crystallography', 'beamstopXserver')
            beamstopPiezoYserver = config.get('Crystallography', 'beamstopYserver')
            beamstopPiezoZserver = config.get('Crystallography', 'beamstopZserver')
            pinholePiezoYserver = config.get('Crystallography', 'pinholeYserver')
            pinholePiezoZserver = config.get('Crystallography', 'pinholeZserver')
            screenPiezoXserver = config.get('Crystallography', 'screenXserver')
            screenPiezoZserver = config.get('Crystallography', 'screenZserver')
            collimatorPiezoYserver = config.get('Crystallography', 'collimatorYserver')
            collimatorPiezoZserver = config.get('Crystallography', 'collimatorZserver')
            
            self.startInSX = bool(int(config.get('Crystallography', 'startinserialcrystallographymode')))
            
            self.piezoServerList = [beamstopPiezoYserver, beamstopPiezoZserver, 
                                    pinholePiezoYserver, pinholePiezoZserver,
                                    screenPiezoXserver, screenPiezoZserver,
                                    collimatorPiezoYserver,collimatorPiezoZserver,
                                    beamstopPiezoXserver]
            self.NominalGoniometerXposition = float(config.get('KohzuPositions', 'NominalGoniometerX'))
            self.NominalGoniometerYposition = float(config.get('KohzuPositions', 'NominalGoniometerY'))
            self.NominalGoniometerZposition = float(config.get('KohzuPositions', 'NominalGoniometerZ'))
            self.NominalMicroscopeYposition = float(config.get('KohzuPositions', 'NominalMicroscopeY'))
            self.NominalMicroscopeZposition = float(config.get('KohzuPositions', 'NominalMicroscopeZ'))
            self.SerialCrystYAGinGoniometerZposition = float(config.get('KohzuPositions', 'SerialCrystYAGinGoniometerZ'))

            self.pinholeZminimumHeight = float(config.get('Pinholes', 'PinholeZminimumHeight'))
            pinholeList = config.get('Pinholes', 'pinholeSizeList')
            pinholePositionsY = config.get('Pinholes', 'pinholeYposList')
            pinholePositionsZ = config.get('Pinholes', 'pinholeZposList')
            self.pinholeList = pinholeList.split(",")
            self.pinholePositionsY = pinholePositionsY.split(",")
            self.pinholePositionsZ = pinholePositionsZ.split(",")
            for pos in range(len(self.pinholeList)):
                self.pinholeList[pos] = float(self.pinholeList[pos])
            for pos in range(len(self.pinholePositionsY)):
                self.pinholePositionsY[pos] = float(self.pinholePositionsY[pos])
            for pos in range(len(self.pinholePositionsZ)):
                self.pinholePositionsZ[pos] = float(self.pinholePositionsZ[pos])
            self.pinholes = numpy.column_stack((self.pinholePositionsY,self.pinholePositionsZ,self.pinholeList))

            pinholeList = []
            for pinhole in self.pinholeList:
                pinholeList.append(str(pinhole) + " " + chr(956) + "m")
            pinholeList[0] = "None"
            comboBoxList = [ \
                self.ui.comboBoxPinhole, \
            ]
            for comboBox in comboBoxList:
                comboBox.addItems(pinholeList)
                QtCore.QObject.connect(comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.selectPinhole)

            yagInPositionX = float(config.get('Screen', 'yagInPositionX'))
            yagInPositionZ = float(config.get('Screen', 'yagInPositionZ'))
            diodeInPositionX = float(config.get('Screen', 'diodeInPositionX'))
            diodeInPositionZ = float(config.get('Screen', 'diodeInPositionZ'))
            screenOutPositionX = float(config.get('Screen', 'screenOutPositionX'))
            screenOutPositionZ = float(config.get('Screen', 'screenOutPositionZ'))
            
            collimatorInPositionY = float(config.get('Collimator', 'collimatorInPositionY'))
            collimatorInPositionZ = float(config.get('Collimator', 'collimatorInPositionZ'))
            collimatorOutPositionY = float(config.get('Collimator', 'collimatorOutPositionY'))
            collimatorOutPositionZ = float(config.get('Collimator', 'collimatorOutPositionZ'))
            
            beamstopmanualmountposition = float(config.get('Beamstop', 'beamstopmanualmountposition'))
            beamstopinposition = float(config.get('Beamstop', 'beamstopinposition'))

            self.piezoPositions = [yagInPositionX,yagInPositionZ,\
                                    diodeInPositionX,diodeInPositionZ,\
                                    screenOutPositionX,screenOutPositionZ,\
                                    collimatorInPositionY,collimatorInPositionZ, \
                                    collimatorOutPositionY,collimatorOutPositionZ , \
                                    beamstopmanualmountposition, beamstopinposition,\
                                  ]
            
            beamstopYposition = float(config.get('Beamstop', 'PositionY'))
            beamstopZposition = float(config.get('Beamstop', 'PositionZ'))
            self.beamstopPosition =  [beamstopYposition,beamstopZposition]
            self.beamPositionX = float(config.get('Beam', 'beamPositionX'))
            self.beamPositionY = float(config.get('Beam', 'beamPositionY'))
            self.beamOriginX = float(config.get('Beam', 'originX'))
            self.beamOriginY = float(config.get('Beam', 'originY'))
            self.directBeamTransmission = float(config.get('Beam', 'directbeamtransmission'))  
            
            #self.beamWidth = float(config.get('Beam', 'beamWidth'))
            #self.beamHeight = float(config.get('Beam', 'beamHeight'))
            self.cameras = []
            host = str(config.get('Camera', 'host')).split(',')
            port = str(config.get('Camera', 'port')).split(',')
            offsetx = str(config.get('Camera', 'offsetx')).split(',')
            offsety = str(config.get('Camera', 'offsety')).split(',')
            flipx = str(config.get('Camera', 'flipx')).split(',')
            flipy = str(config.get('Camera', 'flipy')).split(',')
            pixelsperum = str(config.get('Camera', 'pixelsperum')).split(',')
            for i in range(len(host)):
                self.cameras.append({\
                    "host": host[i].strip(), \
                    "port": port[i].strip(), \
                    "offsetX": int(offsetx[i]), \
                    "offsetY": int(offsety[i]), \
                    "flipX": int(flipx[i]), \
                    "flipY": int(flipy[i]), \
                    "pixelsperum": float(pixelsperum[i]), \
                })
            try:
                self.centringClickImagePath = config.get("Camera", "pathTrainingData")
            except:
                self.centringClickImagePath = None

            self.amarcord = {
                "enabled": False,
                "connection_timeout": 30,
                "raise_on_warnings": True,
                "auth_plugin": "mysql_native_password",
            }
            if config.has_section("Amarcord"):
                self.amarcord["enabled"] = config.getboolean("Amarcord", "enabled")
                self.amarcord["host"] = config.get("Amarcord", "host")
                self.amarcord["database"] = config.get("Amarcord", "database")
                self.amarcord["user"] = config.get("Amarcord", "user")
                self.amarcord["password"] = config.get("Amarcord", "password")
                try:
                    global connector
                    from mysql import connector
                except:
                    print("importing mysql failed")
                    self.amarcord["enabled"] = False

            self.devPathADC = config.get('Photonmeter', 'devPathADC')
            self.devPathVFC = config.get('Photonmeter', 'devPathVFC')
            self.devPathTimer = config.get('Photonmeter', 'devPathTimer')
            self.devPathMono = config.get('Photonmeter', 'devPathMono')
            self.mod = config.getint('Photonmeter', 'mod')
            self.diodeThickness = float(config.get('Photonmeter', 'thickness'))
            self.diodeSampletime = float(config.get('Photonmeter', 'sampletime'))
            self.diodeAmpGain = float(config.get('Photonmeter', 'amplifiergain'))

            self.corrK = float(config.get('DetectorTower', 'linearizationK'))
            self.corrM = float(config.get('DetectorTower', 'linearizationM'))
            
            self.fluorescenceTool = config.get('Fluorescence', 'file')

            self.commissioning = config.getboolean('Beamtime', 'Commissioning')
            self.fallback = config.getboolean('Beamtime', 'Fallback')
            if self.fallback:
                self.path.set_mode(self.path.MODE_FALLBACK)
            elif self.commissioning:
                self.path.set_mode(self.path.MODE_COMMISSIONING)
            else:
                self.path.set_mode(self.path.MODE_BEAMTIME)

            self.simulation = dict()
            self.simulation['petra'] = bool(int(config.get('Simulation', 'petra')))
            self.simulation['monochromator'] = bool(int(config.get('Simulation', 'monochromator')))
            self.simulation['illumination'] = bool(int(config.get('Simulation', 'illumination')))
            self.simulation['goniometer'] = bool(int(config.get('Simulation', 'goniometer')))
            self.simulation['eiger'] = bool(int(config.get('Simulation', 'eiger')))
            self.simulation['robot'] = bool(int(config.get('Simulation', 'robot')))
            self.simulation['piezomotors'] = bool(int(config.get('Simulation', 'piezomotors')))
            self.simulation['detectortower'] = bool(int(config.get('Simulation', 'detectorTower')))
            self.simulation['flux'] = bool(int(config.get('Simulation', 'flux')))
            self.simulation['energy'] = bool(int(config.get('Simulation', 'energy')))
            self.simulation['cryo'] = bool(int(config.get('Simulation', 'cryo')))
            self.simulation['camera'] = bool(int(config.get('Simulation', 'camera')))
            
            self.settingsLoaded = 1
            self.writeToLog("Config loaded")
            self.connectTangoHost()
        else:
            self.writeToLog("Error: config file (config.ini) not found")
            self.settingsLoaded = 0


    def connectTangoHost(self):
        if (self.connected == 0):

            self.writeToLog("Connecting to tango device servers")
            os.putenv("TANGO_HOST", self.tangohost + ':' + self.tangoport)
            
            if(self.simulation['monochromator']):            
                self.proxyMonochromator = SimulationDevice()
            else:
                self.proxyMonochromator = DeviceProxy(self.monoServer)    
            
            if(self.simulation['illumination']):
                self.proxyIllumination = SimulationDevice()
                self.backlight = SimulationDevice()
                self.proxyInlineIllumination = SimulationDevice()
                self.proxyInlineSpot = SimulationDevice()
                self.proxyInlineIris = SimulationDevice()
            else:
                self.proxyIllumination = DeviceProxy(self.illuminationServer)
                self.backlight = DeviceProxy(self.backlightport)
                self.proxyInlineIllumination = DeviceProxy(self.inlineIlluminationServer)
                self.proxyInlineSpot = DeviceProxy(self.inlineSpotServer)
                self.proxyInlineIris = DeviceProxy(self.inlineIrisServer)
            self.writeToLog("Connecting to goniometer")
            self.goniometerThread = GoniometerThread(self.serverList, simulation = self.simulation['goniometer'])
            self.goniometerThread.start(QThread.HighPriority)
            
            if(self.goniometerThread.alive == False):
                self.writeToLog("Goniometer server not running")
            self.connect(self.goniometerThread,SIGNAL("errorSignal(PyQt_PyObject)"),self.threadErrorHandler)
            self.connect(self.goniometerThread,SIGNAL("logSignal(PyQt_PyObject)"),self.writeToLog)
            
            if not self.simulation['robot']:
                self.writeToLog("Connecting to robotserver")
                self.robot = RobotThread(self.robotserver, self)
                self.robot.start()
                if(self.robot.alive == False):
                    self.writeToLog("Robot server not running")
            
            self.writeToLog("Connecting to cryoserver")
            self.cryoThread = CryoThread([self.cryoserver, self.cryoshutter, self.cryoretractorPort], simulation = self.simulation['cryo'])
            self.cryoThread.start()
            if(self.cryoThread.alive == False):
                self.writeToLog("Cryo server not running")
                
            self.writeToLog("Connecting to eiger")
            self.eigerThread = EigerThread([
                self.eigerThreadServer, self.eigerThreadFilewriter, self.eigerThreadMonitor], 
                simulation = self.simulation['eiger'])
            self.eigerThread.start()
            if(self.eigerThread.alive == False):
                self.writeToLog("Eiger server not running")
            self.connect(self.eigerThread,SIGNAL("errorSignal(PyQt_PyObject)"),self.threadErrorHandler)
            self.connect(self.eigerThread,SIGNAL("logSignal(PyQt_PyObject)"),self.writeToLog)
            self.liveView = LiveView(filetype=LiveView.FILETYPE_HDF5, interval=2.0, parent=self)
            
            self.writeToLog("Connecting to piezo motors")
            self.piezoThread = PiezoThread(self.piezoServerList,self.pinholes,self.beamstopPosition,self.piezoPositions,self.pinholeZminimumHeight,self.simulation['piezomotors'])
            self.piezoThread.start()
            if(self.piezoThread.alive == False):
                self.writeToLog("Piezo server not running")
            self.connect(self.piezoThread,SIGNAL("errorSignal(PyQt_PyObject)"),self.threadErrorHandler)
            self.connect(self.piezoThread,SIGNAL("logSignal(PyQt_PyObject)"),self.writeToLog)
            
            self.writeToLog("Connecting to PETRA status")
            self.petraThread = PetraThread(self.petraservers,self.directBeamTransmission,simulation = self.simulation['petra'])
            self.petraThread.start(QThread.LowPriority)
            self.connect(self.petraThread,SIGNAL("errorSignal(PyQt_PyObject)"),self.threadErrorHandler)
            self.connect(self.petraThread,SIGNAL("logSignal(PyQt_PyObject)"),self.writeToLog)
                
            self.writeToLog("Connecting to detector tower")
            self.detectorTowerThread = DetectorTower(self.detectortowerServer,self.detectorManualMountPosition, self.corrK, self.corrM, simulation = self.simulation['detectortower'])
            self.detectorTowerThread.start(QThread.LowPriority)
            self.connect(self.detectorTowerThread,SIGNAL("errorSignal(PyQt_PyObject)"),self.threadErrorHandler)
            self.connect(self.detectorTowerThread,SIGNAL("logSignal(PyQt_PyObject)"),self.writeToLog)

            self.photonmeter = photonThread(self.devPathADC, self.devPathVFC, self.devPathTimer, self.devPathMono, self.diodeSampletime, 10, self.diodeAmpGain, self.diodeThickness, 320, self.mod, self.simulation['flux'])
            self.photonmeter.start(QThread.LowPriority)
            
            self.energyThread = EnergyThread(self.energyserver,self.simulation['energy'])
            self.energyThread.start()
            QtCore.QObject.connect(self.ui.doubleSpinBoxDesiredEnergy, QtCore.SIGNAL("valueChanged(double)"), self.energyThread.setEnergy)

            self.ui.horizontalSliderFocus.setMinimum(int(self.piezoThread.screenXMin))
            self.ui.horizontalSliderFocus.setMaximum(int(self.piezoThread.screenXMax))
            self.ui.horizontalSliderFocus.setValue(int(self.piezoThread.currScreenX))
            
            self.detectorTowerThread.shieldUp()
            self.connected = 1

            self.ui.doubleSpinBoxKohzuGoniometerX.setValue(self.goniometerThread.currentPositionKohzuGoniometerX)
            self.ui.doubleSpinBoxKohzuGoniometerY.setValue(self.goniometerThread.currentPositionKohzuGoniometerY)
            self.ui.doubleSpinBoxKohzuGoniometerZ.setValue(self.goniometerThread.currentPositionKohzuGoniometerZ)
            self.ui.doubleSpinBoxKohzuMicroscopeY.setValue(self.goniometerThread.currentPositionKohzuMicroscopeY)
            self.ui.doubleSpinBoxKohzuMicroscopeZ.setValue(self.goniometerThread.currentPositionKohzuMicroscopeZ)
            
            self.ui.doubleSpinBoxDetectorDistance.setValue(self.detectorTowerThread.currentPositionDetectorTowerServer)
            self.detectorDistance = self.ui.doubleSpinBoxDetectorDistance.value()
            energy = self.petraThread.currentMonoEnergy/1000.
            wavelength = 12.3984/(energy) #in Angstrom
            self.resLimit = wavelength/(2.*math.sin(0.5*math.atan((311./2.)/self.detectorDistance)))
            self.ui.doubleSpinBoxResLimit.setValue(self.resLimit)
            
            if not self.detectorTowerThread.lubricationOK:
                QtGui.QMessageBox.warning(self,"Warning","The detector tower reports that the lubrication isn't working properly.\nPlease inform beamline personnel ASAP since this\ncan destroy the detector tower!","&Ok")
            self.setIllumination(0)

            self.ui.comboBoxFilterSelection.addItems(self.petraThread.filterThicknessList)
            self.ui.doubleSpinBoxDesiredTransmission.setValue(self.petraThread.getDesiredFilterTransmission())
            QObject.connect(self.ui.comboBoxFilterSelection,QtCore.SIGNAL("currentIndexChanged(int)"), self.selectFilters)

            self.currentPinhole = 0
            if self.piezoThread.currentPinholePosition >= 0:
                self.selectPinhole(self.piezoThread.currentPinholePosition)
                self.currentPinhole = self.piezoThread.currentPinholePosition
            self.currentFocus = self.energyThread.beamSize
            for key, item in self.energyThread.beamSizeNames.items():
                self.ui.comboBoxFocus.insertItem(int(key)+1, item)
            QObject.connect(self.ui.comboBoxFocus, QtCore.SIGNAL("currentIndexChanged(int)"), self.selectFocus)
            self.selectFocus(self.currentFocus+1, True)
            self.ui.doubleSpinBoxDesiredEnergy.blockSignals(True)
            self.ui.doubleSpinBoxDesiredEnergy.setValue(self.petraThread.currentMonoEnergy)
            self.ui.doubleSpinBoxDesiredEnergy.blockSignals(False)

            self.ui.doubleSpinBoxPinholePositionY.setMinimum(self.piezoThread.pinholeYMin)
            self.ui.doubleSpinBoxPinholePositionY.setMaximum(self.piezoThread.pinholeYMax)
            self.ui.doubleSpinBoxPinholePositionZ.setMinimum(self.piezoThread.pinholeZMin)
            self.ui.doubleSpinBoxPinholePositionZ.setMaximum(self.piezoThread.pinholeZMax)
            
            self.ui.doubleSpinBoxDetectorDistance.setMinimum(self.detectorTowerThread.minPositionDetectorTowerServer)
            self.ui.doubleSpinBoxDetectorDistance.setMaximum(self.detectorTowerThread.maxPositionDetectorTowerServer)

            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed,self.defaultGoniospeed))
            self.lastPositionKohzuGoniometerY = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Position").w_value
            self.lastPositionKohzuGoniometerZ = self.goniometerThread.proxyKohzuGoniometerZ.read_attribute("Position").w_value
            self.lastPositionFlexureX = self.goniometerThread.proxyFlexureX.read_attribute("Position").w_value
            self.lastPositionFlexureY = self.goniometerThread.proxyFlexureY.read_attribute("Position").w_value
        else: 
            self.writeToLog("Error: already connected.")
            
    def startFluorescenceTool(self):
        try:
            msg = self.fluorescenceTool + " " + \
                self.path.get_path("/beamline/beamtime/raw/user/sample/xrf_number/sample_xrf_number.txt")
            subprocess.Popen(msg, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #os.system("python " + self.fluorescenceTool)
        except:
            self.writeToLog("Failed to start fluorescence tool.")
            return
        self.writeToLog("Fluorescence tool started.")

    #------- Start of GUI update functions ---------#
    
    def updateValuesPosition(self):
        if self.connected:
            self.ui.labelStatusCurrentAngle.setText("Angle: %6.2f" % (round(self.goniometerThread.currentAngle,2)+0) + chr(176))
            self.ui.lineEditCurrentAngle.setText("%6.2f" % (round(self.goniometerThread.currentAngle,2)+0) + chr(176))
            self.ui.labelFlexureXposition.setText("%6.1f" % self.goniometerThread.currentPositionFlexureX)
            self.ui.labelFlexureYposition.setText("%6.1f" % self.goniometerThread.currentPositionFlexureY)
            self.ui.labelGoniometerXposition.setText("%6.1f" %self.goniometerThread.currentPositionKohzuGoniometerX)
            self.ui.labelGoniometerYposition.setText("%6.1f" %self.goniometerThread.currentPositionKohzuGoniometerY)
            self.ui.labelGoniometerZposition.setText("%6.1f" %self.goniometerThread.currentPositionKohzuGoniometerZ)
            self.ui.labelMicroscopeYposition.setText("%6.1f" %self.goniometerThread.currentPositionKohzuMicroscopeY) 
            self.ui.labelMicroscopeZposition.setText("%6.1f" %self.goniometerThread.currentPositionKohzuMicroscopeZ)


    def updateValues(self):
        if self.connected:
                
            ############ BEGIN Top status widgets ###############
            
            current = self.petraThread.currPetraCurrent
            self.ui.labelStatusPetraCurrent.setText("Petra current: %4.2f mA" % current)
            if current >40:
                self.ui.labelStatusPetraCurrent.setStyleSheet("background-color: lightgreen")
            else:
                self.ui.labelStatusPetraCurrent.setStyleSheet("background-color: red")
            
            energy = self.petraThread.currentMonoEnergy/1000.
            wavelength = 12.3984/(energy)
            self.ui.labelStatusMonoEnergy.setText("Energy: %6.3f keV\nWavelength: %6.3f " % (energy, wavelength) + chr(197))
            if energy >3 and energy < 30:
                self.ui.labelStatusMonoEnergy.setStyleSheet("background-color: lightgreen")
            else:
                self.ui.labelStatusMonoEnergy.setStyleSheet("background-color: red")
            
            if self.petraThread.stateVacuum == "OFF":
                self.ui.labelStatusVAC.setStyleSheet("background-color: red")
            else:
                self.ui.labelStatusVAC.setStyleSheet("background-color: lightgreen")
            
            if self.petraThread.statusShutterBS0 == 1:
                self.ui.labelStatusBS0.setStyleSheet("background-color: lightgreen")
            elif self.petraThread.statusShutterBS0 == 0:
                self.ui.labelStatusBS0.setStyleSheet("background-color: red")
            elif self.petraThread.statusShutter == "MOVING":
                self.ui.labelStatusBS0.setStyleSheet("background-color: yellow")
            
            if self.petraThread.statusShutterBS1 == 1:
                self.ui.labelStatusBS1.setStyleSheet("background-color: lightgreen")
            elif self.petraThread.statusShutterBS1 == 0:
                self.ui.labelStatusBS1.setStyleSheet("background-color: red")
            elif self.petraThread.statusShutter == "MOVING":
                self.ui.labelStatusBS1.setStyleSheet("background-color: yellow")
                
            if self.goniometerThread.statusFastShutter:
                self.ui.labelStatusFS.setStyleSheet("background-color: lightgreen")
            else:
                self.ui.labelStatusFS.setStyleSheet("background-color: red")

            if self.detectorTowerThread.shieldIsUp:
                self.ui.labelStatusShield.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
                self.ui.labelStatusShield.setText("Detector shield: up")
            else:
                self.ui.labelStatusShield.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
                self.ui.labelStatusShield.setText("Detector shield: down")
            
            if self.goniometerThread.stateGoniometer == "ON":
                self.ui.labelStatusCurrentAngle.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.goniometerThread.stateGoniometer == "MOVING":
                self.ui.labelStatusCurrentAngle.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.goniometerThread.stateGoniometer == "FAULT":
                self.ui.labelStatusCurrentAngle.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
            
            if self.detectorTowerThread.stateDetectorTower == "ON":
                self.ui.labelStatusDetectorDistance.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.detectorTowerThread.stateDetectorTower == "MOVING":
                self.ui.labelStatusDetectorDistance.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.detectorTowerThread.stateDetectorTower == "FAULT":
                self.ui.labelStatusDetectorDistance.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
            self.ui.labelStatusDetectorDistance.setText("Detector distance:\n%6.1f mm" %self.detectorTowerThread.currentPositionDetectorTowerServer)
            
            if self.cryoThread.tangostate == "ON" or self.cryoThread.tangostate == "OFF":
                self.ui.labelStatusCryo.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
            elif self.cryoThread.tangostate == "RUNNING":
                if self.cryoThread.gasTemp > 120.0:
                    self.ui.labelStatusCryo.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
                else:
                    self.ui.labelStatusCryo.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.cryoThread.tangostate == "FAULT":
                self.ui.labelStatusCryo.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
            self.ui.labelStatusCryo.setText("CryoTemp: %4.1f K\n%s" % (self.cryoThread.gasTemp, self.cryoThread.devStatus))

            if self.eigerThread.stateEiger == "ON":
                self.ui.labelStatusPilatus.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.eigerThread.stateEiger == "RUNNING":
                self.ui.labelStatusPilatus.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.eigerThread.stateEiger == "FAULT":
                self.ui.labelStatusPilatus.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
            self.ui.labelStatusPilatus.setText(self.eigerThread.statusEiger)

            ############ END OF Top Status widgets ###############
            
            
            ############ BEGIN Beam settings tab widgets ###############
            
            #---------------------Pinehole expert centering widgets -------------#
            if self.expert:
                if self.piezoThread.statePinhole == "ON":
                    self.ui.labelPinholePositionY.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
                    self.ui.labelPinholePositionZ.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
                    self.ui.pushButtonAutoCenterPinholes.setEnabled(True)
                    self.ui.doubleSpinBoxPinholePositionY.setEnabled(True)
                    self.ui.doubleSpinBoxPinholePositionZ.setEnabled(True)
                else:
                    self.ui.labelPinholePositionY.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
                    self.ui.labelPinholePositionZ.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
                    self.ui.pushButtonAutoCenterPinholes.setEnabled(False)
                    self.ui.doubleSpinBoxPinholePositionY.setEnabled(False)
                    self.ui.doubleSpinBoxPinholePositionZ.setEnabled(False)

                if self.piezoThread.stateCollimator == "ON":
                    self.ui.labelCollimatorPositionY.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
                    self.ui.labelCollimatorPositionZ.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
                    self.ui.pushButtonAutoCenterCollimator.setEnabled(True)
                    self.ui.doubleSpinBoxCollimatorPositionY.setEnabled(True)
                    self.ui.doubleSpinBoxCollimatorPositionZ.setEnabled(True)
                else:
                    self.ui.labelCollimatorPositionY.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
                    self.ui.labelCollimatorPositionZ.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
                    self.ui.pushButtonAutoCenterCollimator.setEnabled(False)
                    self.ui.doubleSpinBoxCollimatorPositionY.setEnabled(False)
                    self.ui.doubleSpinBoxCollimatorPositionZ.setEnabled(False)

            self.ui.labelPinholePositionY.setText("%7.3f" %self.piezoThread.currPinholeY) 
            self.ui.labelPinholePositionZ.setText("%7.3f" %self.piezoThread.currPinholeZ)
                                
            self.ui.labelCollimatorPositionY.setText("%7.3f" %self.piezoThread.currCollimatorY) 
            self.ui.labelCollimatorPositionZ.setText("%7.3f" %self.piezoThread.currCollimatorZ)
            
            
            if self.piezoThread.stateScreen == "ON":
                self.ui.horizontalSliderFocus.setEnabled(True)
            else:
                self.ui.horizontalSliderFocus.setEnabled(False)
            
            if self.energyThread.state == "ON":
                self.ui.lineEditCurrentEnergy.setStyleSheet("QWidget { background-color: %s;}" % "lightgreen")
            elif self.energyThread.state == "MOVING":
                self.ui.lineEditCurrentEnergy.setStyleSheet("QWidget { background-color: %s;}" % "yellow")
            elif self.energyThread.state == "FAULT":
                self.ui.lineEditCurrentEnergy.setStyleSheet("QWidget { background-color: %s;}" % "red")
            self.ui.lineEditCurrentEnergy.setText("%7.2f eV" % self.energyThread.currentEnergy)
            
            if self.detectorTowerThread.statusInterlock and not self.petraThread.statusShutterBS1:
                self.ui.pushButtonOpenBS1.setEnabled(True)
                self.ui.pushButtonCloseBS1.setEnabled(False)
            elif self.detectorTowerThread.statusInterlock and self.petraThread.statusShutterBS1:
                self.ui.pushButtonOpenBS1.setEnabled(False)
                self.ui.pushButtonCloseBS1.setEnabled(True)
            else:
                self.ui.pushButtonOpenBS1.setEnabled(False)
                self.ui.pushButtonCloseBS1.setEnabled(False)
                
            if not self.goniometerThread.statusFastShutter:
                self.ui.pushButtonCloseShutter.setEnabled(False)
                self.ui.pushButtonOpenShutter.setEnabled(True)
            else:
                self.ui.pushButtonCloseShutter.setEnabled(True)
                self.ui.pushButtonOpenShutter.setEnabled(False)    
    
            if self.waitingForYagIn and self.piezoThread.stateScreen == "ON":
                self.ui.pushButtonYAGin.setEnabled(False)
                self.ui.pushButtonDiodeIn.setEnabled(True)
                self.ui.pushButtonScreenOut.setEnabled(True)
                self.waitingForYagIn = False
                self.ui.pushButtonYAGin.setStyleSheet("background-color: %s" % None)
                self.ui.pushButtonDiodeIn.setStyleSheet("background-color: %s" % None)
                self.ui.pushButtonScreenOut.setStyleSheet("background-color: %s" % None)
            if self.waitingForDiodeIn and self.piezoThread.stateScreen == "ON":
                self.ui.pushButtonYAGin.setEnabled(True)
                self.ui.pushButtonDiodeIn.setEnabled(False)
                self.ui.pushButtonScreenOut.setEnabled(True)
                self.waitingForDiodeIn = False
                self.ui.pushButtonYAGin.setStyleSheet("background-color: %s" % None)
                self.ui.pushButtonDiodeIn.setStyleSheet("background-color: %s" % None)
                self.ui.pushButtonScreenOut.setStyleSheet("background-color: %s" % None)
            if self.waitingForScreenOut and self.piezoThread.stateScreen == "ON":
                self.ui.pushButtonYAGin.setEnabled(True)
                self.ui.pushButtonDiodeIn.setEnabled(True)
                self.waitingForScreenOut = False
                self.ui.pushButtonYAGin.setStyleSheet("background-color: %s" % None)
                self.ui.pushButtonDiodeIn.setStyleSheet("background-color: %s" % None)
                self.ui.pushButtonScreenOut.setStyleSheet("background-color: %s" % None)

            if self.piezoThread.currentScreenPosition == "DiodeIn":
                self.ui.lineEditCurrentFlux.setText("Flux: %6.2e ph/s" % self.photonmeter.Photons)
            else:
                self.ui.lineEditCurrentFlux.setText("diode is out")

            if self.waitingForCollimatorIn and self.piezoThread.stateCollimator == "ON":
                self.ui.pushButtonCollimatorOut.setEnabled(True)
                self.waitingForCollimatorIn = False
                self.ui.pushButtonCollimatorIn.setStyleSheet("background-color: %s" % None)
                self.ui.pushButtonCollimatorOut.setStyleSheet("background-color: %s" % None)
            if self.waitingForCollimatorOut and self.piezoThread.stateCollimator == "ON":
                self.ui.pushButtonCollimatorIn.setEnabled(True)
                self.waitingForCollimatorOut = False
                self.ui.pushButtonCollimatorIn.setStyleSheet("background-color: %s" % None)
                self.ui.pushButtonCollimatorOut.setStyleSheet("background-color: %s" % None)
        
            
            ############ END OF Beam settings tab widgets ###############
            
            ############ BEGIN Sample alignment tab widgets ###############
            if self.goniometerThread.positionContrastscreen == 0:
                self.ui.pushButtonContrastScreenOut.setEnabled(False)
                self.ui.pushButtonContrastScreenIn.setEnabled(True)
            else:
                self.ui.pushButtonContrastScreenOut.setEnabled(True)
                self.ui.pushButtonContrastScreenIn.setEnabled(False)
                
            if self.goniometerThread.stateGoniometer == "ON":
                self.ui.lineEditCurrentAngle.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.goniometerThread.stateGoniometer == "MOVING":
                self.ui.lineEditCurrentAngle.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.goniometerThread.stateGoniometer == "FAULT":
                self.ui.lineEditCurrentAngle.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
                
            if self.goniometerThread.stateFlexureX == "ON":
                self.ui.labelFlexureXposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.goniometerThread.stateFlexureX == "MOVING":
                self.ui.labelFlexureXposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.goniometerThread.stateFlexureX == "FAULT":
                self.ui.labelFlexureXposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
        
            if self.goniometerThread.stateFlexureY == "ON":
                self.ui.labelFlexureYposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.goniometerThread.stateFlexureY == "MOVING":
                self.ui.labelFlexureYposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.goniometerThread.stateFlexureY == "FAULT":
                self.ui.labelFlexureYposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
                
            self.ui.horizontalSliderFlexureXPosition.setMaximum(int(self.goniometerThread.maxPositionFlexureX))
            self.ui.horizontalSliderFlexureXPosition.setMinimum(int(self.goniometerThread.minPositionFlexureX))
            self.ui.horizontalSliderFlexureXPosition.setValue(int(self.goniometerThread.currentPositionFlexureX))
            self.ui.verticalSliderFlexureYPosition.setMaximum(int(self.goniometerThread.maxPositionFlexureY))
            self.ui.verticalSliderFlexureYPosition.setMinimum(int(self.goniometerThread.minPositionFlexureY))
            self.ui.verticalSliderFlexureYPosition.setValue(int(self.goniometerThread.currentPositionFlexureY))
            
            if self.goniometerThread.stateKohzuGoniometerX == "ON":
                self.ui.labelGoniometerXposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.goniometerThread.stateKohzuGoniometerX == "MOVING":
                self.ui.labelGoniometerXposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.goniometerThread.stateKohzuGoniometerX == "FAULT":
                self.ui.labelGoniometerXposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
        
            if self.goniometerThread.stateKohzuGoniometerY == "ON":
                self.ui.labelGoniometerYposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.goniometerThread.stateKohzuGoniometerY == "MOVING":
                self.ui.labelGoniometerYposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.goniometerThread.stateKohzuGoniometerY == "FAULT":
                self.ui.labelGoniometerYposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
        
            if self.goniometerThread.stateKohzuGoniometerZ == "ON":
                self.ui.labelGoniometerZposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.goniometerThread.stateKohzuGoniometerZ == "MOVING":
                self.ui.labelGoniometerZposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.goniometerThread.stateKohzuGoniometerZ == "FAULT":
                self.ui.labelGoniometerZposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
        
            if self.goniometerThread.stateKohzuMicroscopeY == "ON":
                self.ui.labelMicroscopeYposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.goniometerThread.stateKohzuMicroscopeY == "MOVING":
                self.ui.labelMicroscopeYposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.goniometerThread.stateKohzuMicroscopeY == "FAULT":
                self.ui.labelMicroscopeYposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
        
            if self.goniometerThread.stateKohzuMicroscopeZ == "ON":
                self.ui.labelMicroscopeZposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            elif self.goniometerThread.stateKohzuMicroscopeZ == "MOVING":
                self.ui.labelMicroscopeZposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.goniometerThread.stateKohzuMicroscopeZ == "FAULT":
                self.ui.labelMicroscopeZposition.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
                
            if self.goniometerThread.stateGoniometer == "MOVING":
                self.ui.doubleSpinBoxSetAngle.setEnabled(False)
                self.ui.pushButtonAbs0.setEnabled(False)
                self.ui.pushButtonAbs180.setEnabled(False)
                self.ui.pushButtonAbs270.setEnabled(False)
                self.ui.pushButtonAbs90.setEnabled(False)
                self.ui.pushButtonAngleInc.setEnabled(False)
                self.ui.pushButtonAngleDec.setEnabled(False)
            else:
                self.ui.doubleSpinBoxSetAngle.setEnabled(True)
                self.ui.pushButtonAbs0.setEnabled(True)
                self.ui.pushButtonAbs180.setEnabled(True)
                self.ui.pushButtonAbs270.setEnabled(True)
                self.ui.pushButtonAbs90.setEnabled(True)
                self.ui.pushButtonAngleInc.setEnabled(True)
                self.ui.pushButtonAngleDec.setEnabled(True)

            if self.goniometerThread.stateFlexureX == "MOVING" or self.goniometerThread.stateFlexureY == "MOVING":
                self.ui.pushButtonFlexureUp.setEnabled(False)
                self.ui.pushButtonFlexureDown.setEnabled(False)
                self.ui.doubleSpinBoxFlexureXposition.setEnabled(False)
                self.ui.doubleSpinBoxFlexureYposition.setEnabled(False)
            else:
                self.ui.pushButtonFlexureUp.setEnabled(True)
                self.ui.pushButtonFlexureDown.setEnabled(True)
                self.ui.doubleSpinBoxFlexureXposition.setEnabled(True)
                self.ui.doubleSpinBoxFlexureYposition.setEnabled(True)
                
            if not self.cryoThread.cryoRetracted: #extended
                self.ui.pushButtonExtendCryo.setEnabled(False)
                self.ui.pushButtonRetractCryo.setEnabled(True)
            else:
                self.ui.pushButtonExtendCryo.setEnabled(True)
                self.ui.pushButtonRetractCryo.setEnabled(False)
            ############ END OF Sample alignment tab widgets ###############
            
            ############ BEGIN Data collection tab widgets ###############
            
            if self.dataCollectionActive:
                self.ui.groupBoxBeamsize.setEnabled(False)
                self.ui.groupBoxFilter.setEnabled(False)
            else:
                self.ui.groupBoxBeamsize.setEnabled(True)
                self.ui.groupBoxFilter.setEnabled(True)

            if self.petraThread.stateFilter == "MOVING":
                self.ui.comboBoxFilterSelection.setEnabled(False)
                self.ui.doubleSpinBoxDesiredTransmission.setEnabled(False)
            else:
                self.ui.comboBoxFilterSelection.setEnabled(True)
                self.ui.doubleSpinBoxDesiredTransmission.setEnabled(True)
            
            self.ui.comboBoxFilterSelection.blockSignals(True)
            self.ui.doubleSpinBoxDesiredTransmission.blockSignals(True)
            self.ui.comboBoxFilterSelection.setCurrentIndex(self.petraThread.currentFilterPosition)
            self.ui.comboBoxFilterSelection.blockSignals(False)
            self.ui.doubleSpinBoxDesiredTransmission.blockSignals(False)
            
            self.ui.lineEditFilterTransmission.setText("%7.5f" % (100.0*self.petraThread.currentFilterTransmission) + chr(37))
            #self.ui.lineEditFilterTransmission.setStyleSheet("background-color: #{0:02x}{1:02x}20;".format(int(255*self.petraThread.currentFilterTransmission), int(255-255*self.petraThread.currentFilterTransmission)))
            if self.petraThread.stateFilter == "ON":
                self.ui.lineEditFilterTransmission.setStyleSheet("background-color: lightgreen")
            else:
                self.ui.lineEditFilterTransmission.setStyleSheet("background-color: yellow")

            ############ END OF Data collection tab widgets ###############
            
            

            ############ BEGIN Grid scan alignment tab widgets ###############            
            self.updateRasterPosition()
            ############ BEGIN Grid scan alignment tab widgets ###############
            
            if self.helix != None:            
                # To  change graphical items and to see their motion on the main window, 
                # we need to call this function always when changes are done.             
                self.helix.follow()      
                # we could set after the end of motion the 
                #very precise position based on w_values:        
                #self.helix.follow(True) # static = True

            
            QtWidgets.QApplication.processEvents()
#            QtGui.QApplication.processEvents()
            

    

    # update rasterPosition
    # this function needs preinitialized self.sampleIsNotMovingCount 
    # eg in constructor of the owner class 
    def updateRasterPosition(self):  
        sampleIsMoving = False
        if(self.goniometerThread.stateKohzuGoniometerY == "MOVING") or (self.goniometerThread.stateFlexureX == "MOVING") or (self.goniometerThread.stateFlexureY == "MOVING"):                
            sampleIsMoving = True
            self.sampleIsNotMovingCount = 0
        else:
            if self.sampleIsNotMovingCount < 55: # to avoid infinite increment 
                self.sampleIsNotMovingCount = self.sampleIsNotMovingCount + 1
        if ((self.method in ["Grid step scan", "Grid fly scan"]) and (self.raster != None) and (sampleIsMoving or self.sampleWasMoving)):
            if(sampleIsMoving or (self.sampleIsNotMovingCount < 50)): #PP
                posX = self.goniometerThread.currentPositionKohzuGoniometerY                
                angle = self.goniometerThread.currentAngle
                deltaX = self.goniometerThread.currentPositionFlexureX - self.lastPositionFlexureX
                deltaY = self.goniometerThread.currentPositionFlexureY - self.lastPositionFlexureY
            else:
                posX = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Position").w_value
                angle = self.goniometerThread.proxyGoniometer.read_attribute("Position").w_value
                deltaX = self.goniometerThread.proxyFlexureX.read_attribute("Position").w_value - self.lastPositionFlexureX
                deltaY = self.goniometerThread.proxyFlexureY.read_attribute("Position").w_value - self.lastPositionFlexureY                
                self.sampleIsNotMovingCount = 0 # reset counter to 0
            distanceY = deltaX * math.sin(math.radians(angle)) + deltaY * math.cos(math.radians(angle))
            distanceX = posX - self.lastPositionKohzuGoniometerY
            distance = QtCore.QPointF(-distanceX, -distanceY)
            self.raster.raster.move(distance, True, True)
            self.raster.updateRaster()
            self.lastPositionKohzuGoniometerY = posX
            self.lastPositionFlexureX = deltaX + self.lastPositionFlexureX
            self.lastPositionFlexureY = deltaY + self.lastPositionFlexureY
            self.sampleWasMoving = sampleIsMoving
        else:
            self.lastPositionKohzuGoniometerY = self.goniometerThread.currentPositionKohzuGoniometerY
            self.lastPositionFlexureX = self.goniometerThread.currentPositionFlexureX
            self.lastPositionFlexureY = self.goniometerThread.currentPositionFlexureY

    #------- Start of Amarcord functions ---------#

    def initAmarcord(self):
        """ test MySQL connection
        """
        self.writeToLog("Attempting MySQL connection")

        # attempt a connection to the database
        try:
            connection = connector.connect(
                host=self.amarcord["host"],
                database=self.amarcord["database"],
                user=self.amarcord["user"],
                password=self.amarcord["password"],
                connection_timeout=self.amarcord["connection_timeout"],
                raise_on_warnings=self.amarcord["raise_on_warnings"],
                auth_plugin=self.amarcord["auth_plugin"],
            )
        except connector.Error as err:
            if err.errno == connector.errorcode.ER_ACCESS_DENIED_ERROR:
                self.writeToLog("Amarcord Error: wrong user or password")
            elif err.errno == connector.errorcode.ER_BAD_DB_ERROR:
                self.writeToLog("Amarcord Error: database does not exist")
            else:
                self.writeToLog("Amarcord Error: " + str(err))
            self.amarcord["enabled"] = False
        else:
            self.writeToLog(
                "MySQL connection established with database '%s' on '%s'"
                % (self.amarcord["database"], self.amarcord["host"])
            )
            connection.close()

        self.addPersistentSetting(
            "puck_id",
            "general",
            "str",
            "self.ui.lineEditPuckId.text",
            "self.ui.lineEditPuckId.setText",
        )

    def querySampleName(self):
        # sample name comes from the DB if connection is available
        if not self.amarcord["enabled"]:
            return

        dewar_position = int((self.currentSample - 1) / 16) + 1
        # skip demounting
        if dewar_position > 0:
            # from the robot
            puck_position_id = int((self.currentSample - 1) % 16) + 1
            # query puck_id from database
            try:
                connection = connector.connect(
                    host=self.amarcord["host"],
                    database=self.amarcord["database"],
                    user=self.amarcord["user"],
                    password=self.amarcord["password"],
                    connection_timeout=self.amarcord["connection_timeout"],
                    raise_on_warnings=self.amarcord["raise_on_warnings"],
                    auth_plugin=self.amarcord["auth_plugin"],
                )
            except connector.Error as err:
                if err.errno == connector.errorcode.ER_ACCESS_DENIED_ERROR:
                    raise ValueError("Error: wrong user or password")
                elif err.errno == connector.errorcode.ER_BAD_DB_ERROR:
                    raise ValueError("Error: database does not exist")
                else:
                    raise ValueError(err)
            # get the cursor
            cursor = connection.cursor(dictionary=True)
            # execute the query
            try:
                cursor.execute(
                    'SELECT puck_id FROM Dewar_LUT WHERE dewar_position="%s"'
                    % (dewar_position)
                )
            except connector.Error as err:
                raise ValueError("Failed to execute the query: %s" % err)
            # finally fetch the puck ID
            puck_id = cursor.fetchall()
            # all fine?
            if len(puck_id) == 0:
                diag = QtGui.QInputDialog
                qstring, ok = diag.getText(
                    self,
                    QtCore.QString("Puck ID not found"),
                    QtCore.QString("Enter the puck id here:"),
                    QtGui.QLineEdit.Normal,
                )
                puck_id = str(qstring)
                if ok is False:  # user pressed Cancel
                    puck_id = None
                if puck_id == "":  # user entered nothing
                    puck_id = None
            elif len(puck_id) == 1:
                puck_id = puck_id[0]["puck_id"]
            else:
                raise ValueError("Unable to retrieve Crystal ID...")
            connection.commit()
            cursor.close()
            # show info to users
            self.ui.lineEditPuckId.setText(puck_id)

            # query crystal_id from database
            #
            # get the cursor
            cursor = connection.cursor(dictionary=True)
            # execute the query
            try:
                cursor.execute(
                    'SELECT crystal_id FROM Crystal_View WHERE puck_id="%s" AND puck_position_id="%s" AND diffraction is NULL ORDER BY created DESC LIMIT 1;'
                    % (puck_id, puck_position_id)
                )
            except connector.Error as err:
                raise ValueError("Failed to execute the query: %s" % err)
            # finally fetch the sample name (aka crystal_id)
            sample_name = cursor.fetchall()
            # all fine?
            if len(sample_name) == 0:
                diag = QtGui.QInputDialog
                qstring, ok = diag.getText(
                    self,
                    QtCore.QString(
                        "Combination of Puck ID, Puck position and Dewar position returns no results."
                    ),
                    QtCore.QString("Enter the file name here:"),
                    QtGui.QLineEdit.Normal,
                )
                # read the sample name
                sample_name = str(qstring)
                # user pressed Cancel
                if ok is False:
                    sample_name = str(self.ui.lineEditImagePrefix.text())
                # user entered nothing
                if sample_name == "":
                    sample_name = str(self.ui.lineEditImagePrefix.text())
            elif len(sample_name) == 1:
                sample_name = sample_name[0]["crystal_id"]
            else:
                raise ValueError("Unable to retrieve Crystal ID...")
            connection.commit()
            cursor.close()
            connection.close()
            # show info to users
            self.ui.lineEditImagePrefix.setText(sample_name)


    #------- Start of Camera functions ---------#

    def initCamera(self):
        QObject.connect(self.ui.comboBoxCameraZoom, QtCore.SIGNAL("currentIndexChanged(int)"), self.setCameraZoom)
        QObject.connect(self.ui.comboBoxCameraZoom2, QtCore.SIGNAL("currentIndexChanged(int)"), self.setCameraZoom)
        QObject.connect(self.ui.spinBoxCameraGain, QtCore.SIGNAL("valueChanged(int)"), self.setCameraGain)
        QObject.connect(self.ui.spinBoxCameraExposureTime, QtCore.SIGNAL("valueChanged(int)"), self.setCameraExpTime)
        QObject.connect(self.ui.horizontalSliderExposureTime,QtCore.SIGNAL("valueChanged(int)"), self.setCameraExpTime)
        self.camera = VideoThread(self.cameras, self.simulation["camera"])
        self.camera.setImageSize(self.ui.graphicsView.size().width(), self.ui.graphicsView.size().height())
        self.setCameraZoom(0) 
        self.pixelsPerUm = self.camera.getPixelsPerUm()
        self.camera.start()
        self.connect(self.camera, SIGNAL("newFrame()"), self.frameGrabbed)
        self.connect(self.camera, SIGNAL("updateValues()"), self.updateCameraValues)
        self.setCameraZoom(0)

    def updateCameraValues(self):
        self.ui.spinBoxCameraGain.setMinimum(self.camera.gainMin)
        self.ui.spinBoxCameraGain.setMaximum(self.camera.gainMax)
        if not self.ui.spinBoxCameraGain.hasFocus():
            self.ui.spinBoxCameraGain.blockSignals(True)
            self.ui.spinBoxCameraGain.setValue(self.camera.gain)
            self.ui.spinBoxCameraGain.blockSignals(False)
        self.ui.checkBoxCameraAutoGain.setChecked(self.camera.gainAuto)
        self.ui.spinBoxCameraExposureTime.setMinimum(self.camera.exposureMin)
        self.ui.spinBoxCameraExposureTime.setMaximum(200000)
        if not self.ui.spinBoxCameraExposureTime.hasFocus():
            self.ui.spinBoxCameraExposureTime.blockSignals(True)
            self.ui.spinBoxCameraExposureTime.setValue(self.camera.exposure)
            self.ui.spinBoxCameraExposureTime.blockSignals(False)
        self.ui.horizontalSliderExposureTime.setMinimum(self.camera.exposureMin)
        self.ui.horizontalSliderExposureTime.setMaximum(200000)
        self.ui.horizontalSliderExposureTime.blockSignals(True)
        self.ui.horizontalSliderExposureTime.setValue(self.camera.exposure)
        self.ui.horizontalSliderExposureTime.blockSignals(False)
        self.ui.checkBoxCameraAutoExposure.setChecked(self.camera.exposureAuto)
        
    def saveCurrentImage(self):
        timestring = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        angle = "%03ddeg" % round(self.goniometerThread.currentAngle, 0)
        self.path.set_user_and_sample_dir(self.ui.lineEditImagePrefix.text())
        self.path.set_run_number_check(
                    "/beamline/beamtime/raw/user/sample/" +
                    "rotational_number/sample_rotational_number_master.h5")
        self.path.inc_run_number()
        path = self.path.get_path(
                "/beamline/beamtime/raw/user/sample/rotational_number",
                force=True)
        if(path is None):
            self.writeToLog("failed to open run directory")
            return
        self.ui.labelRunNumber.setText(self.path.get_path("number"))
        self.ui.labelRunPath.setText(path)
        path += self.path.get_path(
                "/sample_rotational_number_" +
                "{0}_{1}.jpg".format(angle, timestring))
        self.frameGrabbed(forceUpdate = True)
        pixmap = QtGui.QPixmap.grabWidget(self.ui.graphicsView)
        pixmap.save(path, "JPG", 95)

    def saveOnaxisImageAuto(self):
        angle = "%03ddeg" % round(self.goniometerThread.currentAngle, 0)
        path = self.path.get_path(
                "/beamline/beamtime/raw/user/sample/rotational_number",
                force=True)
        if(path is None):
            self.writeToLog("failed to open run directory")
            return
        path += self.path.get_path(
                "/sample_rotational_number_{0}.jpg".format(angle))
        self.frameGrabbed(forceUpdate = True)
        pixmap = QtGui.QPixmap.grabWidget(self.ui.graphicsView)
        pixmap.save(path, "JPG", 95)

    def saveOnaxisImageScreening(self, angle):
        angle = "%03ddeg" % round(self.goniometerThread.currentAngle, 0)
        path = self.path.get_path(
                "/beamline/beamtime/raw/user/sample/screening_number",
                force=True)
        if(path is None):
            self.writeToLog("failed to open run directory")
            return
        path += self.path.get_path(
                "/sample_screening_number_{0}.jpg".format(angle))
        self.frameGrabbed(forceUpdate = True)
        pixmap = QtGui.QPixmap.grabWidget(self.ui.graphicsView)
        pixmap.save(path, "JPG", 95)
     
    def saveOnaxisImageISMO(self):
        angle = "%03ddeg" % round(self.goniometerThread.currentAngle, 0)
        path = self.path.get_path(
                "/beamline/beamtime/raw/user/sample/grid_number",
                force=True)
        if(path is None):
            self.writeToLog("failed to open run directory")
            return
        path += self.path.get_path(
                "/sample_grid_number_{0}.jpg".format(angle))
        self.frameGrabbed(forceUpdate = True)
        pixmap = QtGui.QPixmap.grabWidget(self.ui.graphicsView)
        pixmap.save(path, "JPG", 95)

    def saveCentringClickImage(self, x, y):
        image = self.camera.camera.camera.raw
        timestring = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        angle = int(round(self.goniometerThread.currentAngle, 0))
        if self.camera.flipX:
            x = -x
        if self.camera.flipY:
            y = -y
        width = int(self.ui.graphicsView.size().width())
        height = int(self.ui.graphicsView.size().height())
        x = x + (width / 2)
        y = y + (height / 2)
        posX = int(round((x / width) * self.camera.camera.width, 0))
        posY = int(round((y / height) * self.camera.camera.height, 0))
        filename = "{0}{1}_{2:03d}_{3:04d}_{4:04d}.jpg".format(
            self.centringClickImagePath, timestring, angle, posX, posY)
        try:
            f = open(filename, "wb")
        except:
            print("error saving centring click image")
            return
        try:
            f.write(image)
        except:
            print("error saving centring click image")
        f.close()

    def frameGrabbed(self,forceUpdate = False):
        frame = self.camera.getFrame()
        if frame is None: return
        self.pixmap = QtGui.QPixmap.fromImage(frame)        
        self.item.setPixmap(self.pixmap)        
        #self.scene.render()
        self.ui.graphicsView.update()

    def setCameraExpTime(self, value = 0):
        self.ui.spinBoxCameraExposureTime.setValue(value)
        self.ui.horizontalSliderExposureTime.setValue(value)
        self.camera.setExposure(value)
        #self.writeToLog("Camera exposure time set to " + str(value))
        
    def setCameraGain(self,value = 0):
        self.ui.spinBoxCameraGain.setValue(value)
        self.camera.setGain(value)
        #self.writeToLog("Camera gain set to " +str(value))

    def setCameraZoom(self, value = 0):
        factor = self.pixelsPerUm
        if(value == 0): #overview picture scaled
            self.camera.changeCamera(1)
            self.camera.setCropSize()
            self.pixelsPerUm = self.camera.getPixelsPerUm()
            self.camera.updateValues()
        elif(value == 1): #full picture scaled
            self.camera.changeCamera(0)
            self.camera.setCropSize()
            self.pixelsPerUm = self.camera.getPixelsPerUm()
            self.camera.updateValues()
        elif(value == 2): #ROI in fitted dimensions
            self.camera.changeCamera(0)
            self.camera.setCropSize(self.ui.graphicsView.size().width(), self.ui.graphicsView.size().height())
            self.pixelsPerUm = self.camera.getPixelsPerUm()
            self.camera.updateValues()
        elif(value == 3): #ROI in fitted dimensions / 2
            self.camera.changeCamera(0)
            self.camera.setCropSize(self.ui.graphicsView.size().width() / 2, self.ui.graphicsView.size().height() / 2)
            self.pixelsPerUm = self.camera.getPixelsPerUm()
            self.camera.updateValues()
        else:
            return
        self.ui.comboBoxCameraZoom.blockSignals(True)
        self.ui.comboBoxCameraZoom.setCurrentIndex(value)
        self.ui.comboBoxCameraZoom.blockSignals(False)
        self.ui.comboBoxCameraZoom2.blockSignals(True)
        self.ui.comboBoxCameraZoom2.setCurrentIndex(value)
        self.ui.comboBoxCameraZoom2.blockSignals(False)
        self.addEllipseAndCrosshair()
        factor = self.pixelsPerUm / factor
        self.raster.raster.setConversion(self.pixelsPerUm)
        self.raster.scale(factor)
        if (self.helix != None):
            self.helix.setPixelsPerUm(self.pixelsPerUm)

    def addEllipseAndCrosshair(self):
        ellipseWidth = self.beamWidth*self.pixelsPerUm
        ellipseHeight = self.beamHeight*self.pixelsPerUm
        #ellipseX = (self.ui.graphicsView.size().width() - ellipseWidth) / 2 + self.ui.doubleSpinBoxBeamPositionHorizontal.value() * self.pixelsPerUm
        #ellipseY = (self.ui.graphicsView.size().height() - ellipseHeight) / 2 + self.ui.doubleSpinBoxBeamPositionVertical.value() * self.pixelsPerUm
        ellipseX = (self.ui.graphicsView.size().width() - ellipseWidth) / 2
        ellipseY = (self.ui.graphicsView.size().height() - ellipseHeight) / 2
        centreX = self.ui.graphicsView.size().width()/ 2
        centreY = self.ui.graphicsView.size().height()/ 2
        n = len(self.items)
        
        try:
            for i in range(n):
                self.scene.removeItem(self.items.pop())
        except:
            pass
        self.items.append(self.scene.addEllipse(ellipseX,ellipseY,ellipseWidth,ellipseHeight,QtGui.QPen(QtGui.QColor("red"))))
        self.items.append(self.scene.addLine(centreX-10,centreY,centreX+10,centreY,QtGui.QPen(QtGui.QColor("red"))))
        self.items.append(self.scene.addLine(centreX,centreY+10,centreX,centreY-10,QtGui.QPen(QtGui.QColor("red"))))
        

    def setCameraAutoExposure(self,newState):
        self.ui.checkBoxCameraAutoExposure.blockSignals(True)
        if newState: #if autogain
            self.ui.checkBoxCameraAutoExposure.setChecked(True)
            self.camera.setAutoExposure(True)
        else:
            self.ui.checkBoxCameraAutoExposure.setChecked(False)
            self.camera.setAutoExposure(False)
        self.ui.checkBoxCameraAutoExposure.blockSignals(False)
    
    def setCameraAutoGain(self,newState):
        self.ui.checkBoxCameraAutoGain.blockSignals(True)
        if newState: #if autogain
            self.ui.checkBoxCameraAutoGain.setChecked(True)
            self.camera.setAutoGain(True) # gain mode auto
        else:
            self.ui.checkBoxCameraAutoGain.setChecked(False)
            self.camera.setAutoGain(False) # gain mode manual
        
        self.ui.checkBoxCameraAutoGain.blockSignals(False)
        

    #------- Start of Misc functions ---------#

    def distancePointToLine(self,pointX,pointY,p1x,p1y,p2x,p2y):
        #If you have points A(xa, ya), B(xb, yb) and C(xc,yc). The distance between point C and line segment AB equals the area of parallelgram ABCC' divided by the length of AB.
        dist = math.sqrt(((p2y-p1y)*(pointX-p1x)-(p2x-p1x)*(pointY-p1y))**2/((p2x-p1x)**2 + (p2y-p1y)**2))
        return dist
    
    def gauss(self,x, p): # p[0]==mean, p[1]==stdev
        return 1.0/(p[1]*numpy.sqrt(2*numpy.pi))*numpy.exp(-(x-p[0])**2/(2*p[1]**2))

    def autoCenterPinhole(self):
        img = self.camera.getFrame()
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.ReadWrite)
        img.save(buffer, "BMP")
        pil_im = Image.open(io.BytesIO(buffer.data()))
        pil_im = pil_im.convert("L")  #make grayscale
        
        pic = numpy.asarray(pil_im)
        # Average the pixel values along vertical axis
        pic_avg     = pic.mean(axis=0)
        (width,height) = pil_im.size
        X = numpy.arange(0,width,1)
        projection = pic_avg
        # Set the min value to zero for a nice fit
        projection /= projection.mean()
        projection -= projection.min()
        Y = projection
        Y /= Y.sum()
        # Fit a gaussian
        p0 = [0,width] # Inital guess is a normal distribution
        errfunc = lambda p, x, y: self.gauss(x, p) - y # Distance to the target function
        p1, success = opt.leastsq(errfunc, p0[:], args=(X, Y))
        fit_mu, fit_stdev = p1
        horizontalFWHM = 2*numpy.sqrt(2*numpy.log(2))*fit_stdev/self.pixelsPerUm
        gaussfit = self.gauss(X,p1)
        
        horizSaved = self.pinholePositionsY[self.currentPinhole]
        horizDelta = (width/2-(numpy.argmax(gaussfit)))/self.pixelsPerUm
        horizCorrected = horizSaved - horizDelta
        
        pic_avg = pic.mean(axis=1)
        X = numpy.arange(0,height,1)
        projection = pic_avg
        # Set the min value to zero for a nice fit
        projection /= projection.mean()
        projection -= projection.min()
        Y = projection
        Y /= Y.sum()
        # Fit a gaussian
        p0 = [0,height] # Inital guess is a normal distribution
        errfunc = lambda p, x, y: self.gauss(x, p) - y # Distance to the target function
        p1, success = opt.leastsq(errfunc, p0[:], args=(X, Y))
        fit_mu, fit_stdev = p1
        verticalFWHM = 2*numpy.sqrt(2*numpy.log(2))*fit_stdev/self.pixelsPerUm
        gaussfit = self.gauss(X,p1)
        
        vertSaved = self.pinholePositionsZ[self.currentPinhole]
        vertDelta = (height/2-(numpy.argmax(gaussfit)))/self.pixelsPerUm
        vertCorrected = vertSaved - vertDelta
        
        if horizontalFWHM < 10 or verticalFWHM < 10:
            self.writeToLog("Error: no pinhole detected.")
            QtGui.QMessageBox.warning(self,"Error","No pinhole detected. FWHM < 10 um.","&Ok")
            return
        else:
            self.writeToLog("Pinhole " + str(self.currentPinhole) + " Horizontal FWHM (um):"+ str(int(horizontalFWHM)))
            self.writeToLog("Pinhole " + str(self.currentPinhole) + " Vertical FWHM:"+ str(int(verticalFWHM)))
            self.writeToLog("Pinhole " + str(self.currentPinhole) + " New horizontal pinhole position:"+ str(horizCorrected))
            self.writeToLog("Pinhole " + str(self.currentPinhole) + " New vertical pinhole position:"+ str(vertCorrected))
    
        self.pinholePositionsY[self.currentPinhole] = horizCorrected
        self.pinholePositionsZ[self.currentPinhole] = vertCorrected
        self.pinholes = numpy.column_stack((self.pinholePositionsY,self.pinholePositionsZ,self.pinholeList))
        
        self.piezoThread.pinholePositions = self.pinholes
        self.selectPinhole(self.currentPinhole)

    
    def autoCenterCollimator(self):
        img = self.camera.getFrame()
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.ReadWrite)
        img.save(buffer, "BMP")
        pil_im = Image.open(io.BytesIO(buffer.data()))
        pil_im = pil_im.convert("L")  #make grayscale
        
        pic = numpy.asarray(pil_im)
        # Average the pixel values along vertical axis
        pic_avg     = pic.mean(axis=0)
        (width,height) = pil_im.size
        X = numpy.arange(0,width,1)
        projection = pic_avg
        # Set the min value to zero for a nice fit
        projection /= projection.mean()
        projection -= projection.min()
        Y = projection
        Y /= Y.sum()
        # Fit a gaussian
        p0 = [0,width] # Inital guess is a normal distribution
        errfunc = lambda p, x, y: self.gauss(x, p) - y # Distance to the target function
        p1, success = opt.leastsq(errfunc, p0[:], args=(X, Y))
        fit_mu, fit_stdev = p1
        horizontalFWHM = 2*numpy.sqrt(2*numpy.log(2))*fit_stdev/self.pixelsPerUm
        gaussfit = self.gauss(X,p1)
        
        horizSaved = self.piezoThread.collimatorInPositionY
        horizDelta = (width/2-(numpy.argmax(gaussfit)))/self.pixelsPerUm
        horizCorrected = horizSaved - horizDelta
        
        pic_avg = pic.mean(axis=1)
        X = numpy.arange(0,height,1)
        projection = pic_avg
        # Set the min value to zero for a nice fit
        projection /= projection.mean()
        projection -= projection.min()
        Y = projection
        Y /= Y.sum()
        # Fit a gaussian
        p0 = [0,height] # Inital guess is a normal distribution
        errfunc = lambda p, x, y: self.gauss(x, p) - y # Distance to the target function
        p1, success = opt.leastsq(errfunc, p0[:], args=(X, Y))
        fit_mu, fit_stdev = p1
        verticalFWHM = 2*numpy.sqrt(2*numpy.log(2))*fit_stdev/self.pixelsPerUm
        gaussfit = self.gauss(X,p1)
        
        vertSaved = self.piezoThread.collimatorInPositionZ
        vertDelta = (height/2-(numpy.argmax(gaussfit)))/self.pixelsPerUm
        vertCorrected = vertSaved - vertDelta
        
        if horizontalFWHM < 10 or verticalFWHM < 10:
            self.writeToLog("Error: no collimator detected.")
            QtGui.QMessageBox.warning(self,"Error","No collimator detected. FWHM < 10 um.","&Ok")
            return
        else:
            self.writeToLog("Collimator " + str(self.currentPinhole) + " Horizontal FWHM (um):"+ str(int(horizontalFWHM)))
            self.writeToLog("Collimator " + str(self.currentPinhole) + " Vertical FWHM:"+ str(int(verticalFWHM)))
            self.writeToLog("Collimator " + str(self.currentPinhole) + " New horizontal collimator position:"+ str(horizCorrected))
            self.writeToLog("Collimator " + str(self.currentPinhole) + " New vertical collimator position:"+ str(vertCorrected))

        self.piezoThread.collimatorInPositionY = horizCorrected
        self.piezoThread.collimatorInPositionZ = vertCorrected
        self.piezoThread.collimatorIn()
        
        
    def autoCenterBeamstop(self):
        if not self.detectorTowerThread.statusInterlock:
            QtGui.QMessageBox.warning(self,"Error","Interlock is not set. Search the hutch!","&Ok")
            return
        if not self.petraThread.statusShutterBS0:
            QtGui.QMessageBox.warning(self,"Error","BS0 is not open. Search the optics hutch and open it! Or ask somebody to do it for you.","&Ok")
            return
        if not self.petraThread.statusShutterBS1:
            QtGui.QMessageBox.warning(self,"Error","BS1 is not open. Open it!","&Ok")
            return
        if not self.detectorTowerThread.shieldIsUp:
            QtGui.QMessageBox.warning(self,"Error","Detector guillotine is not up. What the fuck did you do?","&Ok")
            return
        if not self.goniometerThread.stateGoniometer == "ON":
            QtGui.QMessageBox.warning(self,"Error","Goniometer is moving or not on. ""Not on"" means something broke. Ask an engineer!","&Ok")
            return
        if not self.piezoThread.currentYAGScreenPosition == "Out":
            QtGui.QMessageBox.warning(self,"Error","The YAG/diode screen is in the way. Move it out of the way!","&Ok")
            return
        if self.currentPinhole ==  0:
            QtGui.QMessageBox.warning(self,"Error","You have to select a pinhole first","&Ok")
            return
        if self.petraThread.currentFilterTransmission < 1.:
            QtGui.QMessageBox.warning(self,"Error","You have to move out the filters first","&Ok")
            return
        if self.petraThread.currentFilterTransmission < 1.:
            QtGui.QMessageBox.warning(self,"Error","You have to move out the filters first","&Ok")
            return
        
        self.writeToLog("Starting automatic beamstop centering.")
        if not self.goniometerThread.statusFastShutter:
            self.writeToLog("Opening fast shutter.")
            self.goniometerThread.openShutter()
        self.contrastScreenOut()
        self.piezoThread.moveBeamStopIn()

        p=beamstopCentering(self)
        p.exec_()
        self.writeToLog("Automatic beamstop centering finished.")


    def find_nearest(self,a, a0):
        #"index of element in nd array `a` closest to the scalar value `a0`" 
        idx = numpy.abs(a - a0).argmin()
        return idx
    

    def GetInHMS(self,seconds):
        seconds = round(seconds,0)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)
    

    def checkOrUncheck(self,checkbox,set):
        checkbox.setCheckable(True)
        if set:
            checkbox.setEnabled(True)
            checkbox.setChecked(True)
        else:
            checkbox.setChecked(False)
            checkbox.setEnabled(False)
        

    def setManualMountPosition(self):
        try:
            self.piezoThread.stopPinhole()
        except:
            pass
        try:
            self.piezoThread.stopScreen()
        except:
            pass
        try:
            self.piezoThread.stopCollimator()
        except:
            pass
        try:
            self.detectorTowerThread.stopDetectorTower()
        except:
            pass
        try:
            self.piezoThread.stopBeamstop()
        except:
            pass
        
        if self.sxMode:
            print("Moving beamstop back")
            self.piezoThread.moveBeamStopOut()
            time.sleep(0.5)
            while self.piezoThread.stateBeamstop == "MOVING":
                print("Waiting for beamstop to move back...")
                time.sleep(0.5)
            print("Beamstop is out of the way")
            print("Moving goniometer to manual mount position")
            self.goniometerThread.activateSerialCrystallographyManualMountPosition()
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setAngle, 0))
        else:
            print("Moving beamstop back")
            self.piezoThread.moveBeamStopOut()
            
        self.closeShutter()
        self.oldPinhole = self.currentPinhole
        self.screenOut()
        self.contrastScreenOut()
        self.collimatorOut()
        self.detectorTowerThread.shieldUp()
        self.selectPinhole(0)
        
        self.previousDetectorDistance = self.detectorTowerThread.currentPositionDetectorTowerServer
        if self.previousDetectorDistance < self.detectorManualMountPosition:
            self.detectorTowerThread.resetPositionDetectorTower()
        self.petraThread.closeBS1()
        #self.retractCryo()
        
        self.manualMountConditionsList = { \
            "BS1closed": False, \
            "FSclosed": False, \
#            "CryoRetracted": False, \
#            "PinholesOut": False, \
            "CollimatorOut": False, \
#            "YAGout": False, \
            "BacklightOut": False, \
            "DetectorShieldUp": False, \
            "DetectorTower": False, \
            "BeamstopOut": False, \
            "SampleChanger": False, \
            }
        self.updateTimerManualMountPosition.start(500)
        

    def checkManualMountStatus(self):
        if not self.petraThread.statusShutterBS1:
            self.manualMountConditionsList["BS1closed"] = True
        if not self.goniometerThread.statusFastShutter:
            self.manualMountConditionsList["FSclosed"] = True
#        if self.cryoThread.cryoRetracted:
#            self.manualMountConditionsList["CryoRetracted"] = True
#        if self.piezoThread.statePinhole == "ON":
#            self.manualMountConditionsList["PinholesOut"] = True
        if self.piezoThread.stateCollimator == "ON":
            self.manualMountConditionsList["CollimatorOut"] = True
#        if self.piezoThread.stateScreen == "ON":
#            self.manualMountConditionsList["YAGout"] = True
        if self.goniometerThread.positionContrastscreen == 0:
            self.manualMountConditionsList["BacklightOut"] = True
        if self.detectorTowerThread.shieldIsUp:
            self.manualMountConditionsList["DetectorShieldUp"] = True
        if self.detectorTowerThread.stateDetectorTower == "ON":
            self.manualMountConditionsList["DetectorTower"] = True
        if self.piezoThread.beamstopXInOut == "Out":
            self.manualMountConditionsList["BeamstopOut"] = True
        self.manualMountConditionsList["SampleChanger"] = \
            self.robotThread.tangostate != "MOVING"

        breakInterlock = True
        for condition in list(self.manualMountConditionsList.values()):
            breakInterlock &= condition

        if breakInterlock:
            self.updateTimerManualMountPosition.stop()
            self.petraThread.breakInterlockEH()
            self.updateTimerWaitForInterlockBreak.start(1000)


    def waitForInterlockToBreak(self):
        if not self.detectorTowerThread.statusInterlock:
            self.updateTimerWaitForInterlockBreak.stop()
            self.updateTimerWaitForInterlockSet.start(1000)

    def waitForInterlockToSet(self):
        if self.detectorTowerThread.statusInterlock:
            self.updateTimerWaitForInterlockSet.stop()
            if not self.piezoThread.currentYAGScreenPosition == "In":
                self.extendCryo()
            #self.piezoThread.moveBeamStopIn()
            #self.collimatorIn()
            self.selectPinhole(self.oldPinhole)
            self.setCameraZoom(0)
            newText = "Set manual mount position\n and open hutch"
            self.ui.pushButtonManualMountPositionBreakInterlock.setText(newText)
            self.ui.pushButtonManualMountPositionBreakInterlock.setEnabled(True)

            if self.detectorTowerThread.stateDetectorTower == "ON":
                try:
                    self.detectorTowerThread.setPositionDetectorTower(self.previousDetectorDistance)
                except:
                    pass
            if self.sxMode:
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setAngle, 0))
                self.goniometerThread.activateSerialCrystallographyMode()


    def moveToBeam(self, event):
        deltaX = event.pos().x() - self.pixmap.size().width() / 2
        deltaY = event.pos().y() - self.pixmap.size().height() / 2
        distanceX = deltaX / self.pixelsPerUm
        distanceY = deltaY / self.pixelsPerUm
        if self.centringClickImagePath is not None:
            self.saveCentringClickImage(deltaX, deltaY)
        self.moveSample(distanceX, distanceY)
        if (self.ui.pushButtonThreeClickMode.isChecked()):
            self.incrementGoniometerPosition(90)
        
    def moveToBeamSerialCrystallography(self, event):
        #if(not self.rasterSerialCrystallography.isEmpty()and not self.dragging and not self.rotating and self.ui.checkBoxMoveToBeam_JA.isChecked()):
        #    for pointindex in range(len(self.rasterSerialCrystallography.positions)):
        #        distance = math.sqrt((event.pos().x()-self.rasterSerialCrystallography.positions[pointindex].x())**2+(event.pos().y()-self.rasterSerialCrystallography.positions[pointindex].y())**2)
        #        if distance < self.rasterSerialCrystallography.beamsizeHorizontal/2:
        #            self.writeToLog("Moving to scan point #" + str(pointindex))
        #            self.moveToRasterPositionSerialCrystallography(pointindex)
        #            return

        deltaX = event.pos().x() - self.pixmap.size().width() / 2
        deltaY = event.pos().y() - self.pixmap.size().height() / 2
        distanceX = deltaX / self.pixelsPerUm
        distanceY = deltaY / self.pixelsPerUm
        #self.debugPxDeltaX = 0.0
        #self.debugPxDeltaY = 0.0
        #print "cmpx:", deltaX, deltaY
        self.moveSampleWithKohzu(distanceX, distanceY)

    def moveSample(self, distanceX, distanceY):
        try:
            if self.goniometerThread.stateKohzuGoniometerY != "ON":
                #QtGui.QMessageBox.warning(None,"Error","Wait until motors have stopped moving","&Ok")
                #return
                self.goniometerThread.stopKohzuGoniometerY()
                
            if self.goniometerThread.stateFlexureY != "ON":
                #QtGui.QMessageBox.warning(None,"Error","Wait until motors have stopped moving","&Ok")
                #return
                self.goniometerThread.stopFlexureY()
                
            if self.goniometerThread.stateFlexureX != "ON":
                #QtGui.QMessageBox.warning(None,"Error","Wait until motors have stopped moving","&Ok")
                #return
                self.goniometerThread.stopFlexureX()
        except:
            print(sys.exc_info())
        self.writeToLog(str("Moving sample: deltaX="+"%6.2f"%distanceX+"um, deltaY="+"%6.2f"%distanceY+"um"))
        self.moveFlexuresUpDown(distanceY)
        currentPosition = self.goniometerThread.currentPositionKohzuGoniometerY
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerY, currentPosition + distanceX))
        
    def moveSampleWithKohzu(self, distanceX, distanceY):
        try:
            if self.goniometerThread.stateKohzuGoniometerY != "ON":
                #QtGui.QMessageBox.warning(None,"Error","Wait until motors have stopped moving","&Ok")
                #return
                self.goniometerThread.stopKohzuGoniometerY()
                
            if self.goniometerThread.stateKohzuGoniometerZ != "ON":
                #QtGui.QMessageBox.warning(None,"Error","Wait until motors have stopped moving","&Ok")
                #return
                self.goniometerThread.stopKohzuGoniometerZ()
                
        except:
            print(sys.exc_info())
        self.writeToLog(str("Moving sample: deltaX="+"%6.2f"%distanceX+"um, deltaY="+"%6.2f"%distanceY+"um"))
        
        currentPositionY = self.goniometerThread.currentPositionKohzuGoniometerY
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerY, currentPositionY + distanceX))
        currentPositionZ = self.goniometerThread.currentPositionKohzuGoniometerZ
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerZ, currentPositionZ + distanceY))
        
    def openBS1(self):
        self.petraThread.openBS1()

    def closeBS1(self):
        self.petraThread.closeBS1()

    #------- Start of Log and Error functions ---------#

    def write(self, text):
        z = time.localtime() 
        self.ui.textEditDataCollectionLog.append("[%02d:%02d:%02d] " % (z[3], z[4], z[5]) + str(text))
        self.stdErrBar.setValue(self.stdErrBar.maximum())

    def writeToLog(self, text):
        z = time.localtime() 
        self.stdErrBar.setValue(self.stdErrBar.maximum())
        self.ui.textEditDataCollectionLog.append("[%02d:%02d:%02d] " % (z[3], z[4], z[5]) + str(text))

    def saveLog(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File','.')
        try:
            fname = open(filename, 'w')
            fname.write(self.ui.textEditDataCollectionLog.toPlainText())
            fname.close()
        except:
            pass
        
    def threadErrorHandler(self, error):
        QtGui.QMessageBox.warning(self,"Error",str(error),"&Ok")

    #------- End of Log and error functions ---------#

    #------- Start of Contrast screen functions ---------#
    def contrastScreenOut(self):
        self.goniometerThread.moveContrastScreenOut()
        
    def contrastScreenIn(self):
        self.goniometerThread.moveContrastScreenIn()
#        
    def YAGIn(self):
        self.writeToLog("Moving YAG in")
        self.retractCryo()
        if self.piezoThread.stateScreen == "MOVING":
            self.piezoThread.stopScreen()
            #QtGui.QMessageBox.warning(self,"Error","Wait until screen has stopped moving","&Ok")
            #return
        
        if self.sxMode:
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setAngle, 0))
            while self.goniometerThread.stateGoniometer == "MOVING":
                print("Waiting for goniometer to turn back to 0 degrees")
                time.sleep(0.5)
            if self.goniometerThread.stateKohzuGoniometerZ == "ON":
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerZ, self.SerialCrystYAGinGoniometerZposition))
                print("moving kohzu to",self.SerialCrystYAGinGoniometerZposition)
            else:
                QtGui.QMessageBox.warning(self,"Error","Wait until the goniometer Z motor has stopped moving","&Ok")
                return
        self.piezoThread.yagIn()
        self.ui.pushButtonYAGin.setEnabled(False)
        self.ui.pushButtonDiodeIn.setEnabled(False)
        self.ui.pushButtonScreenOut.setEnabled(False)
        self.waitingForYagIn = True
        self.waitingForDiodeIn = False
        self.waitingForScreenOut = False
        self.ui.pushButtonYAGin.setStyleSheet("background-color: %s" % "yellow")
        self.ui.pushButtonDiodeIn.setStyleSheet("background-color: %s" % None)
        self.ui.pushButtonScreenOut.setStyleSheet("background-color: %s" % None)
        time.sleep(0.1)

    def diodeIn(self):
        self.retractCryo()
        if self.sxMode:
            self.goniometerThread.setAngle(0)
            while self.goniometerThread.stateGoniometer == "MOVING":
                print("Waiting for goniometer to turn back to 0 degrees")
                time.sleep(0.5)
            if self.goniometerThread.stateKohzuGoniometerZ == "ON":
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerZ, self.SerialCrystYAGinGoniometerZposition))
                print("moving kohzu to",self.SerialCrystYAGinGoniometerZposition)
            else:
                QtGui.QMessageBox.warning(self,"Error","Wait until the goniometer Z motor has stopped moving","&Ok")
                return
            #QtGui.QMessageBox.warning(self,"Error","Diode in not possible in serial crystallography mode","&Ok")
            #return
        self.writeToLog("Moving diode in")
        if self.piezoThread.stateScreen == "MOVING":
            #QtGui.QMessageBox.warning(self,"Error","Wait until screen has stopped moving","&Ok")
            #return
            self.piezoThread.stopScreen()
        self.piezoThread.diodeIn()
        self.ui.pushButtonYAGin.setEnabled(False)
        self.ui.pushButtonDiodeIn.setEnabled(False)
        self.ui.pushButtonScreenOut.setEnabled(False)
        self.waitingForYagIn = False
        self.waitingForDiodeIn = True
        self.waitingForScreenOut = False
        self.ui.pushButtonYAGin.setStyleSheet("background-color: %s" % None)
        self.ui.pushButtonDiodeIn.setStyleSheet("background-color: %s" % "yellow")
        self.ui.pushButtonScreenOut.setStyleSheet("background-color: %s" % None)
        time.sleep(0.1)

    def screenOut(self):
        self.retractCryo()
        self.writeToLog("Moving fluorescence/diode screen out")
        if self.piezoThread.stateScreen == "MOVING":
            #QtGui.QMessageBox.warning(self,"Error","Wait until screen has stopped moving","&Ok")
            #return
            self.piezoThread.stopScreen()

        if self.sxMode:
            if self.goniometerThread.stateKohzuGoniometerZ == "ON":
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerZ, self.NominalGoniometerZposition))
                print("moving kohzu to",self.NominalGoniometerZposition)
            else:
                QtGui.QMessageBox.warning(self,"Error","Wait until the goniometer Z motor has stopped moving","&Ok")
                return
        self.piezoThread.screenOut()
        self.ui.pushButtonYAGin.setEnabled(False)
        self.ui.pushButtonDiodeIn.setEnabled(False)
        self.ui.pushButtonScreenOut.setEnabled(False)
        self.waitingForYagIn = False
        self.waitingForDiodeIn = False
        self.waitingForScreenOut = True
        self.ui.pushButtonYAGin.setStyleSheet("background-color: %s" % None)
        self.ui.pushButtonDiodeIn.setStyleSheet("background-color: %s" % None)
        self.ui.pushButtonScreenOut.setStyleSheet("background-color: %s" % "yellow")
        time.sleep(0.1)

    def screenStop(self):
        self.waitingForYagIn = False
        self.waitingForDiodeIn = False
        self.waitingForScreenOut = False
        self.piezoThread.stopScreen()
        self.ui.pushButtonYAGin.setEnabled(True)
        self.ui.pushButtonDiodeIn.setEnabled(True)
        self.ui.pushButtonScreenOut.setEnabled(True)
        self.ui.pushButtonYAGin.setStyleSheet("background-color: %s" % None)
        self.ui.pushButtonDiodeIn.setStyleSheet("background-color: %s" % None)
        self.ui.pushButtonScreenOut.setStyleSheet("background-color: %s" % None)
        
        
    def setYAGfocus(self):
        value = self.ui.horizontalSliderFocus.value()
        self.piezoThread.setScreenFocus(value)
        self.ui.horizontalSliderFocus.setEnabled(False)
    #------- End of Contrast screen functions ---------#

    #------- Start of raster functions ---------#
#     def setISMOTopLeftX(self, value):
#         self.raster.setTopLeft(QtCore.QPointF(value, self.raster.topLeft.y()), True)
#         self.updateISMORaster()
# 
#     def setISMOTopLeftY(self, value):
#         self.raster.setTopLeft(QtCore.QPointF(self.raster.topLeft.x(), value), True)
#         self.updateISMORaster()
# 
#     def setISMOWidth(self, value):
#         self.raster.setWidth(value, True)
#         self.updateISMORaster()
# 
#     def setISMOHeight(self, value):
#         self.raster.setHeight(value, True)
#         self.updateISMORaster()
# 
    def setGridAngle(self, value):
        self.raster.angle.setValue(value) # self.ui.doubleSpinBoxStartAngle_ISMO.value()
        self.ui.doubleSpinBoxStartAngle_Grid.blockSignals(True)
        self.ui.doubleSpinBoxStartAngle_Grid.setValue(value)
        self.ui.doubleSpinBoxStartAngle_Grid.blockSignals(False)
        self.ui.doubleSpinBoxStartAngle_ISMO.blockSignals(True)
        self.ui.doubleSpinBoxStartAngle_ISMO.setValue(value)
        self.ui.doubleSpinBoxStartAngle_ISMO.blockSignals(False)
        self.raster.updateRaster()

    def setGridStepsizeX(self, value):
        stepsize = self.raster.raster.getStepsize()
        stepsize.setX(value) #value = self.ui.doubleSpinBoxStepsizeX_Grid.value()
        self.ui.doubleSpinBoxStepsizeX_Grid.blockSignals(True)
        self.ui.doubleSpinBoxStepsizeX_Grid.setValue(value)
        self.ui.doubleSpinBoxStepsizeX_Grid.blockSignals(False)
        self.ui.doubleSpinBoxStepsizeX_ISMO.blockSignals(True)
        self.ui.doubleSpinBoxStepsizeX_ISMO.setValue(value)
        self.ui.doubleSpinBoxStepsizeX_ISMO.blockSignals(False)
        self.raster.raster.setStepsize(stepsize)                
        self.raster.updateRaster()


    def setGridStepsizeY(self, value):
        stepsize = self.raster.raster.getStepsize()
        stepsize.setY(value) # self.ui.doubleSpinBoxStepsizeX_Grid.value()
        self.ui.doubleSpinBoxStepsizeY_Grid.blockSignals(True)
        self.ui.doubleSpinBoxStepsizeY_Grid.setValue(value)
        self.ui.doubleSpinBoxStepsizeY_Grid.blockSignals(False)
        self.ui.doubleSpinBoxStepsizeY_ISMO.blockSignals(True)
        self.ui.doubleSpinBoxStepsizeY_ISMO.setValue(value)
        self.ui.doubleSpinBoxStepsizeY_ISMO.blockSignals(False)
        self.raster.raster.setStepsize(stepsize)
        self.raster.updateRaster()
        

    def clearGrid(self):
        self.raster.clear()

    def defineGrid(self):
        self.raster.updateRaster()
        self.ui.graphicsView.update()

    def clearSXgrid(self):
        self.ui.pushButtonDefineGrid_SX.setEnabled(True)
        self.ui.pushButtonClearGrid_SX.setEnabled(False)
        self.rasterSerialCrystallography.clear()
        self.updateJetAlignmentRaster()

    def moveToRasterPosition(self, position):
        positions = self.raster.getScanPositions()
        self.moveSample(positions[position].x(), positions[position].y())

    def moveToRasterPositionSerialCrystallography(self, position):
        positions = self.rasterSerialCrystallography.getScanPositions()
        self.moveSampleWithKohzu(positions[position].x(), positions[position].y())

    #------- End of raster functions ---------#

    #------- Start of Roboter functions ---------#
    def initRobot(self):
        self.robotThread = RobotThread(self.robotserver, self)
        self.connect(self.robotThread, SIGNAL("update()"), self.updateRobot)
        self.connect(self.robotThread, SIGNAL("logSignal(PyQt_PyObject)"), self.writeToLog)
        self.connect(self.ui.pushButtonRobotMount, SIGNAL("clicked()"), self.mountSelectedSample)
        self.connect(self.ui.pushButtonRobotDemount, SIGNAL("clicked()"), self.demountSample)
        self.connect(self.ui.pushButtonRobotWash, SIGNAL("clicked()"), self.washSample)
        self.connect(self.ui.pushButtonRobotHome, SIGNAL("clicked()"), self.moveHome)
        self.connect(self.ui.pushButtonRobotCool, SIGNAL("clicked()"), self.coolGripper)
        self.connect(self.ui.pushButtonRobotDeice, SIGNAL("clicked()"), self.deiceGripper)
        self.connect(self.ui.spinBoxRobotDeiceSamples, SIGNAL("valueChanged(int)"), self.deiceSampleInterval)
        self.connect(self.ui.spinBoxRobotDeiceMinutes, SIGNAL("valueChanged(int)"), self.deiceTimeInterval)
        self.ui.treeWidgetSampleChanger.itemDoubleClicked.connect(self.mountSelectedSample)
        self.ui.treeWidgetSampleChanger.itemCollapsed.connect(self.sampleTreeExpanded)
        self.ui.treeWidgetSampleChanger.itemExpanded.connect(self.sampleTreeExpanded)
        #self.ui.pushButtonRobotWash.hide()
        self.ui.label_27.hide()
        self.ui.label_28.hide()
        self.ui.spinBoxRobotDeiceMinutes.hide()
        self.robotThread.start()
        
    def mountSelectedSample(self, item=None, i=None):
        if item is None:
            try:
                item = self.ui.treeWidgetSampleChanger.currentItem()
            except:
                return
        if item.parent() is not None:
            if item.parent().parent() is not None:
                return
            sample = 16 * self.ui.treeWidgetSampleChanger.indexOfTopLevelItem(item.parent()) + item.parent().indexOfChild(item) + 1
        self.mountSample(sample)

    def updateRobot(self):
        if self.robotThread.tangostate != "ON":
            if self.robotThread.tangostate == "INIT":
                self.ui.labelStatusSampleChanger.setText("SampleChanger:\nUnitialized")
                self.ui.labelStatusSampleChanger.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
            elif self.robotThread.tangostate == "MOVING":
                self.ui.labelStatusSampleChanger.setText("SampleChanger:\nMoving")
                self.ui.labelStatusSampleChanger.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "yellow")
            elif self.robotThread.tangostate == "FAULT":
                self.ui.labelStatusSampleChanger.setText("SampleChanger:\nFault")
                self.ui.labelStatusSampleChanger.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "red")
            else:
                self.ui.labelStatusSampleChanger.setText("SampleChanger:\nUnknown" + self.robotThread.tangostate)
                self.ui.labelStatusSampleChanger.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "grey")
            self.ui.pushButtonRobotMount.setEnabled(False)
            self.ui.pushButtonRobotDemount.setEnabled(False)
            self.ui.pushButtonRobotWash.setEnabled(False)
            self.ui.pushButtonRobotHome.setEnabled(False)
            self.ui.pushButtonRobotCool.setEnabled(False)
            self.ui.pushButtonRobotDeice.setEnabled(False)
        else:
            self.ui.labelStatusSampleChanger.setText("SampleChanger:\nReady")
            self.ui.labelStatusSampleChanger.setStyleSheet("QWidget { background-color: %s; font-weight:bold}" % "lightgreen")
            if self.robotThread.statusSampleMounted == 0:
                self.ui.pushButtonRobotMount.setEnabled(True)
            else:
                self.ui.pushButtonRobotDemount.setEnabled(True)
                self.ui.pushButtonRobotWash.setEnabled(True)
            self.ui.pushButtonRobotHome.setEnabled(True)
            self.ui.pushButtonRobotCool.setEnabled(True)
            self.ui.pushButtonRobotDeice.setEnabled(True)
        if not self.ui.spinBoxRobotDeiceSamples.hasFocus():
            self.ui.spinBoxRobotDeiceSamples.setValue(int(self.robotThread.deiceSampleInterval))
        if not self.ui.spinBoxRobotDeiceMinutes.hasFocus():
            self.ui.spinBoxRobotDeiceMinutes.setValue(int(self.robotThread.deiceTimeInterval / 60))
        
        if self.progressDialog is not None:
            if type(self.progressDialog) != QtGui.QDialog:
                return
            elif self.progressDialog.windowTitle() != "SampleMount":
                return
            elif not (self.robotThread.mounting or self.robotThread.demounting):
                #mounting done
                self.contrastScreenIn()
                self.progressDialog.done(QtGui.QDialog.Accepted)
                self.progressDialog = None
                self.querySampleName()
            else:
                i = 0
                for item in self.robotProgressStatus:
                    widget = self.progressDialog.layout().itemAt(i).widget()
                    widget.setChecked(eval(item[1]))
                    i += 1
        else:
            if self.robotThread.statusSampleMounted != self.currentSample:
                self.highlightSample(self.currentSample, False)
                self.highlightSample(self.robotThread.statusSampleMounted)
                self.currentSample = self.robotThread.statusSampleMounted

    def sampleTreeExpanded(self, item):
        self.highlightSample(self.currentSample)

    def highlightSample(self, sample, highlight=True):
        if sample == 0:
            return
        model = self.ui.treeWidgetSampleChanger.model()
        parent = model.index(int((sample - 1) / 16), 0)
        item = parent.child(int((sample - 1)) % 16, 0)
        color = QtGui.QBrush(QtGui.QColor(144, 238, 144))
        background =  QtGui.QBrush(QtGui.QPalette().color(QtGui.QPalette.Base))
        if not highlight:
            color = background
        expanded = False
        if sample > 0:
            expanded = self.ui.treeWidgetSampleChanger.topLevelItem((sample - 1) / 16).isExpanded()
        if expanded:
            model.setData(item, color, QtCore.Qt.BackgroundRole)
            model.emit(QtCore.SIGNAL('dataChanged(QModelIndex)'), item)
            model.setData(parent, background, QtCore.Qt.BackgroundRole)
            model.emit(QtCore.SIGNAL('dataChanged(QModelIndex)'), parent)
        else:
            model.setData(parent, color, QtCore.Qt.BackgroundRole)
            model.emit(QtCore.SIGNAL('dataChanged(QModelIndex)'), parent)

    def showRobotProgressDialog(self):
        self.robotProgressStatus = [ \
            ["Collimator out", "self.robotThread.statusCollimator"], \
            ["Screen out", "self.robotThread.statusScreen"], \
            ["Cryojet out", "self.robotThread.statusCryojet"], \
            ["Goniometer in mount position", "self.robotThread.statusGonio"], \
            ["Guillotine closed", "self.robotThread.statusGuillotine"], \
            ["Collision protection clear", "self.robotThread.statusCollisionProtection"], \
            ["Robot arm powered", "self.robotThread.statusArmPowered"], \
            ["Emergency stop clear", "self.robotThread.statusScreen"], \
            ["Interlock set", "self.robotThread.statusInterlock"], \
        ]
        self.progressDialog = QtGui.QDialog(self)
        self.progressDialog.setWindowTitle("SampleMount")
        self.progressDialog.setLayout(QtGui.QVBoxLayout())
        self.progressDialog.setModal(True)
        self.progressDialog.setWindowFlags(self.progressDialog.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        for item in self.robotProgressStatus:
            widget = QtGui.QCheckBox(item[0])
            widget.setChecked(eval(item[1]))
            widget.setEnabled(False)
            self.progressDialog.layout().addWidget(widget)
        self.progressDialog.show()

    def mountSample(self, sampleNumber=None):
        if sampleNumber is None or self.robotThread.statusSampleMounted > 0:
            return
        if self.robotThread.tangostate == "ON" and not self.robotThread.mounting and not self.robotThread.demounting:
            self.robotThread.startMount(sampleNumber)
            self.highlightSample(sampleNumber)
            self.currentSample = sampleNumber
            self.showRobotProgressDialog()
            self.setCameraZoom(0)
            self.writeToLog("Mounting sample " + str(sampleNumber))
            puck = int((sampleNumber - 1) / 16) + 1
            pin = int((sampleNumber - 1) % 16) + 1
            print("Mounting puck {0}, sample {1}".format(puck, pin))
        else:
            self.writeToLog("Mounting impossible. Robot is in state " + self.robotThread.tangostate)
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Mounting impossible. Robot is in state " + self.robotThread.tangostate, QtGui.QMessageBox.Ok)

    def demountSample(self):
        if self.robotThread.statusSampleMounted == 0:
            self.writeToLog("Unmounting impossible. No sample mounted")
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Unmounting impossible. No sample mounted", QtGui.QMessageBox.Ok)
            return
        if self.robotThread.tangostate == "ON" and not self.robotThread.mounting and not self.robotThread.demounting:
            self.robotThread.startDemount()
            self.highlightSample(self.currentSample, False)
            self.currentSample = 0
            self.showRobotProgressDialog()
            self.writeToLog("Unmounting sample " + str(self.robotThread.statusSampleMounted))
            puck = int((self.robotThread.statusSampleMounted - 1) / 16) + 1
            pin = int((self.robotThread.statusSampleMounted - 1) % 16) + 1
            print("Unmounting puck {0}, sample {1}".format(puck, pin))
        else:
            self.writeToLog("Unmounting impossible. Robot is in state " + self.robotThread.tangostate)
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Unmounting impossible. Robot is in state " + self.robotThread.tangostate, QtGui.QMessageBox.Ok)

    def washSample(self):
        if self.robotThread.statusSampleMounted == 0:
            self.writeToLog("Washing impossible. No sample mounted")
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Washing impossible. No sample mounted", QtGui.QMessageBox.Ok)
            return
        if self.robotThread.tangostate == "ON" and not self.robotThread.mounting and not self.robotThread.demounting:
            self.robotThread.startWashing()
            self.showRobotProgressDialog()
            self.writeToLog("Washing sample " + str(self.robotThread.statusSampleMounted))
        else:
            self.writeToLog("Washing impossible. Robot is in state " + self.robotThread.tangostate)
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Washing impossible. Robot is in state " + self.robotThread.tangostate, QtGui.QMessageBox.Ok)

    def moveHome(self):
        if self.robotThread.tangostate == "ON" and not self.robotThread.mounting and not self.robotThread.demounting:
            self.robotThread.moveHome()
            self.writeToLog("Move to home position")
        else:
            self.writeToLog("Unable to go to home position. Robot is in state " + self.robotThread.tangostate)
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Unable to go to cooling position. Robot is in state " + self.robotThread.tangostate, QtGui.QMessageBox.Ok)

    def coolGripper(self):
        if self.robotThread.tangostate == "ON" and not self.robotThread.mounting and not self.robotThread.demounting:
            self.robotThread.coolGripper()
            self.writeToLog("Cooling Gripper")
        else:
            self.writeToLog("Unable to go to cooling position. Robot is in state " + self.robotThread.tangostate)
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Unable to go to cooling position. Robot is in state " + self.robotThread.tangostate, QtGui.QMessageBox.Ok)

    def deiceGripper(self):
        if self.robotThread.tangostate == "ON" and not self.robotThread.mounting and not self.robotThread.demounting:
            self.robotThread.deiceGripper()
            self.writeToLog("Deicing Gripper")
        else:
            self.writeToLog("Deicing impossible. Robot is in state " + self.robotThread.tangostate)
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Deicing impossible. Robot is in state " + self.robotThread.tangostate, QtGui.QMessageBox.Ok)

    def deiceSampleInterval(self):
        self.robotThread.setDeiceSampleInterval(int(self.ui.spinBoxRobotDeiceSamples.value()))

    def deiceTimeInterval(self):
        self.robotThread.setDeiceTimeInterval(int(self.ui.spinBoxRobotDeiceMinutes.value() * 60.))

    def setRobotSpeed(self):
        #dummy
        self.robotThread.setSpeed(int(self.ui.spinBoxSetSpeed.value()))

    def eStop(self):
        #dummy
        self.writeToLog("Emergency stop")
        self.robotThread.eStop()

    #------- End of Roboter functions ---------#

    #------- Start of Pinhole functions ---------#
    def stopPinhole(self):
        self.piezoThread.stopPinhole()
        self.ui.comboBoxPinhole.blockSignals(True)
        self.ui.comboBoxPinhole.setCurrentIndex(0)
        self.ui.comboBoxPinhole.blockSignals(False)
        self.beamWidth = 200
        self.beamHeight = 200
        self.currentPinhole = 0
        self.addEllipseAndCrosshair()


    def selectPinhole(self,pinhole):
        self.writeToLog("Changing pinhole to number " + str(pinhole))
        if self.piezoThread.statePinhole == "MOVING":
            #QtGui.QMessageBox.warning(self,"Error","Wait until current pinhole is in place","&Ok")
            #return
            self.piezoThread.stopPinhole()
        if self.dataCollectionActive:
            QtGui.QMessageBox.warning(self,"Error","Cannot set pinhole. Data collection is active","&Ok")
            return
        if pinhole == 0:
            self.piezoThread.setPinhole(0)
        if pinhole == 1:
            self.piezoThread.setPinhole(1)
        if pinhole == 2:
            self.piezoThread.setPinhole(2)
        if pinhole == 3:
            self.piezoThread.setPinhole(3)
        if pinhole == 4:
            self.piezoThread.setPinhole(4)
        self.ui.comboBoxPinhole.blockSignals(True)
        self.ui.comboBoxPinhole.setCurrentIndex(pinhole)
        self.ui.comboBoxPinhole.blockSignals(False)
        self.currentPinhole = pinhole
        if self.currentPinhole > 0:
            beamDiameter = min(self.pinholes[self.currentPinhole][2], self.energyThread.beamSizes[self.currentFocus])
        elif self.currentPinhole == 0:
            beamDiameter = self.energyThread.beamSizes[self.currentFocus]
        self.beamWidth = beamDiameter
        self.beamHeight = beamDiameter
        #self.raster.beamsize.setValue(self.beamWidth, self.beamHeight)
        self.addEllipseAndCrosshair()
        self.setRasterBeamSize()


    def startAngleHelixChanged(self):
        if self.helix is None:
            return
        self.helix.p1.gonio.angle = self.ui.doubleSpinBoxStartAngle_Helix.value()
        self.helicalScanParameterChanged()

                
    def helicalScanParameterChanged(self):
        # redefine EndAngle and TotalDuration Time, when DegreesPer Frame is changed
        if self.helix is not None and self.helix.p1.isSet:
            self.helix.p2.gonio.angle = self.helix.p1.gonio.angle + self.ui.spinBoxNumberOfImages_Helix.value() * self.ui.doubleSpinBoxDegPerFrame_Helix.value()   
            self.ui.labelHelicalScanEndAngleVal.setText(str(self.helix.p2.gonio.angle))        
        self.ui.labelHelicalScanScanDurationVal.setText(str(self.ui.spinBoxNumberOfImages_Helix.value() * self.ui.doubleSpinBoxExpTime_Helix.value()/1000)) 


    def selectFocus(self, focus, force=False):
        if not force and focus > 0:
            choice = QtGui.QMessageBox.question(self,'', "Attention, this will change the mirror bending. Do you want to proceed?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        else:
            choice = QtGui.QMessageBox.Yes
        focus -= 1
        if choice == QtGui.QMessageBox.Yes:
            if focus >= 0 and focus < 6:
                
                self.currentFocus = focus
                self.energyThread.setBeamSize(focus)
                if self.currentPinhole > 0:
                    beamDiameter = min(self.pinholes[self.currentPinhole][2], self.energyThread.beamSizes[self.currentFocus])
                elif self.currentPinhole == 0:
                    beamDiameter = self.energyThread.beamSizes[self.currentFocus]
                self.beamWidth = beamDiameter
                self.beamHeight = beamDiameter
                #self.raster.beamsize.setValue(self.beamWidth, self.beamHeight)
                self.addEllipseAndCrosshair()
                self.setRasterBeamSize()
        self.ui.comboBoxFocus.blockSignals(True)
        self.ui.comboBoxFocus.setCurrentIndex(self.currentFocus+1)
        self.ui.comboBoxFocus.blockSignals(False)
        
    #------- Start of Shutter functions ---------#

    def openShutter(self,override=False):
        if self.dataCollectionActive and not override:
            QtGui.QMessageBox.warning(self,"Error","Cannot open shutter. Data collection is active","&Ok")
            return
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.openShutter,0))
        self.writeToLog("Shutter opened")

    def closeShutter(self,override=False):
        if self.dataCollectionActive and not override:
            QtGui.QMessageBox.warning(self,"Error","Cannot close shutter. Data collection is active","&Ok")
            return
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.closeShutter,0))
        self.writeToLog("Shutter closed")


    #------- Start of Collimator functions ---------#

    def collimatorIn(self,override=False):
        if self.dataCollectionActive and not override:
            QtGui.QMessageBox.warning(self,"Error","Cannot move collimator in. Data collection is active","&Ok")
            return
        self.piezoThread.collimatorIn()
        
        self.ui.pushButtonCollimatorIn.setEnabled(False)
        self.ui.pushButtonCollimatorOut.setEnabled(False)
        self.waitingForCollimatorIn = True
        self.waitingForCollimatorOut = False
        self.ui.pushButtonCollimatorIn.setStyleSheet("background-color: %s" % "yellow")
        self.ui.pushButtonCollimatorOut.setStyleSheet("background-color: %s" % None)
        
        self.writeToLog("Moving collimator in")
        
    def collimatorOut(self,override=False):
        if self.dataCollectionActive and not override:
            QtGui.QMessageBox.warning(self,"Error","Cannot move collimator out. Data collection is active","&Ok")
            return
        self.piezoThread.collimatorOut()
        self.ui.pushButtonCollimatorIn.setEnabled(False)
        self.ui.pushButtonCollimatorOut.setEnabled(False)
        self.waitingForCollimatorIn = False
        self.waitingForCollimatorOut = True
        self.ui.pushButtonCollimatorIn.setStyleSheet("background-color: %s" % None)
        self.ui.pushButtonCollimatorOut.setStyleSheet("background-color: %s" % "yellow")
        self.writeToLog("Moving collimator out")

    def collimatorStop(self):
        self.piezoThread.stopCollimator()


    #------- Start of Illumination functions ---------#
    def initIllumination(self):
        QObject.connect(self.ui.horizontalSliderFrontIllumination,QtCore.SIGNAL("valueChanged(int)"), self.setIllumination)
        QObject.connect(self.ui.horizontalSliderBackIllumination,QtCore.SIGNAL("valueChanged(int)"), self.setBacklight)
        QObject.connect(self.ui.horizontalSliderInlineIllumination,QtCore.SIGNAL("valueChanged(int)"), self.setInlineIllumination)
        self.addPersistentSetting("illumination", "general", "int", \
                    "self.ui.horizontalSliderFrontIllumination.value", \
                    "self.setIllumination")
        self.addPersistentSetting("inline_illumination", "general", "int", \
                    "self.ui.horizontalSliderInlineIllumination.value", \
                    "self.setInlineIllumination")
        self.addPersistentSetting("back_illumination", "general", "int", \
                    "self.ui.horizontalSliderBackIllumination.value", \
                    "self.setBacklight")

    def setIllumination(self, value):
        self.ui.horizontalSliderFrontIllumination.blockSignals(True)
        self.ui.horizontalSliderFrontIllumination.setValue(value)
        value = value / 100.
        if value < 0.1: value = 0.01
        try:
            self.proxyIllumination.write_attribute("Voltage", value)
        except:
            raise
        self.ui.horizontalSliderFrontIllumination.blockSignals(False)

    def setInlineIllumination(self, value):
        self.ui.horizontalSliderInlineIllumination.blockSignals(True)
        self.ui.horizontalSliderInlineIllumination.setValue(value)
        value = value / 2000.
        if value < 0.1: value = 0.00
        try:
            self.proxyInlineIllumination.write_attribute("Voltage", value)
        except:
            raise
        self.ui.horizontalSliderInlineIllumination.blockSignals(False)

    def setBacklight(self, value):
        self.ui.horizontalSliderBackIllumination.blockSignals(True)
        self.ui.horizontalSliderBackIllumination.setValue(value)
        value = value / 200.
        if value < 0.1: value = 0.00
        try:
            self.backlight.write_attribute("Voltage", value)
        except:
            raise
        self.ui.horizontalSliderBackIllumination.blockSignals(False)

    def incInlineIris(self):
        try:
            current = self.proxyInlineIris.read_attribute("Position").value
            self.proxyInlineIris.write_attribute("Position", current + 1.)
        except:
            self.writeToLog("failed to write to " + self.proxyInlineIris.name())

    def decInlineIris(self):
        try:
            current = self.proxyInlineIris.read_attribute("Position").value
            self.proxyInlineIris.write_attribute("Position", current - 1.)
        except:
            self.writeToLog("failed to write to " + self.proxyInlineIris.name())

    def incInlineSpot(self):
        try:
            current = self.proxyInlineSpot.read_attribute("Position").value
            self.proxyInlineSpot.write_attribute("Position", current + 1.)
        except:
            self.writeToLog("failed to write to " + self.proxyInlineSpot.name())

    def decInlineSpot(self):
        try:
            current = self.proxyInlineSpot.read_attribute("Position").value
            self.proxyInlineSpot.write_attribute("Position", current - 1.)
        except:
            self.writeToLog("failed to write to " + self.proxyInlineSpot.name())

    #------- End of Illumination functions ---------#


    
    #------- Start of Data collection functions ---------#

    def startDataCollection(self):
        if self.method == "Standard collection":
            self.startDataCollection_Std()
        elif self.method == "Screening":
            self.startDataCollection_Screening()
        elif self.method == "Grid fly scan":
            self.startDataCollection_Grid()
        elif self.method == "Grid step scan":
            self.startDataCollection_ISMO()
        elif self.method == "Helical scan":
            print((self.helix.p1.isSet))
            print((self.helix.p2.isSet))
            print((self.ui.doubleSpinBoxDegPerFrame_Helix.value()))
            print((self.ui.spinBoxNumberOfImages_Helix.value()))
            print((self.ui.doubleSpinBoxExpTime_Helix.value()))
            if (self.helix.p1.isSet and self.helix.p2.isSet and (self.ui.doubleSpinBoxDegPerFrame_Helix.value()>0) and (self.ui.spinBoxNumberOfImages_Helix.value()>0) and (self.ui.doubleSpinBoxExpTime_Helix.value()>0)):
                self.startDataCollectionHelix()
            else:
                QtGui.QMessageBox.warning(self, "Error", "Both points as well as Number of images, Deg/frame and exposure time must be initialized to start Data Collection ", "&Ok")
        else:            
            return

    def showDataCollectionProgressDialog(self, conditionList):
        self.progressDialog = QtGui.QDialog(self)
        self.progressDialog.ui = Ui_dialogDataCollection()
        self.progressDialog.ui.setupUi(self.progressDialog)
        self.progressDialog.setWindowFlags(self.progressDialog.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        for key, value in conditionList.items():
            widget = QtGui.QCheckBox(key)
            widget.setChecked(value)
            widget.setEnabled(False)
            self.progressDialog.ui.verticalLayoutDataCollectionStatus.addWidget(widget)
        self.progressDialog.show()

    def hideDataCollectionProgessDialog(self):
        self.progressDialog.done(QtGui.QDialog.Accepted)
        self.progressDialog = None


    def dataCollectionWaitConditionsUpdate(self):
        conditionsList = self.dataCollector.conditionsList
        for i in range(len(self.dataCollector.conditionsList)):            
            widget = self.progressDialog.ui.verticalLayoutDataCollectionStatus.itemAt(i).widget()            
            widget.setChecked(self.dataCollector.conditionsList[str(widget.text())])

    def dataCollectionProgressUpdate(self):
        try:
            alive = self.dataCollector.alive
        except:
            self.updateTimerDataCollectionProgress.stop()
            self.writeToLog("Data collection thread died unexpectedly")
            self.dataCollectionActive = False
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed,self.defaultGoniospeed))
            self.collimatorOut()
            self.piezoThread.moveBeamStopOut()
            self.hideDataCollectionProgessDialog()
            return
        if not alive:
            self.updateTimerDataCollectionProgress.stop()
            self.progressDialog.ui.labelDataCollectionProgress.setText("Data collection finished")
            self.progressDialog.ui.progressBarDataCollection.setValue(100)
            if hasattr(self.dataCollector, "raster"):
                self.dataCollector.raster.updateRaster()
            self.dataCollectionActive = False
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed,self.defaultGoniospeed))
            self.collimatorOut()
            self.piezoThread.moveBeamStopOut()
            self.contrastScreenIn()
            self.hideDataCollectionProgessDialog()
            return
        if self.dataCollector.dataCollectionActive:
            self.progressDialog.ui.labelCollectionTime.setText(self.GetInHMS(time.time()-self.dataCollector.starttime))
            self.progressDialog.ui.labelDataCollectionTimeRemaining.setText(self.GetInHMS(self.dataCollector.collectionTime()))
            self.progressDialog.ui.progressBarDataCollection.setValue(int(self.dataCollector.collectionTime(True)))
        else:
            conditionsList = self.dataCollector.conditionsList
            for i in range(len(self.dataCollector.conditionsList)):
                widget = self.progressDialog.ui.verticalLayoutDataCollectionStatus.itemAt(i).widget()
                widget.setChecked(self.dataCollector.conditionsList[str(widget.text())])

    def initMethod_Std(self):
        self.addPersistentSetting("start_angle", "std", "float",
                    "self.ui.doubleSpinBoxStartAngle_Std.value",
                    "self.ui.doubleSpinBoxStartAngle_Std.setValue")
        self.addPersistentSetting("start_angle_current", "std", "bool",
                    "self.ui.checkBoxStartAngle_Std.isChecked",
                    "self.ui.checkBoxStartAngle_Std.setChecked")
        self.addPersistentSetting("number_of_frames", "std", "int",
                    "self.ui.spinBoxNumberOfFrames_Std.value",
                    "self.ui.spinBoxNumberOfFrames_Std.setValue")
        self.addPersistentSetting("degrees_per_frame", "std", "float",
                    "self.ui.doubleSpinBoxDegreesPerFrame_Std.value",
                    "self.ui.doubleSpinBoxDegreesPerFrame_Std.setValue")
        self.addPersistentSetting("exposure_time", "std", "float",
                    "self.ui.doubleSpinBoxExpTime_Std.value",
                    "self.ui.doubleSpinBoxExpTime_Std.setValue")
        self.addPersistentSetting("4m_mode", "std", "bool",
                    "self.ui.checkBox4M_Std.isChecked",
                    "self.ui.checkBox4M_Std.setChecked")
        self.addPersistentSetting("live_view", "std", "bool",
                    "self.ui.checkBoxLiveView_Std.isChecked",
                    "self.ui.checkBoxLiveView_Std.setChecked")
        self.addPersistentSetting("start_xdsapp", "std", "bool",
                    "self.ui.checkBoxStartXdsapp_Std.isChecked",
                    "self.ui.checkBoxStartXdsapp_Std.setChecked")
        self.ui.checkBox4M_Std.hide()

    def startDataCollection_Std(self):
        self.setRunnumber()
        filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness + self.petraThread.currentFilter3Thickness
        #filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness
        startAngle = self.ui.doubleSpinBoxStartAngle_Std.value()
        if self.ui.checkBoxStartAngle_Std.isChecked():
            startAngle = self.goniometerThread.currentAngle % 360
            if startAngle < 0.0:
                startAngle += 360.0
        self.dataCollectionActive = True
        self.dataCollector = DataCollector(self.detectorTowerThread, self.goniometerThread, self.petraThread, self.piezoThread, self.eigerThread, self.liveView, self.path)
        self.dataCollector.setParameter("filetype",".cbf")
        self.dataCollector.setParameter("filenumber",1)
        self.dataCollector.setParameter("startangle", startAngle)
        self.dataCollector.setParameter("frames", self.ui.spinBoxNumberOfFrames_Std.value())
        self.dataCollector.setParameter("degreesperframe", self.ui.doubleSpinBoxDegreesPerFrame_Std.value())
        self.dataCollector.setParameter("exposureperiod", self.ui.doubleSpinBoxExpTime_Std.value() / 1000.0)
        self.dataCollector.setParameter("exposuretime", self.ui.doubleSpinBoxExpTime_Std.value() / 1000.0)
        self.dataCollector.setParameter("detectordistance", self.ui.doubleSpinBoxDetectorDistance.value())
        self.dataCollector.setParameter("4mMode", self.ui.checkBox4M_Std.isChecked())
        self.dataCollector.setParameter("liveview", self.ui.checkBoxLiveView_Std.isChecked())
        self.dataCollector.setParameter("pinhole", self.currentPinhole)
        self.dataCollector.setParameter("pinholeDiameter", self.pinholes[self.currentPinhole][2])
        self.dataCollector.setParameter("focus", self.energyThread.beamSizeNames[self.currentFocus])
        self.dataCollector.setParameter("filterTransmission", self.petraThread.currentFilterTransmission)
        self.dataCollector.setParameter("filterThickness", filterThickness)
        self.dataCollector.setParameter("sampleoutDistanceWhenBeamcheck",self.sampleoutDistanceWhenBeamcheck)
        self.dataCollector.setParameter("autostartXDS", self.ui.checkBoxStartXdsapp_Std.isChecked())
        self.dataCollector.setParameter("takeDirectBeamImage", False)
        self.dataCollector.setParameter("beamX", self.beamOriginX + 30.0 * (self.ui.doubleSpinBoxDetectorDistance.value() - 160) / 1000.0)
        self.dataCollector.setParameter("beamY", self.beamOriginY)
        self.dataCollector.setParameter("beamCurrent", self.petraThread.currPetraCurrent)
        
        stopAngle = self.dataCollector.parameters["startangle"] + self.dataCollector.parameters["degreesperframe"] * self.dataCollector.parameters["frames"]
        speed = self.dataCollector.parameters["degreesperframe"] * (1.0 / self.dataCollector.parameters["exposureperiod"])
        totalCollectionTime = (stopAngle-self.dataCollector.parameters["startangle"]) / speed
        
        self.connect(self.dataCollector, SIGNAL("errorSignal(PyQt_PyObject)"), self.dataCollectionErrorHandler)
        self.connect(self.dataCollector, SIGNAL("logSignal(PyQt_PyObject)"), self.writeToLog)
        self.connect(self.dataCollector, SIGNAL("waitConditionsUpdate()"), self.dataCollectionWaitConditionsUpdate)
        self.connect(self.dataCollector, SIGNAL("onaxisImage()"), self.saveOnaxisImageAuto)
        
        self.dataCollector.start()
        self.showDataCollectionProgressDialog(self.dataCollector.conditionsList)
        self.progressDialog.ui.labelDataCollectionSpeed.setText(("%6.2f " % speed) + chr(176) +"/s")    
        self.progressDialog.ui.labelCollectionTime.setText(self.GetInHMS(totalCollectionTime))    
        self.progressDialog.ui.labelDataCollectionTimeRemaining.setText(self.GetInHMS(totalCollectionTime))    
        self.progressDialog.ui.labelDegreesTotal.setText("%6.2f "%(stopAngle - startAngle) + chr(176))
        self.progressDialog.ui.labelDataCollectionProgress.setText("Data collection in progress")
        self.connect(self.progressDialog.ui.pushButtonStopDataCollection, SIGNAL("clicked()"), self.stopDataCollection_Std)
        self.updateTimerDataCollectionProgress.start(100)

    def stopDataCollection_Std(self):
        self.closeShutter(True)
        self.detectorTowerThread.shieldUp()
        self.piezoThread.moveBeamStopOut()
        if self.dataCollectionActive:
            self.writeToLog("Aborting data collection...")
            self.dataCollectionActive = False
            self.dataCollector.stop()
        self.dataCollectionActive = False
        self.collectionParametersSet = False
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.stopMotion))
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed,self.defaultGoniospeed))
        self.eigerThread.cmd_q.put(EigerClientCommand(EigerClientCommand.stopAcquisition))
        self.collimatorOut()
        self.progressDialog.ui.progressBarDataCollection.setValue(0)
        self.progressDialog.ui.labelDataCollectionTimeRemaining.setText(self.GetInHMS(0))
        self.progressDialog.ui.labelDataCollectionProgress.setText("Data collection aborted")
        self.writeToLog("Data collection aborted")

    def initMethod_Screening(self):
        self.addPersistentSetting("start_angle", "screening", "float",
                    "self.ui.doubleSpinBoxStartAngle_Scr.value",
                    "self.ui.doubleSpinBoxStartAngle_Scr.setValue")
        self.addPersistentSetting("start_angle_current", "screening", "bool",
                    "self.ui.checkBoxStartAngle_Scr.isChecked",
                    "self.ui.checkBoxStartAngle_Scr.setChecked")
        self.addPersistentSetting("number_of_frames", "screening", "int",
                    "self.ui.comboBoxNumFrames_Scr.currentIndex",
                    "self.ui.comboBoxNumFrames_Scr.setCurrentIndex")
        self.addPersistentSetting("frame_interval", "screening", "int",
                    "self.ui.comboBoxInterval_Scr.currentIndex",
                    "self.ui.comboBoxInterval_Scr.setCurrentIndex")
        self.addPersistentSetting("degrees_per_frame", "screening", "float",
                    "self.ui.doubleSpinBoxDegreesPerFrame_Scr.value",
                    "self.ui.doubleSpinBoxDegreesPerFrame_Scr.setValue")
        self.addPersistentSetting("exposure_time", "screening", "float",
                    "self.ui.doubleSpinBoxExpTime_Scr.value",
                    "self.ui.doubleSpinBoxExpTime_Scr.setValue")
        self.addPersistentSetting("4m_mode", "screening", "bool",
                    "self.ui.checkBox4M_Scr.isChecked",
                    "self.ui.checkBox4M_Scr.setChecked")
        self.addPersistentSetting("live_view", "screening", "bool",
                    "self.ui.checkBoxLiveView_Scr.isChecked",
                    "self.ui.checkBoxLiveView_Scr.setChecked")
        self.addPersistentSetting("start_mosflm", "screening", "bool",
                    "self.ui.checkBoxStartMosflm_Scr.isChecked",
                    "self.ui.checkBoxStartMosflm_Scr.setChecked")
        self.ui.checkBox4M_Scr.hide()

    def startDataCollection_Screening(self):
        self.setRunnumber_Screening(True)
        filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness + self.petraThread.currentFilter3Thickness
        #filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness
        start_angle = self.ui.doubleSpinBoxStartAngle_Scr.value()
        if self.ui.checkBoxStartAngle_Scr.isChecked():
            start_angle = self.goniometerThread.currentAngle % 360
            if start_angle < 0.0:
                start_angle += 360.0
        totalFrames = int(self.ui.comboBoxNumFrames_Scr.currentText())
        interval = int(self.ui.comboBoxInterval_Scr.currentText()[:-8])   #x degrees
        angles = [((start_angle + i * interval) % 360) for i in range(totalFrames)]
        self.dataCollectionActive = True
        self.dataCollector = ScreeningCollector(self.detectorTowerThread, self.goniometerThread, self.petraThread, self.piezoThread, self.eigerThread, self.liveView, self.path)
        self.dataCollector.setParameter("filetype", ".cbf")
        self.dataCollector.setParameter("filenumber", 1)
        self.dataCollector.setParameter("startangle", start_angle)
        self.dataCollector.setParameter("frames", 1)
        self.dataCollector.setParameter("degreesperframe", self.ui.doubleSpinBoxDegreesPerFrame_Scr.value())
        self.dataCollector.setParameter("exposureperiod", self.ui.doubleSpinBoxExpTime_Scr.value() / 1000.0)
        self.dataCollector.setParameter("exposuretime", self.ui.doubleSpinBoxExpTime_Scr.value() / 1000.0)
        self.dataCollector.setParameter("detectordistance", self.ui.doubleSpinBoxDetectorDistance.value())
        self.dataCollector.setParameter("4mMode", self.ui.checkBox4M_Scr.isChecked())
        self.dataCollector.setParameter("liveview", self.ui.checkBoxLiveView_Scr.isChecked())
        self.dataCollector.setParameter("sampleoutDistanceWhenBeamcheck", self.sampleoutDistanceWhenBeamcheck)
        self.dataCollector.setParameter("pinhole", self.currentPinhole)
        self.dataCollector.setParameter("pinholeDiameter", self.pinholes[self.currentPinhole][2])
        self.dataCollector.setParameter("focus", self.energyThread.beamSizeNames[self.currentFocus])
        self.dataCollector.setParameter("filterTransmission", self.petraThread.currentFilterTransmission)
        self.dataCollector.setParameter("filterThickness", filterThickness)
        self.dataCollector.setParameter("autostartMosflm", self.ui.checkBoxStartMosflm_Scr.isChecked())
        self.dataCollector.setParameter("beamX", self.beamOriginX + 30.0 * (self.ui.doubleSpinBoxDetectorDistance.value() - 160) / 1000.0)
        self.dataCollector.setParameter("beamY", self.beamOriginY)
        self.dataCollector.setParameter("beamCurrent", self.petraThread.currPetraCurrent)
        self.dataCollector.setParameter("angles", angles)
        
        speed = self.dataCollector.parameters["degreesperframe"] * (1.0 / self.dataCollector.parameters["exposureperiod"])
        totalCollectionTime = totalFrames * (1.5 + (self.dataCollector.parameters["exposureperiod"] / 1000.0))

        self.connect(self.dataCollector, SIGNAL("errorSignal(PyQt_PyObject)"), self.dataCollectionErrorHandler)
        self.connect(self.dataCollector, SIGNAL("logSignal(PyQt_PyObject)"), self.writeToLog)
        self.connect(self.dataCollector, SIGNAL("waitConditionsUpdate()"), self.dataCollectionWaitConditionsUpdate)
        self.connect(self.dataCollector, SIGNAL("onaxisScreeningImage(int)"), self.saveOnaxisImageScreening)
        
        self.dataCollector.start()
        self.showDataCollectionProgressDialog(self.dataCollector.conditionsList)
        self.progressDialog.ui.labelDataCollectionSpeed.setText(("%6.2f " % speed) + chr(176) +"/s")    
        self.progressDialog.ui.labelCollectionTime.setText(self.GetInHMS(totalCollectionTime))    
        self.progressDialog.ui.labelDataCollectionTimeRemaining.setText(self.GetInHMS(totalCollectionTime))    
        self.progressDialog.ui.labelDegreesTotal.setText("%6.2f "%(totalFrames * interval) + chr(176))
        self.progressDialog.ui.labelDataCollectionProgress.setText("Screening in progress")
        self.connect(self.progressDialog.ui.pushButtonStopDataCollection, SIGNAL("clicked()"), self.stopDataCollection_Screening)
        self.updateTimerDataCollectionProgress.start(100)

    def stopDataCollection_Screening(self):
        self.closeShutter(True)
        self.detectorTowerThread.shieldUp()
        self.piezoThread.moveBeamStopOut()
        if self.dataCollectionActive:
            self.writeToLog("Aborting screening...")
            self.dataCollectionActive = False
            self.dataCollector.stop()
        self.dataCollectionActive = False
        self.collectionParametersSet = False
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.stopMotion))
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed,self.defaultGoniospeed))
        self.eigerThread.cmd_q.put(EigerClientCommand(EigerClientCommand.stopAcquisition))
        self.collimatorOut()
        # update calls of data in progressDialog are removed, because dialog is removed in call dataCollectionProgressUpdate(self)
        # due to detected alive = False 
        self.writeToLog("Screening aborted")

    def initMethod_Grid(self):
        # QObject.connect(self.ui.doubleSpinBoxTopLeftX_ISMO,QtCore.SIGNAL("valueChanged(double)"), self.setISMOTopLeftX)
        # QObject.connect(self.ui.doubleSpinBoxTopLeftY_ISMO,QtCore.SIGNAL("valueChanged(double)"), self.setISMOTopLeftY)
        # QObject.connect(self.ui.doubleSpinBoxWidth_ISMO,QtCore.SIGNAL("valueChanged(double)"), self.setISMOWidth)
        # QObject.connect(self.ui.doubleSpinBoxHeight_ISMO,QtCore.SIGNAL("valueChanged(double)"), self.setISMOHeight)
        # QObject.connect(self.ui.doubleSpinBoxStartAngle_Grid, QtCore.SIGNAL("valueChanged(double)"), self.setGridAngle)
        QObject.connect(self.ui.doubleSpinBoxStepsizeX_Grid, QtCore.SIGNAL("valueChanged(double)"),
                        self.setGridStepsizeX)
        QObject.connect(self.ui.doubleSpinBoxStepsizeY_Grid, QtCore.SIGNAL("valueChanged(double)"),
                        self.setGridStepsizeY)
        QObject.connect(self.ui.pushButtonClearGrid_Grid, QtCore.SIGNAL("clicked()"), self.clearGrid)

        self.addPersistentSetting("step_size_x", "grid", "float",
                    "self.ui.doubleSpinBoxStepsizeX_Grid.value",
                    "self.setISMOStepsizeX")
        self.addPersistentSetting("step_size_y", "grid", "float",
                    "self.ui.doubleSpinBoxStepsizeY_Grid.value",
                    "self.setISMOStepsizeY")
        self.addPersistentSetting("exposure_time", "grid", "float",
                    "self.ui.doubleSpinBoxExpTime_Grid.value",
                    "self.ui.doubleSpinBoxExpTime_Grid.setValue")
        self.addPersistentSetting("scan_type", "grid", "int",
                    "self.ui.comboBoxScanType_Grid.currentIndex",
                    "self.ui.comboBoxScanType_Grid.setCurrentIndex")
        self.addPersistentSetting("4m_mode", "grid", "bool",
                    "self.ui.checkBox4M_Grid.isChecked",
                    "self.ui.checkBox4M_Grid.setChecked")
        self.addPersistentSetting("live_view", "grid", "bool",
                    "self.ui.checkBoxLiveView_Grid.isChecked",
                    "self.ui.checkBoxLiveView_Grid.setChecked")
        self.ui.checkBox4M_Grid.hide()
        self.ui.comboBoxScanType_Grid.hide()

    def startDataCollection_Grid(self):
        # The following calls are made to be sure that  pixelsPerUm is properly set and ofsett is 0.
        # otherwise raster will be not properly scanned during attempt of second scan.
        self.raster.raster.setConversion(self.pixelsPerUm)
        self.raster.raster.setOffset(0, 0)
        self.raster.updateRaster()  # every time before start of DataCollector, we need to be sure, that rasterItem is in correct state
        self.ui.graphicsView.update()

        self.setRunnumber_Grid(True)
        filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness + self.petraThread.currentFilter3Thickness
        # filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness
        self.dataCollectionActive = True
        self.dataCollector = GridScreeningCollector(self.detectorTowerThread, self.goniometerThread, self.petraThread,
                                                    self.piezoThread, self.eigerThread, self.raster, self.liveView,
                                                    self.path, parent=self, )
        self.dataCollector.setParameter("filetype", ".cbf")
        self.dataCollector.setParameter("filenumber", 1)
        self.dataCollector.setParameter("exposureperiod", self.ui.doubleSpinBoxExpTime_Grid.value() / 1000.)
        self.dataCollector.setParameter("exposuretime", self.ui.doubleSpinBoxExpTime_Grid.value() / 1000.)
        self.dataCollector.setParameter("detectordistance", self.ui.doubleSpinBoxDetectorDistance.value())
        self.dataCollector.setParameter("4mMode", self.ui.checkBox4M_Grid.isChecked())
        self.dataCollector.setParameter("liveview", self.ui.checkBoxLiveView_Grid.isChecked())
        self.dataCollector.setParameter("pinhole", self.currentPinhole)
        self.dataCollector.setParameter("pinholeDiameter", self.pinholes[self.currentPinhole][2])
        self.dataCollector.setParameter("focus", self.energyThread.beamSizeNames[self.currentFocus])
        self.dataCollector.setParameter("filterTransmission", self.petraThread.currentFilterTransmission)
        self.dataCollector.setParameter("filterThickness", filterThickness)
        self.dataCollector.setParameter("beamX", self.beamOriginX + 30.0 * (
                    self.ui.doubleSpinBoxDetectorDistance.value() - 160) / 1000.0)
        self.dataCollector.setParameter("beamY", self.beamOriginY)
        self.dataCollector.setParameter("beamCurrent", self.petraThread.currPetraCurrent)
        self.dataCollector.setParameter("sampleoutDistanceWhenBeamcheck", self.sampleoutDistanceWhenBeamcheck)

        angle = self.goniometerThread.currentAngle
        self.startAngle = self.goniometerThread.currentAngle
        self.startISMOflexureX = self.goniometerThread.currentPositionFlexureX
        self.startISMOflexureY = self.goniometerThread.currentPositionFlexureY
        self.startISMOgonioY = self.goniometerThread.currentPositionKohzuGoniometerY

        scanPoints = []
        rasterPoints = self.raster.raster.getScanPositions()
        for n in range(len(rasterPoints)):
            x = rasterPoints[n].x()
            incrementY = rasterPoints[n].y()
            deltaX = incrementY * math.sin(math.radians(angle))
            deltaY = incrementY * math.cos(math.radians(angle))
            flexX = self.startISMOflexureX + deltaX
            flexY = self.startISMOflexureY + deltaY
            point = x + self.startISMOgonioY, flexX, flexY
            scanPoints.append(point)
        scanPointsTuple = tuple(scanPoints)
        self.dataCollector.setParameter("scanPoints", scanPointsTuple)
        self.dataCollector.setParameter("rows", self.raster.raster.getPositionsPerColumn())
        self.dataCollector.setParameter("columnss", self.raster.raster.getPositionsPerRow())

        self.connect(self.dataCollector, SIGNAL("errorSignal(PyQt_PyObject)"), self.dataCollectionErrorHandler)
        self.connect(self.dataCollector, SIGNAL("logSignal(PyQt_PyObject)"), self.writeToLog)
        self.connect(self.dataCollector, SIGNAL("waitConditionsUpdate()"), self.dataCollectionWaitConditionsUpdate)
        self.connect(self.dataCollector, SIGNAL("onaxisImage_ISMO()"), self.saveOnaxisImageISMO)
        self.connect(self.dataCollector, SIGNAL("exposureTimeChanged(PyQt_PyObject)"),
                     self.ui.doubleSpinBoxExpTime_Grid.setValue)

        self.dataCollector.start()

        self.showDataCollectionProgressDialog(self.dataCollector.conditionsList)
        # self.progressDialog.ui.labelDataCollectionSpeed.setText(("%6.2f " % speed) + unichr(176) +"/s")
        # self.progressDialog.ui.labelCollectionTime.setText(self.GetInHMS(totalCollectionTime))
        # self.progressDialog.ui.labelDataCollectionTimeRemaining.setText(self.GetInHMS(totalCollectionTime))

        self.progressDialog.ui.labelDataCollectionProgress.setText("Grid scan collection in progress")
        # p = QtCore.QPoint(500,100)
        # self.progressDialog.move(p)
        self.connect(self.progressDialog.ui.pushButtonStopDataCollection, SIGNAL("clicked()"),
                     self.stopDataCollection_Grid)
        self.updateTimerDataCollectionProgress.start(100)

    def stopDataCollection_Grid(self):
        self.closeShutter(True)
        self.detectorTowerThread.shieldUp()
        self.piezoThread.moveBeamStopOut()
        if self.dataCollectionActive:
            self.writeToLog("Aborting Grid scan...")
            self.dataCollectionActive = False
            self.dataCollector.stop()
            self.goniometerThread.setPositionKohzuGoniometerY(self.startISMOgonioY)
            self.goniometerThread.setPositionFlexureX(self.startISMOflexureX)
            self.goniometerThread.setPositionFlexureY(self.startISMOflexureY)
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed, self.defaultGoniospeed))
            self.collimatorOut()
        self.updateTimerDataCollectionProgress.stop()
        self.dataCollectionActive = False
        self.collectionParametersSet = False
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.stopMotion))
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed, self.defaultGoniospeed))
        self.eigerThread.cmd_q.put(EigerClientCommand(EigerClientCommand.stopAcquisition))
        self.collimatorOut()
        if (
                self.progressDialog != None):  # check, since it could be already killed by updateTimerDataCollectionProgress
            self.progressDialog.ui.progressBarDataCollection.setValue(0)
            self.progressDialog.ui.labelDataCollectionTimeRemaining.setText(self.GetInHMS(0))
            self.progressDialog.ui.labelDataCollectionProgress.setText("Data collection aborted")
            self.progressDialog.done(QtGui.QDialog.Accepted)
            self.progressDialog = None
        self.writeToLog("Data collection aborted")

    def initMethod_ISMO(self):
        # QObject.connect(self.ui.doubleSpinBoxTopLeftX_ISMO,QtCore.SIGNAL("valueChanged(double)"), self.setISMOTopLeftX)
        # QObject.connect(self.ui.doubleSpinBoxTopLeftY_ISMO,QtCore.SIGNAL("valueChanged(double)"), self.setISMOTopLeftY)
        # QObject.connect(self.ui.doubleSpinBoxWidth_ISMO,QtCore.SIGNAL("valueChanged(double)"), self.setISMOWidth)
        # QObject.connect(self.ui.doubleSpinBoxHeight_ISMO,QtCore.SIGNAL("valueChanged(double)"), self.setISMOHeight)
        QObject.connect(self.ui.doubleSpinBoxStepsizeX_ISMO, QtCore.SIGNAL("valueChanged(double)"),
                        self.setGridStepsizeX)
        QObject.connect(self.ui.doubleSpinBoxStepsizeY_ISMO, QtCore.SIGNAL("valueChanged(double)"),
                        self.setGridStepsizeY)
        QObject.connect(self.ui.pushButtonClearGrid_ISMO, QtCore.SIGNAL("clicked()"), self.clearGrid)

        self.addPersistentSetting("exposure_time", "ismo", "float",
                    "self.ui.doubleSpinBoxExpTime_ISMO.value",
                    "self.ui.doubleSpinBoxExpTime_ISMO.setValue")
        self.addPersistentSetting("images_per_position", "ismo", "int",
                    "self.ui.spinBoxFramesPerPosition_ISMO.value",
                    "self.ui.spinBoxFramesPerPosition_ISMO.setValue")
        self.addPersistentSetting("oscillation_range", "ismo", "float",
                    "self.ui.doubleSpinBoxOscillationRange_ISMO.value",
                    "self.ui.doubleSpinBoxOscillationRange_ISMO.setValue")
        self.addPersistentSetting("step_size_x", "ismo", "float",
                    "self.ui.doubleSpinBoxStepsizeX_ISMO.value",
                    "self.setGridStepsizeX")
        self.addPersistentSetting("step_size_y", "ismo", "float",
                    "self.ui.doubleSpinBoxStepsizeY_ISMO.value",
                    "self.setGridStepsizeY")
        self.addPersistentSetting("scan_type", "ismo", "int",
                    "self.ui.comboBoxScanType_ISMO.currentIndex",
                    "self.ui.comboBoxScanType_ISMO.setCurrentIndex")
        self.addPersistentSetting("4m_mode", "ismo", "bool",
                    "self.ui.checkBox4M_ISMO.isChecked",
                    "self.ui.checkBox4M_ISMO.setChecked")
        self.addPersistentSetting("live_view", "ismo", "bool",
                    "self.ui.checkBoxLiveView_Grid.isChecked",
                    "self.ui.checkBoxLiveView_Grid.setChecked")
        self.ui.checkBox4M_ISMO.hide()
        self.ui.comboBoxScanType_ISMO.hide()

    def startDataCollection_ISMO(self):
        # The following calls are made to be sure that  pixelsPerUm is properly set and ofsett is 0. 
        # otherwise raster will be not properly scanned during attempt of second scan.
        self.raster.raster.setConversion(self.pixelsPerUm)
        self.raster.raster.setOffset(0,0)
        self.raster.updateRaster()   # every time before start of DataCollector, we need to be sure, that rasterItem is in correct state
        self.ui.graphicsView.update()
        
        self.setRunnumber_ISMO(True)
        filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness + self.petraThread.currentFilter3Thickness
        #filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness
        self.dataCollectionActive = True
        self.dataCollector = ISMOCollector(self.detectorTowerThread, self.goniometerThread, self.petraThread, self.piezoThread, self.eigerThread, self.liveView, self.path, parent=self, )
        self.dataCollector.setParameter("filetype",".cbf")
        self.dataCollector.setParameter("filenumber",1) 
        self.dataCollector.setParameter("exposureperiod",self.ui.doubleSpinBoxExpTime_ISMO.value() / 1000.0)
        self.dataCollector.setParameter("exposuretime",self.ui.doubleSpinBoxExpTime_ISMO.value() / 1000.0)
        self.dataCollector.setParameter("detectordistance",self.ui.doubleSpinBoxDetectorDistance.value())                                                                   
        self.dataCollector.setParameter("4mMode", self.ui.checkBox4M_ISMO.isChecked())
        self.dataCollector.setParameter("liveview", self.ui.checkBoxLiveView_ISMO.isChecked())
        self.dataCollector.setParameter("pinhole", self.currentPinhole)
        self.dataCollector.setParameter("pinholeDiameter", self.pinholes[self.currentPinhole][2])
        self.dataCollector.setParameter("focus", self.energyThread.beamSizeNames[self.currentFocus])
        self.dataCollector.setParameter("filterTransmission", self.petraThread.currentFilterTransmission)
        self.dataCollector.setParameter("filterThickness", filterThickness)
        self.dataCollector.setParameter("beamX", self.beamOriginX + 30.0 * (self.ui.doubleSpinBoxDetectorDistance.value() - 160) / 1000.0)
        self.dataCollector.setParameter("beamY", self.beamOriginY)
        self.dataCollector.setParameter("beamCurrent", self.petraThread.currPetraCurrent)
        self.dataCollector.setParameter("sampleoutDistanceWhenBeamcheck",self.sampleoutDistanceWhenBeamcheck)
        self.dataCollector.setParameter("oscillationrange",self.ui.doubleSpinBoxOscillationRange_ISMO.value())
        self.dataCollector.setParameter("framesperposition",self.ui.spinBoxFramesPerPosition_ISMO.value())

        self.startAngle = self.goniometerThread.currentAngle
        self.startISMOflexureX = self.goniometerThread.currentPositionFlexureX
        self.startISMOflexureY = self.goniometerThread.currentPositionFlexureY
        self.startISMOgonioY = self.goniometerThread.currentPositionKohzuGoniometerY
        
        scanPoints=[]  
        rasterPoints = self.raster.raster.getScanPositions()
        angle = self.goniometerThread.currentAngle
        for n in range(len(rasterPoints)):
            x = rasterPoints[n].x()
            incrementY = rasterPoints[n].y()
            deltaX = incrementY*math.sin(math.radians(angle))
            deltaY = incrementY*math.cos(math.radians(angle))
            flexX = self.startISMOflexureX - deltaX
            flexY = self.startISMOflexureY - deltaY
            print(x, self.startISMOgonioY, self.startISMOflexureX, deltaX, self.startISMOflexureY, deltaY)
            point = x + self.startISMOgonioY, flexX, flexY
            scanPoints.append(point)
        scanPointsTuple = tuple(scanPoints)
        self.dataCollector.setParameter("scanPoints",scanPointsTuple)
        self.dataCollector.setParameter("rows", self.raster.raster.getPositionsPerColumn())
        self.dataCollector.setParameter("columns", self.raster.raster.getPositionsPerRow())

        self.connect(self.dataCollector, SIGNAL("errorSignal(PyQt_PyObject)"), self.dataCollectionErrorHandler)
        self.connect(self.dataCollector, SIGNAL("logSignal(PyQt_PyObject)"), self.writeToLog)        
        self.connect(self.dataCollector, SIGNAL("waitConditionsUpdate()"), self.dataCollectionWaitConditionsUpdate)
        self.connect(self.dataCollector, SIGNAL("onaxisImage_ISMO()"), self.saveOnaxisImageISMO)
        self.connect(self.dataCollector, SIGNAL("exposureTimeChanged(PyQt_PyObject)"), self.ui.doubleSpinBoxExpTime_ISMO.setValue)
        
        self.dataCollector.start()
            
        self.showDataCollectionProgressDialog(self.dataCollector.conditionsList)
        #self.progressDialog.ui.labelDataCollectionSpeed.setText(("%6.2f " % speed) + unichr(176) +"/s")    
        #self.progressDialog.ui.labelCollectionTime.setText(self.GetInHMS(totalCollectionTime))    
        #self.progressDialog.ui.labelDataCollectionTimeRemaining.setText(self.GetInHMS(totalCollectionTime))    

        self.progressDialog.ui.labelDataCollectionProgress.setText("Grid scan collection in progress")
        #p = QtCore.QPoint(500,100)
        #self.progressDialog.move(p)
        self.connect(self.progressDialog.ui.pushButtonStopDataCollection, SIGNAL("clicked()"),
                     self.stopDataCollection_ISMO)
        self.updateTimerDataCollectionProgress.start(100)

    def stopDataCollection_ISMO(self):
        self.closeShutter(True)
        self.detectorTowerThread.shieldUp()
        self.piezoThread.moveBeamStopOut()
        if self.dataCollectionActive:
            self.writeToLog("Aborting Grid scan...")
            self.dataCollectionActive = False
            self.dataCollector.stop()
            self.goniometerThread.setPositionKohzuGoniometerY(self.startISMOgonioY)
            self.goniometerThread.setPositionFlexureX(self.startISMOflexureX)
            self.goniometerThread.setPositionFlexureY(self.startISMOflexureY)
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed,self.defaultGoniospeed))
            self.collimatorOut()
        self.updateTimerDataCollectionProgress.stop()
        self.dataCollectionActive = False
        self.collectionParametersSet = False
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.stopMotion))
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed,self.defaultGoniospeed))
        self.eigerThread.cmd_q.put(EigerClientCommand(EigerClientCommand.stopAcquisition))
        self.collimatorOut()
        if (self.progressDialog != None): # check, since it could be already killed by updateTimerDataCollectionProgress
            self.progressDialog.ui.progressBarDataCollection.setValue(0)
            self.progressDialog.ui.labelDataCollectionTimeRemaining.setText(self.GetInHMS(0))
            self.progressDialog.ui.labelDataCollectionProgress.setText("Data collection aborted")
            self.progressDialog.done(QtGui.QDialog.Accepted)
            self.progressDialog = None
        self.writeToLog("Data collection aborted")

    # --------------  Methods related to the helical scan data collection: ---------------------------
    def initMethod_Helix(self):
        QObject.connect(self.ui.spinBoxNumberOfImages_Helix, QtCore.SIGNAL("valueChanged(int)"), self.helicalScanParameterChanged)
        QObject.connect(self.ui.doubleSpinBoxDegPerFrame_Helix, QtCore.SIGNAL("valueChanged(double)"), self.helicalScanParameterChanged)
        QObject.connect(self.ui.doubleSpinBoxExpTime_Helix, QtCore.SIGNAL("valueChanged(double)"), self.helicalScanParameterChanged)        
        QObject.connect(self.ui.doubleSpinBoxStartAngle_Helix, QtCore.SIGNAL("valueChanged(double)"), self.startAngleHelixChanged)
        self.addPersistentSetting("start_angle", "helix", "float", \
                    "self.ui.doubleSpinBoxStartAngle_Helix.value", \
                    "self.ui.doubleSpinBoxStartAngle_Helix.setValue")
        self.addPersistentSetting("number_of_frames", "helix", "int", \
                    "self.ui.spinBoxNumberOfImages_Helix.value", \
                    "self.ui.spinBoxNumberOfImages_Helix.setValue")
        self.addPersistentSetting("degrees_per_frame", "helix", "float", \
                    "self.ui.doubleSpinBoxDegPerFrame_Helix.value", \
                    "self.ui.doubleSpinBoxDegPerFrame_Helix.setValue")
        self.addPersistentSetting("exposure_time", "helix", "float", \
                    "self.ui.doubleSpinBoxExpTime_Helix.value", \
                    "self.ui.doubleSpinBoxExpTime_Helix.setValue")

    def setPointForHelix(self, pointID):
        # get current positions of the relevant motors:
        
        # Users can be very "quick" and try to press this button earlier, than the pont is
        # really in center. To avoid wrong Points, we insert wait loop:
        while ((self.goniometerThread.proxyKohzuGoniometerY.State() != DevState.ON) or \
               (self.goniometerThread.proxyKohzuGoniometerZ.State() != DevState.ON) or \
               (self.goniometerThread.proxyFlexureX.State() != DevState.ON)  or \
               (self.goniometerThread.proxyFlexureY.State() != DevState.ON)  or \
               (self.goniometerThread.proxyGoniometer.State() != DevState.ON)):
            time.sleep(0.1)
           
        
        self.lastPositionKohzuGoniometerY = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Position").w_value
        self.lastPositionKohzuGoniometerZ = self.goniometerThread.proxyKohzuGoniometerZ.read_attribute("Position").w_value
        self.lastPositionFlexureX = self.goniometerThread.proxyFlexureX.read_attribute("Position").w_value
        self.lastPositionFlexureY = self.goniometerThread.proxyFlexureY.read_attribute("Position").w_value

        
        if (pointID==1):
            # For the point 1 we set the angle just the current value of corresponding device
            
            print("Set Point1")
             
            angle = self.goniometerThread.currentAngle
            angle = angle%360            
            self.ui.doubleSpinBoxStartAngle_Helix.setValue(angle)  # sets the start angle value
            self.helix.p1.gonio.set(angle, self.lastPositionKohzuGoniometerY, self.lastPositionKohzuGoniometerZ,  self.lastPositionFlexureX, self.lastPositionFlexureY)
            self.helix.p1.setPoint()
            # Well, once the point 1 is set, the angle of the pont 2 can be computed:             
            self.helix.p2.gonio.angle = angle + self.ui.spinBoxNumberOfImages_Helix.value() * self.ui.doubleSpinBoxDegPerFrame_Helix.value()
        else: # means point 2
            # For the point 2 we set the angle computed via
            print("Set Point2")
            angle = self.ui.doubleSpinBoxStartAngle_Helix.value() + self.ui.spinBoxNumberOfImages_Helix.value() * self.ui.doubleSpinBoxDegPerFrame_Helix.value()
            self.helix.p2.gonio.set(angle, self.lastPositionKohzuGoniometerY, self.lastPositionKohzuGoniometerZ,  self.lastPositionFlexureX, self.lastPositionFlexureY)
            self.helix.p2.setPoint() 
        
        self.helix.show()    
        self.helicalScanParameterChanged()
        
    def  unSetPointForHelix(self,pointID):
        if (pointID==1):                 
            self.helix.p1.unSet()
        else:
            self.helix.p2.unSet()
        self.helix.hide()
        self.helix.show()    
        self.helicalScanParameterChanged()
        
        
        
    def movePointToBeam(self):
        # It moves the active point of the helix to the beam centre
        # in contrast to the moveToBeam method used onclick event, 
        # the coordinates are taken not from the mouse but from 
        # the active point. 
        # Also, the pi/2 rotation is done every time.
         
        print("Got signal from helix. Move point to beam") 
        
        # get position of active point on the scene:        
        l = self.helix.activePoint.pos()        
        #print("ActivePoint position:", l.x()," ", l.y() )
        print(("pixmapsize :", self.pixmap.size().width()," ", self.pixmap.size().height() ))
                    
        deltaX = l.x() - self.pixmap.size().width() / 2
        deltaY = l.y() - self.pixmap.size().height() / 2
        

#        deltaX = event.pos().x() - self.pixmap.size().width() / 2
#        deltaY = event.pos().y() - self.pixmap.size().height() / 2
        
        
        
        print(("deltaX px", deltaX))
        print(("deltaY px", deltaY))
        
        distanceX = deltaX / self.pixelsPerUm # distance in "real" space in Um to move sample
        distanceY = deltaY / self.pixelsPerUm

        print(("distanceY", distanceX))
        print(("distanceX", distanceY))


        self.moveSample(distanceX, distanceY)
        self.incrementGoniometerPosition(90)
        
        # set positions of both points properly:
        # we need to start here actually threading:
        self.helix.setPosActiveToTheCentre()
        
        #self.tmptimer = QTimer(self) #This one updates GUI elements at a slow rate 
        #self.tmptimer.timeout.connect(self.test)
        #self.tmptimer.start(10000) # do it in 10 sec
        
        
        #self.tmptimer.stop()


                
        #self.ui.graphicsView.update()
        


    def startDataCollectionHelix(self):
        self.setRunnumber()
        filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness + self.petraThread.currentFilter3Thickness        
        #filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness
        startAngle = self.helix.p1.gonio.angle  % 360
        if startAngle < 0.0:
            startAngle += 360.0
        self.helix.p2.gonio.angle = self.helix.p1.gonio.angle + self.ui.spinBoxNumberOfImages_Helix.value() * self.ui.doubleSpinBoxDegPerFrame_Helix.value()   
        
        self.dataCollectionActive = True
        self.dataCollector = HelixDataCollector(self.detectorTowerThread, self.goniometerThread, self.petraThread, self.piezoThread, self.eigerThread, self.liveView, self.path, self.helix)
        self.dataCollector.setParameter("startangle", startAngle)
        self.dataCollector.setParameter("frames", int(self.ui.spinBoxNumberOfImages_Helix.value()))
        self.dataCollector.setParameter("degreesperframe", float(self.ui.doubleSpinBoxDegPerFrame_Helix.value()))
        
        # Note: There are exposure time and exposure period! The time is apparently needed for internal operations of detector
                                                                  
        self.dataCollector.setParameter("exposureperiod", self.ui.doubleSpinBoxExpTime_Helix.value())
        self.dataCollector.setParameter("exposuretime", self.ui.doubleSpinBoxExpTime_Helix.value())
        
        # common for many methods:
        self.dataCollector.setParameter("detectordistance", self.ui.doubleSpinBoxDetectorDistance.value())
        self.dataCollector.setParameter("liveview", True)
        self.dataCollector.setParameter("pinhole", self.currentPinhole)
        self.dataCollector.setParameter("pinholeDiameter", self.pinholes[self.currentPinhole][2])
        self.dataCollector.setParameter("filterTransmission", self.petraThread.currentFilterTransmission)
        self.dataCollector.setParameter("filterThickness", filterThickness)
        self.dataCollector.setParameter("sampleoutDistanceWhenBeamcheck",self.sampleoutDistanceWhenBeamcheck)        
        self.dataCollector.setParameter("takeDirectBeamImage", False)
        self.dataCollector.setParameter("beamX", self.beamOriginX + 30.0 * (self.ui.doubleSpinBoxDetectorDistance.value() - 160) / 1000.0)
        self.dataCollector.setParameter("beamY", self.beamOriginY)
        self.dataCollector.setParameter("beamCurrent", self.petraThread.currPetraCurrent)
        
        stopAngle = self.helix.p2.gonio.angle
        
        print(stopAngle) 

        speed = self.dataCollector.parameters["degreesperframe"] * (1.0 / (self.dataCollector.parameters["exposureperiod"] / 1000.0))
        self.dataCollector.setParameter("speed", speed)
        
        totalCollectionTime = self.ui.spinBoxNumberOfImages_Helix.value() * self.ui.doubleSpinBoxExpTime_Helix.value() / 1000
        
        self.dataCollector.setParameter("totalTime", totalCollectionTime)
        
        #(stopAngle-self.dataCollector.parameters["startangle"]) / speed
        
        self.connect(self.dataCollector, SIGNAL("errorSignal(PyQt_PyObject)"), self.dataCollectionErrorHandler)
        self.connect(self.dataCollector, SIGNAL("logSignal(PyQt_PyObject)"), self.writeToLog)
        self.connect(self.dataCollector, SIGNAL("waitConditionsUpdate()"), self.dataCollectionWaitConditionsUpdate)
        self.connect(self.dataCollector, SIGNAL("onaxisImage()"), self.saveOnaxisImageAuto)
        
        self.dataCollector.start()
        self.showDataCollectionProgressDialog(self.dataCollector.conditionsList)
        self.progressDialog.ui.labelDataCollectionSpeed.setText(("%6.2f " % speed) + chr(176) +"/s")    
        self.progressDialog.ui.labelCollectionTime.setText(self.GetInHMS(totalCollectionTime))    
        self.progressDialog.ui.labelDataCollectionTimeRemaining.setText(self.GetInHMS(totalCollectionTime))    
        self.progressDialog.ui.labelDegreesTotal.setText("%6.2f "%(stopAngle - startAngle) + chr(176))
        self.progressDialog.ui.labelDataCollectionProgress.setText("Data collection in progress")
        self.connect(self.progressDialog.ui.pushButtonStopDataCollection, SIGNAL("clicked()"), self.stopDataCollectionHelix)
        self.updateTimerDataCollectionProgress.start(100)

    def stopDataCollectionHelix(self):
        # the method to stop Helical scan data collection is identical to the stop method for standard data collection.  
        self.stopDataCollection_Std()

    # --------------  end of Methods related to the helical scan data collection: ---------------------------


    def startDataCollectionSX(self):
        if self.lineScanThread is not None:
            print("Stopping linescan")
            self.lineScanThread.stop()
            self.lineScanThread.join()
            print("Linescan stopped")
            self.lineScanThread = None
        self.goniometerThread.stopAllSteppers()
        filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness + self.petraThread.currentFilter3Thickness
        #filterThickness = self.petraThread.currentFilter1Thickness + self.petraThread.currentFilter2Thickness
        self.setRunnumber_SX(True)
        self.dataCollectionActive = True
        self.SXcollector = SerialCollector(self.detectorTowerThread, self.goniometerThread, self.petraThread, self.piezoThread, self.eigerThread, self.liveView, self,filesystem, parent=self)
        self.SXcollector.setParameter("scantype",self.ui.comboBoxScanSelection_SX.currentIndex())
        self.SXcollector.setParameter("scanvelocity",self.ui.doubleSpinBoxLinescanVelocity.value())
        self.SXcollector.setParameter("filetype",".cbf")
        self.SXcollector.setParameter("filenumber",1) 
        self.SXcollector.setParameter("frames",self.ui.spinBoxDataCollectionNumberOfFrames_SX.value())
        self.SXcollector.setParameter("exposuretime",self.ui.doubleSpinBoxDataCollectionExpTime_SX.value())
        self.SXcollector.setParameter("detectordistance",self.ui.doubleSpinBoxDataCollectionDetectorDistance_SX.value())
        self.SXcollector.setParameter("liveview",self.ui.checkBoxAlbulaLiveDisplay_SX.isChecked())
        self.SXcollector.setParameter("pinhole", self.currentPinhole)
        self.SXcollector.setParameter("pinholeDiameter", self.pinholes[self.currentPinhole][2])
        self.SXcollector.setParameter("filterTransmission", self.petraThread.currentFilterTransmission)
        self.SXcollector.setParameter("filterThickness", filterThickness)
        self.SXcollector.setParameter("sampleoutDistanceWhenBeamcheck",self.sampleoutDistanceWhenBeamcheck)
        self.startAngle = self.goniometerThread.currentAngle
        self.startSXgonioY = self.goniometerThread.currentPositionKohzuGoniometerY
        self.startSXgonioZ = self.goniometerThread.currentPositionKohzuGoniometerZ
            
        if self.ui.comboBoxScanSelection_SX.currentIndex() == 1: #Line Scan
            x1 = self.ui.doubleSpinBoxPointX1_SX.value()
            y1 = self.ui.doubleSpinBoxPointY1_SX.value()
            x2 = self.ui.doubleSpinBoxPointX2_SX.value()
            y2 = self.ui.doubleSpinBoxPointY2_SX.value()
            scanPoints=[]
            point1 = x1,y1
            point2 = x2,y2
            scanPoints.append(point1)
            scanPoints.append(point2)
            scanPointsTuple = tuple(scanPoints)
            self.SXcollector.setParameter("scanPoints",scanPointsTuple)
            
        elif self.ui.comboBoxScanSelection_SX.currentIndex() == 2: #Grid Scan
            
            angle = self.goniometerThread.currentAngle
            scanPoints=[]
            
            x1 = self.ui.doubleSpinBoxPointX1_SX.value()
            y1 = self.ui.doubleSpinBoxPointY1_SX.value()
            x2 = self.ui.doubleSpinBoxPointX2_SX.value()
            y2 = self.ui.doubleSpinBoxPointY2_SX.value()
            numPo = self.ui.doubleSpinBoxPointStY_SX.value()
            if numPo < 2: 
                return
            switch = False
            hstep = (y2-y1)/(numPo-1)
            for jj in range(numPo):
                if switch is False:
                    scanPoints.append([x1,y1 + hstep*jj])
                    scanPoints.append([x2,y1 + hstep*jj])
                    switch = True
                else:
                    scanPoints.append([x2,y1 + hstep*jj])
                    scanPoints.append([x1,y1 + hstep*jj])
                    switch = False
    
            scanPointsTuple = tuple(scanPoints)
            self.SXcollector.setParameter("scanPoints",scanPointsTuple)
            
        self.connect(self.SXcollector,SIGNAL("errorSignal(PyQt_PyObject)"),self.dataCollectionErrorHandler)
        self.connect(self.SXcollector,SIGNAL("logSignal(PyQt_PyObject)"),self.writeToLog)
        self.connect(self.SXcollector,SIGNAL("waitConditionsUpdate()"),self.dataCollectionSXwaitConditionsUpdate)
        self.connect(self.SXcollector,SIGNAL("onaxisImage_SX(int)"),self.saveOnaxisImageSX)
        
        self.SXcollector.start()
        
        self.updateTimerDataCollectionSXProgress.start(100)
        self.ui.labelDCdataCollectionProgress_SX.setText("Data collection in progress")
        self.ui.pushButtonDataCollectionStartDataCollection_SX.setEnabled(False)
        self.ui.pushButtonDataCollectionStopDataCollection_SX.setEnabled(True)


    def stopDataCollectionSX(self):
        self.closeShutter(True)
        self.detectorTowerThread.shieldUp()
        self.piezoThread.moveBeamStopOut()
        if self.dataCollectionActive:
            self.writeToLog("Aborting data collection...")
            self.dataCollectionActive = False
            self.SXcollector.stop()
            self.goniometerThread.setPositionKohzuGoniometerY(self.startSXgonioY)
            self.goniometerThread.setPositionKohzuGoniometerZ(self.startSXgonioZ)
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed,self.defaultGoniospeed))
            self.collimatorOut()
        self.updateTimerDataCollectionSXProgress.stop()
        time.sleep(0.2)
        self.ui.labelDCdataCollectionProgress_SX.setText("Data collection idle")
        self.ui.pushButtonDataCollectionStartDataCollection_SX.setEnabled(True)
        self.ui.pushButtonDataCollectionStopDataCollection_SX.setEnabled(False)
        self.ui.labelDataCollectionTimeRemaining_SX.setText(self.GetInHMS(0))
        
        self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusBS1_SX, False)
        self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusDetectorInPosition_SX, False)
        self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusExpParamsSet_SX, False)
        self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusCollInPos_SX, False)
        self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusContrastScreenInPos_SX, False)
        self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusShieldDown_SX, False)
        self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusShutterOpen_SX, False)
        self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusAcqRunning_SX, False)


    def dataCollectionSXProgressUpdate(self):
        try:
            alive = self.SXcollector.alive
        except:
            self.updateTimerDataCollectionSXProgress.stop()
            self.writeToLog("Data collection thread died unexpectedly")
            self.ui.pushButtonDataCollectionStartDataCollection_SX.setEnabled(True)
            self.ui.pushButtonDataCollectionStopDataCollection_SX.setEnabled(False)
            self.goniometerThread.setPositionKohzuGoniometerY(self.startSXgonioY)
            self.goniometerThread.setPositionKohzuGoniometerZ(self.startSXgonioZ)
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed,self.defaultGoniospeed))
            self.piezoThread.moveBeamStopOut()
            self.collimatorOut()
            self.dataCollectionActive = False
            return
        if not alive:
            self.updateTimerDataCollectionSXProgress.stop()
            self.ui.labelDCdataCollectionProgress_SX.setText("Data collection finished")
            self.ui.pushButtonDataCollectionStartDataCollection_SX.setEnabled(True)
            self.ui.pushButtonDataCollectionStopDataCollection_SX.setEnabled(False)
            self.goniometerThread.setPositionKohzuGoniometerY(self.startSXgonioY)
            self.goniometerThread.setPositionKohzuGoniometerZ(self.startSXgonioZ)
            #self.goniometerThread.setPositionFlexureX(self.startSXflexureX)
            #self.goniometerThread.setPositionFlexureY(self.startSXflexureY)
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setSpeed,self.defaultGoniospeed))
            self.ui.progressBarDataCollection_SX.setValue(0)
            self.ui.labelDataCollectionTimeRemaining_SX.setText(self.GetInHMS(0))
            self.piezoThread.moveBeamStopOut()
            self.collimatorOut()
            self.dataCollectionActive = False
        else:    
            timeremaining = self.SXcollector.remainingTime
            progress = int(self.SXcollector.progress)
            self.ui.progressBarDataCollection_SX.setValue(progress)
            self.ui.labelDataCollectionTimeRemaining_SX.setText(self.GetInHMS(timeremaining))
            #self.ui.labelDataCollectionTimeRemaining_SX.setText(self.GetInHMS(0))


    def dataCollectionSXwaitConditionsUpdate(self):
        conditionsList = self.SXcollector.conditionsList
        
        if conditionsList["BS1open"]:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusBS1_SX, True)
        else:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusBS1_SX, False)
        
        if conditionsList["DetectorInPosition"]:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusDetectorInPosition_SX, True)
        else:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusDetectorInPosition_SX, False)
        
        if conditionsList["DetectorThresholdSet"]:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusExpParamsSet_SX, True)
        else:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusExpParamsSet_SX, False)
            
        if conditionsList["CollimatorInPosition"]:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusCollInPos_SX, True)
        else:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusCollInPos_SX, False)
            
        if conditionsList["ContrastScreenInPosition"]:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusContrastScreenInPos_SX, True)
        else:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusContrastScreenInPos_SX, False)
            
        if conditionsList["ShieldDown"]:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusShieldDown_SX, True)
        else:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusShieldDown_SX, False)
        
        if conditionsList["FSopen"]:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusShutterOpen_SX, True)
        else:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusShutterOpen_SX, False)
            
        if conditionsList["CollectionStarted"]:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusAcqRunning_SX, True)
        else:
            self.checkOrUncheck(self.ui.checkBoxDCcollectionStatusAcqRunning_SX, False)


    def dataCollectionErrorHandler(self,error):
        print(error, sys.exc_info())        
        QtGui.QMessageBox.warning(None,"Error",str(error),"&Ok")
        if self.dataCollector is not None: self.dataCollector.stop()
        #if self.SXcollector is not None: self.SXcollector.stop()
        #self.ui.pushButtonDataCollectionStopDataCollection.setEnabled(False)
        #self.ui.pushButtonDCstartScreening.setEnabled(True)
        #self.ui.pushButtonDCstopScreening.setEnabled(False)
        #self.ui.pushButtonDataCollectionStartDataCollection_SX.setEnabled(True)
        #self.ui.pushButtonDataCollectionStopDataCollection_SX.setEnabled(False)
        self.ui.pushButtonStartDataCollection.setEnabled(True)
        #self.ui.pushButtonDataCollectionStopDataCollection_ISMO.setEnabled(False)
        self.writeToLog("Aborting data collection...")
        self.dataCollectionActive = False
        self.closeShutter()

    def setRunnumber(self, force=False):
        self.path.set_user_and_sample_dir(self.ui.lineEditImagePrefix.text())
        self.path.set_run_number_check(
                    "/beamline/beamtime/raw/user/sample/" +
                    "rotational_number/sample_rotational_number_master.h5")
        self.path.inc_run_number()
        self.ui.labelRunNumber.setText(self.path.get_path("number"))
        path = self.path.get_path(
                "/beamline/beamtime/raw/user/sample/rotational_number",
                force=force)
        if path is None:
            self.writeToLog("failed to open run directory")
        else:
            self.ui.labelRunPath.setText(path)

    def setRunnumber_Screening(self, force=False):
        self.path.set_user_and_sample_dir(self.ui.lineEditImagePrefix.text())
        self.path.set_run_number_check(
            "/beamline/beamtime/raw/user/sample/" +
            "screening_number/sample_screening_number_master.h5")
        self.path.inc_run_number()
        self.ui.labelRunNumber.setText(self.path.get_path("number"))
        path = self.path.get_path(
            "/beamline/beamtime/raw/user/sample/screening_number",
            force=force)
        if path is None:
            self.writeToLog("failed to open run directory")
        else:
            self.ui.labelRunPath.setText(path)

    def setRunnumber_Grid(self, force=False):
        self.path.set_user_and_sample_dir(self.ui.lineEditImagePrefix.text())
        self.path.set_run_number_check(
            "/beamline/beamtime/raw/user/sample/" +
            "grid_number/sample_grid_number_master.h5")
        self.path.inc_run_number()
        self.ui.labelRunNumber.setText(self.path.get_path("number"))
        path = self.path.get_path(
            "/beamline/beamtime/raw/user/sample/grid_number",
            force=force)
        if path is None:
            self.writeToLog("failed to open run directory")
        else:
            self.ui.labelRunPath.setText(path)

    def setRunnumber_ISMO(self, force=False):
        self.path.set_user_and_sample_dir(self.ui.lineEditImagePrefix.text())
        self.path.set_run_number_check(
            "/beamline/beamtime/raw/user/sample/" +
            "ismo_number/sample_ismo_number_master.h5")
        self.path.inc_run_number()
        self.ui.labelRunNumber.setText(self.path.get_path("number"))
        path = self.path.get_path(
            "/beamline/beamtime/raw/user/sample/ismo_number",
            force=force)
        if path is None:
            self.writeToLog("failed to open run directory")
        else:
            self.ui.labelRunPath.setText(path)

    #------- End of Data collection functions ---------#


    #------- Start of Pilatus functions ---------#
    def recalculateResolutionLimit(self,newDistance):
        energy = self.petraThread.currentMonoEnergy/1000.
        wavelength = 12.3984/(energy) #in Angstrom
        self.detectorDistance = newDistance
        self.resLimit = wavelength/(2.*math.sin(0.5*math.atan((311./2.)/self.detectorDistance)))
        self.ui.doubleSpinBoxResLimit.setValue(self.resLimit)
        
    def recalculateDetectorDistance(self,newResLimit):
        energy = self.petraThread.currentMonoEnergy/1000.
        wavelength = 12.3984/(energy) #in Angstrom
        self.resLimit = newResLimit
        self.detectorDistance = (311./2.)/(math.tan(2.*math.asin(wavelength/(2.*self.resLimit))))
        self.ui.doubleSpinBoxResLimit.setValue(self.resLimit)
        
    def setResolutionLimit(self,value):
        self.ui.groupBoxDetectorDistanceResolution.blockSignals(True)
        self.ui.doubleSpinBoxResLimit.blockSignals(True)
        
        #formula: d = lambda / 2*sin(0.5*arctan((D/2)/L) source# http://www.xray.bioc.cam.ac.uk/xray_resources/distance-calc/calc.php
        energy = self.petraThread.currentMonoEnergy/1000.
        wavelength = 12.3984/(energy) #in Angstrom
        
        minDetectorDistance = self.ui.doubleSpinBoxDetectorDistance.minimum()
        minResLimit = wavelength/(2.*math.sin(0.5*math.atan((311./2.)/minDetectorDistance)))
        if value < minResLimit:
            QtGui.QMessageBox.warning(self,"Error","Minimum resolution is %5.2f A"%(minResLimit),"&Ok")
            return
        
        self.resLimit = value
        self.detectorDistance = (311./2.)/(math.tan(2*math.asin(wavelength/(2*self.resLimit))))
        
        if self.detectorDistance < self.detectorTowerThread.minPositionDetectorTowerServer+0.1:
            QtGui.QMessageBox.warning(self,"Error","Minimum detector distance is %6.1f"%(self.detectorTowerThread.minPositionDetectorTowerServer+0.1),"&Ok")
            return
        if self.detectorDistance > self.detectorTowerThread.maxPositionDetectorTowerServer-0.1:
            QtGui.QMessageBox.warning(self,"Error","Maximum detector distance is %6.1f"%(self.detectorTowerThread.maxPositionDetectorTowerServer-0.1),"&Ok")
            return
        
        if self.detectorTowerThread.connected:
            if self.detectorTowerThread.stateDetectorTower == "ON":
                self.detectorTowerThread.setPositionDetectorTower(self.detectorDistance)
            else:
                QtGui.QMessageBox.warning(self,"Error","Wait until the detector has stopped moving","&Ok")
        else:
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Detector tower server not running", QtGui.QMessageBox.Ok)
            return
        #self.ui.labelResolutionLimit.setText("%5.2f"%self.resLimit +unichr(197)) 
        
        self.ui.doubleSpinBoxResLimit.setValue(self.resLimit)
        self.ui.doubleSpinBoxDetectorDistance.setValue(self.detectorDistance)
        self.ui.groupBoxDetectorDistanceResolution.blockSignals(False)
        self.ui.doubleSpinBoxResLimit.blockSignals(False)
    
    def setDetectorDistance(self,value):
        self.detectorDistance = value
        self.ui.groupBoxDetectorDistanceResolution.blockSignals(True)
        self.ui.doubleSpinBoxResLimit.blockSignals(True)
        
        #formula: d = lambda / 2*sin(0.5*arctan((D/2)/L) source# http://www.xray.bioc.cam.ac.uk/xray_resources/distance-calc/calc.php
        energy = self.petraThread.currentMonoEnergy/1000.
        wavelength = 12.3984/(energy) #in Angstrom
        
        if self.detectorDistance < self.detectorTowerThread.minPositionDetectorTowerServer+0.1:
            QtGui.QMessageBox.warning(self,"Error","Minimum detector distance is %6.1f"%(self.detectorTowerThread.minPositionDetectorTowerServer+0.1),"&Ok")
            return
        if self.detectorDistance > self.detectorTowerThread.maxPositionDetectorTowerServer-0.1:
            QtGui.QMessageBox.warning(self,"Error","Maximum detector distance is %6.1f"%(self.detectorTowerThread.maxPositionDetectorTowerServer-0.1),"&Ok")
            return
        
        if self.detectorTowerThread.connected:
            if self.detectorTowerThread.stateDetectorTower == "ON":
                try:
                    self.detectorTowerThread.setPositionDetectorTower(self.detectorDistance)
                except:
                    print(sys.exc_info())
            else:
                QtGui.QMessageBox.warning(self,"Error","Wait until the detector has stopped moving","&Ok")
        else:
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Goniometer server not running", QtGui.QMessageBox.Ok)
            return
        
        self.resLimit = wavelength/(2.*math.sin(0.5*math.atan((311./2.)/self.detectorDistance)))
        self.ui.doubleSpinBoxResLimit.setValue(self.resLimit)
        self.ui.doubleSpinBoxDetectorDistance.setValue(self.detectorDistance)
        self.ui.groupBoxDetectorDistanceResolution.blockSignals(False)
        self.ui.doubleSpinBoxResLimit.blockSignals(False)

    def stopDetector(self):
        self.detectorTowerThread.stopDetectorTower()

    def selectFilters(self,index):
        self.writeToLog("setting transmission to " + self.petraThread.filterThicknessList[index])
        self.ui.comboBoxFilterSelection.blockSignals(True)
        self.ui.doubleSpinBoxDesiredTransmission.blockSignals(True)
        self.petraThread.setFilters(self.petraThread.filterThicknessDict[int(self.petraThread.filterThicknessList[index][:-3])])
        self.ui.comboBoxFilterSelection.setCurrentIndex(index)
        self.ui.comboBoxFilterSelection.blockSignals(False)
        self.ui.doubleSpinBoxDesiredTransmission.blockSignals(False)
  
    def selectTransmission(self,value):
        self.writeToLog("setting transmission to %f%%"% value)
        self.ui.doubleSpinBoxDesiredTransmission.blockSignals(True)
        self.petraThread.setFilterTransmission(value)
        self.ui.doubleSpinBoxDesiredTransmission.blockSignals(False)
                    
    def stopFilters(self):
        self.petraThread.stopFilters()

    #-------- Start of goniometer functions ----------#
    def setGoniometerPosition(self,position):
        if self.goniometerThread.connected:
            if self.goniometerThread.stateGoniometer == "ON":
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setAngle, position))
            else:
                #QtGui.QMessageBox.warning(self,"Error","Wait until the axis has stopped moving","&Ok")
                self.goniometerThread.stopMotion()
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setAngle, position))
        else:
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Goniometer server not running", QtGui.QMessageBox.Ok)

    def setGoniometerPositionNoMod(self,position):
        if self.goniometerThread.connected:
            if self.goniometerThread.stateGoniometer == "ON":
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setAngleNoMod, position))
            else:
                #QtGui.QMessageBox.warning(self,"Error","Wait until the axis has stopped moving","&Ok")
                self.goniometerThread.stopMotion()
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setAngleNoMod, position))
        else:
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Goniometer server not running", QtGui.QMessageBox.Ok)

    def setGoniometerPositionReturnKey(self,position):
        #if not self.sxMode:
        #    position = self.ui.doubleSpinBoxSetAngle.value()
        #else:
        #    position = self.ui.doubleSpinBoxSetAngle_SX.value()
        self.setGoniometerPosition(position)
    
    def incrementGoniometerPosition(self,increment):
        if not (0.0 <= increment < 360.0):
            if increment < 0:
                increment = abs(increment)
                increment = increment % 360
                increment = 360 - increment
            else:
                increment = increment % 360
        try:
            currentAngle = self.goniometerThread.proxyGoniometer.read_attribute("Position").value
        except:
            currentAngle = self.goniometerThread.currentAngle
        newAngle = currentAngle + increment
        if not (0.0 <= newAngle < 360.0):
            if newAngle < 0:
                newAngle = abs(newAngle)
                newAngle = newAngle % 360
                newAngle = 360 - newAngle
            else:
                newAngle = newAngle % 360
        self.setGoniometerPosition(newAngle)
    
    def incGoniometer(self):
        angle = float(self.ui.comboBoxAngleIncrement.currentText().rstrip(" °"))
        self.incrementGoniometerPosition(angle)
    
    def decGoniometer(self):
        angle = -float(self.ui.comboBoxAngleIncrement.currentText().rstrip(" °"))
        self.incrementGoniometerPosition(angle)
    
    def stopGoniometer(self):
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.stopMotion))
        
    def homeGoniometer(self):
        self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.homeGoniometer))

    def setStartAngle(self):
        self.ui.doubleSpinBoxDataCollectionStartAngle.setValue(self.goniometerThread.currentAngle)
        
    def rotateWithMouseWheel(self, event):
        try:
            position = self.goniometerThread.proxyGoniometer.read_attribute("Position").value + (
                        event.delta() / 120) * 5
        except:
            position = self.goniometerThread.currentAngle + (event.delta() / 120) * 5
        if str(self.goniometerThread.proxyGoniometer.state()) == "ON":
            self.goniometerThread.setAngle(position)
            #angle = float(self.ui.comboBoxAngleIncrement.currentText().removesuffix('°'))
            #self.incrementGoniometerPosition((event.delta() / 120) * angle)
        super(QtGui.QGraphicsView, self.ui.graphicsView).wheelEvent(event)
    #-------- End of goniometer functions ----------#

    #------- Start of flexure functions--------------#

    def focusPlus(self):
        if self.goniometerThread.connected:
            #if not self.sxMode:
            #    increment = float((self.ui.comboBoxStepSize.currentText()[:-3]))
            #else: 
            #    increment = float((self.ui.comboBoxStepSize_SX.currentText()[:-3]))
            increment = self.currentStepSize
            flexureXposition = self.goniometerThread.currentPositionFlexureX
            flexureYposition = self.goniometerThread.currentPositionFlexureY
            angle = self.goniometerThread.currentAngle
            deltaX = increment*math.cos(math.radians(angle))
            deltaY = increment*math.sin(math.radians(angle))
            
            if self.goniometerThread.stateFlexureX == "ON" and self.goniometerThread.stateFlexureY == "ON":
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, flexureXposition+deltaX))
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, flexureYposition+deltaY))
            else:
                #QtGui.QMessageBox.warning(self,"Error","Wait until the motors have stopped moving","&Ok")
                self.goniometerThread.stopFlexures()
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, flexureXposition+deltaX))
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, flexureYposition+deltaY))
                
        else:
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Goniometer server not running", QtGui.QMessageBox.Ok)
        
    def focusMinus(self):
        if self.goniometerThread.connected:
            #if not self.sxMode:
            #    increment = -float((self.ui.comboBoxStepSize.currentText()[:-3]))
            #else:
            #    increment = -float((self.ui.comboBoxStepSize_SX.currentText()[:-3]))
            increment = -self.currentStepSize
            flexureXposition = self.goniometerThread.currentPositionFlexureX
            flexureYposition = self.goniometerThread.currentPositionFlexureY
            angle = self.goniometerThread.currentAngle
            deltaX = increment*math.cos(math.radians(angle))
            deltaY = increment*math.sin(math.radians(angle))
            
            if self.goniometerThread.stateFlexureX == "ON" and self.goniometerThread.stateFlexureY == "ON":
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, flexureXposition+deltaX))
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, flexureYposition+deltaY))
            else:
                #QtGui.QMessageBox.warning(self,"Error","Wait until the motors have stopped moving","&Ok")
                self.goniometerThread.stopFlexures()
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, flexureXposition+deltaX))
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, flexureYposition+deltaY))
        else:
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Goniometer server not running", QtGui.QMessageBox.Ok)
        
    def incrementFlexure(self,direction):
        if self.goniometerThread.connected:
            #if self.ui.tabWidgetMain.tabText(self.ui.tabWidgetMain.currentIndex()) == "Sample alignment":
            #    if direction == "up":
            #        increment = float((self.ui.comboBoxStepSize.currentText()[:-3]))
            #    else:
            #        increment = -float((self.ui.comboBoxStepSize.currentText()[:-3]))
            #if self.ui.tabWidgetMain.tabText(self.ui.tabWidgetMain.currentIndex()) == "Jet alignment":
            #    if direction == "up":
            #        increment = float((self.ui.comboBoxStepSize_SX.currentText()[:-3]))
            #    else:
            #        increment = -float((self.ui.comboBoxStepSize_SX.currentText()[:-3]))
            #if self.ui.tabWidgetMain.tabText(self.ui.tabWidgetMain.currentIndex()) == "Grid scan alignment":
            #    if direction == "up":
            #        increment = float((self.ui.comboBoxStepSize_ISMO.currentText()[:-3]))
            #    else:
            #        increment = -float((self.ui.comboBoxStepSize_ISMO.currentText()[:-3]))
            if direction == "up":
                increment = self.currentStepSize
            else:
                increment = -self.currentStepSize

               
            flexureXposition = self.goniometerThread.currentPositionFlexureX
            flexureYposition = self.goniometerThread.currentPositionFlexureY
            angle = self.goniometerThread.currentAngle
            deltaX = increment*math.sin(math.radians(angle))
            deltaY = increment*math.cos(math.radians(angle))
            
            if self.goniometerThread.stateFlexureX == "ON" and self.goniometerThread.stateFlexureY == "ON":
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, flexureXposition+deltaX))
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, flexureYposition+deltaY))
            else:
                #QtGui.QMessageBox.warning(self,"Error","Wait until the motors have stopped moving","&Ok")
                self.goniometerThread.stopFlexures()
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, flexureXposition+deltaX))
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, flexureYposition+deltaY))
                
        else:
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Goniometer server not running", QtGui.QMessageBox.Ok)

    def moveFlexuresUpDown(self,increment):
        flexureXposition = self.goniometerThread.currentPositionFlexureX
        flexureYposition = self.goniometerThread.currentPositionFlexureY
        angle = self.goniometerThread.currentAngle
        deltaX = increment*math.sin(math.radians(angle))
        deltaY = increment*math.cos(math.radians(angle))
        
        if self.goniometerThread.stateFlexureX == "ON" and self.goniometerThread.stateFlexureY == "ON":
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, flexureXposition+deltaX))
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, flexureYposition+deltaY))
            #self.goniometerThread.setPositionFlexureX(flexureXposition+deltaX)
            #self.goniometerThread.setPositionFlexureY(flexureYposition+deltaY)
        else:
            #QtGui.QMessageBox.warning(self,"Error","Wait until the motors have stopped moving","&Ok")
            self.goniometerThread.stopFlexures()
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, flexureXposition+deltaX))
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, flexureYposition+deltaY))
            

    def moveFlexureX(self,value):
        newPosition = value
        self.ui.doubleSpinBoxFlexureXposition.setValue(newPosition)
        if self.goniometerThread.stateFlexureX == "ON":
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, newPosition))
            
        else:
            #QtGui.QMessageBox.warning(self,"Error","Wait until the motor has stopped moving","&Ok")
            self.goniometerThread.stopFlexureX()
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, newPosition))
            

    def moveFlexureY(self,value):
        newPosition = value
        self.ui.doubleSpinBoxFlexureYposition.setValue(newPosition)
        if self.goniometerThread.stateFlexureY == "ON":
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, newPosition))
        else:
            #QtGui.QMessageBox.warning(self,"Error","Wait until the motor has stopped moving","&Ok")
            self.goniometerThread.stopFlexureY()
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, newPosition))
            

    def stopFlexure(self):
        if self.goniometerThread.connected:
            #self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.stopFlexure, 0))
            self.goniometerThread.stopFlexure()
            self.goniometerThread.stopAllSteppers()
            
    def resetFlexures(self):
        if self.goniometerThread.connected:
            #self.goniometerThread.setPositionFlexureX(0)
            #self.goniometerThread.setPositionFlexureY(0)
            if self.goniometerThread.stateFlexureX == "ON" and self.goniometerThread.stateFlexureY == "ON":
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, 0))
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, 0))
            else:
                #QtGui.QMessageBox.warning(self,"Error","Wait until the motors have stopped moving","&Ok")
                self.goniometerThread.stopFlexures()
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureX, 0))
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionFlexureY, 0))
                
        else:
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Goniometer server not running", QtGui.QMessageBox.Ok)

    def setPinholePositionY(self,override=False):
        if self.piezoThread.statePinhole == "MOVING":
            #QtGui.QMessageBox.warning(self,"Error","Wait until pinhole motor(s) have stopped moving","&Ok")
            #return
            self.piezoThread.stopPinhole()
            
        if self.dataCollectionActive and not override:
            QtGui.QMessageBox.warning(self,"Error","Cannot move pinhole motor(s). Data collection is active","&Ok")
            return
        self.piezoThread.setPinholePositionY(self.ui.doubleSpinBoxPinholePositionY.value())
    
    def setPinholePositionZ(self,override=False):
        if self.piezoThread.statePinhole == "MOVING":
            #QtGui.QMessageBox.warning(self,"Error","Wait until pinhole motor(s) have stopped moving","&Ok")
            #return
            self.piezoThread.stopPinhole()
        if self.dataCollectionActive and not override:
            QtGui.QMessageBox.warning(self,"Error","Cannot move pinhole motor(s). Data collection is active","&Ok")
            return
        self.piezoThread.setPinholePositionZ(self.ui.doubleSpinBoxPinholePositionZ.value())
        
        
    def setCollimatorPositionY(self,override=False):
        if self.piezoThread.stateCollimator == "MOVING":
            #QtGui.QMessageBox.warning(self,"Error","Wait until collimator motor(s) have stopped moving","&Ok")
            #return
            self.piezoThread.stopCollimator()
        if self.dataCollectionActive and not override:
            QtGui.QMessageBox.warning(self,"Error","Cannot move collimator motor(s). Data collection is active","&Ok")
            return
        self.piezoThread.setCollimatorPositionY(self.ui.doubleSpinBoxCollimatorPositionY.value())
    
    def setCollimatorPositionZ(self,override=False):
        if self.piezoThread.stateCollimator == "MOVING":
            #QtGui.QMessageBox.warning(self,"Error","Wait until collimator motor(s) have stopped moving","&Ok")
            #return
            self.piezoThread.stopCollimator()
        if self.dataCollectionActive and not override:
            QtGui.QMessageBox.warning(self,"Error","Cannot move collimator motor(s). Data collection is active","&Ok")
            return
        self.piezoThread.setCollimatorPositionZ(self.ui.doubleSpinBoxCollimatorPositionZ.value())
        
    #------- End of flexure functions--------------#
    
    #------- Start of Kohzu functions--------------#
    def setIncrementInterval(self, text):
        self.ui.comboBoxStepSize.blockSignals(True)
        self.ui.comboBoxStepSize.lineEdit().setText(text)
        self.ui.comboBoxStepSize.blockSignals(False)
        self.currentStepSize = float((self.ui.comboBoxStepSize.currentText()[:-3]))
        self.ui.doubleSpinBoxKohzuGoniometerX.setSingleStep(self.currentStepSize)
        self.ui.doubleSpinBoxKohzuGoniometerY.setSingleStep(self.currentStepSize)
        self.ui.doubleSpinBoxKohzuGoniometerZ.setSingleStep(self.currentStepSize)
        self.ui.doubleSpinBoxKohzuMicroscopeY.setSingleStep(self.currentStepSize)
        self.ui.doubleSpinBoxKohzuMicroscopeZ.setSingleStep(self.currentStepSize)
        self.ui.doubleSpinBoxFlexureXposition.setSingleStep(self.currentStepSize)
        self.ui.doubleSpinBoxFlexureYposition.setSingleStep(self.currentStepSize)

    def stopAllSteppers(self):
        self.goniometerThread.stopAllSteppers()
    
    def setRotationCenter(self):
        self.goniometerThread.setRotationCenter()
    
    def setKohzuGoniometerX(self,newPosition):
        if self.goniometerThread.stateKohzuGoniometerX == "ON":
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerX, newPosition))
        else:
            QtGui.QMessageBox.warning(self,"Error","Wait until the motor has stopped moving","&Ok")
        
    def setKohzuGoniometerY(self,newPosition):
        if self.goniometerThread.stateKohzuGoniometerY == "ON":
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerY, newPosition))
        else:
            QtGui.QMessageBox.warning(self,"Error","Wait until the motor has stopped moving","&Ok")
        
    def incrementKohzuGoniometerY(self,direction):
        if direction == "left":
            stepsize  = self.currentStepSize
        else:
            stepsize  = -self.currentStepSize

        if self.goniometerThread.stateKohzuGoniometerY == "ON":
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerY, self.goniometerThread.currentPositionKohzuGoniometerY+stepsize))
        else:
            QtGui.QMessageBox.warning(self,"Error","Wait until the motor has stopped moving","&Ok")
    
    def incrementKohzuGoniometerZ(self,direction):
        if direction == "up":
            stepsize  = self.currentStepSize
        else:
            stepsize  = -self.currentStepSize

        if self.goniometerThread.stateKohzuGoniometerZ == "ON":
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerZ, self.goniometerThread.currentPositionKohzuGoniometerZ+stepsize))
        else:
            QtGui.QMessageBox.warning(self,"Error","Wait until the motor has stopped moving","&Ok")
            
    def setKohzuGoniometerZ(self,newPosition):
        if self.goniometerThread.stateKohzuGoniometerZ == "ON":
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerZ, newPosition))
        else:
            QtGui.QMessageBox.warning(self,"Error","Wait until the motor has stopped moving","&Ok")
    
    def setKohzuMicroscopeY(self,newPosition):
        if self.goniometerThread.stateKohzuMicroscopeY == "ON":
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuMicroscopeY, newPosition))
        else:
            QtGui.QMessageBox.warning(self,"Error","Wait until the motor has stopped moving","&Ok")
            
    def setKohzuMicroscopeZ(self,newPosition):
        if self.goniometerThread.stateKohzuMicroscopeZ == "ON":
            self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuMicroscopeZ, newPosition))
        else:
            QtGui.QMessageBox.warning(self,"Error","Wait until the motor has stopped moving","&Ok")
    def resetKohzuYZ(self):
        if self.goniometerThread.connected:
            if self.goniometerThread.stateKohzuGoniometerY == "ON" and self.goniometerThread.stateKohzuGoniometerZ == "ON":
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerY, 0))
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerZ, 0))
            else:
                #QtGui.QMessageBox.warning(self,"Error","Wait until the motors have stopped moving","&Ok")
                self.goniometerThread.stopAllSteppers()
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerY, 0))
                self.goniometerThread.cmd_q.put(ClientCommand(ClientCommand.setPositionKohzuGoniometerZ, 0))
                
        else:
            QtGui.QMessageBox.warning(self, 'ATTENTION',"Goniometer server not running", QtGui.QMessageBox.Ok)
            
    def startLinescan(self):
        if self.lineScanThread is None:
            x1 = self.ui.doubleSpinBoxPointX1_SX.value()
            y1 = self.ui.doubleSpinBoxPointY1_SX.value()
            x2 = self.ui.doubleSpinBoxPointX2_SX.value()
            y2 = self.ui.doubleSpinBoxPointY2_SX.value()
            scanPoints=[]
            point1 = x1,y1
            point2 = x2,y2
            scanPoints.append(point1)
            scanPoints.append(point2)
            scanPointsTuple = tuple(scanPoints)
            velocity = self.ui.doubleSpinBoxLinescanVelocity.value()
            self.lineScanThread = GridScanThread(self.goniometerThread,scanPointsTuple,velocity)
            self.lineScanThread.start()
            self.setExposureTimeSX()             ### dirtyHACK by CFEL XXX
            
        else:
            print("Error starting line scan, thread is already running")
            self.lineScanThread.stop()
            self.lineScanThread = None
            
    def stopLinescan(self):
        if self.lineScanThread is not None:
            self.lineScanThread.stop()
            self.lineScanThread = None
        else:
            print("Error stopping line scan, thread is None")
            pass
            
   #------- End of Kohzu functions------------#
   #------- Start of cryo functions------------#
    def retractCryo(self):
        self.cryoThread.retract()

    def extendCryo(self):
        self.cryoThread.extend()

    def setAnnealInterval(self, text):
        self.ui.comboBoxAnnealTime.blockSignals(True)
        self.ui.comboBoxAnnealTime.lineEdit().setText(text)
        self.ui.comboBoxAnnealTime.blockSignals(False)
        self.annealInterval = float(self.ui.comboBoxAnnealTime.currentText().rstrip("s "))

    def anneal(self):
        if QtGui.QMessageBox.question(None, "Question", "Are you sure?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) ==  QtGui.QMessageBox.Yes:
            self.cryoThread.anneal(self.annealInterval)
    #------- End of cryo functions------------#

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))
    #app.setStyle(QtGui.QStyleFactory.create("Plastique"))
    app.setPalette(QtWidgets.QApplication.style().standardPalette())
    splash_pix = QtGui.QPixmap(os.path.realpath(os.path.dirname(sys.argv[0])) + "/img/splash_loading.png")
    #splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash = QtWidgets.QSplashScreen(splash_pix)
    splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage("\n\n   Importing modules...")
    app.processEvents()
    # Create and display the splash screen
    sys.path.insert(0, os.path.realpath(os.path.dirname(sys.argv[0])) + "/lib")
    os.chdir(os.path.realpath(os.path.dirname(sys.argv[0])))
    from PyQt5.QtCore import QThread, QObject, QTimer, QEvent, Qt
#    from PyQt5.QtWidgets import SIGNAL
    from raster import Raster, RasterItem
    from helix import Helix, HelixDataCollector  # classes for helical scan data collection
    from crystalControlGUI import Ui_CrystalControlGUI
    from beamstopGUI import Ui_Beamstop
    from dataCollectionDialog import Ui_dialogDataCollection
    from goniometerThread import GoniometerThread, ClientCommand
    from cryoThread import CryoThread
    from eigerThread import EigerThread, EigerClientCommand
    from piezoThread import PiezoThread
    from petraThread import PetraThread
    from detectorTowerThread import DetectorTower
    from photonThread import photonThread
    from robotThread import RobotThread
    from dataCollectionThread import DataCollector,ISMOCollector, GridScreeningCollector, ScreeningCollector, SerialCollector
    from energyThread import EnergyThread 
    from simulationDevice import SimulationDevice
    from beamstopCentering import beamstopCentering
    from path import P11Path
    from liveViewThread import LiveView
    from videoThread import VideoThread
    from PyTango import DeviceProxy, DevState
    import subprocess
    import time
    import string
    import random
    import threading
    import configparser
    import random
    import math
    import select
    import datetime
    import hashlib
    import numpy
    from numpy import genfromtxt
    from scipy import interpolate
    import subprocess
    from myOrderedDict import OrderedDict
    import io
    import copy
    from PIL import Image
    from scipy import *
    import scipy.optimize as opt
    from pylab import *
#    import PyQt4.Qwt5 as Qwt
#    from PyQt4.Qwt5.anynumpy import *
    import scanThread
    import copy
    from serialCrystallographyThread import GridScanThread    
        
    splash.showMessage("\n\n   Finished importing modules")
    app.processEvents()
    myapp = StartQT4(splash)
    myapp.show()
    sys.exit(app.exec_())

