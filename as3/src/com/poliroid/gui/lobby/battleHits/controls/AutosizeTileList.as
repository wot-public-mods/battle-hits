package com.poliroid.gui.lobby.battleHits.controls
{
	
	import flash.display.DisplayObject;
	import scaleform.clik.constants.DirectionMode;
	import scaleform.clik.interfaces.IListItemRenderer;
	import scaleform.clik.constants.InvalidationType;
	
	import net.wg.gui.components.controls.SimpleTileList;
	
	public dynamic class AutosizeTileList extends SimpleTileList
	{
		private static const INVALIDATE_LAYOUT:String = "invalidate_layout";
		
		private static const INVALIDATE_RENDERER:String = "invalidate_renderer";
		
		public function AutosizeTileList() 
		{
			super();
		}
		override protected function draw() : void
		{
			super.draw();
			if(isInvalid(InvalidationType.SIZE) || isInvalid(InvalidationType.DATA) || isInvalid(INVALIDATE_LAYOUT) || isInvalid(INVALIDATE_RENDERER))
			{
				updateOwnLayout();
			}
			
		}
		private function updateOwnLayout() : void
		{
			var render:IListItemRenderer = null;
			var prevRender:IListItemRenderer = null;
			var renderNum:Number = 0;
			while(renderNum < length)
			{
				render = getRendererAt(renderNum);
				
				if (prevRender != null) 
				{
					render.x = prevRender.x + prevRender.width + horizontalGap;
				} 
				else 
				{
					render.x = 0;
				}
				render.y = verticalGap;
				prevRender = render;
				renderNum++;
			}
		}
	}
}