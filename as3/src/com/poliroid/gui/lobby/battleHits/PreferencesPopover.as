package com.poliroid.gui.lobby.battleHits
{
	import flash.events.MouseEvent;
	import net.wg.gui.components.controls.CheckBox;
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.infrastructure.interfaces.IWrapper;
	import net.wg.gui.components.popovers.PopOver;
	
	import scaleform.clik.constants.InvalidationType;
	
	import com.poliroid.gui.lobby.battleHits.data.BattleHitsPreferencesDataVO;
	import com.poliroid.gui.lobby.battleHits.interfaces.IPreferencesPopover
	import com.poliroid.gui.lobby.battleHits.interfaces.impl.PreferencesPopoverMeta
	
	public class PreferencesPopover extends PreferencesPopoverMeta implements IPreferencesPopover 
	{
		
		private static const RENDERER_HEIGHT:int = 75;
		
		private static const BOTTOM_OFFSET:int = 10;
		
		public var saveOnlySession:CheckBox = null;
		
		public var processReplays:CheckBox = null;
		
		public var changeStyle:SoundButton = null; 
		
		public function PreferencesPopover() 
		{
			super();
		}
		
		override protected function onDispose() : void 
		{
			invokeChangeS(processReplays.selected, saveOnlySession.selected);
			changeStyle.removeEventListener(MouseEvent.CLICK, handeStyleClick);
			super.onDispose();
		}
		
		override protected function configUI() : void 
		{
			changeStyle.addEventListener(MouseEvent.CLICK, handeStyleClick);
			super.configUI();
		}
		
		override protected function setPreferences(data:BattleHitsPreferencesDataVO) : void 
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
			
			height = 120;
		}
		
		private function handeStyleClick(e:MouseEvent) 
		{
			invokeStyleS();
		}
	}
}