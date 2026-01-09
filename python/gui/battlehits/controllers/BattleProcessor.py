# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2026 Andrii Andrushchyshyn

import BattleReplay
import BigWorld
import Math
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

	def __onDestroyBattle(self):

		if not all([self.trackBattle, self.__battleData]):
			return

		if self.battlesHistoryCtrl:
			self.battlesHistoryCtrl.addBattle(self.__battleData)

		self.__battleData = None

	def processVehicleInit(self, vehicle):

		if not all([self.trackBattle, self.__battleData]):
			return

		# update isAlive state for respawned vehicle
		if vehicle and vehicle.isPlayerVehicle:
			self.__isAlive = vehicle.isAlive()

	def onModelsRefresh(self, vehicle, modelState):

		if not all([self.trackBattle, self.__battleData]):
			return

		# update isAlive state by vehicle state
		if vehicle and vehicle.isPlayerVehicle:
			self.__isAlive = modelState == ModelStates.UNDAMAGED

	def processShot(self, vehicle, attackerID, hitPoints, effectsIndex, damage, damageFactor):

		victimID = vehicle.id
		compDescIDs = self.__hitPreparation(attackerID, victimID, effectsIndex)
		if not compDescIDs:
			return
		attackerCompDescID, victimCompDescID = compDescIDs

		pointsData = []
		for hitPoint in hitPoints:
			compIdx, hitEffectCode, startPoint, endPoint = DamageFromShotDecoder.parseHitPoint(hitPoint,
															vehicle.appearance.collisions)
			pointsData.append((compIdx, hitEffectCode, tuple(startPoint), tuple(endPoint)))

		self.__battleData['hits'].append({
			'damageFactor': damageFactor,
			'effectsIndex': effectsIndex,
			'aimParts': vehicle.getAimParams(),
			'isExplosion': False,
			'position': None,
			'points': pointsData,
			'damage': damage,
			'attacker': [attackerID, attackerCompDescID],
			'victim': [victimID, victimCompDescID]
		})

	def processExplosion(self, vehicle, attackerID, center, effectsIndex, damage, damageFactor):

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
			'damage': damage,
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
