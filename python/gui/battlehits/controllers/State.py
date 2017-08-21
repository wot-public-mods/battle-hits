
from gui import ClientHangarSpace as chs
from gui.app_loader.loader import g_appLoader
from gui.ClientHangarSpace import g_clientHangarSpaceOverride
from gui.Scaleform.framework.managers.loaders import ViewLoadParams
from gui.shared.utils.HangarSpace import g_hangarSpace

from gui.battlehits.controllers import g_controllers
from gui.battlehits.data import g_data
from gui.battlehits.events import g_eventsManager
from gui.battlehits.battlehits_constants import BATTLE_HITS_VIEW_ALIAS

class State(object):
	
	enabled = property(lambda self : self.__enabled)
	
	def __setBattleID(self, battleID):
		
		if self.__currentBattleID == battleID:
			return
		
		for availableBattleID, _ in enumerate(g_controllers.battlesHistory.history):
			if availableBattleID != battleID:
				continue
			self.__currentBattleID = battleID
			g_data.currentBattle.battleByID(battleID)
			self.__currentHitID = None
			g_eventsManager.onChangedHitData()
			self.currentHitID = g_data.hits.desiredID
			break
	
	currentBattleID = property(lambda self : self.__currentBattleID, __setBattleID)
	
	def __setHitID(self, hitID):
		
		if hitID == -1:
			return

		if self.__currentHitID == hitID:
			return
		
		for availableHitID, _ in enumerate(g_data.currentBattle.battle['hits']):
			if availableHitID != hitID:
				continue
			self.__currentHitID = hitID
			g_data.currentBattle.hitByID(hitID)
			break
		
	currentHitID = property(lambda self : self.__currentHitID, __setHitID)
	
	def __init__(self):
		self.__enabled = False
		self.__currentBattleID = None
		self.__currentHitID = None
		self.__savedHangarData = {}
	
	def init(self): 
		pass

	def fini(self): 
		pass
	
	def switch(self):
		if not self.__enabled:
			self.enable()
		else:
			self.disable()
		
	def enable(self):
		self.__enabled = True
		
		if self.__currentBattleID is not None:
			
			g_data.currentBattle.battleByID(self.__currentBattleID)
			
			if self.__currentHitID is not None:
				g_data.currentBattle.hitByID(self.__currentHitID)
			else:
				self.currentHitID = 0
		else:
			self.currentBattleID = g_data.battles.desiredID
		
		
		self.__savedHangarData = {
			"_EVENT_HANGAR_PATHS": chs._EVENT_HANGAR_PATHS,
			"path": "spaces/hangar_v2"
		}
		
		if chs._EVENT_HANGAR_PATHS:
			self.__savedHangarData["path"] =  chs._EVENT_HANGAR_PATHS[g_hangarSpace.isPremium]
		else:
			self.__savedHangarData["path"] =  chs._getDefaultHangarPath(g_hangarSpace.isPremium)
		
		g_clientHangarSpaceOverride.setPath('battlehits', g_hangarSpace.isPremium)
		
		g_hangarSpace.onSpaceCreate += g_controllers.hangarScene.create
		g_hangarSpace.onSpaceCreate += g_controllers.hangarCamera.enable
		
		g_appLoader.getDefLobbyApp().loadView(ViewLoadParams(BATTLE_HITS_VIEW_ALIAS, BATTLE_HITS_VIEW_ALIAS), {})
	
	def disable(self):
		
		#g_eventsManager.closeUI()

		g_controllers.hangarCamera.disable()
		g_controllers.hangarScene.destroy()
		
		g_data.currentBattle.clean()
		
		chs._EVENT_HANGAR_PATHS = self.__savedHangarData["_EVENT_HANGAR_PATHS"]
		g_clientHangarSpaceOverride.setPath(self.__savedHangarData["path"], g_hangarSpace.isPremium)
		
		self.__enabled = False
