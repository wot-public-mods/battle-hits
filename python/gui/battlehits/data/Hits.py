
from items import vehicles
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI

from .._constants import SETTINGS
from ..events import g_eventsManager
from ..lang import l10n
from ..utils import getShellParams
from ..data import AbstractDataProvider

_SORTING_LABELS = {
	1: l10n('hits.sorting.num'),
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
	0: l10n('hits.shotResult.armorPiercesNoDamage'),
	1: l10n('hits.shotResult.intermediateRicochet'),
	2: l10n('hits.shotResult.finalRicochet'),
	3: l10n('hits.shotResult.armorNotPierces'),
	4: l10n('hits.shotResult.armorPierces'),
	5: l10n('hits.shotResult.criticalHit'),
	6: l10n('hits.shotResult.criticalHit'),
	7: l10n('hits.shotResult.splash'),
}

class Hits(AbstractDataProvider):

	@property
	def sortingVO(self):
		return self.__sortingVO

	def __init__(self):
		super(Hits, self).__init__()
		self.dataVO = []
		self.selectedIndex = -1
		self.__data = []
		self.__sortingVO = []
		self.__sortingReversed = self.settingsCtrl.get(SETTINGS.SORTING_REVERSED)
		self.__sortingRule = self.settingsCtrl.get(SETTINGS.SORTING_RULE)
		self.__hitsToPlayer = self.settingsCtrl.get(SETTINGS.HITS_TO_PLAYER, True)

		self.__sortingMap = {
			1 : (int, "id", True),
			2 : (str, "vehicle", False),
			3 : (sum, "result", True),
			4 : (int, "damage", True)
		}

	def init(self):
		self.updateData()
		g_eventsManager.onSettingsChanged += self.__onSettingsChanged
		g_eventsManager.onChangedHitData += self.__updateData

	def __updateData(self):
		self.updateData()
		g_eventsManager.invalidateHitsDP()

	def __onSettingsChanged(self, key, value):
		if key == SETTINGS.HITS_TO_PLAYER:
			if value == self.__hitsToPlayer:
				return
			self.__hitsToPlayer = value
			self.stateCtrl.currentHitID = self.desiredID
			g_eventsManager.invalidateHitsDP()

	def updateData(self):
		self.__data = []
		self.dataVO = []

		if not self.battlesHistoryCtrl or not self.battlesHistoryCtrl.history:
			return

		if self.stateCtrl.currentBattleID is None:
			return

		currentBattle = self.battlesHistoryCtrl.history[self.stateCtrl.currentBattleID]

		hitNumber = 1

		for hitID, hitData in enumerate(currentBattle['hits']):
			attackerID, attackerCompDescID = hitData['attacker']
			victimID, victimCompDescID = hitData['victim']
			attackerInfo = currentBattle['players'][attackerID]
			victimInfo = currentBattle['players'][victimID]

			if self.__hitsToPlayer and victimInfo['isPlayer'] and not attackerInfo['isPlayer']:
				vehicleCompDesc = vehicles.VehicleDescr(compactDescr=currentBattle['vehicles'][attackerID][attackerCompDescID])
				shellType, _ = getShellParams(vehicleCompDesc, hitData['effectsIndex'])
			elif not self.__hitsToPlayer and not victimInfo['isPlayer'] and attackerInfo['isPlayer']:
				vehicleCompDesc = vehicles.VehicleDescr(compactDescr=currentBattle['vehicles'][attackerID][attackerCompDescID])
				shellType, _ = getShellParams(vehicleCompDesc, hitData['effectsIndex'])
				vehicleCompDesc = vehicles.VehicleDescr(compactDescr=currentBattle['vehicles'][victimID][victimCompDescID])
			else:
				continue

			# skip hit if shell is not shell (gaus gun of waffentrager, etc)
			if shellType is None:
				continue

			hitResult = [max(_RESULT_LABELS)] if hitData['isExplosion'] else [hitData['points'][-1:][0][1]]
			if hitResult != [4] and hitData['damageFactor'] > 0:
				hitResult += [4]

			if attackerInfo['isPlayer']:
				anonymized = victimInfo['accountDBID'] == 0
			else:
				anonymized = attackerInfo['accountDBID'] == 0

			self.__data.append({
				"id": hitID,
				"number": hitNumber,
				"vehicle": vehicleCompDesc.type.shortUserString,
				"result": hitResult,
				"shell": shellType,
				"damage": hitData["damage"],
				'anonymized': anonymized
			})

			hitNumber += 1

		self.__updateSorting()
		self.__generateVO()

	def __generateVO(self):
		self.dataVO = []

		if not self.__data:
			return

		for itemData in self.__data:
			resultLabel = " + ".join([_RESULT_LABELS[x] for x in itemData["result"]])
			shellLabel = _SHELL_LABELS[itemData["shell"]]
			damageLabel = str(itemData["damage"]) if itemData["damage"] > 0 else "--"
			self.dataVO.append({
				"id": itemData["id"],
				"numberLabel": str(itemData["number"]),
				"vehicleLabel": itemData["vehicle"],
				"resultLabel": resultLabel,
				"shellLabel": shellLabel,
				"damageLabel": damageLabel,
				'anonymized': itemData['anonymized']
			})

	def __updateSorting(self, appendReverse=False):
		rule = self.__sortingMap[self.__sortingRule]

		if appendReverse:
			self.__sortingReversed = rule[2]

		self.__data = sorted(self.__data, key=lambda x: rule[0](x[rule[1]]),
							reverse=self.__sortingReversed)

		if self.__data:
			def genSortItemVO(id, label):
				return {'id': id, 'label': label, 'active': self.__sortingRule == id,
						'reversed': self.__sortingReversed}

			self.__sortingVO = [genSortItemVO(x, _SORTING_LABELS[x]) for x in xrange(1, 5)]

			for itemID, itemData in enumerate(self.__data):
				if self.stateCtrl.currentHitID == itemData["id"]:
					self.selectedIndex = itemID
					break

	def sort(self, row):
		if row == self.__sortingRule:
			self.__sortingReversed = not self.__sortingReversed
			self.__updateSorting()
		else:
			self.__sortingRule = row
			self.__updateSorting(True)

		self.__generateVO()

		g_eventsManager.invalidateHitsDP()

		self.settingsCtrl.apply({SETTINGS.SORTING_REVERSED: self.__sortingReversed,
									SETTINGS.SORTING_RULE: self.__sortingRule})

	def clean(self):
		g_eventsManager.onSettingsChanged -= self.__onSettingsChanged
		g_eventsManager.onChangedHitData -= self.__updateData

		self.selectedIndex = -1
		self.dataVO = []
