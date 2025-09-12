package me.poliroid.battleHits.interfaces 
{
	import flash.events.IEventDispatcher;

	public interface IPreferencesPopover extends IEventDispatcher
	{
		function invokeSettingsChangeS(processReplays:Boolean, saveOnlySession:Boolean): void;
		function invokeStyleChangeS(): void;
		function invokeHistoryDeleteS(): void;
	}
}
