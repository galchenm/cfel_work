import PyTango
from PyQt4.QtCore import SIGNAL, QThread
import random
import os
import time

class SimulationAttribute():
		def __init__(self):
			self.value = random.random()
class SimulationDevice():
		def __init__(self):
			#self.state = "ON"
			self.myattributes = dict()
			self.value = random.random()
		def write_attribute(self,name,value):
			if str(name) in self.myattributes:
				self.myattributes[str(name)] = value
			else:
				self.myattributes.update(dict(name=value))
			if name == "Position":
				pass
				#time.sleep(0.05)
		def read_attribute(self,name):
			if name == "Position":
				print("returning position")
			if str(name) in self.myattributes:
				self.value = self.myattributes[str(name)]
			else:
				self.myattributes.update(dict(name=random.random()))
				
			return SimulationAttribute()
		def state(self):
			return "ON"

class ScanThread2D(QThread):
	def __init__(self, motorY, motorZ, startZ, stepsZ, stopZ, startY, stepsY, stopY, simulation):
		QThread.__init__(self,None)

		self.scanHasStarted = False
		self.startY = startY
		self.stopY = stopY
		self.stepsY = stepsY
		self.startZ = startZ
		self.stopZ = stopZ
		self.stepsZ = stepsZ
		self.simulation = simulation
		
		if simulation:
			self.motorY = SimulationDevice()
			self.motorZ = SimulationDevice()
		else:
			self.motorY = motorY
			self.motorZ = motorZ

		self.positionsY = []
		rangeY = self.stopY - self.startY
		if(self.stepsY < 2):
			self.positionsY.append(rangeY / 2 + self.startY)
		else:
			for i in range(self.stepsY):
				self.positionsY.append((float(i) / (self.stepsY - 1)) * rangeY + self.startY)
		self.positionsZ = []
		rangeZ = self.stopZ - self.startZ
		if(self.stepsZ < 2):
			self.positionsZ.append(rangeZ / 2 + self.startZ)
		else:
			for i in range(self.stepsZ):
				self.positionsZ.append((float(i) / (self.stepsZ - 1)) * rangeZ + self.startZ)

		#print self.positionsY
		#print self.positionsZ
		self.percentDone = 0
		self.numOfSteps = len(self.positionsY) * len(self.positionsZ)
		#print "ScanThread: numofSteps total", self.numOfSteps
		self.running = 0

	def move(self, Y, Z):
		while self.motorY.state() == PyTango.DevState.MOVING:
			time.sleep(0.1)
		while self.motorZ.state() == PyTango.DevState.MOVING:
			time.sleep(0.1)
		time.sleep(0.2)
		self.motorY.write_attribute("Position", Y)
		self.motorZ.write_attribute("Position", Z)
		time.sleep(0.2)
		if not self.simulation:
			while self.motorY.state() == PyTango.DevState.MOVING or \
					self.motorZ.state() == PyTango.DevState.MOVING:
				if not self.running:
					break
				else:
					time.sleep(0.02)
		else:
			time.sleep(0.1)
			
	def run(self):
		self.running = 1
		#if os.path.isfile(self.startAction):
	#		execfile(self.startAction, self.variables)
		self.pos = 0
		revY = True
		revZ = False
		positionsY = []
		positionsZ = list(self.positionsZ)
		positionsZ.reverse()
		while self.motorY.state() == PyTango.DevState.MOVING:
			time.sleep(0.5)
		while self.motorZ.state() == PyTango.DevState.MOVING:
			time.sleep(0.5)
		while self.running:
			#get positions and go there
			if(len(positionsY) == 0):
				revY = not revY
				positionsY = list(self.positionsY)
				if(not revY):
					positionsY.reverse()
				if(len(positionsZ) == 0 and not revZ):
					positionsZ = list(self.positionsZ)
					revZ = True
				elif(len(positionsZ) == 0 and revZ):
					break
				positionZ = positionsZ.pop()
			positionY = positionsY.pop()
			self.move(positionY, positionZ)
			#run action
#			if os.path.isfile(self.shotAction):
				#variables = self.variables
				#variables["pos"] = pos
				#variables["N_pos"] = self.numOfSteps
				#variables["y_req"] = positionY
				#variables["z_req"] = positionZ
				#variables["y_enc"] = self.motorY.read_attribute("Position").value
				#variables["z_enc"] = self.motorZ.read_attribute("Position").value
				#variables["simulation"] = self.simulation
				#print positionY, variables["y_enc"], positionZ, variables["z_enc"]
				#execfile(self.shotAction, variables)
			#self.emit(SIGNAL("newSample(PyQt_PyObject)"),(positionY,positionZ))
			self.pos += 1
			self.percentDone = float(self.pos) * 100. / self.numOfSteps
			self.emit(SIGNAL("shot(int)"),self.pos)
			if self.pos >= self.numOfSteps:
				self.running = False
			
				
				
		#if os.path.isfile(self.stopAction):
			#execfile(self.stopAction, self.variables)
		#self.motorY.write_attribute("ParkingActive", 1)
		#self.motorZ.write_attribute("ParkingActive", 1)

	def stop(self):
		"""Stops the streaming thread.
		
		"""
		self.running = False
		self.wait() # waits until run stops on its own  
