package me.poliroid.battleHits
{
	import flash.events.Event;
	import net.wg.gui.components.controls.CheckBox;
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.gui.components.popovers.PopOver;
	import scaleform.clik.events.ButtonEvent;
	import me.poliroid.battleHits.data.BattleHitsPreferencesDataVO;
	import me.poliroid.battleHits.interfaces.IPreferencesPopover
	import me.poliroid.battleHits.interfaces.impl.PreferencesPopoverMeta

	public class PreferencesPopover extends PreferencesPopoverMeta implements IPreferencesPopover 
	{
		public var saveOnlySession:CheckBox = null;
		public var processReplays:CheckBox = null;
		public var changeStyle:SoundButton = null; 
		public var deleteHistory:SoundButton = null;

		private static const LAYOUT_HEIGHT:uint = 170;

		override protected function onDispose(): void 
		{
			changeStyle.removeEventListener(ButtonEvent.PRESS, handeButtonClick);
			deleteHistory.removeEventListener(ButtonEvent.PRESS, handeButtonClick);

			processReplays.removeEventListener(Event.SELECT, handeCheckBoxSelect);
			saveOnlySession.removeEventListener(Event.SELECT, handeCheckBoxSelect);

			changeStyle.dispose();
			deleteHistory.dispose();
			processReplays.dispose();
			saveOnlySession.dispose();

			changeStyle = null;
			deleteHistory = null;
			processReplays = null;
			saveOnlySession = null;

			super.onDispose();
		}

		override protected function configUI(): void 
		{
			deleteHistory.addEventListener(ButtonEvent.PRESS, handeButtonClick);
			changeStyle.addEventListener(ButtonEvent.PRESS, handeButtonClick);

			processReplays.addEventListener(Event.SELECT, handeCheckBoxSelect);
			saveOnlySession.addEventListener(Event.SELECT, handeCheckBoxSelect);

			super.configUI();
		}

		override protected function setPreferences(data:BattleHitsPreferencesDataVO): void 
		{
			popoverLayout.preferredLayout = 0;

			var popoverWrapper:PopOver = PopOver(wrapper);
			popoverWrapper.title = data.titleLabel;
			popoverWrapper.isCloseBtnVisible = data.closeButtonVisible;

			saveOnlySession.label = data.saveOnlySessionLabel;
			saveOnlySession.toolTip = data.saveOnlySessionDescription;
			saveOnlySession.selected = data.saveOnlySession;

			processReplays.label = data.processReplaysLabel;
			processReplays.toolTip = data.processReplaysDescription;
			processReplays.selected = data.processReplays;

			changeStyle.label = data.changeStyleLabel;

			deleteHistory.label = data.deleteHistoryLabel;

			height = LAYOUT_HEIGHT;

			updateProcessReplays();
		}

		private function handeButtonClick(e:ButtonEvent): void 
		{
			switch (e.target)
			{
				case changeStyle:
					invokeStyleChangeS();
					break;
				case deleteHistory:
					invokeHistoryDeleteS();
					break;
			}
		}

		private function handeCheckBoxSelect(e:Event): void
		{
			invokeSettingsChangeS(processReplays.selected, saveOnlySession.selected);
			updateProcessReplays();
		}

		private function updateProcessReplays(): void
		{
			processReplays.enabled = !saveOnlySession.selected;
			processReplays.infoIcoType = saveOnlySession.selected ? 'warning' : 'info';
		}
	}
}
