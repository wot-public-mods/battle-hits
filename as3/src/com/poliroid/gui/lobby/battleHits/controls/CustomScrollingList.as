package com.poliroid.gui.lobby.battleHits.controls
{
	
	import net.wg.gui.components.controls.ScrollingListEx;
	import scaleform.clik.events.InputEvent;
	import flash.events.MouseEvent;
	
	import com.poliroid.gui.lobby.battleHits.interfaces.IExtendedScrollingList;
	
	public class CustomScrollingList extends ScrollingListEx implements IExtendedScrollingList
	{
		
		public var isOpened:Boolean = true;
		
		public function CustomScrollingList() 
		{
			super();
		}
		
		override public function handleInput(e:InputEvent) : void
		{
			e.handled = false;
		}
		override protected function handleMouseWheel(e:MouseEvent) : void
		{
			if (isOpened) 
			{
				super.handleMouseWheel(e);
			}
		}
		public function get nextItemID(): Number
		{
			if (selectedIndex == -1)
				return -1;
			
			var dest:int = selectedIndex + 1;
			if (dataProvider.length > dest && dest > -1) 
			{
				return dataProvider[dest].id;
			} 
			else 
			{
				return dataProvider[selectedIndex].id;
			}
			return 0;
		}
		
		public function get prevItemID(): Number
		{
			if (selectedIndex == -1)
				return -1;
			
			var dest:int = selectedIndex - 1;
			if (dataProvider.length > dest && dest > -1) 
			{
				return dataProvider[dest].id;
			} 
			else 
			{
				return dataProvider[selectedIndex].id;
			}
			return 0;
		}
	}
}