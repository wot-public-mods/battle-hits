package com.poliroid.gui.lobby.battleHits.controls
{
	import flash.events.MouseEvent;
	import scaleform.clik.events.InputEvent;
	import net.wg.gui.components.controls.ScrollingListEx;

	public class CustomScrollingList extends ScrollingListEx
	{
		public var isOpened:Boolean = true;

		override public function handleInput(e:InputEvent): void
		{
			e.handled = false;
		}

		override protected function handleMouseWheel(e:MouseEvent): void
		{
			if (isOpened) 
			{
				super.handleMouseWheel(e);
			}
		}
	}
}
