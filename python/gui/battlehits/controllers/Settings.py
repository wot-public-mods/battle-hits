import cPickle
import os
import zlib

from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION

from gui.battlehits.events import g_eventsManager
from gui.battlehits._constants import DEFAULT_SETTINGS, SETTINGS_FILE, SETTINGS_VERSION
from gui.battlehits.controllers import AbstractController

class Settings(AbstractController):

	def __init__(self):
		super(Settings, self).__init__()
		self.__settings = DEFAULT_SETTINGS

	def init(self):
		self.__loadData()

	def fini(self):
		self.__saveData()

	def get(self, name, defaultValue=None):
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
		settings_dir = os.path.dirname(SETTINGS_FILE)

		try:
			if not os.path.isdir(settings_dir):
				os.makedirs(settings_dir)
		except IOError:
			LOG_ERROR('Failed to create directory for settings files')
		except Exception:
			LOG_CURRENT_EXCEPTION()

		try:
			if os.path.isfile(SETTINGS_FILE):
				data = None
				with open(SETTINGS_FILE, 'rb') as fh:
					data = fh.read()
					settings, version = cPickle.loads(zlib.decompress(data))
					if version == SETTINGS_VERSION:
						succes = True
						self.__settings = settings
		except Exception: #NOSONAR
			LOG_ERROR('Error while unpickling settings data information', data)

		if not succes:
			self.__saveData()

	def __saveData(self):

		settings_dir = os.path.dirname(SETTINGS_FILE)

		try:
			if not os.path.isdir(settings_dir):
				os.makedirs(settings_dir)
		except IOError:
			LOG_ERROR('Failed to create directory for settings files')
			return
		except Exception:
			LOG_CURRENT_EXCEPTION()
			return

		try:
			with open(SETTINGS_FILE, 'wb') as fh:
				data = zlib.compress(cPickle.dumps((self.__settings, SETTINGS_VERSION)), 1)
				fh.write(data)
		except IOError:
			LOG_ERROR('Failed to write settings file')
			return
		except Exception:
			LOG_CURRENT_EXCEPTION()
			return
