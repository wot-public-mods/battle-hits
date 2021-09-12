import Math
import BigWorld

from CurrentVehicle import g_currentPreviewVehicle
from gui.battlehits._constants import SCENE_OFFSET
from gui.battlehits.controllers import AbstractController
from gui.battlehits.events import g_eventsManager
from gui.battlehits.utils import unpackMatrix
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import TankPartNames, TankPartIndexes, TankNodeNames

class Vehicle(AbstractController):

	hangarSpace = dependency.descriptor(IHangarSpace)

	@property
	def vehicleEntity(self):
		if not self.hangarSpace:
			return
		if not self.hangarSpace.space:
			return
		if not self.hangarSpace.space.spaceLoaded():
			return
		return BigWorld.entity(self.hangarSpace.space.vehicleEntityId)

	@property
	def compoundModel(self):
		vehicleEntity = self.vehicleEntity
		if not vehicleEntity:
			return 
		vAppearance = vehicleEntity._ClientSelectableCameraVehicle__vAppearance
		if vAppearance:
			return vAppearance.compoundModel

	@property
	def collision(self):
		vehicleEntity = self.vehicleEntity
		if not vehicleEntity:
			return
		vAppearance = vehicleEntity._ClientSelectableCameraVehicle__vAppearance
		if vAppearance:
			return vAppearance.collisions

	@property
	def compactDescr(self):
		vehicleEntity = self.vehicleEntity
		if vehicleEntity:
			return vehicleEntity.typeDescriptor

	@property
	def isWheeledTech(self):
		if self.compactDescr:
			return self.compactDescr.type.isWheeledVehicle
		return False

	def initialize(self):
		print g_currentPreviewVehicle.onChanged

		self.__components = {}
		self._vehicleStrCD = None
		self._waitingVisible = False
		g_currentPreviewVehicle.onChanged += self._pw_onChanged

	def init(self):
		g_eventsManager.closeMainView += self.__on_closeMainView

	def fini(self):
		self.__components = {}
		g_eventsManager.closeMainView -= self.__on_closeMainView

	def removeVehicle(self):
		g_currentPreviewVehicle.selectNoVehicle()
		self.__components = {}
		self._vehicleStrCD = None

	def __on_closeMainView(self):
		g_currentPreviewVehicle.onChanged -= self._pw_onChanged
		self.removeVehicle()

	def _pw_onChanged(self):

		if not self.stateCtrl.enabled:
			return
		if self.stateCtrl.currentHitID is None:
			return
		if not self.currentBattleData.victim:
			return

		vEntitie = BigWorld.entity(self.hangarSpace.space.vehicleEntityId)
		if not vEntitie:
			return

		print '_pw_onChanged'
		self.__updateComponents()
		self.__updateAppereance()

		g_eventsManager.onVehicleBuilded()

	def loadVehicle(self):
		if not self.currentBattleData.victim:
			self.removeVehicle()
			return

		vehicleCD = self.currentBattleData.victim['compDescr'].type.compactDescr
		vehicleStrCD = self.currentBattleData.victim['compDescrStr']
		print 'loadVehicle'
		if self._vehicleStrCD != vehicleStrCD:
			self._vehicleStrCD = vehicleStrCD
			g_currentPreviewVehicle.selectVehicle(vehicleCD, vehicleStrCD)
			return

		self.__updateComponents()
		self.__updateAppereance()

		g_eventsManager.onVehicleBuilded()

	def __updateAppereance(self):

		if not self.compoundModel:
			return

		matrix = Math.Matrix()
		matrix.setTranslate(SCENE_OFFSET)
		self.compoundModel.matrix = matrix

		turretYaw, gunPitch = self.currentBattleData.hit['aimParts']

		matrix = Math.Matrix()
		matrix.setRotateYPR((turretYaw, 0.0, 0.0))
		self.compoundModel.node(TankPartNames.TURRET, matrix)

		matrix = Math.Matrix()
		matrix.setRotateYPR((0.0, gunPitch, 0.0))
		self.compoundModel.node(TankNodeNames.GUN_INCLINATION, matrix)
		
		# 
		# TODO 
		# set wheels state
		# broken after swap to ingame model builder
		if self.isWheeledTech:
			for nodeName, matrixData in self.currentBattleData.hit['wheels'].iteritems():
				#self.compoundModel.node(nodeName, unpackMatrix(matrixData))
				pass

	def __updateComponents(self):

		aimParts = self.currentBattleData.hit['aimParts']

		hullOffset = self.compactDescr.chassis.hullPosition
		turretOffset = self.compactDescr.hull.turretPositions[0]
		gunOffset = self.compactDescr.turret.gunPosition

		turretYaw, gunPitch = aimParts

		chassisMatrix = Math.Matrix()
		chassisMatrix.setIdentity()
		self.__components[TankPartNames.CHASSIS] = (self.compactDescr.chassis, chassisMatrix, )

		hullMatrix = Math.Matrix()
		hullMatrix.setTranslate(-hullOffset)
		self.__components[TankPartNames.HULL] = (self.compactDescr.hull, hullMatrix, )

		turretMatrix = Math.Matrix()
		turretMatrix.setTranslate(-hullOffset - turretOffset)
		turretRotate = Math.Matrix()
		turretRotate.setRotateY(-turretYaw)
		turretMatrix.postMultiply(turretRotate)
		self.__components[TankPartNames.TURRET] = (self.compactDescr.turret, turretMatrix)

		gunMatrix = Math.Matrix()
		gunMatrix.setTranslate(-gunOffset)
		gunRotate = Math.Matrix()
		gunRotate.setRotateX(-gunPitch)
		gunMatrix.postMultiply(gunRotate)
		gunMatrix.preMultiply(turretMatrix)
		self.__components[TankPartNames.GUN] = (self.compactDescr.gun, gunMatrix)

		hullMatrix.invert()
		turretMatrix.invert()
		gunMatrix.invert()

	def partDescriptor(self, partIndex):
		partName = self.getComponentName(partIndex)
		return self.__components[partName][0]

	def partWorldMatrix(self, partIndex):

		if self.isWheeledTech and partIndex > TankPartIndexes.ALL[-1]:
			 
			def getNodeNameByPartIndex(partIndex):
				wheelNodeNames = self.compactDescr.chassis.generalWheelsAnimatorConfig.getWheelNodeNames()
				wheelNodeLength = len(wheelNodeNames)
				delta = [2, wheelNodeLength, 4, 6]
				result1, result2 = [], []
				for i in range(wheelNodeLength / 2):
					result1.append(wheelNodeLength - delta[i])
					result2.append(wheelNodeLength - delta[i] + 1)
				result = result1 + result2
				return wheelNodeNames[result.index(partIndex)]

			nodeName = getNodeNameByPartIndex(partIndex - len(TankPartIndexes.ALL))

			if self.compoundModel:
				partLocalMatrix = Math.Matrix(self.compoundModel.node(nodeName))
				partWorldMatrix = Math.Matrix()
				partWorldMatrix.translation = partLocalMatrix.translation + SCENE_OFFSET
				return partWorldMatrix

		partName = self.getComponentName(partIndex)

		# in case of vehicle rebuild
		if partName not in self.__components:
			return Math.Matrix()

		partLocalMatrix = Math.Matrix(self.__components[partName][1])
		partWorldMatrix = Math.Matrix()
		partWorldMatrix.setRotateYPR((partLocalMatrix.yaw, partLocalMatrix.pitch, 0.0))
		partWorldMatrix.translation = partLocalMatrix.translation + SCENE_OFFSET
		return partWorldMatrix

	def getComponentName(self, partIndex):
		if partIndex > TankPartIndexes.ALL[-1]:
			return TankPartNames.CHASSIS
		if partIndex in TankPartIndexes.ALL:
			return TankPartIndexes.getName(partIndex)
		return partIndex
