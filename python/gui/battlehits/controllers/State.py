
from gui import ClientHangarSpace as chs
from gui.ClientHangarSpace import g_clientHangarSpaceOverride
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

from gui.battlehits.controllers import IController
from gui.battlehits.skeletons import IBattlesHistory, IHangarScene, IHangarCamera
from gui.battlehits.data import g_data
from gui.battlehits.events import g_eventsManager

class State(IController):
	
	hangarSpace = dependency.descriptor(IHangarSpace)
	battlesHistoryCtrl = dependency.descriptor(IBattlesHistory)
	hangarSceneCtrl = dependency.descriptor(IHangarScene)
	hangarCameraCtrl = dependency.descriptor(IHangarCamera)
	
	def __init__(self):
		super(State, self).__init__()
		self.__battleID = None
		self.__hitID = None
		self.__savedHangarData = {}
	
	@property
	def currentBattleID(self):
		return self.__battleID
	
	@currentBattleID.setter
	def currentBattleID(self, battleID):
		
		if self.__battleID == battleID:
			return
		
		for availableBattleID, _ in enumerate(self.battlesHistoryCtrl.history):
			if availableBattleID != battleID:
				continue
			self.__battleID = battleID
			g_data.currentBattle.battleByID(battleID)
			self.__hitID = None
			g_eventsManager.onChangedHitData()
			self.currentHitID = g_data.hits.desiredID
			break
	
	@property
	def currentHitID(self):
		return self.__hitID
	
	@currentHitID.setter
	def currentHitID(self, hitID):
		
		if self.__hitID == hitID:
			return
		
		if hitID == -1:
			self.__hitID = None
			if self.enabled:
				self.hangarSceneCtrl.noDataHit()
			return
		
		for availableHitID, _ in enumerate(g_data.currentBattle.battle['hits']):
			if availableHitID != hitID:
				continue
			self.__hitID = hitID
			g_data.currentBattle.hitByID(hitID)
			break
	
	def switch(self):
		if not self.enabled:
			self.enable()
		else:
			self.disable()
	
	def changeBattleID(self, battleID):
		
		if self.currentBattleID == battleID:
			return
		
		for availableBattleID, _ in enumerate(self.battlesHistoryCtrl.history):
			if availableBattleID != battleID:
				continue
			self.currentBattleID = battleID
			g_data.currentBattle.battleByID(battleID)
			if len(g_data.currentBattle.battle['hits']):
				self.currentHitID = g_data.hits.desiredID
			else:
				self.currentHitID = None

	def enable(self):
		
		if self.currentBattleID is not None:
			
			g_data.currentBattle.battleByID(self.currentBattleID)
			
			if self.currentHitID is not None:
				g_data.currentBattle.hitByID(self.currentHitID)
			else:
				self.currentHitID = 0
		else:
			self.currentBattleID = g_data.battles.desiredID
		
		
		self.__savedHangarData = {
			"_EVENT_HANGAR_PATHS": chs._EVENT_HANGAR_PATHS,
			"path": chs._getDefaultHangarPath(False)
		}
		
		if chs._EVENT_HANGAR_PATHS:
			self.__savedHangarData["path"] =  chs._EVENT_HANGAR_PATHS[self.hangarSpace.isPremium]
		
		g_clientHangarSpaceOverride.setPath('battlehits')
		
		self.hangarSpace.onSpaceCreate += self.hangarSceneCtrl.create
		self.hangarSpace.onSpaceCreate += self.hangarCameraCtrl.enable
		
		self.enabled = True
		
	def disable(self):
		
		self.hangarCameraCtrl.disable()
		self.hangarSceneCtrl.destroy()
		
		g_data.currentBattle.clean()
		
		chs._EVENT_HANGAR_PATHS = self.__savedHangarData["_EVENT_HANGAR_PATHS"]
		g_clientHangarSpaceOverride.setPath(self.__savedHangarData["path"], self.hangarSpace.isPremium)
		
		self.enabled = False

		g_eventsManager.closeUI()
		