package com.poliroid.gui.lobby.battleHits.interfaces
{
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHitsVO;
	import net.wg.infrastructure.interfaces.IUIComponentEx;

	public interface IBatHitsHitsPanel extends IUIComponentEx
	{
		function updateDP(model:BatHitsHitsVO): void;
	}
}
