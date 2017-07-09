
from AvatarInputHandler import mathUtils
import BigWorld
import Math
import math

from vehicle_systems.tankStructure import ModelStates, TankPartNames, TankNodeNames
from vehicle_systems.model_assembler import prepareCompoundAssembler
from vehicle_systems.tankStructure import ModelStates
from VehicleEffects import DamageFromShotDecoder

from gui.battlehits.data import g_data
from gui.battlehits.battlehits_constants import SHELL_TYPES

class Analyzer(object):
	
	def __init__(self): 
		pass

	def init(self):
		pass

	def fini(self): 
		pass
	
	def collisions(self):
		
		playerData = g_data.currentBattle.player
		if not playerData:
			return None
		
		enemyData = g_data.currentBattle.enemy
		if not enemyData:
			return None
		
		vehicleDescriptorPlayer = g_data.currentBattle.vDescPlayer
		if not vehicleDescriptorPlayer:
			return None
		
		isExplosion, shellType, points, shellSplash, damageFactor = enemyData['shot']
		
		if isExplosion:
			return None
		
		componentName, shotResult, startPoint, endPoint = points[0]
		
		components = self.__getComponents(vehicleDescriptorPlayer, playerData['aimParts'])
		
		self.__debugpoints(components, shellType, points)
		

	def analize(self, compoundModel, rootPosition):
		
		playerData = g_data.currentBattle.player
		if not playerData:
			return None
		
		enemyData = g_data.currentBattle.enemy
		if not enemyData:
			return None
		
		vehicleDescriptorPlayer = g_data.currentBattle.vDescPlayer
		if not vehicleDescriptorPlayer:
			return None
		
		vehicleDescriptorEnemy = g_data.currentBattle.vDescEnemy
		if not vehicleDescriptorEnemy:
			return None
		
		playerTurretYaw, playerGunPitch = playerData['aimParts']
		isExplosion, shellType, points, shellSplash, damageFactor = enemyData['shot']
		
		#camera = self.__getCameraData(compoundModel, rootPosition, isExplosion, points)
		#shell = self.__getShellData(compoundModel, rootPosition, isExplosion, points)
		#return camera, shell
	
	def __getCameraData(self, compoundModel, rootPosition, isExplosion, points):
		
		if isExplosion:
			
			worldFallenPoint = rootPosition + Math.Vector3(points)
			worldHitDirection = rootPosition - worldFallenPoint
			
			target = worldFallenPoint + Math.Vector3(0.0, (rootPosition - worldFallenPoint).length / 2.0, 0.0)
			yaw = mathUtils.reduceToPI(worldHitDirection.yaw)
			pitch = -math.radians(25.0)
			
			default = (yaw, pitch)
			current = (yaw, pitch, 10.0)
			limits = (None, math.radians(20.0), (4.0, 16.0))
			sens = (0.005, 0.005, 0.001)
			
		else:

			componentName, _, startPoint, endPoint = points[0]
			localStartPoint, localEndPoint = Math.Vector3(startPoint), Math.Vector3(endPoint)
			
			nodeName = componentName
			if componentName == TankPartNames.GUN:
				nodeName = TankNodeNames.GUN_INCLINATION
			
			partWorldMatrix = Math.Matrix(compoundModel.node(nodeName))
			worldStartPoint = partWorldMatrix.applyPoint(localStartPoint)
			worldEndPoint = partWorldMatrix.applyPoint(localEndPoint)
			
			worldHitDirection = worldEndPoint - worldStartPoint
			
			target = worldStartPoint
			yaw = mathUtils.reduceToPI(worldHitDirection.yaw)
			pitch = worldHitDirection.pitch

			default = (yaw, -pitch)
			current = (yaw + 0.2, -pitch, 4.0)
			limits = (math.radians(30.0), math.radians(20.0), (2.5, 7.0))
			sens = (0.005, 0.005, 0.001)
		
		print 'cameraData => target: {0}, yaw: {1}, pitch: {2}'.format(target, math.degrees(yaw), math.degrees(pitch))
		
		return ((default, current, limits, sens, target))




	def __getShellData(self, compoundModel, rootPosition, isExplosion, points):
		
		if isExplosion:
			contactMatrix = Math.Matrix()
			contactMatrix.setRotateYPR((0.0, math.pi / 2, 0.0))
			contactMatrix.translation = Math.Vector3(rootPosition) + Math.Vector3(points)
			
		else:
			
			componentName, _, localStartPoint, localEndPoint = points[0]
			
			nodeName = componentName
			if componentName == TankPartNames.GUN:
				nodeName = TankNodeNames.GUN_INCLINATION
			
			worldStartPoint = compoundModel.node(nodeName).applyPoint(localStartPoint)
			worldEndPoint = compoundModel.node(nodeName).applyPoint(localEndPoint)
			
			hitDirection = worldEndPoint - worldStartPoint
			contactMatrix = Math.Matrix()
			contactMatrix.setRotateYPR((hitDirection.yaw, hitDirection.pitch, 0.0))
			contactMatrix.translation = (worldStartPoint + worldEndPoint) / 2
			
	def __getComponents(self, vehicleDescr, aimParts):
		
		res =[]
		turretYaw, gunPitch = aimParts
		
		# chassis
		chassisMatrix = Math.Matrix()
		chassisMatrix.setIdentity()
		res.append((TankPartNames.CHASSIS, vehicleDescr.chassis, chassisMatrix))
		
		# hull
		hullOffset = vehicleDescr.chassis['hullPosition']
		hullMatrix = Math.Matrix()
		hullMatrix.setTranslate(-hullOffset)
		res.append((TankPartNames.HULL, vehicleDescr.hull, hullMatrix))
		
		# turret
		turretMatrix = Math.Matrix()
		turretMatrix.setTranslate(-hullOffset - vehicleDescr.hull['turretPositions'][0])
		m = Math.Matrix()
		m.setRotateY(-turretYaw)
		turretMatrix.postMultiply(m)
		res.append((TankPartNames.TURRET, vehicleDescr.turret, turretMatrix))

		# gun
		gunMatrix = Math.Matrix()
		gunMatrix.setTranslate(-vehicleDescr.turret['gunPosition'])
		gunTilt = Math.Matrix()
		gunTilt.setRotateX(-gunPitch)
		gunMatrix.postMultiply(gunTilt)
		gunMatrix.preMultiply(turretMatrix)
		res.append((TankPartNames.GUN, vehicleDescr.gun, gunMatrix))
		
		return res
	



	def __debugpoints(self, components, shellType, points):
		
		collisions = []
		ready = False
		for (componentName, shotResult, startPoint, endPoint, ) in points:

			for (compName, compDescr, compMatrix, ) in components:
				
				if componentName not in [compName, TankPartNames.GUN]:
					continue
				
				hitTester = compDescr['hitTester']
				if not hitTester.isBspModelLoaded():
					hitTester.loadBspModel()
				
				collisionDirection = Math.Vector3(endPoint) - Math.Vector3(startPoint)

				prolongedEndPoint = endPoint + collisionDirection.scale(100)

				collisionsResult = hitTester.localHitTest(startPoint, prolongedEndPoint)
				if collisionsResult is None:
					continue
				
				currentID = 0

				for dist, normal, hitAngleCos, matKind in collisionsResult:
				
					matInfo = compDescr['materials'].get(matKind)
					if matInfo is None: 
						matInfo = defaultMatInfo()
					
					dist = round(dist, 5)
					hitAngleCos = math.degrees(math.acos(hitAngleCos))
					armor = matInfo.armor
					mayRicochet = matInfo.mayRicochet
					useHitAngle = matInfo.useHitAngle
					damageFactor = matInfo.vehicleDamageFactor
					
					if currentID != matInfo.kind:
						currentID = matInfo.kind
						input = True
					else:
						input = False
						
					if componentName in [TankPartNames.GUN, TankPartNames.CHASSIS]: itemName = componentName
					elif componentName not in [TankPartNames.CHASSIS, TankPartNames.GUN] and not damageFactor and armor > 0: itemName = "shield"
					elif componentName != TankPartNames.CHASSIS and not damageFactor and armor == 0: itemName = "observe"
					else: itemName = "basicArmor"
					
					if input:
						collisions.append((componentName, itemName, dist, hitAngleCos, armor, damageFactor, input, useHitAngle, mayRicochet))
					
					ready = itemName == "basicArmor"
					
					if ready:
						break
				if ready:
					break
			if ready:
				break

		print collisions



