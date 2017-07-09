package com.poliroid.gui.lobby.battleHits.interfaces
{
	
	import com.poliroid.gui.lobby.battleHits.controls.CustomScrollingList;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsBattlesVO;
	import net.wg.gui.interfaces.IUpdatableComponent;
	
	public interface IBatHitsBattlesPanel extends IUpdatableComponent
	{
		function get _battlesList() : CustomScrollingList;
		
		function updateDP(data:BatHitsBattlesVO) : void;
	}
}
