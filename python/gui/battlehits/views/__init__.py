# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2026 Andrii Andrushchyshyn

from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.framework import (g_entitiesFactories, ComponentSettings, GroupedViewSettings, 
									 ScopeTemplates, ViewSettings)
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.personality import ServicesLocator
from frameworks.wulf import WindowLayer

from .._constants import BATTLE_HITS_MAIN_VIEW_ALIAS, BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, BATTLE_HITS_VIEW_HEADER
from ..events import g_eventsManager
from ..utils import get_parent_window
from .BattleHitsMainView import BattleHitsMainView
from .BattleHitsPreferencesPopover import BattleHitsPreferencesPopover
from .BattleHitsHeaderView import BattleHitsHeaderInjectComponent

def getViewSettings():
	viewSettings = []
	viewSettings.append(
		ViewSettings(
			BATTLE_HITS_MAIN_VIEW_ALIAS,
			BattleHitsMainView,
			'battleHitsMainView.swf',
			WindowLayer.SUB_VIEW,
			None,
			ScopeTemplates.LOBBY_SUB_SCOPE
		)
	)
	viewSettings.append(
		GroupedViewSettings(
			BATTLE_HITS_PREFERENCES_POPOVER_ALIAS,
			BattleHitsPreferencesPopover,
			'battleHitsPreferencesPopover.swf',
			WindowLayer.TOP_WINDOW,
			BATTLE_HITS_PREFERENCES_POPOVER_ALIAS,
			BATTLE_HITS_PREFERENCES_POPOVER_ALIAS,
			ScopeTemplates.WINDOW_VIEWED_MULTISCOPE
		)
	)
	viewSettings.append(
		ComponentSettings(
			BATTLE_HITS_VIEW_HEADER,
			BattleHitsHeaderInjectComponent,
			ScopeTemplates.DEFAULT_SCOPE
		)
	)
	return viewSettings

for item in getViewSettings():
	g_entitiesFactories.addSettings(item)


def showMainView():
	app = ServicesLocator.appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app:
		return
	app.loadView(SFViewLoadParams(BATTLE_HITS_MAIN_VIEW_ALIAS, parent=get_parent_window()))
g_eventsManager.showMainView += showMainView

def showPreferencesPopover():
	app = ServicesLocator.appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app:
		return
	app.loadView(SFViewLoadParams(BATTLE_HITS_PREFERENCES_POPOVER_ALIAS, parent=get_parent_window()))
g_eventsManager.showPreferencesPopover += showPreferencesPopover
