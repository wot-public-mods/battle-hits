
from items import vehicles
from debug_utils import LOG_ERROR, LOG_NOTE

from gui.battlehits._constants import SETTINGS
from gui.battlehits.controllers import g_controllers
from gui.battlehits.events import g_eventsManager
from gui.battlehits.utils import getShellParams

class CurrentBattle(object):
	
	battle = property(lambda self : self.__battle)
	atacker = property(lambda self : self.__atacker)
	victim = property(lambda self : self.__victim)
	
	def __init__(self):
		self.__battle = None
		self.__atacker = None
		self.__victim = None

		self.__hitsToPlayer = g_controllers.settings.get(SETTINGS.HITS_TO_PLAYER, True)
		
		g_eventsManager.onSettingsChanged += self.__onSettingsChanged
	
	def __onSettingsChanged(self, key, value):
		if key == SETTINGS.HITS_TO_PLAYER:
			self.__hitsToPlayer = value
	
	def battleByID(self, battleID):
		
		self.clean()
		
		if g_controllers.battlesHistory:
			_, battleData = g_controllers.battlesHistory.getBattleByID(battleID)
		else:
			return
		
		self.__battle = battleData
		
		g_eventsManager.onChangedBattleData()
	
	def hitByID(self, hitID):
		
		hitData = self.__battle['hits'][hitID]
		
		self.__victim = {
			'name': hitData['attacker']['name'],
			'accountDBID': hitData['attacker']['accountDBID'],
			'clanAbbrev': hitData['attacker']['clanAbbrev'],
			'clanDBID': hitData['attacker']['clanDBID'],
			'vehicle': {}
		}
		
		if hitData['isPlayer']:
			compactDescr = self.__battle['playerCompactDescr']
		else:
			compactDescr = self.__battle['vehicles'][hitData['attacker']['id']]
		
		self.__victim['compactDescr'] = vehicles.VehicleDescr(compactDescr = compactDescr)
		self.__victim['compactDescrStr'] = compactDescr

		if self.__hitsToPlayer:
			shellType, shellSplash = getShellParams(self.__victim['compactDescr'], hitData['effectsIndex'])
		else:
			playerVehicle = vehicles.VehicleDescr(compactDescr = self.__battle['playerCompactDescr'])
			shellType, shellSplash = getShellParams(playerVehicle, hitData['effectsIndex'])
		
		if hitData['isExplosion']:
			self.__victim['shot'] = (hitData['isExplosion'], shellType, hitData['position'], \
									shellSplash, hitData['damageFactor'])
		else:
			self.__victim['shot'] = (hitData['isExplosion'], shellType, hitData['points'], \
									shellSplash, hitData['damageFactor'])
		
		self.__atacker = { 'aimParts': hitData['aimParts'] }

		g_eventsManager.onChangedHitData()
	
	def clean(self):
		self.__battle = None
		self.__atacker = None
		self.__victim = None
		