
from items import vehicles

from gui.battlehits._constants import SETTINGS
from gui.battlehits.controllers import g_controllers
from gui.battlehits.events import g_eventsManager
from gui.battlehits.utils import getShellParams

class CurrentBattle(object):
	
	battle = property(lambda self : self.__battle)
	atacker = property(lambda self : self.__atacker)
	victim = property(lambda self : self.__victim)
	hit = property(lambda self : self.__hit)
	
	def __init__(self):
		self.__battle = None
		self.__atacker = None
		self.__victim = None
		self.__hit = None
	
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
		
		attackerID, attackerCompDescID = hitData['attacker']
		victimID, victimCompDescID = hitData['victim']

		attackerInfo = self.__battle['players'][attackerID]
		victimInfo = self.__battle['players'][victimID]

		attackerCompDescStr = self.__battle['vehicles'][attackerID][attackerCompDescID]
		victimCompDescStr = self.__battle['vehicles'][victimID][victimCompDescID]
		
		attackerCompDesc = vehicles.VehicleDescr(compactDescr = attackerCompDescStr)
		victimCompDesc = vehicles.VehicleDescr(compactDescr = victimCompDescStr)
		
		shellType, shellSplash = getShellParams(attackerCompDesc, hitData['effectsIndex'])
		
		self.__victim = {
			'name': victimInfo['name'],
			'accountDBID': victimInfo['accountDBID'],
			'clanAbbrev': victimInfo['clanAbbrev'],
			'clanDBID': victimInfo['clanDBID'],
			'isPlayer': victimInfo['isPlayer'],
			'compDescrStr': victimCompDescStr,
			'compDescr': victimCompDesc
		}
		
		self.__atacker = { 
			'name': attackerInfo['name'],
			'accountDBID': attackerInfo['accountDBID'],
			'clanAbbrev': attackerInfo['clanAbbrev'],
			'clanDBID': attackerInfo['clanDBID'],
			'isPlayer': attackerInfo['isPlayer'],
			'compDescrStr': attackerCompDescStr,
			'compDescr': attackerCompDesc
		}
		
		self.__hit = {
			'isExplosion': hitData['isExplosion'],
			'damageFactor': hitData['damageFactor'],
			'aimParts': hitData['aimParts'],
			'shellType': shellType,
			'shellSplash': shellSplash,
			'points': hitData['points'],
			'position': hitData['position']
		}

		g_eventsManager.onChangedHitData()
	
	def clean(self):
		self.__battle = None
		self.__atacker = None
		self.__victim = None
		self.__hit = None
		