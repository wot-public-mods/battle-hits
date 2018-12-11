
import Math
import BigWorld

from AvatarInputHandler import mathUtils
from gui.Scaleform.Waiting import Waiting
from vehicle_systems.tankStructure import ColliderTypes, ModelsSetParams, ModelStates, TankPartNames, TankPartIndexes, TankNodeNames
from vehicle_systems.model_assembler import prepareCompoundAssembler

from vehicle_systems.stricted_loading import makeCallbackWeak

from gui.battlehits._constants import SCENE_OFFSET
from gui.battlehits.controllers import AbstractController
from gui.battlehits.events import g_eventsManager

class Vehicle(AbstractController):

	@property
	def compoundModel(self):
		return self.__compoundModel
	
	@property
	def collision(self):
		return self.__collision
	
	def __init__(self):
		super(Vehicle, self).__init__()
		self.__currentBuildIndex = 1
		self.__currentCompDescrStr = None
		self.__components = {}
		self.__compoundModel = None
		self.__collision = None
	
	def loadVehicle(self):
		
		if not self.currentBattleData.victim:
			self.removeVehicle()
			return
		
		if self.__currentCompDescrStr != self.currentBattleData.victim['compDescrStr']:

			compactDescr = self.currentBattleData.victim['compDescr']

			Waiting.show('loadHangarSpaceVehicle', isSingle=True, overlapsUI=False)
	
			self.__currentBuildIndex += 1
			
			spaceID = BigWorld.camera().spaceID
			modelsSet = ModelsSetParams('', ModelStates.UNDAMAGED)
			normalAssembler = prepareCompoundAssembler(compactDescr, modelsSet, spaceID)
			
			capsuleScale = Math.Vector3(1.5, 1.5, 1.5)
			gunScale = Math.Vector3(1.0, 1.0, 1.0)
			bspModels = ((TankPartNames.getIdx(TankPartNames.CHASSIS), compactDescr.chassis.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.HULL), compactDescr.hull.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.TURRET), compactDescr.turret.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.GUN), compactDescr.gun.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.GUN) + 1, compactDescr.hull.hitTester.bspModelName, capsuleScale),
				(TankPartNames.getIdx(TankPartNames.GUN) + 2, compactDescr.turret.hitTester.bspModelName, capsuleScale),
				(TankPartNames.getIdx(TankPartNames.GUN) + 3, compactDescr.gun.hitTester.bspModelName, gunScale))
			
			collisionAssembler = BigWorld.CollisionAssembler(bspModels, spaceID)
			loadCallback = makeCallbackWeak(self.__onModelLoaded, self.__currentBuildIndex)
			BigWorld.loadResourceListBG( (normalAssembler, collisionAssembler, ), loadCallback)
			return

		self.__updateComponents()

		self.__updateTurretAndGun()

		g_eventsManager.onVehicleBuilded()
	
	def removeVehicle(self):
		
		self.__components = {}

		self.__currentCompDescrStr = None

		if self.__compoundModel:
			BigWorld.delModel(self.__compoundModel)
		self.__compoundModel = None

		if self.__collision:
			BigWorld.removeCameraCollider(self.__collision.getColliderID())
			self.__collision.deactivate()
			self.__collision.destroy()
		self.__collision = None

	def __onModelLoaded(self, buildInd, resourceRefs):
		
		if buildInd != self.__currentBuildIndex:
			Waiting.hide('loadHangarSpaceVehicle')
			return
		
		self.removeVehicle()
		
		compactDescr = self.currentBattleData.victim['compDescr']
		
		self.__collision = resourceRefs['collisionAssembler']
		self.__compoundModel = resourceRefs[compactDescr.name]
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
		gunLink = mathUtils.MatrixProviders.product(gunoffset, self.compoundModel.node(TankPartNames.GUN))
		collisionData = ((TankPartNames.getIdx(TankPartNames.GUN) + 1, self.compoundModel.node(TankPartNames.HULL)), 
			(TankPartNames.getIdx(TankPartNames.GUN) + 2, self.compoundModel.node(TankPartNames.TURRET)), 
			(TankPartNames.getIdx(TankPartNames.GUN) + 3, gunLink))
		self.collision.connect(0, ColliderTypes.HANGAR_VEHICLE_COLLIDER, collisionData)
		
		self.collision.activate()
	
		BigWorld.appendCameraCollider((self.collision.getColliderID(), (
			TankPartNames.getIdx(TankPartNames.GUN) + 1,
			TankPartNames.getIdx(TankPartNames.GUN) + 2,
			TankPartNames.getIdx(TankPartNames.GUN) + 3
		)))
		
		self.__updateComponents()
		self.__updateTurretAndGun()

		g_eventsManager.onVehicleBuilded()
	
		Waiting.hide('loadHangarSpaceVehicle')

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

		vehicleDescr = self.currentBattleData.victim['compDescr']
		aimParts = self.currentBattleData.hit['aimParts']

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
		