
from gui.Scaleform.framework import g_entitiesFactories, GroupedViewSettings, ScopeTemplates, ViewSettings, ViewTypes

from gui.battlehits._constants import BATTLE_HITS_VIEW_ALIAS, BATTLE_HITS_PREFERENCES_POPOVER_ALIAS
from gui.battlehits.views.BattleHitsView import BattleHitsView
from gui.battlehits.views.BattleHitsPreferencesPopover import BattleHitsPreferencesPopover

def getViewSettings():
	return ( ViewSettings(BATTLE_HITS_VIEW_ALIAS, BattleHitsView, 'battleHits.swf', ViewTypes.LOBBY_SUB, None, ScopeTemplates.LOBBY_SUB_SCOPE), 
		GroupedViewSettings(BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, BattleHitsPreferencesPopover, 'battleHitsPopover.swf', \
			ViewTypes.WINDOW, BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE) )

for item in getViewSettings():
	g_entitiesFactories.addSettings(item)