
import BigWorld
from Account import PlayerAccount
from gui import ClientHangarSpace as chs
from helpers import dependency
from gui.shared import event_dispatcher
from gui.shared.personality import ServicesLocator
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from skeletons.gui.shared.utils import IHangarSpace

from ..controllers import AbstractController
from ..events import g_eventsManager
from ..utils import getLobbyHeader
from .._constants import BATTLE_HITS_SPACE_PATH, BATTLE_ROYALE_SPACE_PATH, SETTINGS

class State(AbstractController):

	hangarSpace = dependency.descriptor(IHangarSpace)

	def __init__(self):
		super(State, self).__init__()
		self.__battleID = None
		self.__hitID = None
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

	def enable(self):
		if self.hangarSpace is None or self.hangarSpace.space is None:
			return

		# in case if we in Vehicle Preview
		# try load hangar first
		app = ServicesLocator.appLoader.getApp()
		if app is not None and app.containerManager is not None:
			viewKey = ViewKey(VIEW_ALIAS.VEHICLE_PREVIEW)
			previewWindow = app.containerManager.getViewByKey(viewKey)
			if previewWindow is not None:
				event_dispatcher.showHangar()

		# disable lobby header state
		lobbyHeader = getLobbyHeader()
		if lobbyHeader:
			lobbyHeader.disableLobbyHeaderControls(True)

		if self.currentBattleID is not None:
			self.currentBattleData.battleByID(self.currentBattleID)
			if self.currentHitID is not None:
				self.currentBattleData.hitByID(self.currentHitID)
			else:
				self.currentHitID = 0
		else:
			self.currentBattleID = self.battlesData.desiredID

		self.enabled = True

		self.hangarSpace.onSpaceCreate += self._onSpaceCreate
		if self.hangarSpace.spacePath != BATTLE_HITS_SPACE_PATH:
			self.hangarSpace.refreshSpace(self.hangarSpace.isPremium, True)
		else:
			self.hangarCameraCtrl.enable()
			self.hangarSceneCtrl.create()

	def disable(self, silent=False):

		self.__battleID = None
		self.__hitID = None

		self.vehicleCtrl.removeVehicle()
		self.hangarCameraCtrl.disable()
		self.hangarSceneCtrl.destroy()
		self.currentBattleData.clean()

		self.hangarSpace.onSpaceCreate -= self._onSpaceCreate

		self.enabled = False

		if isinstance(BigWorld.player(), PlayerAccount) and not silent:
			self.hangarSpace.refreshSpace(self.hangarSpace.isPremium, True)

		g_eventsManager.closeMainView()

		# restore lobby header state
		lobbyHeader = getLobbyHeader()
		if lobbyHeader:
			lobbyHeader.disableLobbyHeaderControls(False)

	def _onSpaceCreate(self):
		if self.hangarSpace.spacePath == BATTLE_HITS_SPACE_PATH:
			self.hangarSceneCtrl.create()
			self.hangarCameraCtrl.enable()

