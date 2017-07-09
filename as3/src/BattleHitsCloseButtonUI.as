package 
{
	
	import flash.display.DisplayObject;
	import net.wg.gui.components.controls.CloseButtonText
    import net.wg.infrastructure.interfaces.IPopOverCaller;
	
	public  class BattleHitsCloseButtonUI extends CloseButtonText implements IPopOverCaller
	{
		
		public function BattleHitsCloseButtonUI() 
		{
			super();
			this.focusable = false;
		}
		
		// this needs for correct smart popover work
		public function getTargetButton() : DisplayObject 
		{
			return DisplayObject(this);
		}
		
		// this needs for correct smart popover work
		public function getHitArea() : DisplayObject 
		{
			return DisplayObject(this);
		}
		
	}
}
