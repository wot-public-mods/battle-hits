package com.poliroid.gui.lobby.battleHits.interfaces
{
	import net.wg.gui.interfaces.IUpdatableComponent;
	import net.wg.infrastructure.interfaces.IPopOverCaller;

	public interface IBatHitsHeader extends IUpdatableComponent
	{
		function get preferenceButton() : IPopOverCaller
		
		function invalidateSize() : void
		
	}
}
