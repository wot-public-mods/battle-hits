
from gui.battlehits.controllers import g_controllers
from gui.battlehits.data import g_data
from gui.battlehits.events import g_eventsManager
from gui.battlehits.lang import l10n
from gui.battlehits.utils import override

__all__ = ()

from gui.app_loader.settings import APP_NAME_SPACE, GUI_GLOBAL_SPACE_ID
from gui.app_loader.loader import _AppLoader, g_appLoader
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

# app finished
@override(_AppLoader, 'fini')
def appFini(baseMethod, baseObject):
	baseMethod(baseObject)
	g_eventsManager.onAppFinish()

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
	if g_controllers.hangarCamera.enabled:
		g_controllers.hangarCamera.updateCamera(*args)
	else:
		baseMethod(baseObject, *args)

@override(HangarCameraIdle, "_HangarCameraIdle__updateIdleMovement")
def onModelsRefresh(baseMethod, baseObject):
	if not g_controllers.hangarCamera.enabled:
		return baseMethod(baseObject)
	return 0.0

@override(HangarCameraParallax, "_HangarCameraParallax__update")
def onModelsRefresh(baseMethod, baseObject):
	if not g_controllers.hangarCamera.enabled:
		return baseMethod(baseObject)
	return 0.0



# battlesHistory

from Vehicle import Vehicle
from vehicle_systems.CompoundAppearance import CompoundAppearance

@override(Vehicle, "showDamageFromShot")
def showDamageFromShot(baseMethod, baseObject, attackerID, points, effectsIndex, damageFactor):
	baseMethod(baseObject, attackerID, points, effectsIndex, damageFactor)
	g_controllers.battleProcessor.processShot(baseObject, attackerID, points, effectsIndex, damageFactor)

@override(Vehicle, "showDamageFromExplosion")
def showDamageFromExplosion(baseMethod, baseObject, attackerID, center, effectsIndex, damageFactor):
	baseMethod(baseObject, attackerID, center, effectsIndex, damageFactor)
	g_controllers.battleProcessor.processExplosion(baseObject, attackerID, center, effectsIndex, damageFactor)

@override(Vehicle, "onHealthChanged")
def onHealthChanged(baseMethod, baseObject, newHealth, attackerID, attackReasonID):
	baseMethod(baseObject, newHealth, attackerID, attackReasonID)
	g_controllers.battleProcessor.processHealthChanged(baseObject, newHealth, attackerID, attackReasonID)

@override(Vehicle, "onEnterWorld")
def onEnterWorld(baseMethod, baseObject, prereqs):
	baseMethod(baseObject, prereqs)
	g_controllers.battleProcessor.processEnterWorld(baseObject)

@override(CompoundAppearance, "_CompoundAppearance__onModelsRefresh")
def onModelsRefresh(baseMethod, baseObject, modelState, resourceList):
	baseMethod(baseObject, modelState, resourceList)
	g_controllers.battleProcessor.onModelsRefresh(baseObject._CompoundAppearance__vehicle, modelState)


# handling keystrokes

import game

@override(game, 'handleKeyEvent')
def handleKeyEvent(baseMethod, event):
	# handling forced keylistners
	for keyHandler in g_controllers.hotkey.forcedHandlers:
		if keyHandler(event):
			return True
	# handling ingame logic
	result = baseMethod(event)
	# firing key event 
	g_eventsManager.onKeyEvent(event, result)
	return result



# Data Collect
try:
	import BigWorld
	BigWorld.wg_dataCollector.addSoloMod('battle_hit')
except: pass


# modsListApi
from gui.modsListApi import g_modsListApi
g_modsListApi.addModification(
	id = 'battlehits', name = l10n('modslist.name'), description = l10n('modslist.description'), \
	icon = 'gui/maps/battlehits/modsListApi.png', enabled = True, login = False, lobby = True, \
	callback = lambda: None if g_controllers.state.enabled else g_controllers.state.switch()
)

# disable open button in battle queue

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
	
	isInQueue = getQueueType() != 0
	
	g_modsListApi.updateModification(id = "battlehits", enabled = not isInQueue)
	
	if isInQueue and g_controllers.state.enabled:
		g_controllers.state.switch()
	
g_eventsManager.onDestroyBattle += handleAvailability
