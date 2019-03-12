from helpers import dependency
from gui.battlehits.skeletons import (IBattlesHistory, IBattleProcessor, IHangarCamera, \
									IHangarScene, IHotkeys, IState, ISettings, IVehicle, \
									IBattlesData, IHitsData, ICurrentBattleData)

__all__ = ('AbstractController', )

class AbstractController(object):

	battlesHistoryCtrl = dependency.descriptor(IBattlesHistory)
	battleProcessorCtrl = dependency.descriptor(IBattleProcessor)
	hangarCameraCtrl = dependency.descriptor(IHangarCamera)
	hangarSceneCtrl = dependency.descriptor(IHangarScene)
	hotkeysCtrl = dependency.descriptor(IHotkeys)
	stateCtrl = dependency.descriptor(IState)
	settingsCtrl = dependency.descriptor(ISettings)
	vehicleCtrl = dependency.descriptor(IVehicle)
	battlesData = dependency.descriptor(IBattlesData)
	hitsData = dependency.descriptor(IHitsData)
	currentBattleData = dependency.descriptor(ICurrentBattleData)

	def __init__(self):
		self.__enabled = False

	@property
	def enabled(self):
		return self.__enabled

	@enabled.setter
	def enabled(self, value):
		self.__enabled = value

	def init(self):
		pass

	def fini(self):
		pass

def configure():
	from helpers.dependency import _g_manager as manager
	from gui.battlehits.controllers.BattlesHistory import BattlesHistory
	from gui.battlehits.controllers.BattleProcessor import BattleProcessor
	from gui.battlehits.controllers.HangarCamera import HangarCamera
	from gui.battlehits.controllers.HangarScene import HangarScene
	from gui.battlehits.controllers.Hotkeys import Hotkeys
	from gui.battlehits.controllers.State import State
	from gui.battlehits.controllers.Settings import Settings
	from gui.battlehits.controllers.Vehicle import Vehicle

	manager.addInstance(IBattlesHistory, BattlesHistory(), finalizer='fini')
	manager.addInstance(IBattleProcessor, BattleProcessor(), finalizer='fini')
	manager.addInstance(IHangarCamera, HangarCamera(), finalizer='fini')
	manager.addInstance(IHangarScene, HangarScene(), finalizer='destroy')
	manager.addInstance(IHotkeys, Hotkeys(), finalizer='fini')
	manager.addInstance(IState, State(), finalizer='fini')
	manager.addInstance(ISettings, Settings(), finalizer='fini')
	manager.addInstance(IVehicle, Vehicle(), finalizer='fini')

	services = [IBattlesHistory, IBattleProcessor, IHangarCamera, IHangarScene, IHotkeys, IState, \
				ISettings, IVehicle]
	for service in services:
		serviceIns = dependency.instance(service)
		serviceIns.init()

_configured = False
if not _configured:
	_configured = True
	configure()
