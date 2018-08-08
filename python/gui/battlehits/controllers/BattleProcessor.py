
import BattleReplay
import BigWorld
import Math
from items import vehicles
from vehicle_systems.tankStructure import ModelStates
from VehicleEffects import DamageFromShotDecoder

from gui.battlehits._constants import SETTINGS
from gui.battlehits.controllers import g_controllers
from gui.battlehits.events import g_eventsManager

class BattleProcessor(object):
	
	trackBattle = property(lambda self: not BattleReplay.isPlaying() or (BattleReplay.isPlaying() and \
										g_controllers.settings.get(SETTINGS.PROCESS_REPLAYS, False)))
	
	def __init__(self):
		self.__battleData = None
		self.__isAlive = True
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
				'common': {
					'arenaUniqueID': player.arenaUniqueID,
					'arenaTypeID': player.arenaTypeID,
					'arenaBonusType': player.arenaBonusType,
					'arenaGuiType': player.arenaGuiType,
					'playerVehicleID': player.playerVehicleID
				},
				'hits': [],
				'players': {},
				'vehicles': {}
			}

			_vehicleID = player.playerVehicleID
			_vehicle = player.arena.vehicles.get(_vehicleID)
			
			self.__saveCompactDescr(_vehicleID, _vehicle)
			self.__savePlayerInfo(_vehicleID, _vehicle, _vehicleID)

		self.__isAlive = player.vehicle.isAlive()
		
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

		self.__isAlive = False
		
		# validate all hititems 
		# in case of battlereplay with x8-x16 speed
		self.__battleData['hits'] = [hitCtx for hitCtx in self.__battleData['hits'] if isinstance(hitCtx['damage'], int)]

		if g_controllers.battlesHistory and self.__battleData:
			g_controllers.battlesHistory.addBattle(self.__battleData)
	
	def processEnterWorld(self, vehicle):
		
		if not self.trackBattle:
			return
		
		if not self.__isAlive:
			return
		
		try:
			self.__vehicles[vehicle.id] = int(vehicle.health) if vehicle.isCrewActive else 0
		except:
			self.__vehicles[vehicle.id] = -1
	
	def processHealthChanged(self, vehicle, newHealth, attackerID, attackReasonID):
		
		if not self.trackBattle or not self.__isAlive or not attackerID:
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

		if not self.trackBattle or not self.__isAlive or not vehicle.isPlayerVehicle:
			return
		
		if modelState != ModelStates.UNDAMAGED:
			self.__isAlive = True

	def processShot(self, vehicle, attackerID, points, effectsIndex, damageFactor):
		
		if not self.trackBattle or not self.__isAlive or not attackerID:
			return
		
		player, victimID = BigWorld.player(), vehicle.id
		atacker = player.arena.vehicles.get(attackerID)
		victim = player.arena.vehicles.get(vehicle.id)
		
		if not atacker['vehicleType'] or not victim['vehicleType']:
			return
		
		if victimID != player.playerVehicleID and attackerID != player.playerVehicleID:
			return
		
		shotDescr = vehicles.g_cache.shotEffects[effectsIndex]
		if 'airstrikeID' in shotDescr or 'artilleryID' in shotDescr:
			return
		
		attackerCompDescID = self.__saveCompactDescr(attackerID, atacker)
		victimCompDescID = self.__saveCompactDescr(victimID, victim)
		self.__savePlayerInfo(attackerID, atacker, player.playerVehicleID)
		self.__savePlayerInfo(victimID, victim, player.playerVehicleID)

		pointsData = []
		for point in points:
			compIdx, hitEffectCode, startPoint, endPoint = DamageFromShotDecoder.decodeSegment(point, vehicle.appearance.collisions)
			pointsData.append((compIdx, hitEffectCode, tuple(startPoint), tuple(endPoint)))
		
		self.__battleData['hits'].append({
			'damageFactor': damageFactor,
			'effectsIndex': effectsIndex,
			'aimParts': vehicle.getAimParams(),
			'isExplosion': False,
			'position': None,
			'points': pointsData,
			'damage': (attackerID, victimID, ) if damageFactor > 0 else 0,
			'attacker': [attackerID, attackerCompDescID],
			'victim': [victimID, victimCompDescID]
		})

	def processExplosion(self, vehicle, attackerID, center, effectsIndex, damageFactor):
		
		if not self.trackBattle or not self.__isAlive or not attackerID:
			return
		
		player, victimID = BigWorld.player(), vehicle.id
		atacker = player.arena.vehicles.get(attackerID)
		victim = player.arena.vehicles.get(vehicle.id)
		
		if not atacker['vehicleType'] or not victim['vehicleType']:
			return
		
		if victimID != player.playerVehicleID and attackerID != player.playerVehicleID:
			return
		
		shotDescr = vehicles.g_cache.shotEffects[effectsIndex]
		if 'airstrikeID' in shotDescr or 'artilleryID' in shotDescr:
			return
		
		vehicleMatrix = Math.Matrix(vehicle.model.matrix)
		shotPosition = center - vehicle.position
		shotPositionMatrix = Math.Matrix()
		shotPositionMatrix.setTranslate(shotPosition)
		shotMatrixRotated = Math.Matrix()
		shotMatrixRotated.setRotateYPR((-vehicleMatrix.yaw, -vehicleMatrix.pitch, 0.0))
		shotMatrixRotated.preMultiply(shotPositionMatrix)
		position = tuple(shotMatrixRotated.translation)
		
		attackerCompDescID = self.__saveCompactDescr(attackerID, atacker)
		victimCompDescID = self.__saveCompactDescr(victimID, victim)
		self.__savePlayerInfo(attackerID, atacker, player.playerVehicleID)
		self.__savePlayerInfo(victimID, victim, player.playerVehicleID)

		self.__battleData['hits'].append({
			'damageFactor': damageFactor,
			'effectsIndex': effectsIndex,
			'aimParts': vehicle.getAimParams(),
			'isExplosion': True,
			'position': position,
			'points': None,
			'damage': (attackerID, vehicle.id, ) if damageFactor > 0 else 0,
			'attacker': [attackerID, attackerCompDescID],
			'victim': [victimID, victimCompDescID]
		})
	
	def __saveCompactDescr(self, vehicleID, vehicle):
		
		if vehicleID not in self.__battleData['vehicles']:
			self.__battleData['vehicles'][vehicleID] = []
		
		compactDescr = vehicle['vehicleType'].makeCompactDescr()
		if compactDescr not in self.__battleData['vehicles'][vehicleID]:
			self.__battleData['vehicles'][vehicleID].append(compactDescr)
		
		compactDescrIDx = self.__battleData['vehicles'][vehicleID].index(compactDescr)

		return compactDescrIDx
	
	def __savePlayerInfo(self, vehicleID, vehicle, playerVehicleID):
		
		if vehicleID not in self.__battleData['players']:
			
			self.__battleData['players'][vehicleID] = {
				'name': vehicle['name'],
				'accountDBID': vehicle['accountDBID'],
				'clanAbbrev': vehicle['clanAbbrev'],
				'clanDBID': vehicle['clanDBID'],
				'isPlayer': vehicleID == playerVehicleID
			}
