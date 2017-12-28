
from AvatarInputHandler import mathUtils
import BigWorld
import Math
import math
from debug_utils import LOG_ERROR, LOG_NOTE, LOG_DEBUG
from gui.Scaleform.Waiting import Waiting
from gui.shared.utils.HangarSpace import g_hangarSpace
from vehicle_systems.tankStructure import ModelStates, TankPartNames, TankPartIndexes, TankNodeNames
from vehicle_systems.model_assembler import prepareCompoundAssembler

from gui.battlehits.events import g_eventsManager
from gui.battlehits.controllers import g_controllers
from gui.battlehits.data import g_data
from gui.battlehits._constants import MODEL_TYPES, MODEL_PATHS, SETTINGS, SCENE_OFFSET, CAMERA_DEFAULTS

class HangarScene(object):

	def __init__(self):
		
		# data
		self.__rootPosition = SCENE_OFFSET
		self.__useCollision = False
		self.__preCompactDescrStr = None
		
		# resources
		self.__domeModel = None

		self.__compoundModel = None

		self.__collisionModels = []
		self.__shellModels = []
		self.__effectModels = []
		self.__splashModels = []
		self.__ricochetModels = []

		self.__collisionMotors = []
		self.__effectMotors = []
		self.__splashMotors = []
		self.__shellMotors = []
		self.__ricochetMotors = []
	
	def init(self):
		pass
	
	def fini(self):
		self.destroy()
	
	def create(self):
	
		g_hangarSpace.onSpaceCreate -= self.create
		g_eventsManager.onChangedBattleData += self.__onBattleChanged
		g_eventsManager.onChangedHitData += self.__onHitChanged
		g_eventsManager.onSettingsChanged += self.__onSettingsChanged
		
		self.assambleModels()
		
		self.__useCollision = g_controllers.settings.get(SETTINGS.COLLISION_MODEL, False)
		
		g_controllers.hangarCamera.setCameraData(*CAMERA_DEFAULTS)
		
		self.__loadVehicle()
	
	def assambleModels(self):

		currentStyle = g_controllers.settings.get(SETTINGS.CURRENT_STYLE)
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
			
			self.__preCompactDescrStr = None

			if self.__compoundModel:
				BigWorld.delModel(self.__compoundModel)
			self.__compoundModel = None

			for model in self.__collisionModels:
				if model in BigWorld.models():
					BigWorld.delModel(model)
			self.__collisionModels = []
			self.__collisionMotors = []
		
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
		self.__preCompactDescrStr = None
		g_controllers.hangarCamera.setCameraData(*CAMERA_DEFAULTS)
	
	def destroy(self):
		self.freeModels(withResources=True)
		g_eventsManager.onChangedBattleData -= self.__onBattleChanged
		g_eventsManager.onChangedHitData -= self.__onHitChanged
		g_eventsManager.onSettingsChanged -= self.__onSettingsChanged
	
	def __onBattleChanged(self):
		self.freeModels()
	
	def __onHitChanged(self):
		
		if not g_data.currentBattle.victim:
			self.freeModels(freeTankModel=True)
			g_controllers.hangarCamera.setCameraData(*CAMERA_DEFAULTS)
			return
		
		if self.__preCompactDescrStr != g_data.currentBattle.victim['compactDescrStr']:
			self.freeModels()

		self.__loadVehicle()

	def __onSettingsChanged(self, key, value):
		
		if key == SETTINGS.CURRENT_STYLE:
			self.freeModels(freeTankModel=False)
			self.assambleModels()
			self.__loadVehicle()
	
		if key == SETTINGS.COLLISION_MODEL:
			self.__useCollision = value
			self.freeModels(freeTankModel=True)
			self.__loadVehicle()
	
	def __loadVehicle(self):
		
		if not g_data.currentBattle.victim:
			return

		compactDescr = g_data.currentBattle.victim['compactDescr']
		compactDescrStr = g_data.currentBattle.victim['compactDescrStr']
		aimParts = g_data.currentBattle.atacker['aimParts']

		g_controllers.vehicle.setVehicleData(vehicleDescr = compactDescr, aimParts = aimParts)

		if self.__preCompactDescrStr != compactDescrStr:
			Waiting.show('updateCurrentVehicle')
			if self.__useCollision:
				modelsCollision = [ compactDescr.getHitTesters()[idx].bspModelName for idx in TankPartIndexes.ALL ]
				BigWorld.loadResourceListBG(modelsCollision, self.__onCollisionLoaded)
			else:
				assambler = prepareCompoundAssembler(compactDescr, ModelStates.UNDAMAGED, BigWorld.camera().spaceID)
				BigWorld.loadResourceListBG((assambler, ), self.__onModelLoaded)
			self.__preCompactDescrStr = compactDescrStr
		else:
			self.__updateTurretAndGun()
		
		self.__updateCamera()
		self.__updateShell()
		self.__updateEffect()
		self.__updateSplash()
		self.__updateRicochet()

	def __onModelLoaded(self, resources):
		
		compactDescr = g_data.currentBattle.victim['compactDescr']
		
		self.__compoundModel = resources[compactDescr.name]
		
		BigWorld.addModel(self.__compoundModel)
		
		m = Math.Matrix()
		m.setTranslate(self.__rootPosition)
		self.__compoundModel.matrix = m
		self.__updateTurretAndGun()

		Waiting.hide('updateCurrentVehicle')

	def __onCollisionLoaded(self, resources):
		
		compactDescr = g_data.currentBattle.victim['compactDescr']
		modelsCollision = [ compactDescr.getHitTesters()[idx].bspModelName for idx in TankPartIndexes.ALL ]

		self.__collisionModels = [resources[model] for model in modelsCollision]
		self.__collisionMotors = [BigWorld.Servo(Math.Matrix()) for idx in TankPartIndexes.ALL]
		
		for idx in TankPartIndexes.ALL:
			model, motor = self.__collisionModels[idx], self.__collisionMotors[idx]
			model.castsShadow = False
			model.addMotor(motor)
			motor.signal = g_controllers.vehicle.partWorldMatrix(TankPartIndexes.getName(idx))
			BigWorld.addModel(model)
		
		Waiting.hide('updateCurrentVehicle')

	def __updateTurretAndGun(self):
		
		turretYaw, gunPitch = g_data.currentBattle.atacker['aimParts']

		if self.__useCollision:
			for idx in TankPartIndexes.ALL:
				self.__collisionMotors[idx].signal = g_controllers.vehicle.partWorldMatrix(TankPartIndexes.getName(idx))
		else:
			m = Math.Matrix()
			m.setRotateYPR((turretYaw, 0.0, 0.0))
			self.__compoundModel.node(TankPartNames.TURRET, m)
			m = Math.Matrix()
			m.setRotateYPR((0.0, gunPitch, 0.0))
			self.__compoundModel.node(TankNodeNames.GUN_INCLINATION, m)
		
	def __updateCamera(self):
		
		victimData = g_data.currentBattle.victim
		if not victimData:
			return
		
		isExplosion, shellType, points, shellSplash, damageFactor = victimData['shot'] 
		
		if isExplosion:
			
			fallenPoint = self.__rootPosition + Math.Vector3(points)
			worldHitDirection = self.__rootPosition - fallenPoint
			
			targetPoint = fallenPoint + Math.Vector3(0.0, (self.__rootPosition - fallenPoint).length / 2.0, 0.0)
			
			# default, current, limits, sens, targetPoint
			g_controllers.hangarCamera.setCameraData(
				(mathUtils.reduceToPI(worldHitDirection.yaw), -math.radians(25.0)),
				(mathUtils.reduceToPI(worldHitDirection.yaw), -math.radians(25.0), 10.0),
				(None, math.radians(20.0), (5.0, 15.0)),
				(0.005, 0.005, 0.001),
				targetPoint
			)
		else:
			
			componentName, _, startPoint, endPoint = points[0]
			
			worldComponentMatrix = g_controllers.vehicle.partWorldMatrix(componentName)
			
			localStartPoint = Math.Vector3(startPoint)
			localEndPoint = Math.Vector3(endPoint)
			
			worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
			worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)
			
			worldHitDirection = worldEndPoint - worldStartPoint
			
			# default, current, limits, sens, targetPoint
			g_controllers.hangarCamera.setCameraData(
				(worldHitDirection.yaw, -worldHitDirection.pitch),
				(worldHitDirection.yaw + 0.2, -worldHitDirection.pitch, 4.0),
				(math.radians(35.0), math.radians(25.0), (2.9, 9.0)),
				(0.005, 0.005, 0.001),
				worldStartPoint
			)
	
	def __updateShell(self):
		
		for model in self.__shellModels:
			model.visible = False
		
		victimData = g_data.currentBattle.victim
		if not victimData:
			return
		
		isExplosion, shellType, points, shellSplash, damageFactor = victimData['shot'] 
		
		if isExplosion:
			
			worldComponentMatrix = g_controllers.vehicle.partWorldMatrix(TankPartNames.CHASSIS)
			
			worldHitPoint = worldComponentMatrix.applyPoint(points)

			worldContactMatrix = Math.Matrix()
			worldContactMatrix.setRotateYPR((0.0, math.pi / 2, 0.0))
			worldContactMatrix.translation = Math.Vector3(worldHitPoint)
			
			self.__shellMotors[shellType].signal = worldContactMatrix
			self.__shellModels[shellType].visible = True
		
		else:
			
			componentName, _,  startPoint, endPoint = points[0]
			
			localStartPoint = Math.Vector3(startPoint)
			localEndPoint = Math.Vector3(endPoint)
			
			worldComponentMatrix = g_controllers.vehicle.partWorldMatrix(componentName)
			
			worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
			worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)
			
			worldHitPoint = (worldStartPoint + worldEndPoint) / 2
			
			worldHitDirection = worldEndPoint - worldStartPoint
			
			worldContactMatrix = Math.Matrix()
			worldContactMatrix.setRotateYPR((worldHitDirection.yaw, worldHitDirection.pitch, 0.0))
			worldContactMatrix.translation = worldHitPoint
			
			self.__shellMotors[shellType].signal = worldContactMatrix
			self.__shellModels[shellType].visible = True
	
	def __updateEffect(self):
	
		for model in self.__effectModels:
			model.visible = False
		
		victimData = g_data.currentBattle.victim
		if not victimData:
			return
		
		isExplosion, shellType, points, shellSplash, damageFactor = victimData['shot'] 
		
		if not isExplosion:
			
			componentName, shotResult, startPoint, endPoint = points[0]
			
			if shotResult in [0, 1]:
				effectType = 0
			elif shotResult == 2:
				effectType = 1
			elif shotResult == 4 or shotResult == 5 and damageFactor > 0:
				effectType = 2
			elif shotResult in [3, 5]:
				effectType = 3
			else:
				LOG_ERROR('unknown effectType')
			
			localStartPoint = Math.Vector3(startPoint)
			localEndPoint = Math.Vector3(endPoint)
			
			worldComponentMatrix = g_controllers.vehicle.partWorldMatrix(componentName)
			
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
		
		victimData = g_data.currentBattle.victim
		if not victimData:
			return
		
		isExplosion, shellType, points, shellSplash, damageFactor = victimData['shot'] 
		
		if isExplosion:
			if shellSplash <= 4:
				splashIndex = 2
			elif shellSplash <= 8:
				splashIndex = 1
			else:
				splashIndex = 0
			
			worldContactMatrix = Math.Matrix()
			worldContactMatrix.translation = Math.Vector3(self.__rootPosition + Math.Vector3(points))

			self.__splashMotors[splashIndex].signal = worldContactMatrix
			self.__splashModels[splashIndex].visible = True
	
	def __updateRicochet(self):
		
		for model in self.__ricochetModels:
			model.visible = False
		
		victimData = g_data.currentBattle.victim
		if not victimData:
			return
		
		isExplosion, shellType, points, shellSplash, damageFactor = victimData['shot'] 
		
		if isExplosion:
			return
		
		previosPointData = None

		modelsFreeIdx = range(15)

		for (componentName, hitResult, startPoint, endPoint, ) in points:
			
			if previosPointData:
				
				preComponentName, preHitResult, preStartPoint, preEndPoint = previosPointData
				
				if preHitResult == 0:
				
					worldPreComponentMatrix = g_controllers.vehicle.partWorldMatrix(preComponentName)
					localPreStartPoint = Math.Vector3(preStartPoint)
					localPreEndPoint = Math.Vector3(preEndPoint)
					worldPreStartPoint = worldPreComponentMatrix.applyPoint(localPreStartPoint)
					worldPreEndPoint = worldPreComponentMatrix.applyPoint(localPreEndPoint)
					worldStartRicochetPoint = (worldPreStartPoint + worldPreEndPoint) / 2
					
					worldComponentMatrix = g_controllers.vehicle.partWorldMatrix(componentName)
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

			previosPointData = (componentName, hitResult, startPoint, endPoint)
			
		if previosPointData:

			componentName, hitResult, startPoint, endPoint = previosPointData
			
			if hitResult in [0, 1]:
				
				localStartPoint = Math.Vector3(startPoint) 
				localEndPoint = Math.Vector3(endPoint)
				
				worldComponentMatrix = g_controllers.vehicle.partWorldMatrix(componentName)

				worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
				worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)
				worldHitPoint = (worldStartPoint + worldEndPoint) / 2
				
				componentsDescr = g_controllers.vehicle.partDescriptor(componentName)
				hitTester = componentsDescr.hitTester
				if not hitTester.isBspModelLoaded():
					hitTester.loadBspModel()
				collision = hitTester.getBspModel().collideSegment(localStartPoint, localEndPoint)
				hitTester.releaseBspModel()
				if collision:
					_, normal, hitAngleCos, _ = collision[0]
					worldNormalDirection = -worldComponentMatrix.applyVector(normal)
					worldNormalDirection.normalise()
					
					doubleKatet = hitAngleCos * (worldHitPoint - worldStartPoint).length * 2.0
					
					worldRicochetDirection = worldHitPoint - (worldEndPoint + worldNormalDirection.scale(-doubleKatet))
					worldRicochetMatrix = Math.Matrix()
					worldRicochetMatrix.setRotateYPR((worldRicochetDirection.yaw, worldRicochetDirection.pitch, 0.0))
					worldRicochetMatrix.translation = worldHitPoint
					
					self.__ricochetModels[15].visible = True
					self.__ricochetMotors[15].signal = worldRicochetMatrix
		