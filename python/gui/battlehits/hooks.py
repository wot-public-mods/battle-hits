# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2026 Andrii Andrushchyshyn

import game

from constants import PREBATTLE_TYPE, QUEUE_TYPE
from CurrentVehicle import _CurrentVehicle
from debug_utils import LOG_ERROR
from gui.app_loader.settings import APP_NAME_SPACE
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.events_dispatcher import EventDispatcher
from gui.prb_control.prb_getters import getQueueType
from gui.shared import g_eventBus, events
from gui.shared.personality import ServicesLocator
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from Vehicle import Vehicle
from vehicle_systems.CompoundAppearance import CompoundAppearance

from .events import g_eventsManager
from .lang import l10n
from ._skeletons import IBattleProcessor, IHotkeys, IState
from .utils import override

__all__ = ()

GUI_SPACE_BATTLE = 5

# app battle loaded
def onGUISpaceEntered(spaceID):
	if spaceID != GUI_SPACE_BATTLE:
		return
	g_eventsManager.onShowBattle()
ServicesLocator.appLoader.onGUISpaceEntered += onGUISpaceEntered

# app battle destroyed
def onAppDestroyed(event):
	if event.ns != APP_NAME_SPACE.SF_BATTLE:
		return
	g_eventsManager.onDestroyBattle()
g_eventBus.addListener(events.AppLifeCycleEvent.DESTROYED, onAppDestroyed)

# battlesHistory
@override(Vehicle, "showDamageFromShot")
def showDamageFromShot(baseMethod, *args, **kwargs):
	baseMethod(*args, **kwargs)
	battleProcessor = dependency.instance(IBattleProcessor)
	# args: self, attackerID, hitPoints, effectsIndex, prefabEffIndex, damage, damageFactor, lastMaterialIsShield, shellTypeIdx, shellCaliber, shellVelocity
	battleProcessor.processShot(vehicle=args[0], attackerID=args[1], hitPoints=args[2],
							 effectsIndex=args[3], damage=args[5], damageFactor=args[6])

@override(Vehicle, "showDamageFromExplosion")
def showDamageFromExplosion(baseMethod, *args, **kwargs):
	baseMethod(*args, **kwargs)
	battleProcessor = dependency.instance(IBattleProcessor)
	# args: self, attackerID, center, effectsIndex, damage, damageFactor
	battleProcessor.processExplosion(vehicle=args[0], attackerID=args[1], center=args[2],
								  effectsIndex=args[3], damage=args[4], damageFactor=args[5])

@override(Vehicle, "_Vehicle__onAppearanceReady")
def onAppearanceReady(baseMethod, baseObject, appearance):
	baseMethod(baseObject, appearance)
	battleProcessor = dependency.instance(IBattleProcessor)
	battleProcessor.processVehicleInit(baseObject)

@override(CompoundAppearance, "_CompoundAppearance__onModelsRefresh")
def onModelsRefresh(baseMethod, baseObject, modelState, resourceList):
	baseMethod(baseObject, modelState, resourceList)
	vehicle = baseObject.getVehicle()
	if vehicle:
		battleProcessor = dependency.instance(IBattleProcessor)
		battleProcessor.onModelsRefresh(baseObject.getVehicle(), modelState)

@dependency.replace_none_kwargs(appLoader=IAppLoader)
def onAppInitializing(event, appLoader=None):
	if event.ns != APP_NAME_SPACE.SF_LOBBY:
		return
	app = appLoader.getApp()
	from .controllers.State import registerStates, registerTransitions
	app.stateMachine.addStateConfigurator(registerStates)
	app.stateMachine.addTransitionConfigurator(registerTransitions)

g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZING, onAppInitializing)

# handling keystrokes
@override(game, 'handleKeyEvent')
def handleKeyEvent(baseMethod, event):
	# handling forced keylistners
	hotkeys = dependency.instance(IHotkeys)
	for keyHandler in hotkeys.forcedHandlers:
		if keyHandler(event):
			return True
	# handling ingame logic
	result = baseMethod(event)
	# firing key event
	g_eventsManager.onKeyEvent(event, result)
	return result

# Data Collect
g_dataCollector = None
try:
	from ..mods.mod_battlehits import __version__
	from .data_collector import g_dataCollector
except ImportError:
	LOG_ERROR('datacollector broken')
if g_dataCollector:
	g_dataCollector.addSoloMod('battle_hit', __version__)

# modsListApi
g_modsListApi = None
try:
	from gui.modsListApi import g_modsListApi
except ImportError:
	LOG_ERROR('modsListApi not installed')
if g_modsListApi:
	g_modsListApi.addModification(id='battlehits', name=l10n('modslist.name'), enabled=True,
		description=l10n('modslist.description'), icon='gui/maps/battlehits/modsListApi.png',
		login=False, lobby=True, callback=lambda: dependency.instance(IState).switch())

# disable open button in battle queue
@override(EventDispatcher, 'loadBattleQueue')
def loadBattleQueue(baseMethod, baseObject):
	base = baseMethod(baseObject)
	handleAvailability()
	return base

@override(EventDispatcher, 'loadHangar')
def loadHangar(baseMethod, baseObject):
	base = baseMethod(baseObject)
	handleAvailability()
	return base

@override(EventDispatcher, 'loadSquad')
def loadSquad(baseMethod, baseObject, prbType, ctx=None, isTeamReady=False):
	base = baseMethod(baseObject, prbType, ctx, isTeamReady)
	handleAvailability()
	return base

@override(EventDispatcher, 'updateUI')
def updateUI(baseMethod, baseObject, loadedAlias=None):
	base = baseMethod(baseObject, loadedAlias)
	handleAvailability()
	return base

@dependency.replace_none_kwargs(stateCtrl=IState)
def handleAvailability(stateCtrl=None):
	isInQueue = getQueueType() != QUEUE_TYPE.UNKNOWN
	battleRoyaleSquad = False
	dispatcher = g_prbLoader.getDispatcher()
	if dispatcher is not None:
		factories = dispatcher.getControlFactories()
		if factories is not None:
			state = dispatcher.getFunctionalState()
			battleRoyaleSquad = state.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE)
	if g_modsListApi is not None:
		enabled = not isInQueue and not battleRoyaleSquad
		g_modsListApi.updateModification(id="battlehits", enabled=enabled)
	if isInQueue and stateCtrl.enabled:
		stateCtrl.switch()

g_eventsManager.onDestroyBattle += handleAvailability

@override(HangarVehicleAppearance, '_getThisVehicleDossierInsigniaRank')
def getThisVehicleDossierInsigniaRank(baseMethod, baseObject):
	stateCtrl = dependency.instance(IState)
	if stateCtrl.enabled:
		return 0
	return baseMethod(baseObject)

# Fix vehicle rebuild bug on currentVehicle present.
@override(_CurrentVehicle, 'updateVehicleDescriptorInModel')
def isPresent(baseMethod, baseObject):
	stateCtrl = dependency.instance(IState)
	if stateCtrl.enabled:
		return
	return baseMethod(baseObject)

@override(_CurrentVehicle, 'refreshModel')
def isPresent(baseMethod, baseObject, outfit=None):
	stateCtrl = dependency.instance(IState)
	if stateCtrl.enabled:
		return
	return baseMethod(baseObject, outfit)
