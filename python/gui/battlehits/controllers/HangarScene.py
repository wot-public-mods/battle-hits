
from AvatarInputHandler import mathUtils
import BigWorld
import Math
import math
from debug_utils import LOG_ERROR, LOG_NOTE, LOG_DEBUG

from gui.shared.utils.HangarSpace import g_hangarSpace
from vehicle_systems.tankStructure import ModelStates, TankPartNames, TankNodeNames
from vehicle_systems.model_assembler import prepareCompoundAssembler

from gui.battlehits.events import g_eventsManager
from gui.battlehits.controllers import g_controllers
from gui.battlehits.data import g_data


def modepPatch(model):
	style = g_controllers.settings.get('currentStyle')
	return model.format(style=style)

class HangarScene(object):

	def __init__(self):
		
		# data
		self.__rootPosition = Math.Vector3(0.0, 500.0, 0.0)
		
		# resources
		self.__doomModel = None
		
		self.__compoundModel = None
		
		self.__shellModels = None
		self.__effectModels = None
		self.__splashModels = None
		self.__ricochetModels = None
		
		self.__attachmentShell = None
		self.__attachmentEffect = None
		self.__attachmentSplash = None
		self.__attachmentRicochet = None
	
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

		if not g_data.currentBattle.victim:
			return
		
		assambler = prepareCompoundAssembler(g_data.currentBattle.victim['compactDescr'], ModelStates.UNDAMAGED, BigWorld.camera().spaceID)
		BigWorld.loadResourceListBG((assambler, ), self.__onModelLoaded)
	
	def assambleModels(self):
		
		LOG_DEBUG('assambleModels')

		# hangar doom / plane
		self.__doomModel = doomModel = BigWorld.Model("content/interface/battlehits/static/doom.model")
		doomModel.position = self.__rootPosition
		BigWorld.addModel(doomModel, BigWorld.camera().spaceID)
		
		# shells
		self.__shellModels = [
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/shells/ap/shell.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/shells/apcr/shell.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/shells/heat/shell.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/shells/he/shell.model'))
		]
		
		# shells
		self.__effectModels = [
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/effects/ricochet/effect.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/effects/notpenetration/effect.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/effects/penetration/effect.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/effects/critical/effect.model'))
		]

		# splash
		self.__splashModels = [
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/explosions/large/explosion.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/explosions/middle/explosion.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/explosions/small/explosion.model'))
		]
		
		# ricochet
		self.__ricochetModels = [
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/ricochets/large/ricochet.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/ricochets/middle/ricochet.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/ricochets/small/ricochet.model')),
			BigWorld.Model(modepPatch('content/interface/battlehits/{style}/ricochets/cross/ricochet.model'))
		]

		self.__ricochetMotors = [ BigWorld.Servo(Math.Matrix()), BigWorld.Servo(Math.Matrix()), 
									BigWorld.Servo(Math.Matrix()), BigWorld.Servo(Math.Matrix()) ]
		
		for idx in xrange(4):
			self.__ricochetModels[idx].addMotor(self.__ricochetMotors[idx])

		for model in self.__shellModels + self.__splashModels + self.__effectModels + self.__ricochetModels:
			model.castsShadow = False
			model.visible = False
	
	def freeModels(self, freeTankModel = True, withResources = False):
		
		LOG_DEBUG('freeModels', {'freeTankModel': freeTankModel, 'withResources': withResources})

		if self.__shellModels and self.__splashModels and self.__ricochetModels and self.__effectModels:
			for model in self.__shellModels + self.__splashModels + self.__ricochetModels + self.__effectModels:
				model.visible = False
		
		if freeTankModel:
			if self.__compoundModel:
				BigWorld.delModel(self.__compoundModel)
			
			self.__compoundModel = None

		if self.__attachmentSplash:
			BigWorld.delModel(self.__attachmentSplash)
		
		if self.__attachmentRicochet:
			BigWorld.delModel(self.__attachmentRicochet)
		
		self.__attachmentShell = None
		self.__attachmentEffect = None
		self.__attachmentSplash = None
		self.__attachmentRicochet = None
	
		if withResources:
			
			if self.__doomModel:
				BigWorld.delModel(self.__doomModel)
			
			self.__doomModel = None

			self.__shellModels = None
			self.__effectModels = None
			self.__splashModels = None
			self.__ricochetModels = None
			self.__ricochetMotors = None

	def destroy(self):
		
		self.freeModels(withResources=True)
		
		g_eventsManager.onChangedBattleData -= self.__onBattleChanged
		g_eventsManager.onChangedHitData -= self.__onHitChanged
		g_eventsManager.onSettingsChanged -= self.__onSettingsChanged
		
	def __onBattleChanged(self):
		LOG_DEBUG('__onBattleChanged')
		self.freeModels()
	
	def __onHitChanged(self):
		
		LOG_DEBUG('__onHitChanged')

		self.freeModels()
		
		if not g_data.currentBattle.victim:
			
			self.freeModels(freeTankModel=True)
				
			g_controllers.hangarCamera.setCameraData(
				(math.radians(160), -math.radians(25.0)),
				(math.radians(160), -math.radians(25.0), 10.0),
				(math.radians(0.001), math.radians(0.001), (10.0, 10.001)),
				(0.005, 0.005, 0.001),
				self.__rootPosition
			)
			
			return
		
		assambler = prepareCompoundAssembler(g_data.currentBattle.victim['compactDescr'], ModelStates.UNDAMAGED, BigWorld.camera().spaceID)
		BigWorld.loadResourceListBG((assambler, ), self.__onModelLoaded)
	
	def __onSettingsChanged(self, key, value):
		
		LOG_DEBUG('__onSettingsChanged', {'key': key, 'value': value})

		if key == 'currentStyle':
			
			self.freeModels(freeTankModel=False)
			self.assambleModels()
			self.__validateVehicle()
		
		"""
		elif key == 'hitsToPlayer':
			
			if g_data.hits.desiredID == -1:
			
				self.freeModels(freeTankModel=True)
				
				g_controllers.hangarCamera.setCameraData(
					(math.radians(160), -math.radians(25.0)),
					(math.radians(160), -math.radians(25.0), 10.0),
					(math.radians(0.001), math.radians(0.001), (10.0, 10.001)),
					(0.005, 0.005, 0.001),
					self.__rootPosition
				)
		"""
	
	def __onModelLoaded(self, resources):
		
		LOG_DEBUG('__onModelLoaded', resources)

		self.__compoundModel = resources[g_data.currentBattle.victim['compactDescr'].name]
		
		BigWorld.addModel(self.__compoundModel)
		
		m = Math.Matrix()
		m.setTranslate(self.__rootPosition)
		self.__compoundModel.matrix = m

		self.__updateTurretAndGun()
	
	def __validateVehicle(self):
		
		atackerData = g_data.currentBattle.atacker
		if not atackerData:
			return
		
		targetTurretYaw, targetGunPitch = atackerData['aimParts']
		
		if not self.__compoundModel:
			BigWorld.callback(0.01, self.__validateVehicle)
			return
		
		currentPosition = Math.Matrix(self.__compoundModel.node(TankPartNames.CHASSIS)).translation
		currentTurretYaw = Math.Matrix(self.__compoundModel.node(TankPartNames.TURRET)).yaw
		currentGunPitch = Math.Matrix(self.__compoundModel.node(TankNodeNames.GUN_INCLINATION)).pitch
		
		isVehicleUpdated = currentPosition == self.__rootPosition and mathUtils.almostZero(targetTurretYaw - currentTurretYaw) and \
						 mathUtils.almostZero(targetGunPitch - currentGunPitch)
		
		if isVehicleUpdated:
			self.__updateCamera()
			self.__updateShell()
			self.__updateEffect()
			self.__updateRicochet()
			self.__updateSplash()
		else:
			BigWorld.callback(0., self.__validateVehicle)
	
	def __updateTurretAndGun(self):
		
		atackerData = g_data.currentBattle.atacker
		if not atackerData:
			return
		
		turretYaw, gunPitch = atackerData['aimParts']
	
		m = Math.Matrix()
		m.setRotateYPR((turretYaw, 0.0, 0.0))
		self.__compoundModel.node(TankPartNames.TURRET, m)
	
		m = Math.Matrix()
		m.setRotateYPR((0.0, gunPitch, 0.0))
		self.__compoundModel.node(TankNodeNames.GUN_INCLINATION, m)
		
		self.__validateVehicle()
	
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
			
			startPoint, endPoint = Math.Vector3(startPoint), Math.Vector3(endPoint)
			
			nodeName = componentName
			if componentName == TankPartNames.GUN:
				nodeName = TankNodeNames.GUN_INCLINATION
			
			partWorldMat = Math.Matrix(self.__compoundModel.node(nodeName))
			
			worldStartPoint = partWorldMat.applyPoint(startPoint)
			worldEndPoint = partWorldMat.applyPoint(endPoint)
			
			worldHitDirection = worldEndPoint - worldStartPoint
			
			# default, current, limits, sens, targetPoint
			g_controllers.hangarCamera.setCameraData(
				(worldHitDirection.yaw, -worldHitDirection.pitch),
				(worldHitDirection.yaw + 0.2, -worldHitDirection.pitch, 4.0),
				(math.radians(35.0), math.radians(25.0), (2.9, 9.0)),
				(0.005, 0.005, 0.001),
				worldStartPoint
			)
	
	def __updateSplash(self):
		
		if self.__attachmentSplash:
			BigWorld.delModel(self.__attachmentSplash)
		self.__attachmentSplash = None
		
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
			
			self.__attachmentSplash = self.__splashModels[splashIndex]
			self.__attachmentSplash.visible = True
			self.__attachmentSplash.position = self.__rootPosition + Math.Vector3(points)
			BigWorld.addModel(self.__attachmentSplash)
		
	def __updateShell(self):
		
		if self.__attachmentShell:
			nodeName, shellType, _ = self.__attachmentShell
			self.__compoundModel.node(nodeName).detach(self.__shellModels[shellType])
			self.__shellModels[shellType].visible = False
			self.__attachmentShell = None
		
		victimData = g_data.currentBattle.victim
		if not victimData:
			return
		
		isExplosion, shellType, points, shellSplash, damageFactor = victimData['shot'] 
		
		if isExplosion:
			
			nodeName = TankPartNames.CHASSIS
			
			contactMatrix = Math.Matrix()
			contactMatrix.setRotateYPR((0.0, math.pi / 2, 0.0))
			contactMatrix.translation = Math.Vector3(points)
			
			self.__compoundModel.node(nodeName).attach(self.__shellModels[shellType], contactMatrix)
			self.__shellModels[shellType].visible = True
			self.__attachmentShell = (nodeName, shellType, None, )
			
		else:
			
			componentName, _,  startPoint, endPoint = points[0]
			startPoint, endPoint = Math.Vector3(startPoint), Math.Vector3(endPoint)
			
			nodeName = componentName
			if componentName == TankPartNames.GUN:
				nodeName = TankNodeNames.GUN_INCLINATION
			
			hitDirection = endPoint - startPoint
			contactMatrix = Math.Matrix()
			contactMatrix.setRotateYPR((hitDirection.yaw, hitDirection.pitch, 0.0))
			contactMatrix.translation = (startPoint + endPoint) / 2
			
			self.__compoundModel.node(nodeName).attach(self.__shellModels[shellType], contactMatrix)
			
			self.__shellModels[shellType].visible = True
			self.__attachmentShell = (nodeName, shellType, contactMatrix)
	
	def __updateEffect(self):
	
		if self.__attachmentEffect:
			nodeName, effectIndex, _ = self.__attachmentEffect
			self.__compoundModel.node(nodeName).detach(self.__effectModels[effectIndex])
			self.__effectModels[effectIndex].visible = False
			self.__attachmentEffect = None
		
		victimData = g_data.currentBattle.victim
		if not victimData:
			return
		
		isExplosion, shellType, points, shellSplash, damageFactor = victimData['shot'] 
		
		if not isExplosion:
			
			componentName, shotResult, startPoint, endPoint = points[0]
			startPoint, endPoint = Math.Vector3(startPoint), Math.Vector3(endPoint)
			
			if shotResult in [0, 1]:
				effectIndex = 0
			elif shotResult == 2:
				effectIndex = 1
			elif shotResult == 4 or shotResult == 5 and damageFactor > 0:
				effectIndex = 2
			elif shotResult in [3, 5]:
				effectIndex = 3
			else:
				LOG_ERROR('unknown effectIndex')
			
			nodeName = componentName
			if componentName == TankPartNames.GUN:
				nodeName = TankNodeNames.GUN_INCLINATION
			
			hitDirection = endPoint - startPoint
			contactMatrix = Math.Matrix()
			contactMatrix.setRotateYPR((hitDirection.yaw, hitDirection.pitch, 0.0))
			contactMatrix.translation = (startPoint + endPoint) / 2
			
			self.__compoundModel.node(nodeName).attach(self.__effectModels[effectIndex], contactMatrix)
			
			self.__effectModels[effectIndex].visible = True
			self.__attachmentEffect = (nodeName, effectIndex, contactMatrix)
	

	
	def __updateRicochet(self):
		
		if self.__attachmentRicochet:
			BigWorld.delModel(self.__attachmentRicochet)
			self.__attachmentRicochet = None
		
		victimData = g_data.currentBattle.victim
		if not victimData:
			return
		
		isExplosion, shellType, points, shellSplash, damageFactor = victimData['shot'] 
		
		if isExplosion:
			return
		
		for (componentName, hitResult, startPoint, endPoint, ) in points:
			
			if hitResult == 0:
				
				self.__attachmentRicochet = self.__ricochetModels[3]

				nodeName = componentName
				if componentName == TankPartNames.GUN:
					nodeName = TankNodeNames.GUN_INCLINATION
				
				localStartPoint = Math.Vector3(startPoint) 
				localEndPoint = Math.Vector3(endPoint)
				
				worldComponentMatrix = Math.Matrix(self.__compoundModel.node(nodeName))
				
				worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
				worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)
				worldHitPoint = (worldStartPoint + worldEndPoint) / 2
				
				componentsDescr = getattr(g_data.currentBattle.victim['compactDescr'], componentName)
				hitTester = componentsDescr['hitTester']
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
					
					self.__attachmentRicochet.visible = True
					self.__ricochetMotors[3].signal = worldRicochetMatrix
					
					BigWorld.addModel(self.__attachmentRicochet)
