import Math
import BigWorld

from CurrentVehicle import g_currentPreviewVehicle
from gui.battlehits._constants import SCENE_OFFSET
from gui.battlehits.controllers import AbstractController
from gui.battlehits.events import g_eventsManager
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
		self._components = {}
		self._vehicleStrCD = None
		g_currentPreviewVehicle.onChanged += self._preview_onChanged

	def init(self):
		g_eventsManager.closeMainView += self.__on_closeMainView

	def fini(self):
		g_eventsManager.closeMainView -= self.__on_closeMainView
		self._components = {}
		self._vehicleStrCD = None

	def removeVehicle(self):
		g_currentPreviewVehicle.selectNoVehicle()
		self._components = {}
		self._vehicleStrCD = None

	def __on_closeMainView(self):
		g_currentPreviewVehicle.onChanged -= self._preview_onChanged
		self.removeVehicle()

	def _preview_onChanged(self):

		if not self.stateCtrl.enabled:
			return
		if self.stateCtrl.currentHitID is None:
			return
		if not self.currentBattleData.victim:
			return

		vEntitie = BigWorld.entity(self.hangarSpace.space.vehicleEntityId)
		if not vEntitie:
			return

		self.__updateAppereance()
		self.__updateComponents()
		BigWorld.callback(.0, g_eventsManager.onVehicleBuilded)

	def loadVehicle(self):
		if not self.currentBattleData.victim:
			self.removeVehicle()
			return

		vehicleCD = self.currentBattleData.victim['compDescr'].type.compactDescr
		vehicleStrCD = self.currentBattleData.victim['compDescrStr']
		if self._vehicleStrCD != vehicleStrCD:
			self._vehicleStrCD = vehicleStrCD
			g_currentPreviewVehicle.selectVehicle(vehicleCD, vehicleStrCD)
			return

		self.__updateAppereance()
		self.__updateComponents()
		BigWorld.callback(.0, g_eventsManager.onVehicleBuilded)

	def __updateAppereance(self):

		if not self.compoundModel:
			return

		matrix = Math.Matrix()
		matrix.setRotateYPR((0.0, 0.0, 0.0))
		matrix.translation = SCENE_OFFSET
		self.compoundModel.matrix = matrix

		turretYaw, gunPitch = self.currentBattleData.hit['aimParts']

		matrix = Math.Matrix()
		matrix.setRotateYPR((turretYaw, 0.0, 0.0))
		self.compoundModel.node(TankPartNames.TURRET, matrix)

		matrix = Math.Matrix()
		matrix.setRotateYPR((0.0, gunPitch, 0.0))
		self.compoundModel.node(TankNodeNames.GUN_INCLINATION, matrix)

		# TODO - set wheels state
		# UPDATE - we dont need this, bcs collision always same, wheel YPR its only local visual 

	def __updateComponents(self):

		aimParts = self.currentBattleData.hit['aimParts']

		hullOffset = self.compactDescr.chassis.hullPosition
		turretOffset = self.compactDescr.hull.turretPositions[0]
		gunOffset = self.compactDescr.turret.gunPosition

		turretYaw, gunPitch = aimParts

		chassisMatrix = Math.Matrix()
		chassisMatrix.setIdentity()
		self._components[TankPartNames.CHASSIS] = chassisMatrix

		hullMatrix = Math.Matrix()
		hullMatrix.setTranslate(-hullOffset)
		self._components[TankPartNames.HULL] = hullMatrix

		turretMatrix = Math.Matrix()
		turretMatrix.setTranslate(-hullOffset - turretOffset)
		turretRotate = Math.Matrix()
		turretRotate.setRotateY(-turretYaw)
		turretMatrix.postMultiply(turretRotate)
		self._components[TankPartNames.TURRET] = turretMatrix

		gunMatrix = Math.Matrix()
		gunMatrix.setTranslate(-gunOffset)
		gunRotate = Math.Matrix()
		gunRotate.setRotateX(-gunPitch)
		gunMatrix.postMultiply(gunRotate)
		gunMatrix.preMultiply(turretMatrix)
		self._components[TankPartNames.GUN] = gunMatrix

		hullMatrix.invert()
		turretMatrix.invert()
		gunMatrix.invert()

	def partWorldMatrix(self, partIndex):
		defMatrix = Math.Matrix()
		defMatrix.setTranslate(SCENE_OFFSET)

		partName = self.__getPartName(partIndex)
		if partName == partIndex:
			return defMatrix

		if self.compoundModel and self.isWheeledTech and partIndex > TankPartIndexes.ALL[-1]:
			worldMatrix = Math.Matrix(self.compoundModel.node(partName))
			result = Math.Matrix()
			result.setTranslate(worldMatrix.translation)
			return result

		if partName not in self._components:
			return defMatrix

		if not self.isWheeledTech and partIndex <= TankPartIndexes.ALL[-1]:
			localMatrix = self._components[partName]
			rotation = Math.Matrix()
			rotation.setRotateYPR((localMatrix.yaw, localMatrix.pitch, 0.0))
			result = Math.Matrix()
			result.setTranslate(localMatrix.translation + SCENE_OFFSET)
			result.preMultiply(rotation)
			return result

		return defMatrix

	def __getPartName(self, partIndex):
		if partIndex in TankPartIndexes.ALL:
			return TankPartIndexes.getName(partIndex)
		if partIndex > TankPartIndexes.ALL[-1]:
			partIndex -= len(TankPartIndexes.ALL)
			wheelNodeNames = self.compactDescr.chassis.generalWheelsAnimatorConfig.getWheelNodeNames()
			wheelNodeLength = len(wheelNodeNames)
			delta = [2, wheelNodeLength, 4, 6]
			result1, result2 = [], []
			for i in range(wheelNodeLength / 2):
				result1.append(wheelNodeLength - delta[i])
				result2.append(wheelNodeLength - delta[i] + 1)
			result = result1 + result2
			return wheelNodeNames[result.index(partIndex)]
		return partIndex
