import Math
import BigWorld
import CGF

import math_utils
from cgf_obsolete_script.script_game_object import ComponentDescriptor, ScriptGameObject
from gui.battlehits._constants import SCENE_OFFSET
from gui.battlehits.controllers import AbstractController
from gui.battlehits.events import g_eventsManager
from gui.battlehits.utils import unpackMatrix
from gui.Scaleform.Waiting import Waiting
from vehicle_systems.tankStructure import (ColliderTypes, ModelsSetParams, ModelStates, TankPartNames,
										TankPartIndexes, TankNodeNames)
from vehicle_systems.model_assembler import prepareCompoundAssembler
from vehicle_systems.stricted_loading import makeCallbackWeak


class CollisionObject(ScriptGameObject):

	collision = ComponentDescriptor()

	def __init__(self, spaceID):
		ScriptGameObject.__init__(self, spaceID, 'BattleHitsHangarVehicle')

	# 
	# Fix game crash on mod UI close
	#
	# call GameObject.isValid() on desynced GameObject cause game crash
	# call GameObject.id on desynced GameObject cause AssertionError
	# if we get AssertionError GameObject already not longer available
	#
	def isAvailable(self):
		if self.gameObject:
			try:
				self.gameObject.id
			except AssertionError:
				return False
			return self.gameObject.isValid()
		return False

class Vehicle(AbstractController):

	@property
	def compoundModel(self):
		return self.__compoundModel

	@property
	def collision(self):
		if self.__collision and self.__collision.isAvailable():
			return self.__collision.collision

	@collision.setter
	def collision(self, value):
		if self.__collision and self.__collision.isAvailable() and self.__collision.collision and self.__collision.collision is not None:
			BigWorld.removeCameraCollider(self.__collision.collision.getColliderID())
			self.__collision.removeComponentByType(BigWorld.CollisionComponent)
		self.__collision.collision = value

	@property
	def compactDescr(self):
		return self.currentBattleData.victim.get('compDescr', None)

	@property
	def isWheeledTech(self):
		if self.compactDescr:
			return 'wheeledVehicle' in self.compactDescr.type.tags
		return False

	def __init__(self):
		super(Vehicle, self).__init__()
		self.__currentBuildIndex = 1
		self.__currentCompDescrStr = None
		self.__components = {}
		self.__compoundModel = None
		self.__collision = None

	def initialize(self):
		self.__collision = CollisionObject(BigWorld.camera().spaceID)
		self.__collision.activate()

	def __on_closeMainView(self):
		self.removeVehicle()
		if self.__collision and self.__collision.isAvailable():
			self.__collision.destroy()
		self.__collision = None

	def init(self):
		g_eventsManager.closeMainView += self.__on_closeMainView

	def fini(self):
		if self.__collision and self.__collision.isAvailable():
			self.__collision.destroy()
		self.__compoundModel = None

	def loadVehicle(self):

		if not self.currentBattleData.victim:
			self.removeVehicle()
			return

		if self.__currentCompDescrStr != self.currentBattleData.victim['compDescrStr']:

			Waiting.show('loadHangarSpaceVehicle', isSingle=True, overlapsUI=False)

			self.__currentBuildIndex += 1

			spaceID = BigWorld.camera().spaceID
			modelsSet = ModelsSetParams('', ModelStates.UNDAMAGED, [])
			normalAssembler = prepareCompoundAssembler(self.compactDescr, modelsSet, spaceID)

			capsuleScale = Math.Vector3(1.5, 1.5, 1.5)
			gunScale = Math.Vector3(1.0, 1.0, 1.0)
			bspModels = ((TankPartNames.getIdx(TankPartNames.CHASSIS), self.compactDescr.chassis.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.HULL), self.compactDescr.hull.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.TURRET), self.compactDescr.turret.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.GUN), self.compactDescr.gun.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.GUN) + 1, self.compactDescr.hull.hitTester.bspModelName, capsuleScale),
				(TankPartNames.getIdx(TankPartNames.GUN) + 2, self.compactDescr.turret.hitTester.bspModelName, capsuleScale),
				(TankPartNames.getIdx(TankPartNames.GUN) + 3, self.compactDescr.gun.hitTester.bspModelName, gunScale))

			collisionAssembler = BigWorld.CollisionAssembler(bspModels, spaceID)
			loadCallback = makeCallbackWeak(self.__onModelLoaded, self.__currentBuildIndex)
			self.removeVehicle()
			BigWorld.loadResourceListBG((normalAssembler, collisionAssembler, ), loadCallback)
			return

		self.__updateComponents()
		self.__updateTurretAndGun()
		self.__updateWheels()

		g_eventsManager.onVehicleBuilded()

	def removeVehicle(self):

		self.__components = {}

		self.__currentCompDescrStr = None

		if self.collision:
			BigWorld.removeCameraCollider(self.collision.getColliderID())
			# fix for
			# component already registered
			if self.__collision:
				self.__collision.removeComponentByType(BigWorld.CollisionComponent)
		self.collision = None

		if self.__compoundModel:
			BigWorld.delModel(self.__compoundModel)
			# fix for 
			# Usage of dangling PyModelNodeAdapter is forbidden!
			self.__compoundModel.reset()
		self.__compoundModel = None

	def __onModelLoaded(self, buildInd, resourceRefs):

		if buildInd != self.__currentBuildIndex:
			Waiting.hide('loadHangarSpaceVehicle')
			return

		# in case of vehicle rebuild
		if not self.compactDescr:
			Waiting.hide('loadHangarSpaceVehicle')
			return

		# skip build if target vehicle dont loaded
		if not resourceRefs.has_key(self.compactDescr.name):
			Waiting.hide('loadHangarSpaceVehicle')
			return

		# skip build if collision dont loaded
		if not resourceRefs.has_key('collisionAssembler'):
			Waiting.hide('loadHangarSpaceVehicle')
			return

		self.removeVehicle()

		self.collision = self.__collision.createComponent(BigWorld.CollisionComponent, resourceRefs['collisionAssembler'])
		self.__compoundModel = resourceRefs[self.compactDescr.name]
		self.__currentCompDescrStr = self.currentBattleData.victim['compDescrStr']

		BigWorld.addModel(self.compoundModel)

		m = Math.Matrix()
		m.setTranslate(SCENE_OFFSET)
		self.compoundModel.matrix = m

		# connect VEHICLE_COLLIDER
		chassisColisionMatrix = Math.WGAdaptiveMatrixProvider()
		chassisColisionMatrix.target = self.compoundModel.matrix
		collisionData = ((TankPartNames.getIdx(TankPartNames.HULL), self.compoundModel.node(TankPartNames.HULL)),
			(TankPartNames.getIdx(TankPartNames.TURRET), self.compoundModel.node(TankPartNames.TURRET)),
			(TankPartNames.getIdx(TankPartNames.CHASSIS), chassisColisionMatrix),
			(TankPartNames.getIdx(TankPartNames.GUN), self.compoundModel.node(TankNodeNames.GUN_INCLINATION)))
		self.collision.connect(0, ColliderTypes.VEHICLE_COLLIDER, collisionData)

		# connect HANGAR_VEHICLE_COLLIDER
		gunColBox = self.collision.getBoundingBox(TankPartNames.getIdx(TankPartNames.GUN) + 3)
		center = 0.5 * (gunColBox[1] - gunColBox[0])
		gunoffset = Math.Matrix()
		gunoffset.setTranslate((0.0, 0.0, center.z + gunColBox[0].z))
		gunLink = math_utils.MatrixProviders.product(gunoffset, self.compoundModel.node(TankPartNames.GUN))
		collisionData = ((TankPartNames.getIdx(TankPartNames.GUN) + 1, self.compoundModel.node(TankPartNames.HULL)),
			(TankPartNames.getIdx(TankPartNames.GUN) + 2, self.compoundModel.node(TankPartNames.TURRET)),
			(TankPartNames.getIdx(TankPartNames.GUN) + 3, gunLink))
		self.collision.connect(0, ColliderTypes.HANGAR_VEHICLE_COLLIDER, collisionData)

		BigWorld.appendCameraCollider((self.collision.getColliderID(), (
			TankPartNames.getIdx(TankPartNames.GUN) + 1,
			TankPartNames.getIdx(TankPartNames.GUN) + 2,
			TankPartNames.getIdx(TankPartNames.GUN) + 3
		)))

		self.__updateComponents()
		self.__updateTurretAndGun()
		self.__updateWheels()

		BigWorld.callback(0, g_eventsManager.onVehicleBuilded)

		Waiting.hide('loadHangarSpaceVehicle')

	def __updateWheels(self):

		if not self.compoundModel:
			return

		if not self.isWheeledTech:
			return

		for nodeName, matrixData in self.currentBattleData.hit['wheels'].iteritems():
			self.compoundModel.node(nodeName, unpackMatrix(matrixData))

	def __updateTurretAndGun(self):

		if not self.compoundModel:
			return

		turretYaw, gunPitch = self.currentBattleData.hit['aimParts']

		matrix = Math.Matrix()
		matrix.setRotateYPR((turretYaw, 0.0, 0.0))
		self.compoundModel.node(TankPartNames.TURRET, matrix)

		matrix = Math.Matrix()
		matrix.setRotateYPR((0.0, gunPitch, 0.0))
		self.compoundModel.node(TankNodeNames.GUN_INCLINATION, matrix)

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
				for i in xrange(0, wheelNodeLength / 2):
					result1.append(wheelNodeLength - delta[i])
					result2.append(wheelNodeLength - delta[i] + 1)
				result = result1 + result2
				return wheelNodeNames[result.index(partIndex)]

			nodeName = getNodeNameByPartIndex(partIndex - len(TankPartIndexes.ALL))

			if self.compoundModel:
				partWorldMatrix = Math.Matrix()
				partWorldMatrix.setTranslate(self.compoundModel.node(nodeName).position)
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
