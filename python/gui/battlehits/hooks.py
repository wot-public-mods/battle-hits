
import BigWorld

from helpers import dependency

from gui.battlehits.events import g_eventsManager
from gui.battlehits.lang import l10n
from gui.battlehits.skeletons import IHangarCamera, IBattleProcessor, IHotkeys, IState
from gui.battlehits.utils import override

__all__ = ()

from gui.app_loader.settings import APP_NAME_SPACE, GUI_GLOBAL_SPACE_ID
from gui.app_loader.loader import g_appLoader
from gui.shared import g_eventBus, events

# app battle loaded
def onGUISpaceEntered(spaceID):
	if spaceID != GUI_GLOBAL_SPACE_ID.BATTLE:
		return
	g_eventsManager.onShowBattle()
g_appLoader.onGUISpaceEntered += onGUISpaceEntered

# app battle destroyed
def onAppDestroyed(event):
	if event.ns != APP_NAME_SPACE.SF_BATTLE:
		return
	g_eventsManager.onDestroyBattle()
g_eventBus.addListener(events.AppLifeCycleEvent.DESTROYED, onAppDestroyed)

# fix space change vehicle getVehicleEntity error
from gui.ClientHangarSpace import ClientHangarSpace
@override(ClientHangarSpace, 'getVehicleEntity')
def getVehicleEntity(baseMethod, baseObject):
	return BigWorld.entity(baseObject.vehicleEntityId) if baseObject.vehicleEntityId else None


# hangarCamera
from gui.hangar_cameras.hangar_camera_manager import HangarCameraManager
from gui.hangar_cameras.hangar_camera_idle import HangarCameraIdle
from gui.hangar_cameras.hangar_camera_parallax import HangarCameraParallax

@override(HangarCameraManager, "_HangarCameraManager__updateCameraByMouseMove")
def updateCameraByMouseMove(baseMethod, baseObject, *args):
	hangarCamera = dependency.instance(IHangarCamera)
	if hangarCamera.enabled:
		hangarCamera.updateCamera(*args)
	else:
		baseMethod(baseObject, *args)

@override(HangarCameraIdle, "_HangarCameraIdle__updateIdleMovement")
def onModelsRefresh(baseMethod, baseObject):
	hangarCamera = dependency.instance(IHangarCamera)
	if not hangarCamera.enabled:
		return baseMethod(baseObject)
	return 0.0

@override(HangarCameraParallax, "_HangarCameraParallax__update")
def onModelsRefresh(baseMethod, baseObject):
	hangarCamera = dependency.instance(IHangarCamera)
	if not hangarCamera.enabled:
		return baseMethod(baseObject)
	return 0.0



# battlesHistory

from Vehicle import Vehicle
from vehicle_systems.CompoundAppearance import CompoundAppearance

@override(Vehicle, "showDamageFromShot")
def showDamageFromShot(baseMethod, baseObject, attackerID, points, effectsIndex, damageFactor):
	baseMethod(baseObject, attackerID, points, effectsIndex, damageFactor)
	battleProcessor = dependency.instance(IBattleProcessor)
	battleProcessor.processShot(baseObject, attackerID, points, effectsIndex, damageFactor)

@override(Vehicle, "showDamageFromExplosion")
def showDamageFromExplosion(baseMethod, baseObject, attackerID, center, effectsIndex, damageFactor):
	baseMethod(baseObject, attackerID, center, effectsIndex, damageFactor)
	battleProcessor = dependency.instance(IBattleProcessor)
	battleProcessor.processExplosion(baseObject, attackerID, center, effectsIndex, damageFactor)

@override(Vehicle, "onHealthChanged")
def onHealthChanged(baseMethod, baseObject, newHealth, attackerID, attackReasonID):
	baseMethod(baseObject, newHealth, attackerID, attackReasonID)
	battleProcessor = dependency.instance(IBattleProcessor)
	battleProcessor.processHealthChanged(baseObject, newHealth, attackerID, attackReasonID)

@override(Vehicle, "onEnterWorld")
def onEnterWorld(baseMethod, baseObject, prereqs):
	baseMethod(baseObject, prereqs)
	battleProcessor = dependency.instance(IBattleProcessor)
	battleProcessor.processEnterWorld(baseObject)

@override(CompoundAppearance, "_CompoundAppearance__onModelsRefresh")
def onModelsRefresh(baseMethod, baseObject, modelState, resourceList):
	baseMethod(baseObject, modelState, resourceList)
	battleProcessor = dependency.instance(IBattleProcessor)
	battleProcessor.onModelsRefresh(baseObject._CompoundAppearance__vehicle, modelState)


# handling keystrokes

import game

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
from gui.battlehits import __version__
from gui.battlehits.data_collector import g_dataCollector
g_dataCollector.addSoloMod('battle_hit', __version__)



# modsListApi
from gui.modsListApi import g_modsListApi

def handleClick():
	state = dependency.instance(IState)
	state.switch()

g_modsListApi.addModification(
	id = 'battlehits', name = l10n('modslist.name'), description = l10n('modslist.description'), \
	icon = 'gui/maps/battlehits/modsListApi.png', enabled = True, login = False, lobby = True, \
	callback = handleClick
)

# disable open button in battle queue

from constants import QUEUE_TYPE
from gui.prb_control.prb_getters import getQueueType
from gui.prb_control.events_dispatcher import EventDispatcher

@override(EventDispatcher, 'loadBattleQueue')
def loadBattleQueue(baseMethod, baseObject):
	base = baseMethod(baseObject)
	handleAvailability()
	return base

@override(EventDispatcher, 'loadHangar')
def loadBattleQueue(baseMethod, baseObject):
	base = baseMethod(baseObject)
	handleAvailability()
	return base

def handleAvailability():
	isInQueue = getQueueType() != QUEUE_TYPE.UNKNOWN
	g_modsListApi.updateModification(id = "battlehits", enabled = not isInQueue)
	state = dependency.instance(IState)
	if isInQueue and state.enabled:
		state.switch()
	
g_eventsManager.onDestroyBattle += handleAvailability
