import datetime
import ArenaType
from helpers import i18n
from items import vehicles

from gui.battlehits.events import g_eventsManager
from gui.battlehits.lang import l10n
from gui.battlehits.data import AbstractDataProvider

def getVehicleLabel(battleData):
	# get playerVehicleID from players ctx list
	playerVehicleID = None
	for vehicleID, userCtx in battleData['players'].iteritems():
		if userCtx['isPlayer']:
			playerVehicleID = vehicleID
			break
	if not playerVehicleID:
		return ""
	if playerVehicleID not in battleData['vehicles']:
		return ""
	resultStr = ""
	vehiclesCounter = 0
	# in case multivehicles
	for compactDescr in battleData['vehicles'][playerVehicleID]:
		try:
			vehicle = vehicles.VehicleDescr(compactDescr=compactDescr)
		except: # dont raise on "compact descriptor to XML mismatch"
			continue
		vName = vehicle.type.shortUserString
		if resultStr and vName != resultStr:
			vehiclesCounter += 1
		else:
			resultStr = vName
	if vehiclesCounter:
		resultStr += l10n('ui.battle.multiVehicle') % str(vehiclesCounter)
	return resultStr


class Battles(AbstractDataProvider):

	def __init__(self):
		super(Battles, self).__init__()
		self.dataVO = []
		self.selectedIndex = -1
		self.__sortingReversed = True
		self.__sortingRule = (int, "id")

	def init(self):
		g_eventsManager.onChangedBattleData += self.__updateData
		self.updateData()

	def __updateData(self):
		self.updateData()
		g_eventsManager.invalidateBattlesDP()

	def updateData(self):
		self.dataVO = []
		self.selectedIndex = -1

		if not self.battlesHistoryCtrl or not self.battlesHistoryCtrl.history:
			return

		for battleID, battleData in enumerate(self.battlesHistoryCtrl.history):

			arenaTypeID = battleData['common']['arenaTypeID']

			if arenaTypeID not in ArenaType.g_cache:
				continue

			battleStartTime = battleData['common']['arenaUniqueID'] & 4294967295L
			battleStartLabel = datetime.datetime.fromtimestamp(battleStartTime).strftime('%d.%m.%Y %H:%M:%S')

			vehicleNameLabel = getVehicleLabel(battleData)
			if not vehicleNameLabel:
				continue

			self.dataVO.append({
				"id": battleID,
				"mapNameLabel": i18n.makeString(ArenaType.g_cache[arenaTypeID].name),
				"vehicleNameLabel": vehicleNameLabel,
				"battleStartLabel": battleStartLabel
			})

		rule = self.__sortingRule
		self.dataVO = sorted(self.dataVO, key=lambda x: rule[0](x[rule[1]]), reverse=self.__sortingReversed)

		for itemID, battleVO in enumerate(self.dataVO):
			if battleVO["id"] == self.stateCtrl.currentBattleID:
				self.selectedIndex = itemID
				break

	def clean(self):
		g_eventsManager.onChangedBattleData -= self.__updateData
		self.selectedIndex = -1
		self.dataVO = []
