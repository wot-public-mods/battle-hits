
from items import vehicles

from gui.battlehits._constants import SETTINGS
from gui.battlehits.controllers import g_controllers
from gui.battlehits.events import g_eventsManager
from gui.battlehits.lang import l10n
from gui.battlehits.utils import getShellParams

_SORTING_LABELS = {
	1: l10n('hits.sorting.tank'),
	2: l10n('hits.sorting.result'),
	3: l10n('hits.sorting.damage')
}

_SHELL_LABELS = {
	0: l10n('hits.shellType.ap'),
	1: l10n('hits.shellType.apcr'),
	2: l10n('hits.shellType.heap'),
	3: l10n('hits.shellType.he'),
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

class Hits(object):
	
	dataVO = property(lambda self : self.__dataVO)
	sortingVO = property(lambda self : self.__sortingVO)
	selectedIndex = property(lambda self : self.__selectedIndex)
	nextItemID = property(lambda self : self.__getItemID(1))
	prevItemID = property(lambda self : self.__getItemID(-1))
	hitsToPlayer = property(lambda self : self.__hitsToPlayer)
	desiredID = property(lambda self : self.__getDesiredID())

	def __init__(self):
		self.__data = []
		self.__dataVO = []
		self.__sortingVO = []
		self.__selectedIndex = -1
		self.__sortingReversed = g_controllers.settings.get(SETTINGS.SORTING_REVERSED)
		self.__sortingRule = g_controllers.settings.get(SETTINGS.SORTING_RULE)
		self.__hitsToPlayer = g_controllers.settings.get(SETTINGS.HITS_TO_PLAYER, True)
		self.__sortingMap = {
			1 : (str, "vehicle", False),
			2 : (sum, "result", True),
			3 : (int, "damage", True)
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
				g_controllers.state.currentHitID = self.desiredID
				g_eventsManager.invalidateHitsDP()
	
	def updateData(self):
		
		self.__data = []
		self.__dataVO = []
		
		battlesHistory = g_controllers.battlesHistory
		if not battlesHistory or not battlesHistory.history:
			return
		
		if battlesHistory.history and g_controllers.state.currentBattleID is not None:
			
			currentBattle = battlesHistory.history[g_controllers.state.currentBattleID]

			for hitID, hitData in enumerate(currentBattle['hits']):
				
				hitResult = [6] if hitData['isExplosion'] else [hitData['points'][-1:][0][1]]
				if hitResult != [4] and hitData['damageFactor'] > 0:
					hitResult += [4]
				
				vehicle = vehicles.VehicleDescr(compactDescr = currentBattle['vehicles'][hitData['attacker']['id']])
				if self.__hitsToPlayer:
					shellType, _ = getShellParams(vehicle, hitData['effectsIndex'])
				else:
					playerVehicle = vehicles.VehicleDescr(compactDescr = currentBattle['playerCompactDescr'])
					shellType, _ = getShellParams(playerVehicle, hitData['effectsIndex'])
				
				if self.__hitsToPlayer and hitData['isPlayer']:
					self.__data.append({
						"id": hitID,
						"vehicle": vehicle.type.shortUserString,
						"result": hitResult,
						"shell": shellType,
						"damage": hitData["damage"]
					})
				if not self.__hitsToPlayer and not hitData['isPlayer']:
					self.__data.append({
						"id": hitID,
						"vehicle": vehicle.type.shortUserString,
						"result": hitResult,
						"shell": shellType,
						"damage": hitData["damage"]
					})
			
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
					"enemyTankLabel": itemData["vehicle"],
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
			
			self.__sortingVO = [ genSortItemVO(x, _SORTING_LABELS[x]) for x in xrange(1, 4) ]
		
			for itemID, itemData in enumerate(self.__data):
				if g_controllers.state.currentHitID == itemData["id"]:
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

		g_controllers.settings.apply({SETTINGS.SORTING_REVERSED: self.__sortingReversed, \
									SETTINGS.SORTING_RULE: self.__sortingRule})
	
	def clean(self):
		
		g_eventsManager.onSettingsChanged -= self.__onSettingsChanged
		g_eventsManager.onChangedHitData -= self.__updateData
		
		self.__selectedIndex = -1
		self.__dataVO = []
