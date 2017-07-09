
import cPickle
import os
import zlib

import BattleReplay
from debug_utils import LOG_ERROR

from gui.battlehits.controllers import g_controllers
from gui.battlehits.battlehits_constants import CACHE_FILE

class BattlesHistory(object):
	
	history = property(lambda self : self.__battles)
	
	def __init__(self):
		self.__battles = list()
	
	def init(self):
		self.__loadData()
	
	def fini(self):
		if g_controllers.settings.get('saveOnlySession', True):
			self.__battles = list()
		self.__saveData()
	
	def getBattleByUniqueID(self, arenaUniqueID):
		if self.__battles:
			for idx, battle in enumerate(self.__battles):
				if battle['arena']['arenaUniqueID'] != arenaUniqueID:
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
		
		if BattleReplay.isPlaying() and not g_controllers.settings.get('processReplays', False):
			return
		
		idx, _ = self.getBattleByUniqueID(data['arena']['arenaUniqueID'])
		if idx is not None:
			self.__battles[idx] = data
			g_controllers.state.currentBattleID = idx
		else:
			self.__battles.append(data)
			g_controllers.state.currentBattleID = len(self.__battles) - 1
	
	def __loadData(self):
		
		if BattleReplay.isPlaying() and not g_controllers.settings.get('processReplays', False):
			return
		
		succes = False
		
		cacheDir = os.path.dirname(CACHE_FILE)
		
		if not os.path.isdir(cacheDir):
			os.makedirs(cacheDir)
		
		if os.path.isfile(CACHE_FILE):
			try:
				with open(CACHE_FILE, 'rb') as fh:
					data = fh.read()
					self.__battles = cPickle.loads(zlib.decompress(data))
					succes = True
			except Exception:
				LOG_ERROR('Error while unpickling cache data information', data) 
		
		if not succes:
			self.__saveData()
	
	def __saveData(self):
		
		with open(CACHE_FILE, 'wb') as fh:
			data = zlib.compress(cPickle.dumps(self.__battles), 1)
			fh.write(data)
