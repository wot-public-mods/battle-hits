package com.poliroid.gui.lobby.battleHits.controls
{
	import flash.display.DisplayObject;
	import net.wg.gui.components.controls.CloseButtonText;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	
	public class PopoverCallerButton extends CloseButtonText implements IPopOverCaller
	{
		public function PopoverCallerButton() 
		{
			super();
			focusable = false;
		}

		// this needs for correct preferences smart popover work
		public function getTargetButton() : DisplayObject 
		{
			return DisplayObject(this);
		}
		
		// this needs for correct preferences smart popover work
		public function getHitArea() : DisplayObject 
		{
			return DisplayObject(this);
		}
	}
}