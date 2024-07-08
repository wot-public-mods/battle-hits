# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

import BattleReplay
import BigWorld
import Math
from constants import ATTACK_REASON
from items import vehicles
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.tankStructure import ModelStates
from VehicleEffects import DamageFromShotDecoder

from .._constants import SETTINGS
from ..events import g_eventsManager
from ..controllers import AbstractController
from ..utils import simplifyVehicleCompactDescr

class BattleProcessor(AbstractController):

	guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

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

		# if the user chooses the observer mode in the training room
		# we skip the battle.
		if player.isObserver():
			return

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

		self.__isAlive = player.isVehicleAlive

		self.__vehicles = {}

		arenaDP = self.guiSessionProvider.getArenaDP()
		for vInfoVO in arenaDP.getVehiclesInfoIterator():
			self.__vehicles[vInfoVO.vehicleID] = vInfoVO.vehicleType.maxHealth

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

	def processVehicleInit(self, vehicle):
		
		# update isAlive state for respawned vehicle
		if vehicle and vehicle.isPlayerVehicle:
			self.__isAlive = vehicle.isAlive()

		if not all([self.trackBattle, self.__battleData, self.__isAlive]):
			return

		try:
			self.__vehicles[vehicle.id] = int(vehicle.health) if vehicle.isAlive() else 0
		except: #NOSONAR
			self.__vehicles[vehicle.id] = -1

	def processHealthChanged(self, vehicle, newHealth, attackerID, attackReasonID):
		
		# skip if any condition fired
		if not all([self.trackBattle, self.__battleData, self.__isAlive]):
			return

		# we got uninitialized vehicle as victim
		if vehicle.id not in self.__vehicles:
			return

		# get damage from HP Cache
		damage = self.__vehicles[vehicle.id]
		if newHealth > 0:
			damage = self.__vehicles[vehicle.id] - newHealth
		self.__vehicles[vehicle.id] = newHealth

		# skip if atacker is not Vehicle
		if not attackerID:
			return

		# skip if atack reason is not shot
		if attackReasonID != ATTACK_REASON.getIndex(ATTACK_REASON.SHOT):
			return

		# skip if atacker and victim is not a player
		if not vehicle.isPlayerVehicle and attackerID != BigWorld.player().playerVehicleID:
			return

		# find target hit, and update data there
		for hitIdx, hitCtx in enumerate(self.__battleData['hits']):
			if isinstance(hitCtx['damage'], tuple):
				_attackerID, _victimID = hitCtx['damage']
				if _attackerID == attackerID and _victimID == vehicle.id:
					self.__battleData['hits'][hitIdx]['damage'] = damage
					break

	def onModelsRefresh(self, vehicle, modelState):

		if not all([self.trackBattle, self.__battleData]):
			return

		if vehicle is None or not vehicle.isPlayerVehicle:
			return

		self.__isAlive = modelState == ModelStates.UNDAMAGED

	def processShot(self, vehicle, attackerID, points, effectsIndex, damageFactor):

		victimID = vehicle.id
		compDescIDs = self.__hitPreparation(attackerID, victimID, effectsIndex)
		if not compDescIDs:
			return
		attackerCompDescID, victimCompDescID = compDescIDs

		pointsData = []
		for point in points:
			maxComponentIdx = vehicle.calcMaxComponentIdx()
			compIdx, hitEffectCode, startPoint, endPoint = DamageFromShotDecoder.decodeSegment(point,
															vehicle.appearance.collisions, maxComponentIdx,
															vehicle.appearance.typeDescriptor)
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

		victimID = vehicle.id
		compDescIDs = self.__hitPreparation(attackerID, victimID, effectsIndex)
		if not compDescIDs:
			return
		attackerCompDescID, victimCompDescID = compDescIDs

		vehicleMatrix = Math.Matrix(vehicle.model.matrix)
		shotPosition = center - vehicle.position
		shotPositionMatrix = Math.Matrix()
		shotPositionMatrix.setTranslate(shotPosition)
		shotMatrixRotated = Math.Matrix()
		shotMatrixRotated.setRotateYPR((-vehicleMatrix.yaw, -vehicleMatrix.pitch, 0.0))
		shotMatrixRotated.preMultiply(shotPositionMatrix)
		position = tuple(shotMatrixRotated.translation)

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

	def __hitPreparation(self, attackerID, victimID, effectsIndex):
		# skip if any condition gives False or None
		if not all([self.trackBattle, self.__battleData, self.__isAlive, attackerID]):
			return None

		player = BigWorld.player()

		# skip if player is not attacker or victim
		if player.playerVehicleID != victimID and player.playerVehicleID != attackerID:
			return None

		atacker = player.arena.vehicles.get(attackerID)
		victim = player.arena.vehicles.get(victimID)

		# skip if attacker or victim not presented (fog ow war)
		if not atacker or not victim:
			return None

		# skip if attacker or victim vehicleType not initizlized
		if not atacker['vehicleType'] or not victim['vehicleType']:
			return None

		# skip on use airstrike bombers or artilery strike
		shotDescr = vehicles.g_cache.shotEffects[effectsIndex]
		if 'airstrikeID' in shotDescr or 'artilleryID' in shotDescr:
			return None

		# save vehicles info
		attackerCompDescID = self.__saveCompactDescr(attackerID, atacker)
		victimCompDescID = self.__saveCompactDescr(victimID, victim)
		self.__savePlayerInfo(attackerID, atacker, player.playerVehicleID)
		self.__savePlayerInfo(victimID, victim, player.playerVehicleID)
		return attackerCompDescID, victimCompDescID

	def __saveCompactDescr(self, vehicleID, vehicle):

		if vehicleID not in self.__battleData['vehicles']:
			self.__battleData['vehicles'][vehicleID] = []

		if not vehicle or not vehicle['vehicleType']:
			return

		compactDescr = vehicle['vehicleType'].makeCompactDescr()
		compactDescr = simplifyVehicleCompactDescr(compactDescr)
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
