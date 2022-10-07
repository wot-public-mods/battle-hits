from helpers import dependency
from gui.Scaleform.framework.entities.abstract.AbstractPopOverView import AbstractPopOverView

from .._constants import SETTINGS, MODEL_STYLE
from ..skeletons import IBattlesHistory, ISettings
from ..lang import l10n

class BattleHitsPreferencesPopoverMeta(AbstractPopOverView):

	def invokeSettingsChange(self, processReplays, saveOnlySession, swapHangar):
		self._printOverrideError('invokeSettingsChange')

	def invokeStyleChange(self):
		self._printOverrideError('invokeStyleChange')

	def invokeHistoryDelete(self):
		self._printOverrideError('invokeHistoryDelete')

	def as_setPreferencesS(self, data):
		""":param data: Represented by BattleHitsPreferencesDataVO (AS)"""
		if self._isDAAPIInited():
			return self.flashObject.as_setPreferences(data)

class BattleHitsPreferencesPopover(BattleHitsPreferencesPopoverMeta):

	settingsCtrl = dependency.descriptor(ISettings)
	battlesHistoryCtrl = dependency.descriptor(IBattlesHistory)

	def _populate(self):
		super(BattleHitsPreferencesPopover, self)._populate()
		self.__updateStaticData()

	def invokeSettingsChange(self, processReplays, saveOnlySession, swapHangar):
		if not self.settingsCtrl:
			return
		self.settingsCtrl.apply({SETTINGS.PROCESS_REPLAYS: processReplays,
								SETTINGS.SAVE_ONLY_SESSION: saveOnlySession,
								SETTINGS.SWAP_HANGAR: swapHangar})

	def invokeStyleChange(self):
		if not self.settingsCtrl:
			return
		newStyle = MODEL_STYLE.CLEAN
		if self.settingsCtrl.get(SETTINGS.CURRENT_STYLE) == newStyle:
			newStyle = MODEL_STYLE.NICE
		self.settingsCtrl.apply({SETTINGS.CURRENT_STYLE: newStyle})

	def invokeHistoryDelete(self):
		self.battlesHistoryCtrl.deleteHistory()

	def __updateStaticData(self):
		self.as_setPreferencesS({'titleLabel': l10n('popover.titleLabel'),
			'closeButtonVisible': True,
			'saveOnlySession': self.settingsCtrl.get(SETTINGS.SAVE_ONLY_SESSION),
			'saveOnlySessionLabel': l10n('popover.saveOnlySessionLabel'),
			'saveOnlySessionDescription': l10n('popover.saveOnlySessionDescription'),
			'processReplays': self.settingsCtrl.get(SETTINGS.PROCESS_REPLAYS),
			'processReplaysLabel': l10n('popover.processReplaysLabel'),
			'processReplaysDescription': l10n('popover.processReplaysDescription'),
			'swapHangar': self.settingsCtrl.get(SETTINGS.SWAP_HANGAR),
			'swapHangarLabel': l10n('popover.swapHangarLabel'),
			'swapHangarDescription': l10n('popover.swapHangarDescription'),
			'changeStyleLabel': l10n('popover.changeStyleLabel'),
			'deleteHistoryLabel': l10n('popover.deleteHistoryLabel'),
			})
