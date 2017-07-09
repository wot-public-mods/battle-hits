
from gui.Scaleform.framework.entities.abstract.AbstractPopOverView import AbstractPopOverView

from gui.battlehits.controllers import g_controllers
from gui.battlehits.data import g_data
from gui.battlehits.lang import l10n
from gui.battlehits.events import g_eventsManager

class BattleHitsPreferencesPopoverMeta(AbstractPopOverView):
	
	def invokeChange(self):
		self._printOverrideError('invokeChange')
	
	def as_setPreferencesS(self, data):
		# :param data: Represented by BattleHitsPreferencesDataVO (AS)
		if self._isDAAPIInited():
			return self.flashObject.as_setPreferences(data)

class BattleHitsPreferencesPopover(BattleHitsPreferencesPopoverMeta):
	
	def _populate(self):
		super(BattleHitsPreferencesPopover, self)._populate()
		self.__updateStaticData()

	def invokeChange(self, processReplays, saveOnlySession):
		if g_controllers.settings:
			g_controllers.settings.apply({'processReplays': processReplays, 'saveOnlySession':saveOnlySession})
	
	def invokeStyle(self):
		if g_controllers.settings.get('currentStyle') == 'style1':
			g_controllers.settings.apply({'currentStyle': 'style2'})
		else:
			g_controllers.settings.apply({'currentStyle': 'style1'})
	
	def __updateStaticData(self):

		self.as_setPreferencesS({
			'titleLabel': l10n('popover.titleLabel'), 
			'closeButtonVisible': True, 
			'saveOnlySession': g_controllers.settings.get('saveOnlySession'),
			'saveOnlySessionLabel': l10n('popover.saveOnlySessionLabel'),
			'saveOnlySessionDescription': l10n('popover.saveOnlySessionDescription'),
			'processReplays': g_controllers.settings.get('processReplays'),
			'processReplaysLabel': l10n('popover.processReplaysLabel'),
			'processReplaysDescription': l10n('popover.processReplaysDescription'),
			'changeStyleLabel': l10n('popover.changeStyleLabel')
		})