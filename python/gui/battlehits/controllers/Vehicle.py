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
		self._vehicleStrCD = None
		self._waitingVisible = False
		g_currentPreviewVehicle.onChanged += self._preview_onChanged

	def init(self):
		g_eventsManager.closeMainView += self.__on_closeMainView

	def fini(self):
		g_eventsManager.closeMainView -= self.__on_closeMainView

	def removeVehicle(self):
		g_currentPreviewVehicle.selectNoVehicle()
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

	def partWorldMatrix(self, partIndex):
		result = Math.Matrix()
		result.translation = SCENE_OFFSET
		if not self.compoundModel:
			return result
		if self.isWheeledTech and partIndex > TankPartIndexes.ALL[-1]:
			nodeName = self.getComponentName(partIndex)
			worldMatrix = Math.Matrix(self.compoundModel.node(nodeName))
			result.translation = worldMatrix.translation
		else:
			nodeName = self.getComponentName(partIndex)
			worldMatrix = Math.Matrix(self.compoundModel.node(nodeName))
			result.setRotateYPR((worldMatrix.yaw, worldMatrix.pitch, 0.0))
			result.translation = worldMatrix.translation
		if result.translation.y < SCENE_OFFSET.y / 2:
			result.translation = worldMatrix.translation + SCENE_OFFSET
		return result

	def getComponentName(self, partIndex):
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
