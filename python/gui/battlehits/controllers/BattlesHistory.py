# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

import cPickle
import os
import zlib

import BattleReplay
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION

from .._constants import CACHE_FILE, CACHE_VERSION, SETTINGS
from ..controllers import AbstractController
from ..events import g_eventsManager

class BattlesHistory(AbstractController):

	def __init__(self):
		super(BattlesHistory, self).__init__()
		self.__battles = list()

	def init(self):
		self.__loadData()

	def fini(self):
		if self.settingsCtrl.get(SETTINGS.SAVE_ONLY_SESSION, True):
			self.__battles = list()
		self.__saveData()

	@property
	def	history(self):
		return self.__battles

	def getBattleByUniqueID(self, arenaUniqueID):
		if self.__battles:
			for idx, battle in enumerate(self.__battles):
				if battle['common']['arenaUniqueID'] != arenaUniqueID:
					continue
				return idx, battle
		return None, None

	def getBattleByID(self, battleID):
		if self.__battles:
			for idx, battle in enumerate(self.__battles):
				if idx != battleID:
					continue
				return battle
		return None

	def addBattle(self, data):

		# skip battle if its replay and user disable replays record
		if BattleReplay.isPlaying() and not self.settingsCtrl.get(SETTINGS.PROCESS_REPLAYS, False):
			return

		# store or update battle data
		idx, _ = self.getBattleByUniqueID(data['common']['arenaUniqueID'])
		if idx is not None:
			self.__battles[idx] = data
		else:
			self.__battles.append(data)

	def deleteHistory(self):
		self.__battles = list()
		self.currentBattleData.clean()
		g_eventsManager.onChangedBattleData()
		g_eventsManager.onChangedHitData()
		self.stateCtrl.currentBattleID = None
		self.stateCtrl.currentHitID = None

	def __loadData(self):

		if BattleReplay.isPlaying() and not self.settingsCtrl.get(SETTINGS.PROCESS_REPLAYS, False):
			return

		succes = False
		cache_dir = os.path.dirname(CACHE_FILE)

		try:
			if not os.path.isdir(cache_dir):
				os.makedirs(cache_dir)
		except IOError:
			LOG_ERROR('Failed to create directory for cache files')
		except Exception:
			LOG_CURRENT_EXCEPTION()

		try:
			if os.path.isfile(CACHE_FILE):
				with open(CACHE_FILE, 'rb') as fh:
					data = fh.read()
					battles, version = cPickle.loads(zlib.decompress(data))
					if version == CACHE_VERSION:
						succes = True
						self.__battles = battles
		except Exception:
			LOG_ERROR('Error while unpickling cache data information', data)

		if not succes:
			self.__saveData()

	def __saveData(self):

		cache_dir = os.path.dirname(CACHE_FILE)

		try:
			if not os.path.isdir(cache_dir):
				os.makedirs(cache_dir)
		except IOError:
			LOG_ERROR('Failed to create directory for cache files')
			return
		except Exception:
			LOG_CURRENT_EXCEPTION()
			return

		try:
			with open(CACHE_FILE, 'wb') as fh:
				data = zlib.compress(cPickle.dumps((self.__battles, CACHE_VERSION)), 1)
				fh.write(data)
		except IOError:
			LOG_ERROR('Failed to write cache file')
			return
		except Exception:
			LOG_CURRENT_EXCEPTION()
			return
