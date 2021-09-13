package com.poliroid.gui.lobby.battleHits.interfaces
{
	import com.poliroid.gui.lobby.battleHits.data.BatHitsBattlesVO;
	import net.wg.infrastructure.interfaces.IUIComponentEx;

	public interface IBatHitsBattlesPanel extends IUIComponentEx
	{
		function updateDP(model:BatHitsBattlesVO): void;
	}
}
