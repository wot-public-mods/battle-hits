package com.poliroid.gui.lobby.battleHits.events
{
	import flash.events.Event;
	
	public class BatHitsEvent extends Event
	{
		
		public static const CLOSE_CLICK:String = "closeClick";
		
		public static const PREFERENCES_CLICK:String = "preferencesClick";
		
		public static const TO_PLAYER_CLICK:String = "toPlayerClick";
		
		public static const FROM_PLAYER_CLICK:String = "fromPlayerClick";
		
		public function BatHitsEvent(type:String, bubbles:Boolean = false, cancelable:Boolean = false)
		{
			super(type, bubbles, cancelable);
		}
		
		override public function clone() : Event
		{
			return new BatHitsEvent(type, bubbles, cancelable);
		}
		
	}
}
