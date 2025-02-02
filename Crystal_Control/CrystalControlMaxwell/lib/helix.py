"""
This package is created to perform Helical Scan using crystalControl software of P11 beamline, DESY
made by Pavel Paulau

The main class is Helix which contains Information about scan parameters, 
and visual representation functions. The Helix class has two members p1 
and p2 of class MyPoint and one member of QGraphicsLineItem 

The MyPoint class has all information about single point and methods of 
visualisation of a single point. It has the member of the GonioParam
class. 

The  GonioParam class is just kind of structure, containing all positions of motors.

The HelixDataCollector(DataCollector) inherits standard Data collection stuff and 
gets Helix object as argument in constructor. So the HelixDataCollector performs scan 

   

""" 

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QThread
import sys, time, math
from dataCollectionThread import DataCollector 
from PyTango import DevState
from math import sin, cos, pi

class HelixDataCollector(DataCollector):
    """
    This class is defined here, not in usual way in dataCollectionThread.py 
    just to separate code, which process Helical Scan from other code in this 
    helix.py modul
    
    The HelixDataCollector could be easily moved into  dataCollectionThread.py 
    but may be better would be to make Data Collection methods  - as members of Helix.
    
    our class is very similar to the standard data collection!!! 
    actually, the only thing, which we must change: add simultaneous linear 
    motion in space during rotation.
    
    To do it, we just inherit DataCollector and override needed functions
    """

    # we override constructor:    
    def __init__(self, detectorTowerThread, goniometerThread, petraThread, piezoThread, pilatusThread, liveViewThread, filesystem, helix, parent = None, simulation = False):
        # we call constructor of parent class        
        DataCollector.__init__(self, detectorTowerThread, goniometerThread, petraThread, piezoThread, pilatusThread, liveViewThread, filesystem)
        self.helix = helix 
        # we need to add some additional parameters to the dictionary of parent object:
        self.parameters["totalTime"] = 0.0        
        self.parameters["speed"] = 0.0 # "angular velocity of phi rotation"
        
        self.parameters["sampleoutDistanceWhenBeamcheck"] = -500.0 # "angular velocity of phi rotation"

        # memorize default (assumed fast or maximal optimal) velocities of motors:        
        self.vMaxX = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("SlewRate").value            
        self.vMaxFlexY = self.goniometerThread.proxyFlexureY.read_attribute("Velocity").value            
        self.vMaxFlexX = self.goniometerThread.proxyFlexureX.read_attribute("Velocity").value            
        self.vMaxSpeedPhi = self.goniometerThread.proxyGoniometer.read_attribute("Velocity").value
        self.convGonioY = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Conversion").value
        
        

    def doMotion(self):
        """
        This method performs linear motion between points p1 and p2 of self.helix object
        and simultaneously rotation of goniometer axis
        
        Note 1: goniometerThread can do something with flexure and tower motors, but not really all, what we need. e.g. set speed etc. 
        In general, it would be good to have "goniometer DeviceServer, who knows all commands, that we need to use"
        self.goniometerThread.startAcquisitionRun(self.parameters["startangle"], stopAngle, speed)
        

        Note 2: in this approximation we neglect the "acceleration phase" of motors and assume it infinite, 
        so that sample moves with constant velocity between the points.            
        This approximation should be generally good for small velocities of motion. 
            
        To take into account acceleration phase, one needs really to start not from the point 1,
        but from the point, which is shifted in direction away from p2 with the time offsets for each motor to 
        be in point 1 simultaneously.
          
        """
        try:
            
            currentOperations = " move sample fast(with default velocities) to the point 1"   # will appear as message in case of exception
            print(currentOperations)
            self.helix.p1.gonio.angle = self.helix.p1.gonio.angle - 0.1
            self.goniometerThread.stopMotion()
            self.moveDiffractometerToPoint(self.helix.p1)
            currentOperations = " wait until motion is complete  "  # will appear as message in case of exception
            print(currentOperations)
            self.waitDiffractometerToComplete()  
        
            currentOperations = " set proper velocities to move sample from the point 1 to the point 2:  "  # will appear as message in case of exception
            # just via v = (x2-x1)/t
            print(currentOperations)
            
            T = self.parameters["totalTime"]
                        
            vGonioY =  abs(self.helix.p2.gonio.PositionKohzuGoniometerY - self.helix.p1.gonio.PositionKohzuGoniometerY) / T  
            vGonioY = self.convGonioY * vGonioY # attention, velocity must be taken with some conversion Factor (defined in constructor, read from DeviceServer)!
            
            vFlexX = abs(self.helix.p2.gonio.PositionFlexureX - self.helix.p1.gonio.PositionFlexureX) / T
            vFlexY = abs(self.helix.p2.gonio.PositionFlexureY - self.helix.p1.gonio.PositionFlexureY) / T
            vSpeedPhi = abs(self.helix.p2.gonio.angle - self.helix.p1.gonio.angle) / T               
            
            self.setDiffractometerVelocities(vGonioY, vFlexX, vFlexY, vSpeedPhi)
            currentOperations = " move the sample from the point 1 to the point 2:  "  # will appear as message in case of exception            
            print(currentOperations)            

            # Immediately after Start of motion, we set "start" acquisition:
            self.goniometerThread.SetPSOcontrolArm(self.helix.p1.gonio.angle, self.helix.p2.gonio.angle) 
            time.sleep(0.1) 
            self.moveDiffractometerToPoint(self.helix.p2)  # start move sample according to defined motion law                        
            
            # The following three parameters are to update a progress bar
            self.goniometerThread.acquisitionTimeStart = time.time()
            self.goniometerThread.acquisitionTimeTotal = self.parameters["totalTime"]
            self.goniometerThread.acquisitionInProgress = True
            
            self.waitDiffractometerToComplete()
            self.setDiffractometerVelocities(self.vMaxX, self.vMaxFlexX, self.vMaxFlexY, self.vMaxSpeedPhi) # set velocities back to default

        except:
            print(sys.exc_info())
            print(("ERROR DURING: ", currentOperations))
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"), currentOperations)            
            self.alive = False
            return

    def moveDiffractometerToPoint(self, p):
        # description:
         
        # for angle = 0, FlexY is vertical dimension.
        # for angle = 90 grad, FlexX is vertical Dimension
        
        self.goniometerThread.setPositionFlexureX(p.gonio.PositionFlexureX)                          
        self.goniometerThread.setPositionFlexureY(p.gonio.PositionFlexureY)
        self.goniometerThread.setPositionKohzuGoniometerY(p.gonio.PositionKohzuGoniometerY)
        self.goniometerThread.setAngle(p.gonio.angle)
        

    def waitDiffractometerToComplete(self):        
        time.sleep(0.1)
        while((self.goniometerThread.proxyFlexureX.state() == DevState.MOVING or \
                self.goniometerThread.proxyFlexureY.state() == DevState.MOVING or \
                self.goniometerThread.proxyKohzuGoniometerY.state() == DevState.MOVING or \
                self.goniometerThread.proxyGoniometer.state() == DevState.MOVING ) and self.alive):
            self.remainingTime = self.goniometerThread.remainingMoveTime
            self.msleep(self.WAIT_CONDITIONS_INTERVAL_NEXTSCANPOINT)
    
    def setDiffractometerVelocities(self, vGoniometerY, vFlexX, vFlexY, speed):
        self.goniometerThread.proxyKohzuGoniometerY.write_attribute("SlewRate", max(vGoniometerY, 1))
        self.goniometerThread.proxyFlexureX.write_attribute("Velocity", max(vFlexX, 0.01))
        self.goniometerThread.proxyFlexureY.write_attribute("Velocity", max(vFlexY, 0.01))
        self.goniometerThread.proxyGoniometer.write_attribute("Velocity", speed)


    def run(self):
        self.prepareRun() # prepareRun is inherited from parent class.
        
        self.dataCollectionActive = True
        #self.remainingTime = self.remainingTime/1000 # now, time in seconds 
                
        
        if(self.err == self.ERR_NO_ERROR):
            self.doMotion() # ... and start acquisition during motion. The key method to move a sample!!!
        
        self.prepareExit() # prepareExit is inherited from parent class.


    def prepareExit(self):
            
        if(self.err == self.ERR_NO_ERROR):
            
            self.dataCollectionActive = True
            if(self.parameters["degreesperframe"] != 0.0):
                self.timerOnaxisImage.start(45000.0/self.parameters["degreesperframe"])
            else:
                self.timerOnaxisImage.start(30000)
            
            #data collection running
            self.preStarted = False
            self.fullStarted = False
            path = self.filesystem.getPath(self.filesystem.FS_ROOT_LOCAL + self.filesystem.FS_SUB_RAW + self.filesystem.FS_TYPE_REGULAR)
            filePre = self.filesystem.getFilename(self.filesystem.FS_TYPE_REGULAR, "{0:05d}".format(self.parameters["autostartXDScbfIndex"]) + self.parameters["filetype"])
            fileFull = self.filesystem.getFilename(self.filesystem.FS_TYPE_REGULAR, "{0:05d}".format(self.parameters["frames"]/2) + self.parameters["filetype"])
            while(True):
                #end reached
                if(self.pilatusThread.statePilatus == "ON"):
                    print("STATE", self.pilatusThread.statePilatus)
                    break
                #abort data collection
                if(self.pilatusThread.statePilatus == "FAULT"):
                    self.breakDataCollection("Data collection error: Pilatus is in FAULT state.")
                    break
                if(not self.alive):
                    self.breakDataCollection("Data collection aborted.")                    
                    break
                if self.parameters["autostartXDS"] and (not self.preStarted) and self.filesystem.checkFileExistence(path + "/" + filePre):
                    print("Starting pre processing")
                    self.startProcessing(True)
                    self.preStarted = True
                #if self.parameters["autostartXDS"] and (not self.fullStarted) and self.filesystem.checkFileExistence(path + "/" + fileFull):
                #    print "Starting full processing"
                #    self.startProcessing()
                #    self.fullStarted = True
                #wait
                self.msleep(250)
                self.remainingTime = self.goniometerThread.remainingMoveTime
                    
            #stop data collection
            self.goniometerThread.stopMotion()
            self.timerOnaxisImage.stop()
            self.dataCollectionActive = False

        elif(self.err > self.ERR_CANCELLED):
            #error
            self.emit(SIGNAL("errorSignal(PyQt_PyObject)"),"Data collection error: "+ str(self.ERR_MSGS[self.err]))
            self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Data collection error: "+ str(self.ERR_MSGS[self.err]))
        self.detectorTowerThread.shieldUp()
        if(self.parameters["autostartXDS"]):
            self.startProcessing()
        if self.parameters["liveview"]:
            self.liveViewThread.stop(3.0)
        print("Data collector thread: Thread for Data collector died")

        self.emit(SIGNAL("logSignal(PyQt_PyObject)"),"Data collection finished.")
        self.alive = False

 

    def breakDataCollection(self, message):
        """ 
        The method  is called in the Abort or Fail cases.  
        In particular we need to Stop all relevant motors.
        In parent class it was only goniometer
        """
                
        self.pilatusThread.stopAcquisition()
        self.goniometerThread.stopMotion()
        
        self.goniometerThread.proxyKohzuGoniometerY.StopMove()        
        self.goniometerThread.proxyFlexureX.Stop()
        self.goniometerThread.proxyFlexureY.Stop()
        
        self.emit(SIGNAL("logSignal(PyQt_PyObject)"), message)
  
    
    
class GonioParam():
    """ just the structure to store the state parameters of Diffractometer(Goniometer): """
    def __init__(self):
        self.angle = None
        self.PositionKohzuGoniometerY = None
        self.PositionKohzuGoniometerZ = None # not used for helix, but used for generality in g etScreenCoordinates 
        self.PositionFlexureX = None
        self.PositionFlexureY = None
    
    def set(self, angle, PositionKohzuGoniometerY, PositionKohzuGoniometerZ, PositionFlexureX, PositionFlexureY): #      
        self.angle = angle
        self.anglerad = angle/360.0*pi*2.0  # for convenience angle in radians
        self.PositionKohzuGoniometerY = PositionKohzuGoniometerY
        self.PositionKohzuGoniometerZ =  PositionKohzuGoniometerZ
        self.PositionFlexureX = PositionFlexureX
        self.PositionFlexureY = PositionFlexureY


class MyPoint(QtGui.QGraphicsItemGroup):
    """ 
    For graphical operation of the Helical Scan Method, we need to manipulate:
        * each of two points independently by setting them up.
        * synchronously during Data Acquisition.
    To do it, it is reasonable to implement class to handle the point.
    
    """
 
    def __init__(self, name, x, y, communicator, parent=None):
        """Initializes the object
        constructor has obligatory arguments:
        name - name of the object
        x, y - coordinates of the point on the scene.
        communicator - object to emit events        
        parent -- optional QGraphicsItem
        """
        QtGui.QGraphicsItem.__init__(self, parent)

        
        # The point is characterized via its position on the scene
        self.posx = x
        self.posy = y 
        
        # we set initially the point into origin of coordinate system of the scene
        x0 = 0
        y0 = 0
        
        # The point will be represented via cross and circle, 
        # since just point would be not good visible. 
        # The circle will have diameter (in pixels):
         
        self.circleWidth = 15 #  
        self.circleHeight = 15
        
        # For the state of point, which has not yet been configured using eg movetobeam method:
        # The following parameter will be true, if Point is initialized to start Data Acquisition
        self.isSet = False 
         
        #pen - QPen that is used to paint the QGraphicsPolygonItem
        #brush - QBrush that is used to paint the QGraphicsPolygonItem
        self.pencross = QtGui.QPen(QtGui.QColor("red")) # cross will be red 
        self.pencircle = QtGui.QPen(QtGui.QColor("blue")) # circle - blue

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        
        self.circleX = x0 - self.circleWidth / 2
        self.circleY = y0 - self.circleHeight / 2

        # circle:        
        self.circle = QtGui.QGraphicsEllipseItem(self.circleX,  self.circleY, self.circleWidth, self.circleHeight) #
        self.circle.setBrush(Qt.red)            
        self.circle.setOpacity(0.2)                        
        self.addToGroup(self.circle)
        
        # cross:        
        self.linex = QtGui.QGraphicsLineItem(x0-5, y0, x0+5, y0)        
        self.addToGroup(self.linex)
        
        self.liney = QtGui.QGraphicsLineItem(x0, y0+5, x0, y0-5)        
        self.addToGroup(self.liney)        
                
        # text label
        font = QtGui.QFont() 
        font.setPixelSize(15);
        font.setBold(True);
        font.setFamily("Calibri");

        self.name = name
        tl = QtGui.QGraphicsTextItem(name)
        tl.setFont(font)
        tl.setPos( QtCore.QPointF (x0-7 , y0-35)) # -35 means above
        self.addToGroup(tl)
        
        # We move the point into coordinates given in constructor:
        self.setPos( self.pos() + QtCore.QPointF (x , y))
        
        # we need to communicate information from this object to other objects,
        # specifically to the object of class Helix
        # to do it, we need method emit() of the class QtCore.QObject
        # therefore we must get communicator object of class QtCore.QObject
        # from the constructor:
         
        self.communicator = communicator 
        
        # parameters of the goniometer device:
        self.gonio = GonioParam()
        
        
    def mousePressEvent(self, event):        
        QtGui.QGraphicsItemGroup.mousePressEvent(self, event) # call method of parent        
        # just call "activated" method of communicator (owner) classs
        self.communicator.emit( SIGNAL("activated"), self)
        
                
    def mouseReleaseEvent(self, event):        
        QtGui.QGraphicsItemGroup.mouseReleaseEvent(self, event) # call method of parent class
        
        #self.setPos(QtCore.QPointF (event.pos().x() , event.pos().y()))
                
        # emit signal, which must be processed by the main program,
        # the movePointToBeam method must be called.
        
        if not self.isSet: 
            self.communicator.emit( SIGNAL("pointMouseReleaseEvent"))
        
    def setPoint(self):               
        self.circle.setBrush(Qt.green)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        self.isSet = True
        self.show()

    def unSet(self):
                
        #self.circle.setBrush(Qt.red)
        #self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.isSet = False
        

class Helix(QtCore.QObject):    
    """
    This class inherits QObject to provide communication with the MyPoint class using emit() 
    the self of Helix is passed as argument to initialize p1 and p2 objects of MyPoint, which are 
    properties of the Helix class.
    
    Not very nice, but it works.
    
    Class to provide parameters for Helical Scan.
    These are basically coordinates of two points:
    p1 - start Point
    p2 - end Point
        
    In practice, we set:
    * two coordinates of centering stage for the point(typically to have the point 
      exactly on axis of phi rotation)
      
    * phi
    
    * ygoniometer motor position - to set the position of the sample in horizontal direction, 
      orthogonal to the X-ray beam.
      
    Note,  the vertical position of goniometer tower is preconfigured separately, so that 
    The rotation axis comes via center of scene! So, that we do not need to take care of this coordinate in our code.
    
    Additionally, we need:
    * speed of linear motion (or the total motion time)
    * angular velocity of rotation
    * exposure time (how many frames must be taken during the scan)
    
    """
    
    def __init__(self, gv, goniometerThread, pixelsPerUm): # 

        QtCore.QObject.__init__(self)
        self.connect(self, SIGNAL("activated"), self.activate)
        
        self.goniometerThread = goniometerThread
        self.gv = gv # to show graphical items on the scene
                        
        # position of the point on 1 the scene:    
        self.p1 = MyPoint("1", 500, 500, self) # group of graphical items for point 1 is returned.
        self.p2 = MyPoint("2", 500, 600, self) # group of graphical items for point 2 is returned.

        # Line, connecting two points:
        # should be also updated in "follow" procedure as well as to setPosActiveToTheCentre
        self.connectingLine = QtGui.QGraphicsLineItem(self.p1.x(), self.p1.y(), self.p2.x(), self.p2.y())
        self.penline = QtGui.QPen(QtGui.QColor("white")) #                
        self.connectingLine.setPen (self.penline)

        # During the stage of setting  data acquisition parameters, the current class
        # has only one active point. Initially, the point 1 is active: 
        self.activePoint = self.p1        
        # mouse click on the  point 2 or 1 makes it "active" 
        # it means, that procedure of setting the point up will 
        # work with the corresponding active point     
        
        
        self.font = QtGui.QFont() 
        self.font.setPixelSize(18);
        self.font.setBold(True);
        self.font.setFamily("Calibri");
        
        # this help message will be shown if points need to be set:
        self.msgUnSet = ""  # no help messages in the working GUI. All goes to documentation files urls 
        
        #      "Initialisation of Parameters for Helical Scan!\n\n" + \
        #      "Please drag the point \"1\" to \n" + \
        #      "a desired position using the mouse \n" + \
        #      "Repeat this operation until \n" + \
        #      "the sample is centered. Afterwards, confirm the choice \n" + \
        #      "of the point via \"set point\" button! \n" + \
        #      "Perform the operations above for the point \"2\"."

        # this help message will be shown if points are properly set:
        self.msgSet = ""
        #      "Ponts are properly set. Ready to start Data Collection!\n\n" + \
        #      "If you want to reset the point \"1\" or the point \"2\" \n" + \
        #      "then click corresponding point with the mouse \n" + \
        #      "and press Unset Point button."                            
              

        
        self.gv.scene().addItem(self.p1)
        self.gv.scene().addItem(self.p2)
        
        self.gv.scene().addItem(self.connectingLine)
        
        

        
        # to get the laboratory coordinates of the point of crystal
        # (which are changed via motion of motors) and to transform 
        # this coordinates into   
        # the screen coordinates, we need following:
                 
        self.pixelsPerUm = pixelsPerUm
        
#        print("================")
        self.yGonioCornerPix = gv.size().width() /2.0  
        self.zGonioCornerPix = gv.size().height() /2.0 
        
        
    def __del__(self): # destructor
        
        print("Destructor Done")
    
    def activate(self, point):
        # This Method just reset active point. 
        # it is connected with mousePressEvent of corresponding MyPoint via emit
        self.activePoint = point

    def moveBy(self, dx, dy):
        # move both points:        
        self.p1.setPos( self.p1.pos() + QtCore.QPointF (dx , dy))        
        self.p2.setPos( self.p2.pos() + QtCore.QPointF (dx , dy))
        
    def setPosActiveToTheCentre(self):
        # The active point must be set into to the center, where the beam will be.
        # We can be in this place of code only, when activePoint.isSet = False
                     
        self.activePoint.setPos(QtCore.QPointF (self.yGonioCornerPix, self.zGonioCornerPix))        
        time.sleep(0.1)
        
        self.connectingLine.setLine(self.p1.x(), self.p1.y(), self.p2.x(), self.p2.y()) # QtGui.QGraphicsLineItem  
        
        # Now try to update positions of both points 
        # if the other (nonactive) point is set, then it will start to adjust its position on the screen 
        #self.startFollow() 


    def follow(self, static = False):
        """
        Updates positions of the points on the screen during motion.
        or during static(=motionless state (once)).        
        """
        
        self.updateScreenCoordinates(self.p1, static)        
        self.updateScreenCoordinates(self.p2, static)
        self.connectingLine.setLine(self.p1.x(), self.p1.y(), self.p2.x(), self.p2.y()) # QtGui.QGraphicsLineItem        
                    

        
    def hide(self):
        """
        We need to hide helical scan points for unrelated tabs
        """
        self.p1.hide()
        self.p2.hide()
        self.connectingLine.hide()
        
        
    def show(self):
        """
        We need to show helical scan points for related tab
        """
        if self.p1.isSet: 
            self.p1.show()
        if self.p2.isSet:                     
            self.p2.show()
            
        if self.p1.isSet and self.p2.isSet:   
            self.connectingLine.show()
        

    def updateScreenCoordinates(self, p, static = False):  
        """
        The selected point p typically belongs to a crystal. 
        During "Set Point" procedure, we define the point 
        in 3D (via Positions of all motors) for a given 
        orientation and position of the crystal.
        
        If we rotate or move the crystal, then the selected point p 
        moves  in 3D too. The point p gets new coordinates in 
        laboratory reference frame.
        
        The purpose of this function is to return the current screen coordinates of the point p.
        
        The optional boolean argument "static" is responsible for getting coordinates during motion or
        during static (=motionless) state.
        
        If the current positions of all motors of the diffractometer are equal to the positions of the point p, 
        then we must see the point p in the centre.
        Otherwise, one needs to adjust position on the screen, taking into account, current positions of the diffractometer. 
        
        Every point in space can be defined via 3 coordinates, e.g. in Cartesian reference frame.
        As the laboratory reference frame it is natural to chose the reference frame of goniometer 
        tower motors. 
        The origin of the frame is the point where the camera would look to, if gonioy = 0 and gonioz = 0. (goniox=0)
        
        We omit gonio in following and call coordinates just (x,y,z)
               
        To make projection of any point onto the plane, we need to know the distance from the plane to camera. 
        We do not know it exactly, but it has order of 10^5 mum. Which is much higher, than vertical and horizontal 
        sizes of our samples (max around 300mum). So, the good first approximation is to consider camera distance = infinity.
        
        Then, every point with coordinates (x, y, z) would be projected onto the plane x=0 to the point:
        (y, z). (for infinite distance to camera, otherwise must be adjusted).
                
        """
        #print(self.pixelsPerUm)
        if p.isSet: # it will be done only if the point is set
            
            #The coordinates of the point p in 3D during Set Point(initial coordinates):            
            self.y = p.gonio.PositionKohzuGoniometerY # horizonthal dimension
            self.z = p.gonio.PositionKohzuGoniometerZ + p.gonio.PositionFlexureX * sin(p.gonio.anglerad)  + p.gonio.PositionFlexureY * cos(p.gonio.anglerad) # vertical dimension
            
            """ 
            if we move the sample, we also move the  point p. 
            We want now to move the point p on the screen together with the sample. 
            
            To do it, we need the current positions of motors and according coordinates in laboratory reference frame of the central point of the screen:
            """
            if static:
                self.currentAngleRad = self.goniometerThread.proxyGoniometer.read_attribute("Position").w_value/360.0*pi*2.0
                self.currentPositionFlexureX = self.goniometerThread.proxyFlexureX.read_attribute("Position").w_value #.value
                self.currentPositionFlexureY = self.goniometerThread.proxyFlexureY.read_attribute("Position").w_value #.value        
                self.currentPositionKohzuGoniometerY = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Position").w_value #.value
                self.currentPositionKohzuGoniometerZ = self.goniometerThread.proxyKohzuGoniometerZ.read_attribute("Position").w_value # .value
            else:
                self.currentAngleRad = self.goniometerThread.proxyGoniometer.read_attribute("Position").value/360.0*pi*2.0
                self.currentPositionFlexureX = self.goniometerThread.proxyFlexureX.read_attribute("Position").value #.value
                self.currentPositionFlexureY = self.goniometerThread.proxyFlexureY.read_attribute("Position").value #.value        
                self.currentPositionKohzuGoniometerY = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Position").value #.value
                self.currentPositionKohzuGoniometerZ = self.goniometerThread.proxyKohzuGoniometerZ.read_attribute("Position").value # .value
        
            ## uff. 
            # the point is assumed to be in centre of rotation, therefore, eg, changing phi angle only, the point
            # must stay in the centre. 
            
            # To take it into account, we actually need the "difference" in the flexure positions:   
            dflexX = self.currentPositionFlexureX - p.gonio.PositionFlexureX
            dflexY = self.currentPositionFlexureY - p.gonio.PositionFlexureY
            dgonioZ = self.currentPositionKohzuGoniometerZ - p.gonio.PositionKohzuGoniometerZ  
            
            # the current position  of the point in the center of the screen (in the laboratory reference frame) is:
            y_curr = self.currentPositionKohzuGoniometerY 
            z_curr = self.z + dgonioZ + dflexX * sin(self.currentAngleRad)  + dflexY * cos(self.currentAngleRad) # vertical dimension
    
            # the position of the point relative to the current center point is        
            dy = y_curr - self.y
            dz = z_curr - self.z
            
            # then, the position of the selected point relative to current point is :
            y_sc = self.yGonioCornerPix - dy * self.pixelsPerUm
            z_sc = self.zGonioCornerPix - dz * self.pixelsPerUm
                    
            
            # We must transform no mus into pixels:
            y_sc = y_sc  
            z_sc = z_sc 
            
            pp = QtCore.QPointF (y_sc, z_sc)
            
            # an put the point into new position on the screen:
            p.setPos(pp)
        
    def setPixelsPerUm(self, pixelsPerUm):
        self.pixelsPerUm = pixelsPerUm
