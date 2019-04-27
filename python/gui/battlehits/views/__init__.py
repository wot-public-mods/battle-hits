
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.framework import (g_entitiesFactories, GroupedViewSettings, ScopeTemplates,
									 ViewSettings, ViewTypes)
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.personality import ServicesLocator

from gui.battlehits._constants import BATTLE_HITS_MAIN_VIEW_ALIAS, BATTLE_HITS_PREFERENCES_POPOVER_ALIAS
from gui.battlehits.events import g_eventsManager
from gui.battlehits.views.BattleHitsMainView import BattleHitsMainView
from gui.battlehits.views.BattleHitsPreferencesPopover import BattleHitsPreferencesPopover

def getViewSettings():
	viewSettings = []
	viewSettings.append(ViewSettings(BATTLE_HITS_MAIN_VIEW_ALIAS, BattleHitsMainView, 'battleHitsMainView.swf',
			ViewTypes.LOBBY_SUB, None, ScopeTemplates.LOBBY_SUB_SCOPE))
	viewSettings.append(GroupedViewSettings(BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, BattleHitsPreferencesPopover,
			'battleHitsPreferencesPopover.swf', ViewTypes.WINDOW, BATTLE_HITS_PREFERENCES_POPOVER_ALIAS,
			BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE))
	return viewSettings

for item in getViewSettings():
	g_entitiesFactories.addSettings(item)


def showMainView():
	app = ServicesLocator.appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app:
		return
	app.loadView(SFViewLoadParams(BATTLE_HITS_MAIN_VIEW_ALIAS), {})
g_eventsManager.showMainView += showMainView

def showPreferencesPopover():
	app = ServicesLocator.appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app:
		return
	app.loadView(SFViewLoadParams(BATTLE_HITS_PREFERENCES_POPOVER_ALIAS), {})
g_eventsManager.showPreferencesPopover += showPreferencesPopover
