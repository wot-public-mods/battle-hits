
from AvatarInputHandler import mathUtils
import BigWorld
import Math
import math
from debug_utils import LOG_ERROR
from gui.Scaleform.Waiting import Waiting
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import ColliderTypes, ModelStates, TankPartNames, TankNodeNames, ModelsSetParams
from vehicle_systems.model_assembler import prepareCompoundAssembler
from vehicle_systems.stricted_loading import makeCallbackWeak

from gui.battlehits.events import g_eventsManager
from gui.battlehits._constants import MODEL_TYPES, MODEL_PATHS, SETTINGS, SCENE_OFFSET, CAMERA_DEFAULTS
from gui.battlehits.controllers import IController
from gui.battlehits.skeletons import ISettings, IHangarCamera, IVehicle

class HangarScene(IController):

	hangarSpace = dependency.descriptor(IHangarSpace)
	hangarCameraCtrl = dependency.descriptor(IHangarCamera)
	settingsCtrl = dependency.descriptor(ISettings)
	vehicleCtrl = dependency.descriptor(IVehicle)
	
	def __init__(self):
		super(HangarScene, self).__init__()
		
		# data
		self.__curBuildInd = 1
		self.__rootPosition = SCENE_OFFSET
		self.__preCompDescrStr = None
		self.__forceCameraUpdate = False
		
		# resources
		self.collision = None
		self.compoundModel = None

		self.__domeModel = None

		self.__shellModels = []
		self.__effectModels = []
		self.__splashModels = []
		self.__ricochetModels = []

		self.__effectMotors = []
		self.__splashMotors = []
		self.__shellMotors = []
		self.__ricochetMotors = []
	
	def fini(self):
		self.destroy()
	
	def create(self):
	
		self.hangarSpace.onSpaceCreate -= self.create
		g_eventsManager.onChangedBattleData += self.__onBattleChanged
		g_eventsManager.onChangedHitData += self.__onHitChanged
		g_eventsManager.onSettingsChanged += self.__onSettingsChanged
		
		self.assambleModels()
		
		self.hangarCameraCtrl.setCameraData(*CAMERA_DEFAULTS)
		
		self.__forceCameraUpdate = True

		g_eventsManager.showUI()

		self.__loadVehicle()
	
	def assambleModels(self):
		
		currentStyle = self.settingsCtrl.get(SETTINGS.CURRENT_STYLE)
		currentSpaceID = BigWorld.camera().spaceID

		self.__domeModel = BigWorld.Model(MODEL_PATHS.DOME)
		self.__domeModel.position = self.__rootPosition
		BigWorld.addModel(self.__domeModel, currentSpaceID)
		
		SHELL_SET = (self.__shellModels, self.__shellMotors, MODEL_TYPES.SHELL, MODEL_PATHS.SHELL)
		EFFECT_SET = (self.__effectModels, self.__effectMotors, MODEL_TYPES.EFFECT, MODEL_PATHS.EFFECT)
		SPLASH_SET = (self.__splashModels, self.__splashMotors, MODEL_TYPES.SPLASH, MODEL_PATHS.SPLASH)
		RICOCHET_SET = (self.__ricochetModels, self.__ricochetMotors, MODEL_TYPES.RICOCHET, MODEL_PATHS.RICOCHET)

		for (models, motors, modelTypes, modelPath) in (SHELL_SET, EFFECT_SET, SPLASH_SET, RICOCHET_SET):
			del models[:], motors[:]
			for modelType in modelTypes:
				model = BigWorld.Model(modelPath % (currentStyle, modelType))
				motor = BigWorld.Servo(Math.Matrix())
				model.addMotor(motor)
				models.append(model)
				motors.append(motor)
				model.castsShadow = model.visible = False
				BigWorld.addModel(model, currentSpaceID)
	
	def freeModels(self, freeTankModel = True, withResources = False):
		
		for model in self.__shellModels + self.__splashModels + self.__ricochetModels + self.__effectModels:
			model.visible = False
		
		if freeTankModel:
			
			self.__preCompDescrStr = None

			if self.compoundModel:
				BigWorld.delModel(self.compoundModel)
			self.compoundModel = None

			if self.collision:
				BigWorld.removeCameraCollider(self.collision.getColliderID())
				self.collision.deactivate()
				self.collision.destroy()
			self.collision = None

		if withResources:
			
			if self.__domeModel:
				if self.__domeModel in BigWorld.models():
					BigWorld.delModel(self.__domeModel)
				self.__domeModel = None
			
			SHELL_SET = (self.__shellModels, self.__shellMotors)
			EFFECT_SET = (self.__effectModels, self.__effectMotors)
			SPLASH_SET = (self.__splashModels, self.__splashMotors)
			RICOCHET_SET = (self.__ricochetModels, self.__ricochetMotors)
			
			for (models, motors, ) in (SHELL_SET, EFFECT_SET, SPLASH_SET, RICOCHET_SET):
				for model in models:
					if model in BigWorld.models():
						BigWorld.delModel(model)
				del models[:], motors[:]
	
	def noDataHit(self):
		self.freeModels(freeTankModel=True)
		self.__preCompDescrStr = None
		self.hangarCameraCtrl.setCameraData(*CAMERA_DEFAULTS)
	
	def destroy(self):
		self.freeModels(withResources=True)
		g_eventsManager.onChangedBattleData -= self.__onBattleChanged
		g_eventsManager.onChangedHitData -= self.__onHitChanged
		g_eventsManager.onSettingsChanged -= self.__onSettingsChanged
	
	def __onBattleChanged(self):
		self.freeModels()
	
	def __onHitChanged(self):
		
		if not self.currentBattleData.victim:
			self.freeModels(freeTankModel=True)
			self.hangarCameraCtrl.setCameraData(*CAMERA_DEFAULTS)
			return
		
		if self.__preCompDescrStr != self.currentBattleData.victim['compDescrStr']:
			self.freeModels()
		
		self.__loadVehicle()
	
	def __onSettingsChanged(self, key, value):
		
		if key == SETTINGS.CURRENT_STYLE:
			self.freeModels(freeTankModel=False)
			self.assambleModels()
			self.__loadVehicle()
	
	def __loadVehicle(self):
		
		if not self.currentBattleData.victim:
			return
		
		compactDescr = self.currentBattleData.victim['compDescr']
		compactDescrStr = self.currentBattleData.victim['compDescrStr']
		aimParts = self.currentBattleData.hit['aimParts']
		
		self.vehicleCtrl.setVehicleData(vehicleDescr = compactDescr, aimParts = aimParts)

		if self.__preCompDescrStr != compactDescrStr:
			
			Waiting.show('loadHangarSpaceVehicle', isSingle=True, overlapsUI=False)

			self.__curBuildInd += 1

			spaceID = BigWorld.camera().spaceID
			
			normalAssembler = prepareCompoundAssembler(compactDescr, ModelsSetParams('', ModelStates.UNDAMAGED), spaceID)
			
			capsuleScale = Math.Vector3(2.0, 2.0, 2.0)
			gunScale = Math.Vector3(1.0, 1.0, 1.0)
			bspModels = ((TankPartNames.getIdx(TankPartNames.CHASSIS), compactDescr.chassis.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.HULL), compactDescr.hull.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.TURRET), compactDescr.turret.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.GUN), compactDescr.gun.hitTester.bspModelName),
				(TankPartNames.getIdx(TankPartNames.GUN) + 1, compactDescr.hull.hitTester.bspModelName, capsuleScale),
				(TankPartNames.getIdx(TankPartNames.GUN) + 2, compactDescr.turret.hitTester.bspModelName, capsuleScale),
				(TankPartNames.getIdx(TankPartNames.GUN) + 3, compactDescr.gun.hitTester.bspModelName, gunScale))
			
			collisionAssembler = BigWorld.CollisionAssembler(bspModels, spaceID)
			BigWorld.loadResourceListBG( (normalAssembler, collisionAssembler, ), makeCallbackWeak(self.__onModelLoaded, self.__curBuildInd) )

			self.__preCompDescrStr = compactDescrStr
		else:
			self.__updateTurretAndGun()
			self.__updateHitPoints()
		
		
		if not self.currentBattleData.hit:
			return
		
		self.__updateCamera()
		self.__updateShell()
		self.__updateEffect()
		self.__updateSplash()
		self.__updateRicochet()

	def __onModelLoaded(self, buildInd, resourceRefs):
		
		if buildInd != self.__curBuildInd:
			Waiting.hide('loadHangarSpaceVehicle')
			return
		
		if self.collision:
			BigWorld.removeCameraCollider(self.collision.getColliderID())
			self.collision.deactivate()
			self.collision.destroy()
		self.collision = resourceRefs['collisionAssembler']
	
		if self.compoundModel:
			BigWorld.delModel(self.compoundModel)
		
		compactDescr = self.currentBattleData.victim['compDescr']
		
		self.compoundModel = resourceRefs[compactDescr.name]
		
		BigWorld.addModel(self.compoundModel)
		
		m = Math.Matrix()
		m.setTranslate(self.__rootPosition)
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

		colliderData = (self.collision.getColliderID(), (TankPartNames.getIdx(TankPartNames.GUN) + 1, TankPartNames.getIdx(TankPartNames.GUN) + 2, TankPartNames.getIdx(TankPartNames.GUN) + 3))
		BigWorld.appendCameraCollider(colliderData)
		
		self.__updateTurretAndGun()
		self.__updateHitPoints()
		
		Waiting.hide('loadHangarSpaceVehicle')

	def __updateCamera(self):
		
		hitData = self.currentBattleData.hit
		
		if hitData['isExplosion']:
			
			fallenPoint = self.__rootPosition + Math.Vector3(hitData['position'])
			worldHitDirection = self.__rootPosition - fallenPoint
			
			targetPoint = fallenPoint + Math.Vector3(0.0, (self.__rootPosition - fallenPoint).length / 2.0, 0.0)
			
			# default, current, limits, sens, targetPoint
			self.hangarCameraCtrl.setCameraData(
				(mathUtils.reduceToPI(worldHitDirection.yaw), -math.radians(25.0)),
				(mathUtils.reduceToPI(worldHitDirection.yaw), -math.radians(25.0), 10.0),
				(None, math.radians(20.0), (5.0, 15.0)),
				(0.005, 0.005, 0.001),
				targetPoint,
				self.__forceCameraUpdate
			)
		else:
			
			componentIDx, _, startPoint, endPoint = hitData['points'][0]
			
			worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(componentIDx)
			
			worldStartPoint = worldComponentMatrix.applyPoint(startPoint)
			worldEndPoint = worldComponentMatrix.applyPoint(endPoint)
			
			worldHitDirection = worldEndPoint - worldStartPoint
			
			# default, current, limits, sens, targetPoint
			self.hangarCameraCtrl.setCameraData(
				(worldHitDirection.yaw, -worldHitDirection.pitch),
				(worldHitDirection.yaw + 0.2, -worldHitDirection.pitch, 4.0),
				(math.radians(35.0), math.radians(25.0), (2.9, 9.0)),
				(0.005, 0.005, 0.001),
				worldStartPoint,
				self.__forceCameraUpdate
			)
		
		if self.__forceCameraUpdate:
			self.__forceCameraUpdate = False

	def __updateShell(self):
		
		for model in self.__shellModels:
			model.visible = False
		
		hitData = self.currentBattleData.hit
		
		if hitData['isExplosion']:
			
			worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(TankPartNames.CHASSIS)
			
			worldHitPoint = worldComponentMatrix.applyPoint(hitData['position'])

			worldContactMatrix = Math.Matrix()
			worldContactMatrix.setRotateYPR((0.0, math.pi / 2, 0.0))
			worldContactMatrix.translation = Math.Vector3(worldHitPoint)
			
			self.__shellMotors[hitData['shellType']].signal = worldContactMatrix
			self.__shellModels[hitData['shellType']].visible = True
		
		else:
			
			componentIDx, _,  startPoint, endPoint = hitData['points'][0]
			
			localStartPoint = Math.Vector3(startPoint)
			localEndPoint = Math.Vector3(endPoint)
			
			worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(componentIDx)
			
			worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
			worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)
			
			worldHitPoint = (worldStartPoint + worldEndPoint) / 2
			
			worldHitDirection = worldEndPoint - worldStartPoint
			
			worldContactMatrix = Math.Matrix()
			worldContactMatrix.setRotateYPR((worldHitDirection.yaw, worldHitDirection.pitch, 0.0))
			worldContactMatrix.translation = worldHitPoint
			
			self.__shellMotors[hitData['shellType']].signal = worldContactMatrix
			self.__shellModels[hitData['shellType']].visible = True
	
	def __updateEffect(self):
	
		for model in self.__effectModels:
			model.visible = False
		
		hitData = self.currentBattleData.hit
		
		if not hitData['isExplosion']:
			
			componentIDx, shotResult, startPoint, endPoint = hitData['points'][0]
			
			if shotResult in [0, 1]:
				effectType = 0
			elif shotResult == 2:
				effectType = 1
			elif shotResult == 4 or shotResult == 5 and hitData['damageFactor'] > 0:
				effectType = 2
			elif shotResult in [3, 5]:
				effectType = 3
			else:
				LOG_ERROR('unknown effectType')
			
			localStartPoint = Math.Vector3(startPoint)
			localEndPoint = Math.Vector3(endPoint)
			
			worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(componentIDx)
			
			worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
			worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)
			
			worldHitPoint = (worldStartPoint + worldEndPoint) / 2
			
			worldHitDirection = worldEndPoint - worldStartPoint
			
			worldContactMatrix = Math.Matrix()
			worldContactMatrix.setRotateYPR((worldHitDirection.yaw, worldHitDirection.pitch, 0.0))
			worldContactMatrix.translation = worldHitPoint
			
			self.__effectMotors[effectType].signal = worldContactMatrix
			self.__effectModels[effectType].visible = True
	
	def __updateSplash(self):
		
		for model in self.__splashModels:
			model.visible = False
		
		hitData = self.currentBattleData.hit
		
		if hitData['isExplosion']:
			if hitData['shellSplash'] <= 4:
				splashIndex = 2
			elif hitData['shellSplash'] <= 8:
				splashIndex = 1
			else:
				splashIndex = 0
			
			worldContactMatrix = Math.Matrix()
			worldContactMatrix.translation = Math.Vector3(self.__rootPosition + Math.Vector3(hitData['position']))

			self.__splashMotors[splashIndex].signal = worldContactMatrix
			self.__splashModels[splashIndex].visible = True
	
	def __updateRicochet(self):
		
		for model in self.__ricochetModels:
			model.visible = False
		
		hitData = self.currentBattleData.hit
	
		if hitData['isExplosion']:
			return
		
		previosPointData = None

		modelsFreeIdx = range(15)

		for (componentIDx, hitResult, startPoint, endPoint, ) in hitData['points']:
			
			if previosPointData:
				
				preComponentIDx, preHitResult, preStartPoint, preEndPoint = previosPointData
				
				if preHitResult == 0:
				
					worldPreComponentMatrix = self.vehicleCtrl.partWorldMatrix(preComponentIDx)
					localPreStartPoint = Math.Vector3(preStartPoint)
					localPreEndPoint = Math.Vector3(preEndPoint)
					worldPreStartPoint = worldPreComponentMatrix.applyPoint(localPreStartPoint)
					worldPreEndPoint = worldPreComponentMatrix.applyPoint(localPreEndPoint)
					worldStartRicochetPoint = (worldPreStartPoint + worldPreEndPoint) / 2
					
					worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(componentIDx)
					localStartPoint = Math.Vector3(startPoint)
					localEndPoint = Math.Vector3(endPoint)
					worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
					worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)
					worldEndRicochetPoint = (worldStartPoint + worldEndPoint) / 2

					distance = (worldStartRicochetPoint - worldEndRicochetPoint).length
					
					worldRicochetDirection = worldStartRicochetPoint - worldEndRicochetPoint
					worldRicochetMatrix = Math.Matrix()
					worldRicochetMatrix.setRotateYPR((worldRicochetDirection.yaw, worldRicochetDirection.pitch, 0.0))
					worldRicochetMatrix.translation = worldStartRicochetPoint
					
					perfectIdx = int(distance * 3.2)
					targetIdx = min(modelsFreeIdx, key=lambda x:abs(x-perfectIdx))
					modelsFreeIdx.pop(targetIdx)
					
					self.__ricochetModels[targetIdx].visible = True
					self.__ricochetMotors[targetIdx].signal = worldRicochetMatrix

			previosPointData = (componentIDx, hitResult, startPoint, endPoint)
		
		"""
			TODO
			fuck this shit
		"""
		
		return

		debug = lambda name, matrix: '{0} x:{1}, y:{2}, z:{3}, yaw:{4}, pitch:{5}, length:{6} '.format(name, matrix.x, matrix.y, matrix.z, matrix.yaw, matrix.pitch, matrix.length)
		
		if previosPointData:

			componentName, hitResult, startPoint, endPoint = previosPointData
			
			if hitResult in [0, 1]:
				
				localStartPoint = Math.Vector3(startPoint) 
				localEndPoint = Math.Vector3(endPoint)
				
				worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(componentName)

				worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
				worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)
				worldHitPoint = (worldStartPoint + worldEndPoint) / 2
				
				componentsDescr = self.vehicleCtrl.partDescriptor(componentName)
				
				collisions = None
				
				if self.collision is not None:
					collisions = self.collision.collideAllWorld(worldStartPoint, worldEndPoint)
				
				if collisions:
					_, hitAngleCos, _, _ = collisions[0]
					
					# we need normal, from collider, not this one shit
					normal = localStartPoint - localEndPoint
					normal.normalise()
					print debug('normal local', normal)
					
					localNormalDirection = worldComponentMatrix.applyVector(normal)
					localNormalDirection.normalise()
					print debug('direction local', localNormalDirection)
					
					normal = worldStartPoint - worldEndPoint
					normal.normalise()
					print debug('normal world', normal)
					
					worldNormalDirection = worldComponentMatrix.applyVector(normal)
					worldNormalDirection.normalise()
					print debug('direction world', worldNormalDirection)
					

					doubleCathetus = hitAngleCos * (worldHitPoint - worldStartPoint).length * 2.0
					
					worldRicochetDirection = worldHitPoint - (worldEndPoint + worldNormalDirection.scale(-doubleCathetus))
					worldRicochetMatrix = Math.Matrix()
					worldRicochetMatrix.setRotateYPR((worldRicochetDirection.yaw, worldRicochetDirection.pitch, 0.0))
					worldRicochetMatrix.translation = worldHitPoint
					
					self.__ricochetModels[15].visible = True
					self.__ricochetMotors[15].signal = worldRicochetMatrix
	
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
	
	def __updateHitPoints(self):
		pass
	
