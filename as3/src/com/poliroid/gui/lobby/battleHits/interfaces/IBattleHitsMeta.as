package com.poliroid.gui.lobby.battleHits.interfaces
{
	import flash.events.IEventDispatcher;
	
	public interface IBattleHitsMeta extends IEventDispatcher
	{
		
		function closeViewS() : void;

		function preferencesClickS() : void;
		
		function hitsToPlayerClickS(toPlayer:Boolean) : void;
		
		function onBattleSelectS(id:Number) : void;
		
		function onHitSelectS(id:Number) : void;
		
		function onSortClickS(id:Number) : void;
		
		function as_setStaticData(data:Object) : void;
		
		function as_updateBattlesDPData(data:Object) : void;
		
		function as_updateHitsDPData(data:Object) : void;
		
	}
}
