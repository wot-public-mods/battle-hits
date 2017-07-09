package com.poliroid.gui.lobby.battleHits.events
{
	import flash.events.Event;
	
	public class BatHitsIndexEvent extends Event
	{
		
		public static const BATTLE_CHANGED:String = "battleChanged";
		
		public static const HIT_CHANGED:String = "hitChanged";
		
		public static const SORT_CLICKED:String = "sortClicked";
		
		private var _selectedIndex:Number;
		
		public function BatHitsIndexEvent(type:String, index:int = -1, bubbles:Boolean = false, cancelable:Boolean = false)
		{
			super(type, bubbles, cancelable);
			this._selectedIndex = index;
		}
		
		override public function clone() : Event
		{
			return new BatHitsIndexEvent(type, this._selectedIndex, bubbles, cancelable);
		}
		
		public function get selectedIndex() : Number
		{
			return this._selectedIndex;
		}
	}
}
