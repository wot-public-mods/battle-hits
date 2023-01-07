import BigWorld
import game

from constants import PREBATTLE_TYPE, QUEUE_TYPE
from CurrentVehicle import _CurrentVehicle
from debug_utils import LOG_ERROR
from helpers import dependency
from gui import ClientHangarSpace
from gui.app_loader.settings import APP_NAME_SPACE
from gui.hangar_cameras.hangar_camera_manager import HangarCameraManager
from gui.hangar_cameras.hangar_camera_idle import HangarCameraIdle
from gui.hangar_cameras.hangar_camera_parallax import HangarCameraParallax
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.events_dispatcher import EventDispatcher
from gui.prb_control.prb_getters import getQueueType
from gui.shared import g_eventBus, events
from gui.shared.personality import ServicesLocator
from Vehicle import Vehicle
from vehicle_systems.CompoundAppearance import CompoundAppearance

from ._constants import SETTINGS, BATTLE_HITS_SPACE_PATH, DEFAULT_HANGAR_SPACES
from .events import g_eventsManager
from .lang import l10n
from .skeletons import IHangarCamera, IBattleProcessor, IHotkeys, IState, ISettings
from .utils import override

__all__ = ()

GUI_SPACE_BATTLE = 6

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

# fix space change vehicle getVehicleEntity error
@override(ClientHangarSpace.ClientHangarSpace, 'getVehicleEntity')
def getVehicleEntity(baseMethod, baseObject):
	return BigWorld.entity(baseObject.vehicleEntityId) if baseObject.vehicleEntityId else None

# hangarCamera
@override(HangarCameraManager, "_HangarCameraManager__updateCameraByMouseMove")
def hangarCameraManager_updateCameraByMouseMove(baseMethod, baseObject, dx, dy, dz):
	hangarCamera = dependency.instance(IHangarCamera)
	if hangarCamera.enabled:
		hangarCamera.updateCamera(dx, dy, dz)
	else:
		baseMethod(baseObject, dx, dy, dz)

@override(HangarCameraIdle, "_HangarCameraIdle__updateIdleMovement")
def hangarCameraIdle_updateIdleMovement(baseMethod, baseObject):
	hangarCamera = dependency.instance(IHangarCamera)
	if not hangarCamera.enabled:
		return baseMethod(baseObject)
	return 0.0

@override(HangarCameraParallax, "_HangarCameraParallax__update")
def hangarCameraParallax_update(baseMethod, baseObject):
	hangarCamera = dependency.instance(IHangarCamera)
	if not hangarCamera.enabled:
		return baseMethod(baseObject)
	return 0.0

# battlesHistory
@override(Vehicle, "showDamageFromShot")
def showDamageFromShot(baseMethod, baseObject, attackerID, points, effectsIndex, damageFactor, lastMaterialIsShield):
	baseMethod(baseObject, attackerID, points, effectsIndex, damageFactor, lastMaterialIsShield)
	battleProcessor = dependency.instance(IBattleProcessor)
	battleProcessor.processShot(baseObject, attackerID, points, effectsIndex, damageFactor)

@override(Vehicle, "showDamageFromExplosion")
def showDamageFromExplosion(baseMethod, baseObject, attackerID, center, effectsIndex, damageFactor):
	baseMethod(baseObject, attackerID, center, effectsIndex, damageFactor)
	battleProcessor = dependency.instance(IBattleProcessor)
	battleProcessor.processExplosion(baseObject, attackerID, center, effectsIndex, damageFactor)

@override(Vehicle, "onHealthChanged")
def onHealthChanged(baseMethod, baseObject, newHealth, oldHealth, attackerID, attackReasonID):
	baseMethod(baseObject, newHealth, oldHealth, attackerID, attackReasonID)
	battleProcessor = dependency.instance(IBattleProcessor)
	battleProcessor.processHealthChanged(baseObject, newHealth, attackerID, attackReasonID)

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
	from gui.battlehits import __version__
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

@dependency.replace_none_kwargs(settingsCtrl=ISettings, stateCtrl=IState)
def fixHangarPath(path, settingsCtrl=None, stateCtrl=None):
	if stateCtrl.enabled:
		return BATTLE_HITS_SPACE_PATH
	swapHangar = settingsCtrl.get(SETTINGS.SWAP_HANGAR, False)
	if not swapHangar:
		return path
	if path not in DEFAULT_HANGAR_SPACES:
		return path
	return BATTLE_HITS_SPACE_PATH

@override(ClientHangarSpace, 'getDefaultHangarPath')
def getDefaultHangarPath(baseMethod, isPremium):
	path = baseMethod(isPremium)
	return fixHangarPath(path)

@override(ClientHangarSpace, '_getHangarPath')
def _getHangarPath(baseMethod, isPremium, isPremIGR):
	path = baseMethod(isPremium, isPremIGR)
	return fixHangarPath(path)

# Fix vehicle insignia rank display on preview vehicle.
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
