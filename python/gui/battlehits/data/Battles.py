
import datetime
import ArenaType
from helpers import i18n
from items import vehicles

from gui.battlehits.controllers import g_controllers
from gui.battlehits.events import g_eventsManager

class Battles(object):
	
	dataVO = property(lambda self : self.__dataVO)
	selectedIndex = property(lambda self : self.__selectedIndex)
	nextItemID = property(lambda self : self.__getItemID(1))
	prevItemID = property(lambda self : self.__getItemID(-1))
	desiredID = property(lambda self : self.__getDesiredID())
	
	def __init__(self):
		
		self.__dataVO = []
		self.__sortingReversed = True
		self.__sortingRule = (int, "id")
		self.__selectedIndex = -1
		
		self.updateData()
		g_eventsManager.onChangedBattleData += self.updateData
	
	def updateData(self, _ = None):
		
		self.__dataVO = []
		self.__selectedIndex = -1
		
		battlesHistory = g_controllers.battlesHistory
		if not battlesHistory or not battlesHistory.history:
			return
		
		for battleID, battleData in enumerate(battlesHistory.history):
			
			arenaTypeID = battleData['arena']['arenaTypeID']
			playerVehicle = vehicles.VehicleDescr(compactDescr = battleData['playerCompactDescr'])
			battleStartTime = battleData['arena']['arenaUniqueID'] & 4294967295L
			
			mapNameLabel = i18n.makeString(ArenaType.g_cache[arenaTypeID].name)
			vehicleNameLabel = str(playerVehicle.type.shortUserString)
			battleStartLabel = datetime.datetime.fromtimestamp(battleStartTime).strftime('%d.%m.%Y %H:%M:%S')
			
			self.__dataVO.append({
				"id": battleID,
				"mapNameLabel": mapNameLabel,
				"vehicleNameLabel": vehicleNameLabel,
				"battleStartLabel": battleStartLabel
			})
		
		self.__dataVO = sorted(self.__dataVO, key = lambda x: self.__sortingRule[0](x[self.__sortingRule[1]]), reverse = self.__sortingReversed)
		
		for itemID, battleVO in enumerate(self.__dataVO):
			if battleVO["id"] == g_controllers.state.currentBattleID:
				self.__selectedIndex = itemID
				break
		
		g_eventsManager.invalidateBattlesDP()
	
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
	
	def clean(self):
		
		g_eventsManager.onChangedBattleData -= self.updateData
		
		self.__selectedIndex = -1
		self.__dataVO = []
