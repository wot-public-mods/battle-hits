package com.poliroid.gui.lobby.battleHits
{
	import net.wg.gui.components.controls.CheckBox;
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.gui.components.popovers.PopOver;
	import scaleform.clik.events.ButtonEvent;
	import com.poliroid.gui.lobby.battleHits.data.BattleHitsPreferencesDataVO;
	import com.poliroid.gui.lobby.battleHits.interfaces.IPreferencesPopover
	import com.poliroid.gui.lobby.battleHits.interfaces.impl.PreferencesPopoverMeta

	public class PreferencesPopover extends PreferencesPopoverMeta implements IPreferencesPopover 
	{
		public var saveOnlySession:CheckBox = null;
		public var processReplays:CheckBox = null;
		public var changeStyle:SoundButton = null; 
		public var deleteHistory:SoundButton = null;

		override protected function onBeforeDispose(): void
		{
			invokeChangeS(processReplays.selected, saveOnlySession.selected);
			super.onBeforeDispose();
		}

		override protected function onDispose(): void 
		{
			changeStyle.removeEventListener(ButtonEvent.PRESS, handeButtonClick);
			deleteHistory.removeEventListener(ButtonEvent.PRESS, handeButtonClick);

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

			height = 165;
		}

		private function handeButtonClick(e:ButtonEvent): void 
		{
			switch (e.target)
			{
				case changeStyle:
					invokeStyleS();
					break;
				case deleteHistory:
					invokeDataS();
					break;
			}
		}
	}
}
