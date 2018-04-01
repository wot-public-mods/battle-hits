
from gui.app_loader.loader import g_appLoader
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.framework import g_entitiesFactories, GroupedViewSettings, ScopeTemplates, ViewSettings, ViewTypes
from gui.Scaleform.framework.managers.loaders import ViewLoadParams

from gui.battlehits._constants import BATTLE_HITS_VIEW_ALIAS, BATTLE_HITS_PREFERENCES_POPOVER_ALIAS
from gui.battlehits.events import g_eventsManager
from gui.battlehits.views.BattleHitsView import BattleHitsView
from gui.battlehits.views.BattleHitsPreferencesPopover import BattleHitsPreferencesPopover

def getViewSettings():
	return ( ViewSettings(BATTLE_HITS_VIEW_ALIAS, BattleHitsView, 'battleHits.swf', ViewTypes.LOBBY_SUB, None, ScopeTemplates.LOBBY_SUB_SCOPE), 
		GroupedViewSettings(BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, BattleHitsPreferencesPopover, 'battleHitsPopover.swf', \
			ViewTypes.WINDOW, BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE) )

for item in getViewSettings():
	g_entitiesFactories.addSettings(item)


def handleShowUI():
	app = g_appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app:
		return
	app.loadView(ViewLoadParams(BATTLE_HITS_VIEW_ALIAS, BATTLE_HITS_VIEW_ALIAS), {})
g_eventsManager.showUI += handleShowUI

def handleShowPopover():
	app = g_appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app:
		return
	app.loadView(ViewLoadParams(BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, \
								BATTLE_HITS_PREFERENCES_POPOVER_ALIAS), {})
g_eventsManager.showPopover += handleShowPopover