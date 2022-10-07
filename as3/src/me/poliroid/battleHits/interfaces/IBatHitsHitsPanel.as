package me.poliroid.battleHits.interfaces
{
	import me.poliroid.battleHits.data.BatHitsHitsVO;
	import net.wg.infrastructure.interfaces.IUIComponentEx;

	public interface IBatHitsHitsPanel extends IUIComponentEx
	{
		function updateDP(model:BatHitsHitsVO): void;
	}
}
