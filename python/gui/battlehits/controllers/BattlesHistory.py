
import cPickle
import os
import zlib

import BattleReplay
from debug_utils import LOG_ERROR

from gui.battlehits._constants import CACHE_FILE, CACHE_VERSION, SETTINGS
from gui.battlehits.controllers import AbstractController

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
				return (idx, battle)
		return (None, None)
	
	def getBattleByID(self, battleID):
		if self.__battles:
			for idx, battle in enumerate(self.__battles):
				if idx != battleID:
					continue
				return (idx, battle)
		return (None, None)
	
	def addBattle(self, data):
		
		if BattleReplay.isPlaying() and not self.settingsCtrl.get(SETTINGS.PROCESS_REPLAYS, False):
			return
		
		idx, _ = self.getBattleByUniqueID(data['common']['arenaUniqueID'])
		if idx is not None:
			self.__battles[idx] = data
			self.stateCtrl.changeBattleID(idx)
		else:
			self.__battles.append(data)
			self.stateCtrl.changeBattleID(len(self.__battles) - 1)
	
	def __loadData(self):
		
		if BattleReplay.isPlaying() and not self.settingsCtrl.get(SETTINGS.PROCESS_REPLAYS, False):
			return
		
		succes = False
		
		cacheDir = os.path.dirname(CACHE_FILE)
		
		if not os.path.isdir(cacheDir):
			os.makedirs(cacheDir)
		
		if os.path.isfile(CACHE_FILE):
			try:
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
		
		with open(CACHE_FILE, 'wb') as fh:
			data = zlib.compress(cPickle.dumps((self.__battles, CACHE_VERSION)), 1)
			fh.write(data)
