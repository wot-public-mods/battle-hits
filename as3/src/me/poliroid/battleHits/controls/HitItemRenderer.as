package me.poliroid.battleHits.controls 
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.constants.InvalidationType;
	import net.wg.gui.components.controls.SoundListItemRenderer;
	import me.poliroid.battleHits.data.BatHitsHitVO;
	import me.poliroid.battleHits.events.BatHitsIndexEvent;

	public class HitItemRenderer extends SoundListItemRenderer
	{
		public var hitIdTF:TextField = null;
		public var vehicleTF:TextField = null;
		public var resultTF:TextField = null;
		public var damageTF:TextField = null;
		public var hitAreaA:MovieClip = null;
		public var anonymizedMC:MovieClip = null;

		public var shell:ShellRenderer = null;

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
			shell = null;
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
				shell.setData(model);
				damageTF.text = model.damageLabel;
				anonymizedMC.visible =  model.anonymized;
				anonymizedMC.x = Number((vehicleTF.x + vehicleTF.width / 2) + (vehicleTF.textWidth / 2));
			}
		}
	}
}
