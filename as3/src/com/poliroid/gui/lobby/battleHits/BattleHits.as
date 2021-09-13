package com.poliroid.gui.lobby.battleHits
{
	import flash.display.InteractiveObject;
	import scaleform.clik.motion.Tween;
	import net.wg.gui.events.LobbyEvent;

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
		private static const POPOVER_ALIAS:String = 'BattleHitsPreferencesPopover';
		private static const ANIMATION_DURATION:int = 200;
		private static const ANIMATION_DELAY:int = 150;
		private static const SHOW_SLOTS_ALPHA:Number = 1;
		private static const HIDE_SLOTS_ALPHA:Number = 0;

		public var header:IBatHitsHeader = null;
		public var hitsPanel:IBatHitsHitsPanel = null;
		public var battlesPanel:IBatHitsBattlesPanel = null;

		private var _tweenInfoHide:Tween = null;
		private var _tweenInfoShow:Tween = null;

		override public function updateStage(_width:Number, _height:Number): void
		{
			header.invalidateSize();
			battlesPanel.x = int(_width - battlesPanel.width);
		}

		override protected function setStaticData(model:BatHitsStaticDataVO): void
		{
			header.updateDP(model.header);
			battlesPanel.updateDP(model.battles);
			hitsPanel.updateDP(model.hits);
		}

		override protected function updateBattlesDPData(model:BatHitsBattlesVO): void
		{
			battlesPanel.updateDP(model);
		}

		override protected function updateHitsDPData(model:BatHitsHitsVO): void
		{
			hitsPanel.updateDP(model);
		}

		override protected function onInitModalFocus(target:InteractiveObject): void
		{
			super.onInitModalFocus(target);
			setFocus(this);
		}

		override protected function onPopulate(): void
		{
			super.onPopulate();

			App.stage.dispatchEvent(new LobbyEvent(LobbyEvent.REGISTER_DRAGGING));

			addEventListener(BatHitsEvent.CLOSE_CLICK, onCloseClickHandler);
			addEventListener(BatHitsEvent.PREFERENCES_CLICK, onPreferencesClickHandler);
			addEventListener(BatHitsEvent.TO_PLAYER_CLICK, onToPlayerClickHandler);
			addEventListener(BatHitsEvent.FROM_PLAYER_CLICK, onFromPlayerClickHandler);
			addEventListener(BatHitsIndexEvent.BATTLE_CHANGED, onBattleSelectHandler);
			addEventListener(BatHitsIndexEvent.HIT_CHANGED, onHitSelectHandler);
			addEventListener(BatHitsIndexEvent.SORT_CLICKED, onSortClickHandler);

			App.stage.addEventListener(LobbyEvent.DRAGGING_START, onDraggingStartHandler);
			App.stage.addEventListener(LobbyEvent.DRAGGING_END, onDraggingEndHandler);

			updateStage(App.appWidth, App.appHeight);
		}

		override protected function onBeforeDispose(): void
		{
			App.stage.removeEventListener(LobbyEvent.DRAGGING_START, onDraggingStartHandler);
			App.stage.removeEventListener(LobbyEvent.DRAGGING_END, onDraggingEndHandler);

			App.stage.dispatchEvent(new LobbyEvent(LobbyEvent.UNREGISTER_DRAGGING));

			removeEventListener(BatHitsEvent.CLOSE_CLICK, onCloseClickHandler);
			removeEventListener(BatHitsEvent.PREFERENCES_CLICK, onPreferencesClickHandler);
			removeEventListener(BatHitsEvent.TO_PLAYER_CLICK, onToPlayerClickHandler);
			removeEventListener(BatHitsEvent.FROM_PLAYER_CLICK, onFromPlayerClickHandler);
			removeEventListener(BatHitsIndexEvent.BATTLE_CHANGED, onBattleSelectHandler);
			removeEventListener(BatHitsIndexEvent.HIT_CHANGED, onHitSelectHandler);
			removeEventListener(BatHitsIndexEvent.SORT_CLICKED, onSortClickHandler);

			super.onBeforeDispose();
		}

		override protected function onDispose(): void
		{
			if(_tweenInfoHide != null)
			{
				_tweenInfoHide.paused = true;
				_tweenInfoHide.dispose();
			}
			_tweenInfoHide = null;

			if(_tweenInfoShow != null)
			{
				_tweenInfoShow.paused = true;
				_tweenInfoShow.dispose();
			}
			_tweenInfoShow = null;

			header.dispose();
			hitsPanel.dispose();
			battlesPanel.dispose();

			header = null;
			hitsPanel = null;
			battlesPanel = null;

			super.onDispose();
		}

		private function onDraggingEndHandler(e:LobbyEvent): void
		{
			if(_tweenInfoHide)
			{
				_tweenInfoHide.paused = true;
			}
			if(_tweenInfoShow)
			{
				_tweenInfoShow.paused = true;
				_tweenInfoShow.dispose();
			}
			if(this.alpha != SHOW_SLOTS_ALPHA)
			{
				_tweenInfoShow = new Tween(ANIMATION_DURATION, this, {"alpha": SHOW_SLOTS_ALPHA}, {});
			}
		}

		private function onDraggingStartHandler(e:LobbyEvent): void
		{
			if(_tweenInfoShow)
			{
				_tweenInfoShow.paused = true;
			}
			if(_tweenInfoHide)
			{
				_tweenInfoHide.paused = true;
				_tweenInfoHide.dispose();
			}
			_tweenInfoHide = new Tween(ANIMATION_DURATION, this, {"alpha": HIDE_SLOTS_ALPHA}, {"delay": ANIMATION_DELAY});
		}

		private function onCloseClickHandler(e:BatHitsEvent): void
		{
			closeViewS();
		}

		private function onBattleSelectHandler(e:BatHitsIndexEvent): void
		{
			onBattleSelectS(e.selectedIndex);
		}

		private function onHitSelectHandler(e:BatHitsIndexEvent): void
		{
			onHitSelectS(e.selectedIndex);
		}

		private function onSortClickHandler(e:BatHitsIndexEvent): void
		{
			onSortClickS(e.selectedIndex);
		}

		private function onPreferencesClickHandler(e:BatHitsEvent): void
		{
			preferencesClickS();
			App.popoverMgr.hide();
			App.popoverMgr.show(header.preferenceButton, POPOVER_ALIAS);
		}

		private function onToPlayerClickHandler(e:BatHitsEvent): void
		{
			hitsToPlayerClickS(true);
		}

		private function onFromPlayerClickHandler(e:BatHitsEvent): void
		{
			hitsToPlayerClickS(false);
		}
	}
}
