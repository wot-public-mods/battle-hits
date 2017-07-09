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
		
		public var enemyTankTF:TextField = null;
		
		public var resultTF:TextField = null;
		
		public var shellTF:TextField = null;
		
		public var damageTF:TextField = null;
		
		public var hitAreaA:MovieClip = null;
		
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
		
		override public function setData(data:Object) : void 
		{
			if (data == null) 
				return;
			
			super.setData(data);
			
			model = BatHitsHitVO(data);
			invalidateData();
		}
		
		override protected function onDispose(): void
		{
			enemyTankTF = null;
			resultTF = null;
			shellTF = null;
			damageTF = null;
			hitAreaA = null;
			
			super.onDispose();
		}
		
		override protected function draw() : void 
		{
			super.draw();
			if(model != null)
			{
				if (isInvalid(InvalidationType.DATA)) 
				{
					enemyTankTF.text = model.enemyTankLabel;
					resultTF.text = model.resultLabel;
					shellTF.text = model.shellLabel;
					damageTF.text = model.damageLabel;
				}
			}
		}
		
	}
}