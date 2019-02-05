
import BattleReplay
import BigWorld
import Math
from items import vehicles
from vehicle_systems.tankStructure import ModelStates, TankPartIndexes
from VehicleEffects import DamageFromShotDecoder

from gui.battlehits._constants import SETTINGS
from gui.battlehits.events import g_eventsManager
from gui.battlehits.controllers import AbstractController

class BattleProcessor(AbstractController):
	
	def __init__(self):
		super(BattleProcessor, self).__init__()
		self.__battleData = None
		self.__isAlive = False
		self.__vehicles = {}
		
	def init(self):	
		g_eventsManager.onShowBattle += self.__onShowBattle
		g_eventsManager.onDestroyBattle += self.__onDestroyBattle
	
	def fini(self):
		g_eventsManager.onShowBattle -= self.__onShowBattle
		g_eventsManager.onDestroyBattle -= self.__onDestroyBattle
	
	@property
	def trackBattle(self):
		isReplay = BattleReplay.isPlaying()
		if not isReplay:
			return True 
		if isReplay and self.settingsCtrl.get(SETTINGS.PROCESS_REPLAYS, False):
			return True
		return False
	
	def __onShowBattle(self):
		
		if not self.trackBattle:
			return
		
		player = BigWorld.player()

		processedData = None

		if self.battlesHistoryCtrl:
			_, processedData = self.battlesHistoryCtrl.getBattleByUniqueID(player.arenaUniqueID)
		
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
		
		if not all([self.trackBattle, self.__battleData]):
			return
		
		# validate all hititems 
		# in case of battlereplay with x8-x16 speed
		self.__battleData['hits'] = [hitCtx for hitCtx in self.__battleData['hits'] if isinstance(hitCtx['damage'], int)]

		if self.battlesHistoryCtrl:
			self.battlesHistoryCtrl.addBattle(self.__battleData)
		
		self.__battleData = None
		self.__vehicles = {}
	
	def processEnterWorld(self, vehicle):
		
		if not all([self.trackBattle, self.__battleData, self.__isAlive]):
			return
		
		try:
			self.__vehicles[vehicle.id] = int(vehicle.health) if vehicle.isCrewActive else 0
		except:
			self.__vehicles[vehicle.id] = -1
	
	def processHealthChanged(self, vehicle, newHealth, attackerID, attackReasonID):
		
		if not all([self.trackBattle, self.__battleData, self.__isAlive, attackerID]):
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
		
		if not all([self.trackBattle, self.__battleData, self.__isAlive]):
			return
		
		if vehicle is None or not vehicle.isPlayerVehicle:
			return
		
		if modelState == ModelStates.UNDAMAGED:
			self.__isAlive = True
		else:
			self.__isAlive = False
	
	def processShot(self, vehicle, attackerID, points, effectsIndex, damageFactor):
		
		if not all([self.trackBattle, self.__battleData, self.__isAlive, attackerID]):
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
			maxComponentIdx = TankPartIndexes.ALL[-1]
			wheelsConfig = vehicle.appearance.typeDescriptor.chassis.generalWheelsAnimatorConfig
			if wheelsConfig:
				maxComponentIdx = maxComponentIdx + wheelsConfig.getWheelsCount()
			compIdx, hitEffectCode, startPoint, endPoint = DamageFromShotDecoder.decodeSegment(point, vehicle.appearance.collisions, maxComponentIdx)
			
			# TODO implement vehicle whells
			# temporary skip hit to whell
			if compIdx > TankPartIndexes.ALL[-1]:
				return
			
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
		
		if not all([self.trackBattle, self.__battleData, self.__isAlive, attackerID]):
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
