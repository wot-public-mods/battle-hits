package me.poliroid.battleHits.interfaces.impl
{
	import me.poliroid.battleHits.data.BatHitsBattlesVO;
	import me.poliroid.battleHits.data.BatHitsHitsVO;
	import net.wg.data.constants.Errors;
	import net.wg.infrastructure.base.AbstractView;
	import net.wg.infrastructure.exceptions.AbstractException;
	import me.poliroid.battleHits.data.BatHitsStaticDataVO;

	public class BattleHitsMeta extends AbstractView
	{
		public var closeView:Function;
		public var selectBattle:Function;
		public var selectHit:Function;
		public var sortClick:Function;
		public var preferencesClick:Function;
		public var hitsToPlayerClick:Function;

		public function closeViewS(): void
		{
			App.utils.asserter.assertNotNull(closeView, "closeView" + Errors.CANT_NULL);
			closeView();
		}

		public function preferencesClickS(): void
		{
			App.utils.asserter.assertNotNull(preferencesClick, "preferencesClick" + Errors.CANT_NULL);
			preferencesClick();
		}

		public function hitsToPlayerClickS(param1: Boolean): void
		{
			App.utils.asserter.assertNotNull(hitsToPlayerClick, "hitsToPlayerClick" + Errors.CANT_NULL);
			hitsToPlayerClick(param1);
		}

		public function onBattleSelectS(param1: Number): void
		{
			App.utils.asserter.assertNotNull(selectBattle, "selectBattle" + Errors.CANT_NULL);
			selectBattle(param1);
		}

		public function onHitSelectS(param1: Number): void
		{
			App.utils.asserter.assertNotNull(selectHit, "selectHit" + Errors.CANT_NULL);
			selectHit(param1);
		}

		public function onSortClickS(param1: Number): void
		{
			App.utils.asserter.assertNotNull(sortClick, "sortClick" + Errors.CANT_NULL);
			sortClick(param1);
		}

		public final function as_setStaticData(param1:Object): void
		{
			var data:BatHitsStaticDataVO = new BatHitsStaticDataVO(param1);
			setStaticData(data);
			if(data)
				data.dispose();
		}

		protected function setStaticData(data:BatHitsStaticDataVO): void
		{
			var message:String = "as_setStaticData" + Errors.ABSTRACT_INVOKE;
			DebugUtils.LOG_ERROR(message);
			throw new AbstractException(message);
		}

		public final function as_updateBattlesDPData(param1:Object): void
		{
			var data:BatHitsBattlesVO = new BatHitsBattlesVO(param1);
			updateBattlesDPData(data);
			if(data)
				data.dispose();
		}

		protected function updateBattlesDPData(data:BatHitsBattlesVO): void
		{
			var message:String = "as_updateBattlesDPData" + Errors.ABSTRACT_INVOKE;
			DebugUtils.LOG_ERROR(message);
			throw new AbstractException(message);
		}

		public final function as_updateHitsDPData(param1:Object): void
		{
			var data:BatHitsHitsVO = new BatHitsHitsVO(param1);
			updateHitsDPData(data);
			if(data)
				data.dispose();
		}

		protected function updateHitsDPData(data:BatHitsHitsVO): void
		{
			var message:String = "as_updateHitsDPData" + Errors.ABSTRACT_INVOKE;
			DebugUtils.LOG_ERROR(message);
			throw new AbstractException(message);
		}
	}
}
