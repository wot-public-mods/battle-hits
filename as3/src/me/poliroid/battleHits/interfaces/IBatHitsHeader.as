package me.poliroid.battleHits.interfaces
{
	import net.wg.infrastructure.interfaces.IUIComponentEx;
	import net.wg.infrastructure.interfaces.IPopOverCaller;
	import me.poliroid.battleHits.data.BatHitsHeaderVO;

	public interface IBatHitsHeader extends IUIComponentEx
	{
		function get preferenceButton(): IPopOverCaller;
		function invalidateSize(): void;
		function updateDP(model:BatHitsHeaderVO): void;
	}
}
