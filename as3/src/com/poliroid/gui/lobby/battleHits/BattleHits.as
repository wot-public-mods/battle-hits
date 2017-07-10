package com.poliroid.gui.lobby.battleHits
{
	import flash.display.InteractiveObject;
	import flash.events.KeyboardEvent;
	import flash.ui.Keyboard;
	import net.wg.data.constants.Linkages;
	import net.wg.gui.components.controls.DropdownMenu;
	import net.wg.gui.components.controls.ScrollingListEx;
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	import scaleform.clik.events.ButtonEvent;
	
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.events.InputEvent;
	import scaleform.clik.data.DataProvider;
	
	import net.wg.data.constants.generated.VEHPREVIEW_CONSTANTS;
	import net.wg.gui.events.LobbyEvent;
	import net.wg.gui.interfaces.IUpdatableComponent;
	
	import com.poliroid.gui.lobby.battleHits.data.BatHitsBattlesVO;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHitsVO;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsStaticDataVO;
	import com.poliroid.gui.lobby.battleHits.events.BatHitsEvent;
	import com.poliroid.gui.lobby.battleHits.events.BatHitsIndexEvent;
	import com.poliroid.gui.lobby.battleHits.interfaces.IBatHitsHeader;
	import com.poliroid.gui.lobby.battleHits.interfaces.IBatHitsHitsPanel;
	import com.poliroid.gui.lobby.battleHits.interfaces.IBatHitsBattlesPanel;
	import com.poliroid.gui.lobby.battleHits.interfaces.IBattleHitsMeta;
	import com.poliroid.gui.lobby.battleHits.interfaces.impl.BattleHitsMeta;
	
	public class BattleHits extends BattleHitsMeta implements IBattleHitsMeta
	{
		
		private static const BOTTOM_MARGIN:int = 100;
		
		private static const BOTTOM_OFFSET:Number = 50;
		
		private static const GAP:int = 2;
		
		private static const POPOVER_ALIAS:String = 'BattleHitsPreferencesPopover';
		
		public var header:IBatHitsHeader = null;
		
		public var hitsPanel:IBatHitsHitsPanel = null;
		
		public var battlesPanel:IBatHitsBattlesPanel = null;
		
		public function BattleHits()
		{
			super();
		}
		
		override public function updateStage(_width:Number, _height:Number) : void
		{
			setSize(_width, _height);
		}
		
		override protected function setStaticData(data:BatHitsStaticDataVO) : void
		{
			header.update(data.header);
			battlesPanel.update(data.battles);
			hitsPanel.update(data.hits);
			//detailedShotPanel.update(data.detailedShot);
		}
		
		override protected function updateBattlesDPData(data:BatHitsBattlesVO) : void
		{
			battlesPanel.updateDP(data);
		}
		
		override protected function updateHitsDPData(data:BatHitsHitsVO) : void
		{
			hitsPanel.updateDP(data);
		}
		
		override protected function configUI() : void
		{
			super.configUI();
			
			App.stage.dispatchEvent(new LobbyEvent(LobbyEvent.REGISTER_DRAGGING));
			
			layout();
			
			addEventListener(BatHitsEvent.CLOSE_CLICK, onCloseClickHandler);
			addEventListener(BatHitsEvent.PREFERENCES_CLICK, onPreferencesClickHandler);
			addEventListener(BatHitsEvent.TO_PLAYER_CLICK, onToPlayerClickHandler);
			addEventListener(BatHitsEvent.FROM_PLAYER_CLICK, onFromPlayerClickHandler);
			addEventListener(BatHitsIndexEvent.BATTLE_CHANGED, onBattleSelectHandler);
			addEventListener(BatHitsIndexEvent.HIT_CHANGED, onHitSelectHandler);
			addEventListener(BatHitsIndexEvent.SORT_CLICKED, onSortClickHandler);
			
			App.gameInputMgr.setKeyHandler(Keyboard.UP, KeyboardEvent.KEY_DOWN, onUpKeyUpHandler, true);
			App.gameInputMgr.setKeyHandler(Keyboard.DOWN, KeyboardEvent.KEY_DOWN, onDownKeyUpHandler, true);
			App.gameInputMgr.setKeyHandler(Keyboard.LEFT, KeyboardEvent.KEY_DOWN, onLeftKeyUpHandler, true);
			App.gameInputMgr.setKeyHandler(Keyboard.RIGHT, KeyboardEvent.KEY_DOWN, onRightKeyUpHandler, true);
			App.gameInputMgr.setKeyHandler(Keyboard.ESCAPE, KeyboardEvent.KEY_DOWN, onEscapeKeyUpHandler, true);
			
		}
		
		override protected function onInitModalFocus(param1:InteractiveObject) : void
        {
            super.onInitModalFocus(param1);
            setFocus(this);
        }
		
		override protected function onDispose() : void
		{
			App.gameInputMgr.clearKeyHandler(Keyboard.UP, KeyboardEvent.KEY_DOWN);
			App.gameInputMgr.clearKeyHandler(Keyboard.DOWN, KeyboardEvent.KEY_DOWN);
			App.gameInputMgr.clearKeyHandler(Keyboard.LEFT, KeyboardEvent.KEY_DOWN);
			App.gameInputMgr.clearKeyHandler(Keyboard.RIGHT, KeyboardEvent.KEY_DOWN);
			App.gameInputMgr.clearKeyHandler(Keyboard.ESCAPE, KeyboardEvent.KEY_DOWN);
			
			App.stage.dispatchEvent(new LobbyEvent(LobbyEvent.UNREGISTER_DRAGGING));
			
			removeEventListener(BatHitsEvent.CLOSE_CLICK, onCloseClickHandler);
			removeEventListener(BatHitsEvent.PREFERENCES_CLICK, onPreferencesClickHandler);
			removeEventListener(BatHitsEvent.TO_PLAYER_CLICK, onToPlayerClickHandler);
			removeEventListener(BatHitsEvent.FROM_PLAYER_CLICK, onFromPlayerClickHandler);
			removeEventListener(BatHitsIndexEvent.BATTLE_CHANGED, onBattleSelectHandler);
			removeEventListener(BatHitsIndexEvent.HIT_CHANGED, onHitSelectHandler);
			removeEventListener(BatHitsIndexEvent.SORT_CLICKED, onSortClickHandler);
			
			header = null;
			
			hitsPanel = null;
			
			battlesPanel = null;
			
			//detailedShotPanel = null;
			
			super.onDispose();
		}
		
		override protected function draw() : void
		{
			super.draw();
			if(isInvalid(InvalidationType.SIZE))
			{
				var sceneWidth:Number = width;
				var sceneHeight:Number = height;
				header.width = sceneWidth;
				layout();
			}
		}
		
		private function layout() : void
		{
			var sceneWidth:Number = width;
			var sceneHeight:Number = height;
			hitsPanel.height = sceneHeight / 2;
			battlesPanel.height = sceneHeight / 2;
			battlesPanel.x = sceneWidth - battlesPanel.width;
		}
		
		private function onUpKeyUpHandler(e:InputEvent) : void
		{
			onBattleSelectS(battlesPanel._battlesList.prevItemID);
		}
		
		private function onDownKeyUpHandler(e:InputEvent) : void
		{
			onBattleSelectS(battlesPanel._battlesList.nextItemID);
		}
		
		private function onLeftKeyUpHandler(e:InputEvent) : void
		{
			onHitSelectS(hitsPanel._hitsList.prevItemID);
		}
		
		private function onRightKeyUpHandler(e:InputEvent) : void
		{
			onHitSelectS(hitsPanel._hitsList.nextItemID);
		}
		
		private function onEscapeKeyUpHandler(e:InputEvent) : void
		{
			closeViewS();
		}
		
		private function onCloseClickHandler(e:BatHitsEvent) : void
		{
			closeViewS();
		}
		
		private function onBattleSelectHandler(e:BatHitsIndexEvent) : void
		{
			onBattleSelectS(e.selectedIndex);
		}
		
		private function onHitSelectHandler(e:BatHitsIndexEvent) : void
		{
			onHitSelectS(e.selectedIndex);
		}
		
		private function onSortClickHandler(e:BatHitsIndexEvent) : void
		{
			onSortClickS(e.selectedIndex);
		}
		
		private function onPreferencesClickHandler(e:BatHitsEvent) : void
		{
			preferencesClickS();
			App.popoverMgr.hide();
			App.popoverMgr.show(header as IPopOverCaller, POPOVER_ALIAS);
		}
		
		private function onToPlayerClickHandler(e:BatHitsEvent) : void
		{
			hitsToPlayerClickS(true);
		}
		
		private function onFromPlayerClickHandler(e:BatHitsEvent) : void
		{
			hitsToPlayerClickS(false);
		}
		
	}
}
