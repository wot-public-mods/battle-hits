
from items import vehicles
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI

from gui.battlehits._constants import SETTINGS
from gui.battlehits.events import g_eventsManager
from gui.battlehits.lang import l10n
from gui.battlehits.utils import getShellParams
from gui.battlehits.data import AbstractData

_SORTING_LABELS = {
	1: '№',
	2: l10n('hits.sorting.tank'),
	3: l10n('hits.sorting.result'),
	4: l10n('hits.sorting.damage')
}

_SHELL_LABELS = {
	0: INGAME_GUI.DAMAGELOG_SHELLTYPE_ARMOR_PIERCING,
	1: INGAME_GUI.DAMAGELOG_SHELLTYPE_ARMOR_PIERCING_CR,
	2: INGAME_GUI.DAMAGELOG_SHELLTYPE_HOLLOW_CHARGE,
	3: INGAME_GUI.DAMAGELOG_SHELLTYPE_HIGH_EXPLOSIVE,
}

_RESULT_LABELS = {
	0: l10n('hits.shotResult.intermediateRicochet'),
	1: l10n('hits.shotResult.finalRicochet'), 
	2: l10n('hits.shotResult.armorNotPierces'),
	3: l10n('hits.shotResult.armorPiercesNoDamage'), 
	4: l10n('hits.shotResult.armorPierces'),
	5: l10n('hits.shotResult.criticalHit'),
	6: l10n('hits.shotResult.splash'),
}

class Hits(AbstractData):
	
	dataVO = property(lambda self : self.__dataVO)
	sortingVO = property(lambda self : self.__sortingVO)
	selectedIndex = property(lambda self : self.__selectedIndex)
	nextItemID = property(lambda self : self.__getItemID(1))
	prevItemID = property(lambda self : self.__getItemID(-1))
	desiredID = property(lambda self : self.__getDesiredID())

	def __init__(self):
		super(Hits, self).__init__()
		self.__data = []
		self.__dataVO = []
		self.__sortingVO = []
		self.__selectedIndex = -1
		self.__sortingReversed = self.settingsCtrl.get(SETTINGS.SORTING_REVERSED)
		self.__sortingRule = self.settingsCtrl.get(SETTINGS.SORTING_RULE)
		self.__hitsToPlayer = self.settingsCtrl.get(SETTINGS.HITS_TO_PLAYER, True)
		
		self.__sortingMap = {
			1 : (int, "id", True),
			2 : (str, "vehicle", False),
			3 : (sum, "result", True),
			4 : (int, "damage", True)
		}
		
		self.updateData()

		g_eventsManager.onSettingsChanged += self.__onSettingsChanged
		g_eventsManager.onChangedHitData += self.__updateData
	
	def __updateData(self, _ = None):
		self.updateData()
		g_eventsManager.invalidateHitsDP()
	
	def __onSettingsChanged(self, key, value):
		if key == SETTINGS.HITS_TO_PLAYER:
			if value != self.__hitsToPlayer:
				self.__hitsToPlayer = value
				self.stateCtrl.currentHitID = self.desiredID
				g_eventsManager.invalidateHitsDP()
	
	def updateData(self):
		
		self.__data = []
		self.__dataVO = []
		
		if not self.battlesHistoryCtrl or not self.battlesHistoryCtrl.history:
			return
		
		if self.battlesHistoryCtrl.history and self.stateCtrl.currentBattleID is not None:
			
			currentBattle = self.battlesHistoryCtrl.history[self.stateCtrl.currentBattleID]
			
			playerHitID, enemyHitID = 1, 1

			for hitID, hitData in enumerate(currentBattle['hits']):
				
				attackerID, attackerCompDescID = hitData['attacker']
				victimID, victimCompDescID = hitData['victim']

				attackerInfo = currentBattle['players'][attackerID]
				victimInfo = currentBattle['players'][victimID]

				attackerCompDescStr = currentBattle['vehicles'][attackerID][attackerCompDescID]
				victimCompDescStr = currentBattle['vehicles'][victimID][victimCompDescID]
				
				attackerCompDesc = vehicles.VehicleDescr(compactDescr = attackerCompDescStr)
				victimCompDesc = vehicles.VehicleDescr(compactDescr = victimCompDescStr)
				
				shellType, shellSplash = getShellParams(attackerCompDesc, hitData['effectsIndex'])
				
				hitResult = [6] if hitData['isExplosion'] else [hitData['points'][-1:][0][1]]
				if hitResult != [4] and hitData['damageFactor'] > 0:
					hitResult += [4]
				
				if not self.__hitsToPlayer and not victimInfo['isPlayer'] and attackerInfo['isPlayer']:
					self.__data.append({
						"id": hitID,
						"number": playerHitID,
						"vehicle": victimCompDesc.type.shortUserString,
						"result": hitResult,
						"shell": shellType,
						"damage": hitData["damage"]
					})
					playerHitID += 1
				
				if self.__hitsToPlayer and victimInfo['isPlayer'] and not attackerInfo['isPlayer']:
					self.__data.append({
						"id": hitID,
						"number": enemyHitID,
						"vehicle": attackerCompDesc.type.shortUserString,
						"result": hitResult,
						"shell": shellType,
						"damage": hitData["damage"]
					})
					enemyHitID += 1
					
			self.__updateSorting()
			self.__generateVO()
	
	def __generateVO(self):
		
		self.__dataVO = []
		
		if self.__data:
			
			for itemData in self.__data:
				
				resultLabel = " + ".join([_RESULT_LABELS[x] for x in itemData["result"]])
				
				shellLabel = _SHELL_LABELS[itemData["shell"]]
				
				damageLabel = str(itemData["damage"]) if itemData["damage"] > 0 else "--"
				
				self.__dataVO.append({
					"id": itemData["id"],
					"numberLabel": str(itemData["number"]),
					"vehicleLabel": itemData["vehicle"],
					"resultLabel": resultLabel,
					"shellLabel": shellLabel,
					"damageLabel": damageLabel
				})
	
	def __updateSorting(self, appendReverse = False):
		
		rule = self.__sortingMap[self.__sortingRule]
		
		if appendReverse:
			self.__sortingReversed = rule[2]
		
		self.__data = sorted(self.__data, key = lambda x: rule[0](x[rule[1]]), \
							reverse = self.__sortingReversed)
		
		if self.__data:
			
			def genSortItemVO(id, label):
				return { 'id': id, 'label': label, 'active': self.__sortingRule == id, \
						'reversed': self.__sortingReversed }
			
			self.__sortingVO = [ genSortItemVO(x, _SORTING_LABELS[x]) for x in xrange(1, 5) ]
		
			for itemID, itemData in enumerate(self.__data):
				if self.stateCtrl.currentHitID == itemData["id"]:
					self.__selectedIndex = itemID
					break
	
	def __getDesiredID(self):
		result = -1
		self.updateData()
		if self.__dataVO:
			result = self.__dataVO[0]["id"]
		return result
	
	def __getItemID(self, offset):
		
		if self.__selectedIndex == -1:
			return -1
		
		destination = self.__selectedIndex + offset
		
		if len(self.__dataVO) > destination and destination > -1:
			return self.__dataVO[destination]['id']
		else:
			return self.__dataVO[self.__selectedIndex]['id']
		return 0
	
	def sort(self, row):
		
		if row == self.__sortingRule:
			self.__sortingReversed = not self.__sortingReversed
			self.__updateSorting()
		else:
			self.__sortingRule = row
			self.__updateSorting(True)
		
		self.__generateVO()
		
		g_eventsManager.invalidateHitsDP()

		self.settingsCtrl.apply({SETTINGS.SORTING_REVERSED: self.__sortingReversed, \
									SETTINGS.SORTING_RULE: self.__sortingRule})
	
	def clean(self):
		
		g_eventsManager.onSettingsChanged -= self.__onSettingsChanged
		g_eventsManager.onChangedHitData -= self.__updateData
		
		self.__selectedIndex = -1
		self.__dataVO = []
