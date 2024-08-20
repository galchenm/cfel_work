# -*- coding: utf-8 -*-
from PyQt4.QtCore import SIGNAL, QThread
from pilatusThread import PilatusClientCommand
from goniometerThread import ClientCommand
import time
class GridScanThread(QThread):
   

    # A thread is started by calling QThread.start() never by calling run() directly!
    def __init__(self, goniometerThread, points, velocity = None, parent = None, scantype = None):
        QThread.__init__(self, parent)
        #self.MainWindow = mainwindowPassing
        print("Gridscan thread: Starting thread")
        self.goniometerThread = goniometerThread
        self.startPositionY = self.goniometerThread.currentPositionKohzuGoniometerY
        self.startPositionZ = self.goniometerThread.currentPositionKohzuGoniometerZ
        
        self.myparent = parent
        self.points = list(points)
        self.startSlewRateY = self.goniometerThread.proxyKohzuGoniometerY.read_attribute("SlewRate").value
        self.startSlewRateZ = self.goniometerThread.proxyKohzuGoniometerZ.read_attribute("SlewRate").value
        if velocity is None:
            return
        if scantype == 1:
            velocity = float(velocity)
            v1 = velocity*self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Conversion").value
            if(self.points[1][0] == self.points[0][0]):
               v2 = 1
            else:
                v2 = abs(self.points[1][1] - self.points[0][1]) / abs(self.points[1][0] - self.points[0][0]) * v1
            if(v1<1.0): v1 = 1
            if(v2<1.0): v2 = 1
            print("velocity:", v1, v2)
            print("velocity:", v1)
            self.goniometerThread.proxyKohzuGoniometerY.write_attribute("SlewRate",int(v1))
            self.goniometerThread.proxyKohzuGoniometerZ.write_attribute("SlewRate",int(v2))
        else:
            velocity = float(velocity)
            v1 = velocity*self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Conversion").value
            self.goniometerThread.proxyKohzuGoniometerY.write_attribute("SlewRate",int(velocity*self.goniometerThread.proxyKohzuGoniometerY.read_attribute("Conversion").value))
            self.goniometerThread.proxyKohzuGoniometerZ.write_attribute("SlewRate",int(velocity*self.goniometerThread.proxyKohzuGoniometerZ.read_attribute("Conversion").value))
            
            
        
    def stop(self):
        print("Gridscan thread: Stopping thread")
        self.alive = False
        time.sleep(0.2)
        print("Gridscan thread: Stopping all steppers in stop()")
        self.goniometerThread.stopAllSteppers()
        time.sleep(0.2)
        
        while self.alive and (self.goniometerThread.stateKohzuGoniometerY == "MOVING" or self.goniometerThread.stateKohzuGoniometerZ == "MOVING"):            
            time.sleep(0.01)
        print("Gridscan thread: All steppers stopped in wait()")
        self.goniometerThread.proxyKohzuGoniometerY.write_attribute("SlewRate",self.startSlewRateY)
        self.goniometerThread.proxyKohzuGoniometerZ.write_attribute("SlewRate",self.startSlewRateZ)
        
        print("Gridscan thread: Moving to start position")
        self.goniometerThread.setPositionKohzuGoniometerY(self.startPositionY)
        self.goniometerThread.setPositionKohzuGoniometerZ(self.startPositionZ)
        while self.alive and (self.goniometerThread.stateKohzuGoniometerY == "MOVING" or self.goniometerThread.stateKohzuGoniometerZ == "MOVING"):
            time.sleep(0.01)
        print("Gridscan thread: In start position")
        
        self.wait() # waits until run stops on his own

    def join(self, timeout=None):
        print("Gridscan thread: join method")
        self.alive = False
        print("Gridscan thread: Stopping all steppers in join()")
        self.goniometerThread.stopAllSteppers()
        time.sleep(0.2)
        
        while self.alive and (self.goniometerThread.stateKohzuGoniometerY == "MOVING" or self.goniometerThread.stateKohzuGoniometerZ == "MOVING"):
            time.sleep(0.1)
        print("Gridscan thread: All steppers stopped in join()")
        self.goniometerThread.proxyKohzuGoniometerY.write_attribute("SlewRate",self.startSlewRateY)
        self.goniometerThread.proxyKohzuGoniometerZ.write_attribute("SlewRate",self.startSlewRateZ)
        
    def run(self):
        self.alive = True
        while self.alive:
            for point in self.points:
                nextPointX = point[0]
                nextPointZ = point[1]
                
                while self.alive and (self.goniometerThread.stateKohzuGoniometerY == "MOVING" or self.goniometerThread.stateKohzuGoniometerZ == "MOVING"):
                    time.sleep(0.01)
                if not self.alive: return
                try:
                    self.goniometerThread.setPositionKohzuGoniometerY(nextPointX)
                    self.goniometerThread.setPositionKohzuGoniometerZ(nextPointZ)
                except:
                    time.sleep(0.5)
                    self.goniometerThread.setPositionKohzuGoniometerY(nextPointX)
                    self.goniometerThread.setPositionKohzuGoniometerZ(nextPointZ)
                if not self.alive: return
                time.sleep(0.2)
                while self.alive and (self.goniometerThread.stateKohzuGoniometerY == "MOVING" or self.goniometerThread.stateKohzuGoniometerZ == "MOVING"):
                    time.sleep(0.01)
                if not self.alive: return

#             self.points.reverse()
#             print "Scanning in negative direction"
#             for point in self.points:
#                 nextPointX = point[0]
#                 nextPointFlexureX = point[1]
#                 nextPointFlexureY = point[2]
#                 while self.alive and (self.goniometerThread.stateFlexureX == "MOVING" or self.goniometerThread.stateFlexureY == "MOVING" or self.goniometerThread.stateKohzuGoniometerY == "MOVING"):
#                     time.sleep(0.01)
#                 try:
#                     self.goniometerThread.setPositionFlexureX(nextPointFlexureX)
#                     self.goniometerThread.setPositionFlexureY(nextPointFlexureY)
#                     self.goniometerThread.setPositionKohzuGoniometerY(nextPointX)
#                 except:
#                     time.sleep(0.5)
#                     self.goniometerThread.setPositionFlexureX(nextPointFlexureX)
#                     self.goniometerThread.setPositionFlexureY(nextPointFlexureY)
#                     self.goniometerThread.setPositionKohzuGoniometerY(nextPointX)
#                 
#                 time.sleep(0.2)
#                 while self.alive and (self.goniometerThread.stateFlexureX == "MOVING" or self.goniometerThread.stateFlexureY == "MOVING" or self.goniometerThread.stateKohzuGoniometerY == "MOVING"):
#                     time.sleep(0.01)
#                 if not self.alive: return