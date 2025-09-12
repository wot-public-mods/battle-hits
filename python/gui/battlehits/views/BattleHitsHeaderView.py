
from collections import OrderedDict

from helpers import dependency

from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.pub.view_component import ViewComponent
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from openwg_gameface import ModDynAccessor

from .._constants import SETTINGS, BATTLE_HITS_VIEW_HEADER
from .._skeletons import ISettings
from ..events import g_eventsManager
from ..lang import l10n

class MenuItemModel(ViewModel):

	def __init__(self, properties=2, commands=0):
		super(MenuItemModel, self).__init__(properties=properties, commands=commands)

	def getTabId(self):
		return self._getString(0)

	def setTabId(self, value):
		self._setString(0, value)

	def getTabLabel(self):
		return self._getString(1)

	def setTabLabel(self, value):
		self._setString(1, value)

	def _initialize(self):
		super(MenuItemModel, self)._initialize()
		self._addStringProperty('tabId', '')
		self._addStringProperty('tabLabel', '')

class BattleHitsHeaderModel(ViewModel):
	TO_ME = 'to_me'
	BY_ME = 'by_me'

	def __init__(self, properties=2, commands=2):
		super(BattleHitsHeaderModel, self).__init__(properties=properties, commands=commands)

	def getActiveTab(self):
		return self._getString(0)

	def setActiveTab(self, value):
		self._setString(0, value)

	def getMenuItems(self):
		return self._getArray(1)

	def setMenuItems(self, value):
		self._setArray(1, value)

	@staticmethod
	def getMenuItemsType():
		return MenuItemModel

	def _initialize(self):
		super(BattleHitsHeaderModel, self)._initialize()
		self._addStringProperty('activeTab', BattleHitsHeaderModel.TO_ME)
		self._addArrayProperty('menuItems', Array())
		self.openSettingsPopup = self._addCommand('openSettingsPopup')
		self.changeActiveTab = self._addCommand('changeActiveTab')

class BattleHitsHeaderView(ViewComponent[BattleHitsHeaderModel]):

	viewLayoutID = ModDynAccessor(BATTLE_HITS_VIEW_HEADER)
	settingsCtrl = dependency.descriptor(ISettings)

	def __init__(self):
		super(BattleHitsHeaderView, self).__init__(
			layoutID=BattleHitsHeaderView.viewLayoutID(),
			model=BattleHitsHeaderModel
		)

	@property
	def viewModel(self):
		return super(BattleHitsHeaderView, self).getViewModel()

	def _getEvents(self):
		eventsTuple = super(BattleHitsHeaderView, self)._getEvents()
		return eventsTuple + (
			(self.viewModel.openSettingsPopup, self.__openSettingsPopup),
			(self.viewModel.changeActiveTab, self.__changeActiveTab),
		)

	def _onLoading(self, *args, **kwargs):
		super(BattleHitsHeaderView, self)._onLoading(*args, **kwargs)
		with self.viewModel.transaction() as model:
			hitsToPlayer = self.settingsCtrl.get(SETTINGS.HITS_TO_PLAYER, False)
			activeTab = BattleHitsHeaderModel.TO_ME if hitsToPlayer else BattleHitsHeaderModel.BY_ME
			model.setActiveTab(activeTab)
			self.__updateMenuItems(model)

	def _finalize(self):
		super(BattleHitsHeaderView, self)._finalize()

	def __openSettingsPopup(self):
		g_eventsManager.showPreferencesPopover()

	def __changeActiveTab(self, context={}):
		newTabId = context.get('tabId', None)
		if newTabId is None:
			return
		self.settingsCtrl.apply({
			SETTINGS.HITS_TO_PLAYER: newTabId == BattleHitsHeaderModel.TO_ME
		})
		with self.viewModel.transaction() as model:
			model.setActiveTab(newTabId)

	def __getMenuItems(self):
		return OrderedDict([
			(BattleHitsHeaderModel.TO_ME, l10n('ui.typeMe')),
			(BattleHitsHeaderModel.BY_ME, l10n('ui.typeEnemys')),
		])

	def __updateMenuItems(self, model):
		menuItems = self.__getMenuItems()
		menuItemsModel = model.getMenuItems()
		menuItemsModel.clear()
		for (tabId, tabLabel) in menuItems.items():
			menuItemModel = MenuItemModel()
			menuItemModel.setTabId(tabId)
			menuItemModel.setTabLabel(tabLabel)
			menuItemsModel.addViewModel(menuItemModel)
		menuItemsModel.invalidate()

class BattleHitsHeaderInjectComponent(InjectComponentAdaptor):

	def _makeInjectView(self):
		return BattleHitsHeaderView()
