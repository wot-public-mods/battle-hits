package com.poliroid.gui.lobby.battleHits.controls 
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.constants.InvalidationType;
	import net.wg.gui.components.controls.SoundListItemRenderer;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHitVO;
	import com.poliroid.gui.lobby.battleHits.events.BatHitsIndexEvent;

	public class HitItemRenderer extends SoundListItemRenderer
	{
		public var hitIdTF:TextField = null;
		public var vehicleTF:TextField = null;
		public var resultTF:TextField = null;
		public var shellTF:TextField = null;
		public var damageTF:TextField = null;
		public var hitAreaA:MovieClip = null;
		public var anonymizedMC:MovieClip = null;

		private var model:BatHitsHitVO = null;

		public function HitItemRenderer() 
		{
			super();
			scaleY = 1;
			scaleX = 1;
			hitArea = hitAreaA;
			preventAutosizing = true;
		}

		override protected function configUI(): void
		{
			super.configUI();
			mouseEnabledOnDisabled = true;
		}

		override public function setData(data:Object): void 
		{
			if (data == null) 
				return;
			super.setData(data);
			model = BatHitsHitVO(data);
			invalidateData();
		}

		override protected function onDispose(): void
		{
			if (model != null)
				model.dispose();
			model = null;

			hitIdTF = null;
			vehicleTF = null;
			resultTF = null;
			shellTF = null;
			damageTF = null;
			hitAreaA = null;
			anonymizedMC = null;

			super.onDispose();
		}

		override protected function draw(): void 
		{
			super.draw();
			if ((model != null) && (isInvalid(InvalidationType.DATA)))
			{
				hitIdTF.text = model.numberLabel;
				vehicleTF.text = model.vehicleLabel;
				resultTF.text = model.resultLabel;
				shellTF.text = model.shellLabel;
				damageTF.text = model.damageLabel;
				anonymizedMC.visible =  model.anonymized;
				anonymizedMC.x = Number((vehicleTF.x + vehicleTF.width / 2) + (vehicleTF.textWidth / 2));
			}
		}
	}
}
