
from helpers import dependency
from gui.Scaleform.framework.entities.abstract.AbstractPopOverView import AbstractPopOverView

from gui.battlehits._constants import SETTINGS
from gui.battlehits.skeletons import ISettings
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
	
	settingsCtrl = dependency.descriptor(ISettings)

	def _populate(self):
		
		super(BattleHitsPreferencesPopover, self)._populate()
		
		self.__updateStaticData()

	def invokeChange(self, processReplays, saveOnlySession):
		
		if not self.settingsCtrl:
			return
			
		self.settingsCtrl.apply({SETTINGS.PROCESS_REPLAYS: processReplays, \
									SETTINGS.SAVE_ONLY_SESSION: saveOnlySession})
	
	def invokeStyle(self):
		
		if not self.settingsCtrl:
			return
			
		if self.settingsCtrl.get(SETTINGS.CURRENT_STYLE) == 'style1':
			self.settingsCtrl.apply({SETTINGS.CURRENT_STYLE: 'style2'})
		else:
			self.settingsCtrl.apply({SETTINGS.CURRENT_STYLE: 'style1'})
	
	def __updateStaticData(self):
		self.as_setPreferencesS({
			'titleLabel': l10n('popover.titleLabel'), 
			'closeButtonVisible': True, 
			'saveOnlySession': self.settingsCtrl.get(SETTINGS.SAVE_ONLY_SESSION),
			'saveOnlySessionLabel': l10n('popover.saveOnlySessionLabel'),
			'saveOnlySessionDescription': l10n('popover.saveOnlySessionDescription'),
			'processReplays': self.settingsCtrl.get(SETTINGS.PROCESS_REPLAYS),
			'processReplaysLabel': l10n('popover.processReplaysLabel'),
			'processReplaysDescription': l10n('popover.processReplaysDescription'),
			'changeStyleLabel': l10n('popover.changeStyleLabel')
		})