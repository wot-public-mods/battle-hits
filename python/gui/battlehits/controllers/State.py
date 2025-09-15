# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

from gui.lobby_state_machine.states import SFViewLobbyState, LobbyStateDescription, SubScopeSubLayerState
from gui.Scaleform.framework.entities.View import ViewKey
from gui.shared.event_dispatcher import showHangar
from gui.subhangar.subhangar_state_groups import SubhangarStateGroupConfigProvider, SubhangarStateGroups, SubhangarStateGroupConfig
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

from ..controllers import AbstractController
from ..events import g_eventsManager
from .._constants import BATTLE_HITS_MAIN_VIEW_ALIAS
from .._skeletons import IState
from ..lang import l10n

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
		if self.enabled:
			return

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

		BattleHitsState.goTo()
		self.enabled = True
		self.hangarSceneCtrl.create()

	def disable(self, goToHangar=True):
		if not self.enabled:
			return

		self.__battleID = None
		self.__hitID = None

		self.vehicleCtrl.removeVehicle()
		self.hangarSceneCtrl.destroy()
		self.currentBattleData.clean()

		self.enabled = False

		if goToHangar:
			showHangar()

@SubScopeSubLayerState.parentOf
class BattleHitsState(SFViewLobbyState, SubhangarStateGroupConfigProvider):

	VIEW_KEY = ViewKey(BATTLE_HITS_MAIN_VIEW_ALIAS)
	STATE_ID = "battlehits"

	def getSubhangarStateGroupConfig(self):
		return SubhangarStateGroupConfig((
			SubhangarStateGroups.VehicleHub,
			SubhangarStateGroups.VehicleHubArmorLargeTank,
		))

	def getNavigationDescription(self):
		return LobbyStateDescription(title=l10n('ui.title'))

	def registerTransitions(self):
		lsm = self.getMachine()
		lsm.addNavigationTransitionFromParent(self)

	@dependency.replace_none_kwargs(stateCtrl=IState)
	def _onExited(self, stateCtrl=None):
		stateCtrl.disable(goToHangar=False)
		super(BattleHitsState, self)._onExited()

def registerStates(machine):
	machine.addState(BattleHitsState())

def registerTransitions(machine):
	battlhits = machine.getStateByCls(BattleHitsState)
	machine.addNavigationTransitionFromParent(battlhits)
