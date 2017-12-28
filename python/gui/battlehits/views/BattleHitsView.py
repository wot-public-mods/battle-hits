
from gui.app_loader.loader import g_appLoader
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import ViewLoadParams
from gui.shared import event_dispatcher
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.sounds.ambients import LobbySubViewEnv
from debug_utils import LOG_ERROR, LOG_NOTE

from gui.battlehits._constants import SETTINGS, BATTLE_HITS_PREFERENCES_POPOVER_ALIAS
from gui.battlehits.controllers import g_controllers
from gui.battlehits.data import g_data
from gui.battlehits.events import g_eventsManager
from gui.battlehits.lang import l10n


class BattleHitsMeta(LobbySubView, View):
	
	def hitsToPlayerClick(self):
		self._printOverrideError('hitsToPlayerClick')
	
	def selectBattle(self):
		self._printOverrideError('selectBattle')
	
	def selectHit(self):
		self._printOverrideError('selectHit')
	
	def sortClick(self):
		self._printOverrideError('sortClick')
	
	def preferencesClick(self):
		self._printOverrideError('preferencesClick')
	
	def as_setStaticDataS(self, data):
		""" :param data: Represented by BatHitsStaticDataVO (AS)
		"""
		if self._isDAAPIInited():
			return self.flashObject.as_setStaticData(data)

	def as_updateBattlesDPDataS(self, data):
		""" :param data: Represented by BatHitsBattlesVO (AS)
		"""
		if self._isDAAPIInited():
			return self.flashObject.as_updateBattlesDPData(data)

	def as_updateHitsDPDataS(self, data):
		""" :param data: Represented by BatHitsHitsVO (AS)
		"""
		if self._isDAAPIInited():
			return self.flashObject.as_updateHitsDPData(data)

	def as_updateDetailedHitDataS(self, data):
		""" :param data: Represented by BatHitsDetailedHitVO (AS)
		"""
		if self._isDAAPIInited():
			return self.flashObject.as_updateDetailedHitData(data)

class BattleHitsView(BattleHitsMeta):

	__sound_env__ = LobbySubViewEnv
	__background_alpha__ = 0.0
	
	def __init__(self, ctx = None):
		super(BattleHitsView, self).__init__(ctx)
		self.__vehicleCD = ctx.get('itemCD')
		self.__backAlias = ctx.get('previewAlias', VIEW_ALIAS.LOBBY_HANGAR)
	
	def _populate(self):
		super(BattleHitsView, self)._populate()
		self.__updateStaticData()
		g_eventsManager.invalidateBattlesDP += self.__onBattlesDPUpdated
		g_eventsManager.invalidateHitsDP += self.__onHitsDPUpdated
		g_eventsManager.closeUI += self.closeView
	
	def _dispose(self):
		if g_controllers.state and g_controllers.state.enabled:
			g_controllers.state.switch()
		g_eventsManager.invalidateBattlesDP -= self.__onBattlesDPUpdated
		g_eventsManager.invalidateHitsDP -= self.__onHitsDPUpdated
		g_eventsManager.closeUI -= self.closeView
		super(BattleHitsView, self)._dispose()
	
	def closeView(self):
		self.onBackClick()

	def onBackClick(self):
		if self.__backAlias == VIEW_ALIAS.LOBBY_RESEARCH:
			event_dispatcher.showResearchView(self.__vehicleCD)
		else:
			event = g_entitiesFactories.makeLoadEvent(self.__backAlias)
			self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

	def hitsToPlayerClick(self, toPlayer):
		if g_controllers.settings:
			g_controllers.settings.apply({SETTINGS.HITS_TO_PLAYER: toPlayer})
	
	def selectBattle(self, battleID):
		battleID = int(battleID)
		if g_controllers.state.currentBattleID != battleID:
			g_controllers.state.currentBattleID = battleID
	
	def selectHit(self, hitID):
		hitID = int(hitID)
		if g_controllers.state.currentHitID != hitID:
			g_controllers.state.currentHitID = hitID
	
	def sortClick(self, sortRow):
		sortRow = int(sortRow)
		g_data.hits.sort(sortRow)
	
	def preferencesClick(self):
		app = g_appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
		if app:
			app.loadView(ViewLoadParams(BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, \
										BATTLE_HITS_PREFERENCES_POPOVER_ALIAS), {})
	
	def __updateStaticData(self):
		self.as_setStaticDataS(self.__getStaticData())
	
	def __getStaticData(self):
		
		if g_data.hits.hitsToPlayer:
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
				'typeBtnMeActive': g_data.hits.hitsToPlayer,
				'typeBtnEnemysActive': not g_data.hits.hitsToPlayer
			},
			'battles': {
				'noDataLabel': l10n('ui.battle.noData'),
				'battles': g_data.battles.dataVO,
				'selectedIndex': g_data.battles.selectedIndex
			},
			'hits': {
				'noDataLabel': hitsNoDataLabel,
				'hits': g_data.hits.dataVO,
				'sorting': g_data.hits.sortingVO,
				'selectedIndex': g_data.hits.selectedIndex
			},
			'detailedHit': {
				'noDataLabel': l10n('ui.detailedhit.noData')
			}
		}
	
	def __onBattlesDPUpdated(self):
		self.as_updateBattlesDPDataS({
			'noDataLabel': l10n('ui.battle.noData'),
			'battles': g_data.battles.dataVO,
			'selectedIndex': g_data.battles.selectedIndex
		})
	
	def __onHitsDPUpdated(self):
		
		if g_data.hits.hitsToPlayer:
			noDataLabel = l10n('ui.hits.noDataMe')
		else:
			noDataLabel = l10n('ui.hits.noDataEnemys')
		
		self.as_updateHitsDPDataS({
			'noDataLabel': noDataLabel,
			'hits': g_data.hits.dataVO,
			'sorting': g_data.hits.sortingVO,
			'selectedIndex': g_data.hits.selectedIndex
		})
	