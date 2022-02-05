package com.poliroid.gui.lobby.battleHits.interfaces 
{
	import flash.events.IEventDispatcher;

	public interface IPreferencesPopover extends IEventDispatcher
	{
		function invokeSettingsChangeS(processReplays:Boolean,
			saveOnlySession:Boolean, swapHangar:Boolean): void;
		function invokeStyleChangeS(): void;
		function invokeHistoryDeleteS(): void;
	}
}
