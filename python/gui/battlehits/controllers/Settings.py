
import cPickle
import os
import zlib

import BigWorld

from gui.battlehits.events import g_eventsManager
from gui.battlehits.battlehits_constants import DEFAULT_SETTINGS, SETTINGS_FILE

from debug_utils import *

class Settings(object):
	
	def __init__(self):
		self.__settings = DEFAULT_SETTINGS
	
	def init(self):
		self.__loadData()
	
	def fini(self):
		self.__saveData()
	
	def get(self, name, defaultValue = None):
		if name in self.__settings:
			return self.__settings[name]
		return defaultValue
	
	def apply(self, data):
		for key, value in data.iteritems():
			if self.__settings[key] != value:
				self.__settings[key] = value
				g_eventsManager.onSettingsChanged(key, value)
			else:
				self.__settings[key] = value
	
	def __loadData(self):
		
		succes = False
		
		cacheDir = os.path.dirname(SETTINGS_FILE)
		
		if not os.path.isdir(cacheDir):
			os.makedirs(cacheDir)
		
		if os.path.isfile(SETTINGS_FILE):
			try:
				with open(SETTINGS_FILE, 'rb') as fh:
					data = fh.read()
					self.__settings = cPickle.loads(zlib.decompress(data))
					succes = True
			except Exception:
				LOG_ERROR('Error while unpickling settings data information', data) 
		
		if not succes:
			self.__saveData()
	
	def __saveData(self):
		
		with open(SETTINGS_FILE, 'wb') as fh:
			data = zlib.compress(cPickle.dumps(self.__settings), 1)
			fh.write(data)
