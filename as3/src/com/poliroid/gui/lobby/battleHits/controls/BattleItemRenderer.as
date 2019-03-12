package com.poliroid.gui.lobby.battleHits.controls 
{
	
	import flash.display.MovieClip;
	import flash.text.TextField;
	import scaleform.clik.events.ButtonEvent;
	
	import scaleform.clik.constants.InvalidationType;
	
	import net.wg.gui.components.controls.SoundListItemRenderer;
	
	import com.poliroid.gui.lobby.battleHits.data.BatHitsBattleVO;
	import com.poliroid.gui.lobby.battleHits.events.BatHitsIndexEvent;
	import scaleform.clik.events.InputEvent;
	
	public class BattleItemRenderer extends SoundListItemRenderer
	{
		
		public var mapNameTF:TextField = null;
		
		public var tankNameTF:TextField = null;
		
		public var dateTimeTF:TextField = null;
		
		public var hitAreaA:MovieClip = null;
		
		private var model:BatHitsBattleVO = null;
		
		public function BattleItemRenderer() 
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
			
			model = BatHitsBattleVO(data);
			invalidateData();
		}
		
		override protected function onDispose(): void
		{
			mapNameTF = null;
			tankNameTF = null;
			dateTimeTF = null;
			
			super.onDispose();
		}
		
		override protected function draw() : void 
		{
			super.draw();
			if ((model != null) && (isInvalid(InvalidationType.DATA)))
			{
				mapNameTF.text = model.mapNameLabel;
				tankNameTF.text = model.vehicleNameLabel;
				dateTimeTF.text = model.battleStartLabel;
			}
		}
		
	}
}