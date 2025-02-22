# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

import Keys

from helpers import dependency
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.sounds.ambients import LobbySubViewEnv
from gui.veh_post_progression.sounds import PP_VIEW_SOUND_SPACE

from .._constants import SETTINGS
from ..events import g_eventsManager
from ..lang import l10n
from .._skeletons import IHotkeys, ISettings, IState, IBattlesData, IHitsData
from ..utils import getParentWindow

class BattleHitsMainViewMeta(LobbySubView, View):

	def hitsToPlayerClick(self, hitsToPlayer):
		self._printOverrideError('hitsToPlayerClick')

	def selectBattle(self, battleID):
		self._printOverrideError('selectBattle')

	def selectHit(self, hitID):
		self._printOverrideError('selectHit')

	def sortClick(self, sortRow):
		self._printOverrideError('sortClick')

	def preferencesClick(self):
		self._printOverrideError('preferencesClick')

	def as_setStaticDataS(self, data):
		""":param data: Represented by BatHitsStaticDataVO (AS)"""
		if self._isDAAPIInited():
			return self.flashObject.as_setStaticData(data)

	def as_updateBattlesDPDataS(self, data):
		""":param data: Represented by BatHitsBattlesVO (AS)"""
		if self._isDAAPIInited():
			return self.flashObject.as_updateBattlesDPData(data)

	def as_updateHitsDPDataS(self, data):
		""":param data: Represented by BatHitsHitsVO (AS)"""
		if self._isDAAPIInited():
			return self.flashObject.as_updateHitsDPData(data)

	def as_updateDetailedHitDataS(self, data):
		""":param data: Represented by BatHitsDetailedHitVO (AS)"""
		if self._isDAAPIInited():
			return self.flashObject.as_updateDetailedHitData(data)

class BattleHitsMainView(BattleHitsMainViewMeta):

	__sound_env__ = LobbySubViewEnv
	__background_alpha__ = 0.0
	_COMMON_SOUND_SPACE = PP_VIEW_SOUND_SPACE

	hotkeysCtrl = dependency.descriptor(IHotkeys)
	settingsCtrl = dependency.descriptor(ISettings)
	stateCtrl = dependency.descriptor(IState)
	hits = dependency.descriptor(IHitsData)
	battles = dependency.descriptor(IBattlesData)

	def _populate(self):
		super(BattleHitsMainView, self)._populate()
		self.__updateStaticData()
		g_eventsManager.invalidateBattlesDP += self.__onBattlesDPUpdated
		g_eventsManager.invalidateHitsDP += self.__onHitsDPUpdated
		g_eventsManager.closeMainView += self.closeView
		self.hotkeysCtrl.addForced(self.handleKeyEvent)

	def _dispose(self):
		g_eventsManager.invalidateBattlesDP -= self.__onBattlesDPUpdated
		g_eventsManager.invalidateHitsDP -= self.__onHitsDPUpdated
		g_eventsManager.closeMainView -= self.closeView
		if self.hotkeysCtrl:
			self.hotkeysCtrl.delForced(self.handleKeyEvent)
		if self.stateCtrl.enabled:
			self.stateCtrl.switch()
		super(BattleHitsMainView, self)._dispose()

	def closeView(self):
		params = SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR, parent=getParentWindow())
		self.fireEvent(g_entitiesFactories.makeLoadEvent(params), scope=EVENT_BUS_SCOPE.LOBBY)

	def hitsToPlayerClick(self, hitsToPlayer):
		if self.settingsCtrl:
			self.settingsCtrl.apply({SETTINGS.HITS_TO_PLAYER: hitsToPlayer})

	def selectBattle(self, battleID):
		battleID = int(battleID)
		if self.stateCtrl.currentBattleID != battleID:
			self.stateCtrl.currentBattleID = battleID

	def selectHit(self, hitID):
		hitID = int(hitID)
		if self.stateCtrl.currentHitID != hitID:
			self.stateCtrl.currentHitID = hitID

	def sortClick(self, sortRow):
		sortRow = int(sortRow)
		self.hits.sort(sortRow)

	def preferencesClick(self):
		g_eventsManager.showPreferencesPopover()

	def handleKeyEvent(self, event):
		result = False
		if not event.isKeyDown():
			result = False
		elif event.key == Keys.KEY_UPARROW:
			self.selectBattle(self.battles.prevItemID)
			result = True
		elif event.key == Keys.KEY_DOWNARROW:
			self.selectBattle(self.battles.nextItemID)
			result = True
		elif event.key == Keys.KEY_LEFTARROW:
			self.selectHit(self.hits.prevItemID)
			result = True
		elif event.key == Keys.KEY_RIGHTARROW:
			self.selectHit(self.hits.nextItemID)
			result = True
		elif event.key == Keys.KEY_TAB:
			hitsToPlayer = self.settingsCtrl.get(SETTINGS.HITS_TO_PLAYER, False)
			self.hitsToPlayerClick(not hitsToPlayer)
			self.__updateStaticData()
			result = True
		elif event.key == Keys.KEY_ESCAPE:
			self.closeView()
			result = True
		return result

	def __updateStaticData(self):
		self.as_setStaticDataS(self.__getStaticData())

	def __getStaticData(self):
		hitsToPlayer = self.settingsCtrl.get(SETTINGS.HITS_TO_PLAYER, False)
		if hitsToPlayer:
			hitsNoDataLabel = l10n('ui.hits.noDataMe')
		else:
			hitsNoDataLabel = l10n('ui.hits.noDataEnemys')

		return {
			'header': {
				'closeBtnLabel': l10n('ui.closeButton'),
				'settingsLabel': l10n('ui.settingsButton'),
				'titleLabel': l10n('ui.title'),
				'typeBtnMe': l10n('ui.typeMe'),
				'typeBtnEnemys': l10n('ui.typeEnemys'),
				'typeBtnMeActive': hitsToPlayer,
				'typeBtnEnemysActive': not hitsToPlayer
			},
			'battles': {
				'noDataLabel': l10n('ui.battle.noData'),
				'battles': self.battles.dataVO,
				'selectedIndex': self.battles.selectedIndex
			},
			'hits': {
				'noDataLabel': hitsNoDataLabel,
				'hits': self.hits.dataVO,
				'sorting': self.hits.sortingVO,
				'selectedIndex': self.hits.selectedIndex
			},
			'detailedHit': {
				'noDataLabel': l10n('ui.detailedhit.noData')
			}
		}

	def __onBattlesDPUpdated(self):
		self.as_updateBattlesDPDataS({
			'noDataLabel': l10n('ui.battle.noData'),
			'battles': self.battles.dataVO,
			'selectedIndex': self.battles.selectedIndex
		})

	def __onHitsDPUpdated(self):
		hitsToPlayer = self.settingsCtrl.get(SETTINGS.HITS_TO_PLAYER, False)
		if hitsToPlayer:
			noDataLabel = l10n('ui.hits.noDataMe')
		else:
			noDataLabel = l10n('ui.hits.noDataEnemys')

		self.as_updateHitsDPDataS({
			'noDataLabel': noDataLabel,
			'hits': self.hits.dataVO,
			'sorting': self.hits.sortingVO,
			'selectedIndex': self.hits.selectedIndex
		})
