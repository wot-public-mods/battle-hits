
import BattleReplay
import BigWorld
import Math
from vehicle_systems.tankStructure import ModelStates
from VehicleEffects import DamageFromShotDecoder

from gui.battlehits.controllers import g_controllers
from gui.battlehits.events import g_eventsManager

class BattleProcessor(object):
	
	trackBattle = property(lambda self: not BattleReplay.isPlaying() or (BattleReplay.isPlaying() and g_controllers.settings.get('processReplays', False)))
	
	def __init__(self):
		self.__battleData = None
		self.isAlive = True
		self.__vehicles = {}
		
	def init(self):	
		g_eventsManager.onShowBattle += self.__onShowBattle
		g_eventsManager.onDestroyBattle += self.__onDestroyBattle
	
	def fini(self):
		g_eventsManager.onShowBattle -= self.__onShowBattle
		g_eventsManager.onDestroyBattle -= self.__onDestroyBattle
	
	def __onShowBattle(self):
		
		if not self.trackBattle:
			return
		
		player = BigWorld.player()
		
		processedData = None
		
		if g_controllers.battlesHistory:
			_, processedData = g_controllers.battlesHistory.getBattleByUniqueID(player.arenaUniqueID)
		
		if processedData is not None:
			self.__battleData = processedData
		else:
			self.__battleData = {
				'arena': {
					'arenaUniqueID': player.arenaUniqueID,
					'arenaTypeID': player.arenaTypeID,
					'arenaBonusType': player.arenaBonusType,
					'arenaGuiType': player.arenaGuiType
				},
				'playerCompactDescr': player.vehicle.publicInfo.compDescr,
				'hits': [],
				'vehicles': {}
			}
		
		self.isAlive = player.vehicle.isAlive()
	
		self.__vehicles = {}

		for vehicleID, vehicle in player.arena.vehicles.iteritems():
			if vehicleID not in self.__vehicles:
				try:
					self.__vehicles[vehicleID] = int(vehicle['vehicleType'].maxHealth)
				except:
					self.__vehicles[vehicleID] = -1
		
	def __onDestroyBattle(self):
		
		if not self.trackBattle:
			return
		
		self.__vehicles = {}

		self.isAlive = False
		
		if g_controllers.battlesHistory:
			g_controllers.battlesHistory.addBattle(self.__battleData)
	
	def processEnterWorld(self, vehicle):
		
		if not self.trackBattle:
			return
		
		if not self.isAlive:
			return
		
		try:
			self.__vehicles[vehicle.id] = int(vehicle.health) if vehicle.isCrewActive else 0
		except:
			self.__vehicles[vehicle.id] = -1
		
		
	def processHealthChanged(self, vehicle, newHealth, attackerID, attackReasonID):
		
		if not self.trackBattle or not self.isAlive or not attackerID:
			return
		
		damage = 0
		if vehicle.id in self.__vehicles:
			damage = self.__vehicles[vehicle.id] - newHealth if newHealth >= 0.0 else self.__vehicles[vehicle.id]
			self.__vehicles[vehicle.id] = newHealth
		
		if attackReasonID != 0 or not vehicle.isPlayerVehicle and attackerID != BigWorld.player().playerVehicleID:
			return
		
		hitID = None
		for hitIdx, hitCtx in enumerate(self.__battleData['hits']):
			if isinstance(hitCtx['damage'], tuple):
				_attackerID, _victimID = hitCtx['damage']
				if _attackerID == attackerID and _victimID == vehicle.id:
					hitID = hitIdx
					break
		
		if hitID is not None:
			self.__battleData['hits'][hitID]['damage'] = damage
	
	def onModelsRefresh(self, vehicle, modelState):
		
		if vehicle is None:
			return

		if not self.trackBattle or not self.isAlive or not vehicle.isPlayerVehicle:
			return
		
		if modelState != ModelStates.UNDAMAGED:
			self.isAlive = True

	def processShot(self, vehicle, attackerID, points, effectsIndex, damageFactor):
		
		if not self.trackBattle or not self.isAlive or not attackerID:
			return
		
		atacker = BigWorld.player().arena.vehicles.get(attackerID)
		victim = BigWorld.player().arena.vehicles.get(vehicle.id)
		
		if not atacker['vehicleType'] or not victim['vehicleType']:
			return
		
		if not vehicle.isPlayerVehicle and attackerID != BigWorld.player().playerVehicleID:
			return
		
		pointsData = []
		for (compName, hitEffectCode, startPoint, endPoint) in [DamageFromShotDecoder.decodeSegment(point, vehicle.typeDescriptor) for point in points]:
			pointsData.append((compName, hitEffectCode, tuple(startPoint), tuple(endPoint)))
		
		if vehicle.isPlayerVehicle:
			target, targetID = atacker, attackerID
		else:
			target, targetID = victim, vehicle.id
		
		self.__battleData['hits'].append({
			'damageFactor': damageFactor,
			'effectsIndex': effectsIndex,
			'aimParts': vehicle.getAimParams(),
			'isExplosion': False,
			'points': pointsData,
			'damage': (attackerID, vehicle.id, ) if damageFactor > 0 else 0,
			'isPlayer': vehicle.isPlayerVehicle,
			'attacker': {
				'id': targetID,
				'name': target['name'],
				'accountDBID': target['accountDBID'],
				'clanAbbrev': target['clanAbbrev'],
				'clanDBID': target['clanDBID']
			}
		})

		if targetID not in self.__battleData['vehicles']:
			self.__battleData['vehicles'][targetID] = target['vehicleType'].makeCompactDescr()
		
	
	def processExplosion(self, vehicle, attackerID, center, effectsIndex, damageFactor):
		
		if not self.trackBattle or not self.isAlive or not attackerID:
			return
		
		atacker = BigWorld.player().arena.vehicles.get(attackerID)
		victim = BigWorld.player().arena.vehicles.get(vehicle.id)
		
		if not atacker['vehicleType'] or not victim['vehicleType']:
			return
		
		if not vehicle.isPlayerVehicle and attackerID != BigWorld.player().playerVehicleID:
			return
		
		vehicleMatrix = Math.Matrix(vehicle.model.matrix)
		shotPosition = center - vehicle.position
		shotPositionMatrix = Math.Matrix()
		shotPositionMatrix.setTranslate(shotPosition)
		shotMatrixRotated = Math.Matrix()
		shotMatrixRotated.setRotateYPR((-vehicleMatrix.yaw, -vehicleMatrix.pitch, 0.0))
		shotMatrixRotated.preMultiply(shotPositionMatrix)
		position = tuple(shotMatrixRotated.translation)
		
		if vehicle.isPlayerVehicle:
			target, targetID = atacker, attackerID
		else:
			target, targetID = victim, vehicle.id
		
		self.__battleData['hits'].append({
			'damageFactor': damageFactor,
			'effectsIndex': effectsIndex,
			'aimParts': vehicle.getAimParams(),
			'isExplosion': True,
			'position': position,
			'damage': (attackerID, vehicle.id, ) if damageFactor > 0 else 0,
			'isPlayer': vehicle.isPlayerVehicle,
			'attacker': {
				'id': targetID,
				'name': target['name'],
				'accountDBID': target['accountDBID'],
				'clanAbbrev': target['clanAbbrev'],
				'clanDBID': target['clanDBID']
			}
		})
		
		if targetID not in self.__battleData['vehicles']:
			self.__battleData['vehicles'][targetID] = target['vehicleType'].makeCompactDescr()
		