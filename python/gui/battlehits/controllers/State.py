
import BigWorld
from Account import PlayerAccount
from gui import ClientHangarSpace as chs
from gui.battlehits.controllers import AbstractController
from gui.battlehits.events import g_eventsManager
from gui.ClientHangarSpace import g_clientHangarSpaceOverride
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class State(AbstractController):

	hangarSpace = dependency.descriptor(IHangarSpace)

	def __init__(self):
		super(State, self).__init__()
		self.__battleID = None
		self.__hitID = None
		self.__savedHangarData = {}
		self.enabled = False

	@property
	def currentBattleID(self):
		return self.__battleID

	@currentBattleID.setter
	def currentBattleID(self, battleID):

		if battleID is None:
			self.__battleID = None
			return

		if self.__battleID == battleID:
			return

		for availableBattleID, _ in enumerate(self.battlesHistoryCtrl.history):
			if availableBattleID != battleID:
				continue
			self.__battleID = battleID
			self.currentBattleData.battleByID(battleID)
			self.__hitID = None
			g_eventsManager.onChangedHitData()
			self.currentHitID = self.hitsData.desiredID
			break

	@property
	def currentHitID(self):
		return self.__hitID

	@currentHitID.setter
	def currentHitID(self, hitID):

		if hitID is None:
			self.__hitID = None
			return

		if self.__hitID == hitID:
			return

		if hitID == -1:
			self.__hitID = None
			if self.enabled:
				self.hangarSceneCtrl.processNoData()
			return

		for availableHitID, _ in enumerate(self.currentBattleData.battle['hits']):
			if availableHitID != hitID:
				continue
			self.__hitID = hitID
			self.currentBattleData.hitByID(hitID)
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
			self.currentBattleData.battleByID(battleID)
			if self.currentBattleData.battle['hits']:
				self.currentHitID = self.hitsData.desiredID
			else:
				self.currentHitID = None

	def enable(self):
		if self.hangarSpace is None or self.hangarSpace.space is None:
			return

		if self.currentBattleID is not None:
			self.currentBattleData.battleByID(self.currentBattleID)
			if self.currentHitID is not None:
				self.currentBattleData.hitByID(self.currentHitID)
			else:
				self.currentHitID = 0
		else:
			self.currentBattleID = self.battlesData.desiredID

		self.__savedHangarData = {
			"_EVENT_HANGAR_PATHS": chs._EVENT_HANGAR_PATHS,
			"path": chs._getDefaultHangarPath(False)
		}

		if chs._EVENT_HANGAR_PATHS:
			self.__savedHangarData["path"] = chs._EVENT_HANGAR_PATHS[self.hangarSpace.isPremium][0]

		g_clientHangarSpaceOverride.setPath('battlehits')

		self.hangarSpace.onSpaceCreate += self.hangarSceneCtrl.create
		self.hangarSpace.onSpaceCreate += self.hangarCameraCtrl.enable

		self.enabled = True

	def disable(self):
		self.__battleID = None
		self.__hitID = None

		self.vehicleCtrl.removeVehicle()
		self.hangarCameraCtrl.disable()
		self.hangarSceneCtrl.destroy()
		self.currentBattleData.clean()

		chs._EVENT_HANGAR_PATHS = self.__savedHangarData["_EVENT_HANGAR_PATHS"]

		isHangar = isinstance(BigWorld.player(), PlayerAccount)
		if isHangar:
			g_clientHangarSpaceOverride.setPath(path=self.__savedHangarData["path"],
												isPremium=self.hangarSpace.isPremium)

		self.enabled = False

		g_eventsManager.closeMainView()
