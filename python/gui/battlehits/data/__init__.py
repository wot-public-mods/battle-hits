
__all__ = ('AbstractData', )
	
from helpers import dependency
from gui.battlehits.skeletons import (IBattlesHistory, IBattleProcessor, IHangarCamera, \
									IHangarScene, IHotkeys, IState, ISettings, IVehicle, \
									IBattlesData, IHitsData, ICurrentBattleData)

class AbstractData(object):

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
	
	def clean(self):
		pass

def configure():
	from helpers.dependency import _g_manager as manager
	from gui.battlehits.data.CurrentBattle import CurrentBattle
	from gui.battlehits.data.Hits import Hits
	from gui.battlehits.data.Battles import Battles

	manager.addInstance(ICurrentBattleData, CurrentBattle(), finalizer='clean')
	manager.addInstance(IHitsData, Hits(), finalizer='clean')
	manager.addInstance(IBattlesData, Battles(), finalizer='clean')
	
_configured = False
if not _configured:
	_configured = True
	configure()
	