
from gui.Scaleform.framework.entities.abstract.AbstractPopOverView import AbstractPopOverView

from gui.battlehits._constants import SETTINGS
from gui.battlehits.controllers import g_controllers
from gui.battlehits.lang import l10n

class BattleHitsPreferencesPopoverMeta(AbstractPopOverView):
	
	def invokeChange(self):
		self._printOverrideError('invokeChange')
	
	def as_setPreferencesS(self, data):
		""" :param data: Represented by BattleHitsPreferencesDataVO (AS)
		"""
		if self._isDAAPIInited():
			return self.flashObject.as_setPreferences(data)

class BattleHitsPreferencesPopover(BattleHitsPreferencesPopoverMeta):
	
	def _populate(self):
		
		super(BattleHitsPreferencesPopover, self)._populate()
		
		self.__updateStaticData()

	def invokeChange(self, processReplays, saveOnlySession):
		
		if not g_controllers.settings:
			return
			
		g_controllers.settings.apply({SETTINGS.PROCESS_REPLAYS: processReplays, \
									SETTINGS.SAVE_ONLY_SESSION: saveOnlySession})
	
	def invokeStyle(self):
		
		if not g_controllers.settings:
			return
			
		if g_controllers.settings.get(SETTINGS.CURRENT_STYLE) == 'style1':
			g_controllers.settings.apply({SETTINGS.CURRENT_STYLE: 'style2'})
		else:
			g_controllers.settings.apply({SETTINGS.CURRENT_STYLE: 'style1'})
	
	def __updateStaticData(self):
		self.as_setPreferencesS({
			'titleLabel': l10n('popover.titleLabel'), 
			'closeButtonVisible': True, 
			'saveOnlySession': g_controllers.settings.get(SETTINGS.SAVE_ONLY_SESSION),
			'saveOnlySessionLabel': l10n('popover.saveOnlySessionLabel'),
			'saveOnlySessionDescription': l10n('popover.saveOnlySessionDescription'),
			'processReplays': g_controllers.settings.get(SETTINGS.PROCESS_REPLAYS),
			'processReplaysLabel': l10n('popover.processReplaysLabel'),
			'processReplaysDescription': l10n('popover.processReplaysDescription'),
			'changeStyleLabel': l10n('popover.changeStyleLabel')
		})