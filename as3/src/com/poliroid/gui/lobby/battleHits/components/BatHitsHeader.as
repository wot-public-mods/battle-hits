package com.poliroid.gui.lobby.battleHits.components
{
	
	import flash.display.DisplayObject;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.text.TextField;
	import flash.text.TextFormat;
	import net.wg.gui.components.controls.ScrollingListEx;
	
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.events.ButtonEvent;
	
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.gui.components.controls.CloseButtonText;
	import net.wg.gui.interfaces.ISoundButtonEx;
	import net.wg.infrastructure.base.UIComponentEx;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHeaderVO;
	import com.poliroid.gui.lobby.battleHits.controls.HitTypeButton;
	import com.poliroid.gui.lobby.battleHits.events.BatHitsEvent;
	import com.poliroid.gui.lobby.battleHits.interfaces.IBatHitsHeader;
	import com.poliroid.gui.lobby.battleHits.interfaces.IHitTypeButton;
	
	public class BatHitsHeader extends UIComponentEx implements IPopOverCaller, IBatHitsHeader
	{
		
		private static const CLOSE_BTN_OFFSET:int = 15;
		
		private static const HIT_TYPE_BTN_OFFSET:int = 127;
		
		public var background:Sprite;
		
		public var titleTF:TextField;
		
		public var closeBtn:CloseButtonText;
		
		public var settingsBtn:CloseButtonText;
		
		public var hitsTypeToPlayer:HitTypeButton;
		
		public var hitsTypeFromPlayer:HitTypeButton;
		
		public function BatHitsHeader()
		{
			super();
		}
		
		override protected function onDispose() : void
		{
			closeBtn.removeEventListener(ButtonEvent.CLICK, onCloseBtnClickHandler);
			settingsBtn.removeEventListener(ButtonEvent.CLICK, onPreferencesClickHandler);
			hitsTypeToPlayer.removeEventListener(ButtonEvent.CLICK, onToPlayerClickHandler);
			hitsTypeFromPlayer.removeEventListener(ButtonEvent.CLICK, onFromPlayerClickHandler);
			
			//background.dispose();
			closeBtn.dispose();
			settingsBtn.dispose();
			hitsTypeToPlayer.dispose();
			hitsTypeFromPlayer.dispose();
			
			background = null;
			closeBtn = null;
			settingsBtn = null;
			hitsTypeToPlayer = null;
			hitsTypeFromPlayer = null;
			
			super.onDispose();
		}
		
		override protected function configUI() : void
		{
			super.configUI();
			
			closeBtn.addEventListener(ButtonEvent.CLICK, onCloseBtnClickHandler);
			settingsBtn.addEventListener(ButtonEvent.CLICK, onPreferencesClickHandler);
			hitsTypeToPlayer.addEventListener(ButtonEvent.CLICK, onToPlayerClickHandler);
			hitsTypeFromPlayer.addEventListener(ButtonEvent.CLICK, onFromPlayerClickHandler);
		}
		
		override protected function draw() : void
		{
			super.draw();
			
			if(isInvalid(InvalidationType.SIZE))
			{
				background.width = width;
				layout();
			}
		}
		
		public function get preferenceBtn() : IPopOverCaller
		{
			return settingsBtn as IPopOverCaller;
		}
		
		public function update(ctx:Object) : void
		{
			closeBtn.label = ctx.closeBtnLabel;
			settingsBtn.label = ctx.settingsLabel;
			titleTF.text = ctx.titleLabel;
			
			hitsTypeToPlayer.label = ctx.typeBtnMe;
			hitsTypeFromPlayer.label = ctx.typeBtnEnemys;
			hitsTypeToPlayer.isActive = ctx.typeBtnMeActive;
			hitsTypeFromPlayer.isActive = ctx.typeBtnEnemysActive;
			
			layout();
			ctx.dispose();
		}
		
		private function layout() : void
		{
			titleTF.x = Number((width - titleTF.width) / 2);
			closeBtn.x = width - closeBtn.width - CLOSE_BTN_OFFSET;
			settingsBtn.x = closeBtn.x  - settingsBtn.width;
			hitsTypeToPlayer.x = Number((width - HIT_TYPE_BTN_OFFSET * 2) / 2);
			hitsTypeFromPlayer.x = hitsTypeToPlayer.x + HIT_TYPE_BTN_OFFSET;
		}
		
		private function onCloseBtnClickHandler(e:ButtonEvent) : void
		{
			dispatchEvent(new BatHitsEvent(BatHitsEvent.CLOSE_CLICK, true));
		}
		
		private function onPreferencesClickHandler(e:ButtonEvent) : void
		{
			dispatchEvent(new BatHitsEvent(BatHitsEvent.PREFERENCES_CLICK, true));
		}
		
		private function onToPlayerClickHandler(e:ButtonEvent) : void
		{
			dispatchEvent(new BatHitsEvent(BatHitsEvent.TO_PLAYER_CLICK, true));
			hitsTypeToPlayer.isActive = true;
			hitsTypeFromPlayer.isActive = false;
		}
		
		private function onFromPlayerClickHandler(e:ButtonEvent) : void
		{
			dispatchEvent(new BatHitsEvent(BatHitsEvent.FROM_PLAYER_CLICK, true));
			hitsTypeToPlayer.isActive = false;
			hitsTypeFromPlayer.isActive = true;
		}
		
		// this needs for correct preferences smart popover work
		public function getTargetButton() : DisplayObject 
		{
			return DisplayObject(settingsBtn);
		}
		
		// this needs for correct preferences smart popover work
		public function getHitArea() : DisplayObject 
		{
			return DisplayObject(settingsBtn);
		}
	}
}
