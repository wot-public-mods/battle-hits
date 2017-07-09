package com.poliroid.gui.lobby.battleHits.interfaces
{
	import com.poliroid.gui.lobby.battleHits.controls.CustomScrollingList;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHitsVO;
	import net.wg.gui.interfaces.IUpdatableComponent;
	
	public interface IBatHitsHitsPanel extends IUpdatableComponent
	{
		
		function get _hitsList() : CustomScrollingList;
		
		function updateDP(ctx:BatHitsHitsVO) : void;
	}
}
