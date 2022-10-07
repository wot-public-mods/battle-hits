package me.poliroid.battleHits.interfaces
{
	import me.poliroid.battleHits.data.BatHitsBattlesVO;
	import net.wg.infrastructure.interfaces.IUIComponentEx;

	public interface IBatHitsBattlesPanel extends IUIComponentEx
	{
		function updateDP(model:BatHitsBattlesVO): void;
	}
}
