# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

from helpers import dependency
from .._skeletons import *

__all__ = ('AbstractData', 'AbstractDataProvider')

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

	def init(self):
		pass

	def clean(self):
		pass

class AbstractDataProvider(AbstractData):

	def __init__(self):
		super(AbstractDataProvider, self).__init__()
		self.__dataVO = []
		self.__selectedIndex = -1

	@property
	def dataVO(self):
		return self.__dataVO

	@dataVO.setter
	def dataVO(self, value):
		self.__dataVO = value

	@property
	def selectedIndex(self):
		return self.__selectedIndex

	@selectedIndex.setter
	def selectedIndex(self, value):
		self.__selectedIndex = value

	@property
	def nextItemID(self):
		return self.__getItemID(1)

	@property
	def prevItemID(self):
		return self.__getItemID(-1)

	@property
	def desiredID(self):
		return self.__getDesiredID()

	def updateData(self):
		pass

	def __getDesiredID(self):
		result = -1
		self.updateData()
		if self.__dataVO:
			result = self.__dataVO[0]["id"]
		return result

	def __getItemID(self, offset):
		result = 0
		if self.__selectedIndex == -1:
			result = -1
		else:
			destination = self.__selectedIndex + offset
			if len(self.__dataVO) > destination and destination > -1:
				result = self.__dataVO[destination]['id']
			else:
				if self.__selectedIndex < len(self.__dataVO):
					result = self.__dataVO[self.__selectedIndex]['id']
		return result


def configure():
	from helpers.dependency import _g_manager as manager
	from .CurrentBattle import CurrentBattle
	from .Hits import Hits
	from .Battles import Battles

	manager.addInstance(ICurrentBattleData, CurrentBattle(), finalizer='clean')
	manager.addInstance(IHitsData, Hits(), finalizer='clean')
	manager.addInstance(IBattlesData, Battles(), finalizer='clean')

	services = [IHitsData, IBattlesData]
	for service in services:
		serviceIns = dependency.instance(service)
		serviceIns.init()

_configured = False
if not _configured:
	_configured = True
	configure()
