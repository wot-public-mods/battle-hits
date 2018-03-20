
from AvatarInputHandler import mathUtils
import BigWorld
import Math
import math
from vehicle_systems.tankStructure import ModelStates, TankPartNames, TankPartIndexes, TankNodeNames
from gui.battlehits._constants import SCENE_OFFSET

class Vehicle(object):

	def __init__(self):
		self.__components = {}
	
	def init(self):
		pass

	def fini(self):
		pass
	
	def setVehicleData(self, vehicleDescr, aimParts):
		
		hullOffset = vehicleDescr.chassis.hullPosition
		turretOffset = vehicleDescr.hull.turretPositions[0]
		gunOffset = vehicleDescr.turret.gunPosition
		
		turretYaw, gunPitch = aimParts

		chassisMatrix = Math.Matrix()
		chassisMatrix.setIdentity()
		self.__components[TankPartNames.CHASSIS] = (vehicleDescr.chassis, chassisMatrix, )
		
		hullMatrix = Math.Matrix()
		hullMatrix.setTranslate(-hullOffset)
		self.__components[TankPartNames.HULL] = (vehicleDescr.hull, hullMatrix, )

		turretMatrix = Math.Matrix()
		turretMatrix.setTranslate(-hullOffset - turretOffset)
		turretRotate = Math.Matrix()
		turretRotate.setRotateY(-turretYaw)
		turretMatrix.postMultiply(turretRotate)
		self.__components[TankPartNames.TURRET] = (vehicleDescr.turret, turretMatrix)

		gunMatrix = Math.Matrix()
		gunMatrix.setTranslate(-gunOffset)
		gunRotate = Math.Matrix()
		gunRotate.setRotateX(-gunPitch)
		gunMatrix.postMultiply(gunRotate)
		gunMatrix.preMultiply(turretMatrix)
		self.__components[TankPartNames.GUN] = (vehicleDescr.gun, gunMatrix)
		
		hullMatrix.invert()
		turretMatrix.invert()
		gunMatrix.invert()

	def partDescriptor(self, partName):
		partName = self.getComponentName(partName)
		return self.__components[partName][0]
		
	def partLocalMatrix(self, partName):
		partName = self.getComponentName(partName)
		partLocalMatrix = Math.Matrix(self.__components[partName][1])
		return partLocalMatrix

	def partWorldMatrix(self, partName):
		partName = self.getComponentName(partName)
		partLocalMatrix = Math.Matrix(self.__components[partName][1])
		partWorldMatrix = Math.Matrix()
		partWorldMatrix.setRotateYPR((partLocalMatrix.yaw, partLocalMatrix.pitch, 0.0))
		partWorldMatrix.translation = partLocalMatrix.translation + SCENE_OFFSET
		return partWorldMatrix
	
	def getComponentName(self, partIndex):
		if partIndex in TankPartIndexes.ALL:
			return TankPartIndexes.getName(partIndex)
		return partIndex
		