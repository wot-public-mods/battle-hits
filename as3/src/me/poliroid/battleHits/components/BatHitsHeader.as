package me.poliroid.battleHits.components
{
	import flash.display.Sprite;
	import flash.text.TextField;
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.events.ButtonEvent;
	import net.wg.gui.components.controls.CloseButtonText;
	import net.wg.infrastructure.base.UIComponentEx;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	import me.poliroid.battleHits.controls.HitTypeButton;
	import me.poliroid.battleHits.controls.PopoverCallerButton;
	import me.poliroid.battleHits.data.BatHitsHeaderVO;
	import me.poliroid.battleHits.events.BatHitsEvent;
	import me.poliroid.battleHits.interfaces.IBatHitsHeader;

	public class BatHitsHeader extends UIComponentEx implements IBatHitsHeader
	{
		private static const CLOSE_BTN_OFFSET:int = 15;
		private static const HIT_TYPE_BTN_OFFSET:int = 127;

		public var background:Sprite;
		public var titleTF:TextField;
		public var closeBtn:CloseButtonText;
		public var settingsBtn:PopoverCallerButton;
		public var hitsTypeToPlayer:HitTypeButton;
		public var hitsTypeFromPlayer:HitTypeButton;

		override protected function onDispose(): void
		{
			closeBtn.removeEventListener(ButtonEvent.CLICK, onCloseBtnClickHandler);
			settingsBtn.removeEventListener(ButtonEvent.CLICK, onPreferencesClickHandler);
			hitsTypeToPlayer.removeEventListener(ButtonEvent.CLICK, onToPlayerClickHandler);
			hitsTypeFromPlayer.removeEventListener(ButtonEvent.CLICK, onFromPlayerClickHandler);

			closeBtn.dispose();
			settingsBtn.dispose();
			hitsTypeToPlayer.dispose();
			hitsTypeFromPlayer.dispose();

			closeBtn = null;
			settingsBtn = null;
			hitsTypeToPlayer = null;
			hitsTypeFromPlayer = null;
			background = null;
			titleTF = null;

			super.onDispose();
		}

		override protected function configUI(): void
		{
			super.configUI();

			closeBtn.addEventListener(ButtonEvent.CLICK, onCloseBtnClickHandler);
			settingsBtn.addEventListener(ButtonEvent.CLICK, onPreferencesClickHandler);
			hitsTypeToPlayer.addEventListener(ButtonEvent.CLICK, onToPlayerClickHandler);
			hitsTypeFromPlayer.addEventListener(ButtonEvent.CLICK, onFromPlayerClickHandler);
		}

		override protected function draw(): void
		{
			super.draw();

			if(isInvalid(InvalidationType.SIZE))
			{
				var screenWidth:int = App.appWidth;
				background.width = int(screenWidth);
				titleTF.x = int((screenWidth - titleTF.width) / 2);
				closeBtn.x = int(screenWidth - closeBtn.width - CLOSE_BTN_OFFSET);
				settingsBtn.x = int(closeBtn.x  - settingsBtn.width);
				hitsTypeToPlayer.x = int((screenWidth - HIT_TYPE_BTN_OFFSET * 2) / 2);
				hitsTypeFromPlayer.x = int(hitsTypeToPlayer.x + HIT_TYPE_BTN_OFFSET);
			}
		}

		public function get preferenceButton(): IPopOverCaller
		{
			return settingsBtn as IPopOverCaller;
		}

		public function updateDP(model:BatHitsHeaderVO): void
		{
			closeBtn.label = model.closeBtnLabel;
			settingsBtn.label = model.settingsLabel;
			titleTF.text = model.titleLabel;
			hitsTypeToPlayer.label = model.typeBtnMe;
			hitsTypeFromPlayer.label = model.typeBtnEnemys;
			hitsTypeToPlayer.isActive = model.typeBtnMeActive;
			hitsTypeFromPlayer.isActive = model.typeBtnEnemysActive;
			invalidateSize();
		}

		private function onCloseBtnClickHandler(e:ButtonEvent): void
		{
			dispatchEvent(new BatHitsEvent(BatHitsEvent.CLOSE_CLICK, true));
		}

		private function onPreferencesClickHandler(e:ButtonEvent): void
		{
			dispatchEvent(new BatHitsEvent(BatHitsEvent.PREFERENCES_CLICK, true));
		}

		private function onToPlayerClickHandler(e:ButtonEvent): void
		{
			dispatchEvent(new BatHitsEvent(BatHitsEvent.TO_PLAYER_CLICK, true));
			hitsTypeToPlayer.isActive = true;
			hitsTypeFromPlayer.isActive = false;
		}

		private function onFromPlayerClickHandler(e:ButtonEvent): void
		{
			dispatchEvent(new BatHitsEvent(BatHitsEvent.FROM_PLAYER_CLICK, true));
			hitsTypeToPlayer.isActive = false;
			hitsTypeFromPlayer.isActive = true;
		}
	}
}
