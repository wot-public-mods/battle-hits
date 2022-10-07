import Math
import BigWorld

from gui.shared.gui_items.Vehicle import Vehicle as VehicleItem
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from VehicleEffects import DamageFromShotDecoder
from vehicle_outfit.outfit import Outfit
from vehicle_systems.tankStructure import TankPartNames, TankPartIndexes, TankNodeNames

from .._constants import SCENE_OFFSET
from ..controllers import AbstractController
from ..events import g_eventsManager
from ..utils import simplifyVehicleCompactDescr, cancelCallbackSafe

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
		return self.hangarSpace.space.getVehicleEntity()

	@property
	def compoundModel(self):
		vEntity = self.vehicleEntity
		if not vEntity:
			return 
		vAppearance = vEntity.appearance
		if vAppearance:
			return vAppearance.compoundModel

	@property
	def collision(self):
		vEntity = self.vehicleEntity
		if not vEntity:
			return
		vAppearance = vEntity._ClientSelectableCameraVehicle__vAppearance
		if vAppearance:
			return vAppearance.collisions

	@property
	def compactDescr(self):
		vEntity = self.vehicleEntity
		if vEntity:
			return vEntity.typeDescriptor

	@property
	def isWheeledTech(self):
		if self.compactDescr:
			return self.compactDescr.type.isWheeledVehicle
		return False

	def initialize(self):
		self._components = {}
		self._vehicleStrCD = None
		self._presentCBID = None
		self.hangarSpace.onVehicleChanged += self._onVehicleChanged

	def init(self):
		g_eventsManager.closeMainView += self.__on_closeMainView

	def fini(self):
		g_eventsManager.closeMainView -= self.__on_closeMainView
		self._components = {}
		self._presentCBID = None
		self._vehicleStrCD = None

	def removeVehicle(self):
		self.hangarSpace.removeVehicle()
		if self._presentCBID is not None:
			cancelCallbackSafe(self._presentCBID)
			self._presentCBID = None
		self._components = {}
		self._presentCBID = None
		self._vehicleStrCD = None

	def __on_closeMainView(self):
		self.hangarSpace.onVehicleChanged -= self._onVehicleChanged
		self.removeVehicle()

	def _onVehicleChanged(self):
		self.onVehicleChanged()
		if not self.vehicleEntity:
			BigWorld.callback(.1, self.onVehicleChanged)

	def onVehicleChanged(self):

		if not self.stateCtrl.enabled:
			return
		if self.stateCtrl.currentHitID is None:
			return
		if not self.currentBattleData.victim:
			return

		vEntity = self.vehicleEntity
		if not vEntity or not vEntity.typeDescriptor:
			return

		compDescrStr = vEntity.typeDescriptor.makeCompactDescr()
		self._vehicleStrCD = simplifyVehicleCompactDescr(compDescrStr)

		self.__updateAppereance()
		self.__updateComponents()
		BigWorld.callback(.0, g_eventsManager.onVehicleBuilded)

		if self._presentCBID is not None:
			cancelCallbackSafe(self._presentCBID)
			self._presentCBID = None
		self._presentCBID = BigWorld.callback(.1, self._presentCallback)

	def loadVehicle(self):
		if not self.currentBattleData.victim:
			self.removeVehicle()
			return
		vehicleStrCD = simplifyVehicleCompactDescr(self.currentBattleData.victim['compDescrStr'])
		if self._vehicleStrCD != vehicleStrCD:
			vehicle, outfit = VehicleItem(strCompactDescr=vehicleStrCD), Outfit()
			self.hangarSpace.updatePreviewVehicle(vehicle, outfit)
		else:
			self._presentCallback()

	def _presentCallback(self):
		self._presentCBID = None
		if not self.currentBattleData.hit:
			return
		if not self.stateCtrl.enabled:
			return
		if not self.compoundModel:
			self._presentCBID = BigWorld.callback(.1, self._presentCallback)
			return
		self.__updateAppereance()
		self.__updateComponents()
		g_eventsManager.onVehicleBuilded()

	def __updateAppereance(self):
		if not self.compoundModel:
			return
		if not self.currentBattleData.hit:
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

	def __updateComponents(self):

		if not self.currentBattleData.hit:
			return

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
		partName = self.__getPartName(partIndex)

		if partName in self._components:
			localMatrix = self._components[partName]
			rotation = Math.Matrix()
			rotation.setRotateYPR((localMatrix.yaw, localMatrix.pitch, 0.0))
			result = Math.Matrix()
			result.setTranslate(localMatrix.translation + SCENE_OFFSET)
			result.preMultiply(rotation)
			return result

		if self.compoundModel and self.isWheeledTech and partIndex > TankPartIndexes.ALL[-1]:
			worldMatrix = Math.Matrix(self.compoundModel.node(partName))
			result = Math.Matrix()
			result.setTranslate(worldMatrix.translation)
			return result

		result = Math.Matrix()
		result.setTranslate(SCENE_OFFSET)
		return result

	def __getPartName(self, partIndex):

		if partIndex in TankPartIndexes.ALL:
			return TankPartIndexes.getName(partIndex)

		tracksConfig = self.compactDescr.chassis.tracks
		if tracksConfig is not None:
			return DamageFromShotDecoder.convertComponentIndex(partIndex, self.compactDescr)

		wheelsConfig = self.compactDescr.chassis.generalWheelsAnimatorConfig
		if wheelsConfig is not None:
			partIndex -= len(TankPartIndexes.ALL)
			wheelNodeNames = wheelsConfig.getWheelNodeNames()
			wheelNodeLength = len(wheelNodeNames)
			delta = [2, wheelNodeLength, 4, 6]
			result1, result2 = [], []
			for i in range(wheelNodeLength / 2):
				result1.append(wheelNodeLength - delta[i])
				result2.append(wheelNodeLength - delta[i] + 1)
			result = result1 + result2
			return wheelNodeNames[result.index(partIndex)]

		return partIndex
