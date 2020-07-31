package com.poliroid.gui.lobby.battleHits.interfaces 
{
	
	import flash.events.IEventDispatcher;
	
	public interface IPreferencesPopover extends IEventDispatcher
	{
		function invokeChangeS(processReplays:Boolean, saveOnlySession:Boolean) : void;
		function invokeStyleS() : void;
		function invokeDataS() : void;
	}
}