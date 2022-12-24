from items import vehicles

from ..events import g_eventsManager
from ..utils import getShell, getShellParams
from ..data import AbstractData

class CurrentBattle(AbstractData):

	@property
	def battle(self):
		return self.__battle

	@property
	def atacker(self):
		return self.__atacker

	@property
	def victim(self):
		return self.__victim

	@property
	def hit(self):
		return self.__hit

	def __init__(self):
		super(CurrentBattle, self).__init__()
		self.__battle = None
		self.__atacker = None
		self.__victim = None
		self.__hit = None

	def battleByID(self, battleID):
		self.clean()

		if self.battlesHistoryCtrl:
			self.__battle = self.battlesHistoryCtrl.getBattleByID(battleID)
			g_eventsManager.onChangedBattleData()

	def hitByID(self, hitID):

		hitData = self.__battle['hits'][hitID]

		attackerID, attackerCompDescID = hitData['attacker']
		victimID, victimCompDescID = hitData['victim']

		attackerInfo = self.__battle['players'][attackerID]
		victimInfo = self.__battle['players'][victimID]

		attackerCompDescStr = self.__battle['vehicles'][attackerID][attackerCompDescID]
		victimCompDescStr = self.__battle['vehicles'][victimID][victimCompDescID]

		attackerCompDesc = vehicles.VehicleDescr(compactDescr=attackerCompDescStr)
		victimCompDesc = vehicles.VehicleDescr(compactDescr=victimCompDescStr)

		shellType, shellSplash, _ = getShellParams(attackerCompDesc, hitData['effectsIndex'])

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
			'position': hitData['position'],
			'descriptor': getShell(attackerCompDesc, hitData['effectsIndex'])
		}

		g_eventsManager.onChangedHitData()

	def clean(self):
		self.__battle = None
		self.__atacker = None
		self.__victim = None
		self.__hit = None
