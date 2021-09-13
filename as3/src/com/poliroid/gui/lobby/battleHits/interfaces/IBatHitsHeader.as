package com.poliroid.gui.lobby.battleHits.interfaces
{
	import net.wg.infrastructure.interfaces.IUIComponentEx;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHeaderVO;

	public interface IBatHitsHeader extends IUIComponentEx
	{
		function get preferenceButton(): IPopOverCaller;
		function invalidateSize(): void;
		function updateDP(model:BatHitsHeaderVO): void;
	}
}
