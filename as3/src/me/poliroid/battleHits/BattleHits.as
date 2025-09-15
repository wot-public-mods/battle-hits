package me.poliroid.battleHits
{
	import flash.display.InteractiveObject;
	import flash.events.KeyboardEvent;
	import flash.ui.Keyboard;

	import scaleform.clik.events.InputEvent;
	import scaleform.clik.motion.Tween;

	import net.wg.gui.components.containers.inject.GFInjectComponent;
	import net.wg.gui.events.LobbyEvent;

	import me.poliroid.battleHits.data.BatHitsBattlesVO;
	import me.poliroid.battleHits.data.BatHitsHitsVO;
	import me.poliroid.battleHits.data.BatHitsStaticDataVO;
	import me.poliroid.battleHits.events.BatHitsIndexEvent;
	import me.poliroid.battleHits.interfaces.IBatHitsBattlesPanel;
	import me.poliroid.battleHits.interfaces.IBatHitsHitsPanel;
	import me.poliroid.battleHits.interfaces.IBattleHitsMeta;
	import me.poliroid.battleHits.interfaces.impl.BattleHitsMeta;

	public class BattleHits extends BattleHitsMeta implements IBattleHitsMeta
	{
		private static const POPOVER_ALIAS:String = 'BattleHitsPreferencesPopover';
		private static const ANIMATION_DURATION:int = 200;
		private static const ANIMATION_DELAY:int = 150;
		private static const SHOW_SLOTS_ALPHA:Number = 1;
		private static const HIDE_SLOTS_ALPHA:Number = 0;

		public var hitsPanel:IBatHitsHitsPanel = null;
		public var battlesPanel:IBatHitsBattlesPanel = null;

		private var _tweenInfoHide:Tween = null;
		private var _tweenInfoShow:Tween = null;

		public var _headerInject:GFInjectComponent = null;
		private static const HEADER_INJECT_ALIAS:String = 'BattleHitsHeaderView';
		private static const HEADER_INJECT_WIDTH:int = 400;
		private static const HEADER_INJECT_HEIGHT:int = 90;

		override public function updateStage(_width:Number, _height:Number): void
		{
			battlesPanel.x = int(_width - battlesPanel.width);
			_updateHeaderInject();
		}

		override protected function configUI(): void
		{
			super.configUI();
			_createHeaderInject();
		}

		override protected function setStaticData(model:BatHitsStaticDataVO): void
		{
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

			App.gameInputMgr.setKeyHandler(Keyboard.ESCAPE, KeyboardEvent.KEY_DOWN, onEscapeKeyDownHandler, true);

			App.stage.dispatchEvent(new LobbyEvent(LobbyEvent.REGISTER_DRAGGING));

			addEventListener(BatHitsIndexEvent.BATTLE_CHANGED, onBattleSelectHandler);
			addEventListener(BatHitsIndexEvent.HIT_CHANGED, onHitSelectHandler);
			addEventListener(BatHitsIndexEvent.SORT_CLICKED, onSortClickHandler);

			App.stage.addEventListener(LobbyEvent.DRAGGING_START, onDraggingStartHandler);
			App.stage.addEventListener(LobbyEvent.DRAGGING_END, onDraggingEndHandler);

			updateStage(App.appWidth, App.appHeight);
		}

		override protected function onBeforeDispose(): void
		{
			App.gameInputMgr.clearKeyHandler(Keyboard.ESCAPE, KeyboardEvent.KEY_DOWN, onEscapeKeyDownHandler);
			
			App.stage.removeEventListener(LobbyEvent.DRAGGING_START, onDraggingStartHandler);
			App.stage.removeEventListener(LobbyEvent.DRAGGING_END, onDraggingEndHandler);

			App.stage.dispatchEvent(new LobbyEvent(LobbyEvent.UNREGISTER_DRAGGING));

			removeEventListener(BatHitsIndexEvent.BATTLE_CHANGED, onBattleSelectHandler);
			removeEventListener(BatHitsIndexEvent.HIT_CHANGED, onHitSelectHandler);
			removeEventListener(BatHitsIndexEvent.SORT_CLICKED, onSortClickHandler);

			_destroyHeaderInject();

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

			hitsPanel.dispose();
			battlesPanel.dispose();

			hitsPanel = null;
			battlesPanel = null;

			App.toolTipMgr.hide();

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

		private function onEscapeKeyDownHandler(event:InputEvent):void
		{
			closeWindowS();
		}

		private function _createHeaderInject(): void
		{
			if (_headerInject)
				return;
			_headerInject = new GFInjectComponent();
			_headerInject.setManageSize(true);
			addChild(_headerInject);
			registerFlashComponentS(_headerInject, HEADER_INJECT_ALIAS);
		}

		private function _destroyHeaderInject(): void
		{
			if (!_headerInject)
				return;
			unregisterFlashComponentS(HEADER_INJECT_ALIAS);
			removeChild(_headerInject);
			_headerInject = null;
		}

		private function _updateHeaderInject(): void
		{
			if (!_headerInject)
				return;
			_headerInject.x = int((App.appWidth - HEADER_INJECT_WIDTH) * 0.5);
			_headerInject.y = 0;
			_headerInject.setSize(HEADER_INJECT_WIDTH, HEADER_INJECT_HEIGHT);
		}
	}
}
