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
		public var swapHangar:CheckBox = null;
		public var processFlamethrowers:CheckBox = null;
		public var changeStyle:SoundButton = null; 
		public var deleteHistory:SoundButton = null;

		private static const LAYOUT_HEIGHT:uint = 200;
		private static const LAYOUT_HEIGHT_WITH_FLAMETHROVER:uint = 240;

		override protected function onDispose(): void 
		{
			changeStyle.removeEventListener(ButtonEvent.PRESS, handeButtonClick);
			deleteHistory.removeEventListener(ButtonEvent.PRESS, handeButtonClick);

			processReplays.removeEventListener(Event.SELECT, handeCheckBoxSelect);
			saveOnlySession.removeEventListener(Event.SELECT, handeCheckBoxSelect);
			swapHangar.removeEventListener(Event.SELECT, handeCheckBoxSelect);
			processFlamethrowers.removeEventListener(Event.SELECT, handeCheckBoxSelect);

			changeStyle.dispose();
			deleteHistory.dispose();
			processReplays.dispose();
			saveOnlySession.dispose();
			swapHangar.dispose();
			processFlamethrowers.dispose();

			changeStyle = null;
			deleteHistory = null;
			processReplays = null;
			saveOnlySession = null;
			swapHangar = null;
			processFlamethrowers = null;

			super.onDispose();
		}

		override protected function configUI(): void 
		{
			deleteHistory.addEventListener(ButtonEvent.PRESS, handeButtonClick);
			changeStyle.addEventListener(ButtonEvent.PRESS, handeButtonClick);

			processReplays.addEventListener(Event.SELECT, handeCheckBoxSelect);
			saveOnlySession.addEventListener(Event.SELECT, handeCheckBoxSelect);
			swapHangar.addEventListener(Event.SELECT, handeCheckBoxSelect);
			processFlamethrowers.addEventListener(Event.SELECT, handeCheckBoxSelect);

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

			swapHangar.label = data.swapHangarLabel;
			swapHangar.toolTip = data.swapHangarDescription;
			swapHangar.selected = data.swapHangar;

			changeStyle.label = data.changeStyleLabel;

			deleteHistory.label = data.deleteHistoryLabel;

			processFlamethrowers.label = data.processFlamethrowersLabel;
			processFlamethrowers.toolTip = data.processFlamethrowersDescription;
			processFlamethrowers.selected = data.processFlamethrowers;
			processFlamethrowers.visible = data.flamethrowersMechanicExist;

			height = data.flamethrowersMechanicExist ? LAYOUT_HEIGHT_WITH_FLAMETHROVER : LAYOUT_HEIGHT;

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
			invokeSettingsChangeS(processReplays.selected, saveOnlySession.selected, swapHangar.selected, processFlamethrowers.selected);
			updateProcessReplays();
		}

		private function updateProcessReplays(): void
		{
			processReplays.enabled = !saveOnlySession.selected;
			processReplays.infoIcoType = saveOnlySession.selected ? 'warning' : 'info';
		}
	}
}
