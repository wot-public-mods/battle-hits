package me.poliroid.battleHits.data
{
	import net.wg.data.constants.Errors;
	import net.wg.infrastructure.interfaces.entity.IDisposable;
	import net.wg.data.daapi.base.DAAPIDataClass;
	import me.poliroid.battleHits.data.BatHitsBattleVO;

	public class BatHitsBattlesVO extends DAAPIDataClass
	{
		private static const BATTLES_FIELD_NAME:String = "battles";

		public var battlesList:Array = null;
		public var selectedIndex:Number = 0;
		public var noDataLabel:String = "";

		public function BatHitsBattlesVO(data:Object): void
		{
			super(data);
		}

		override protected function onDataWrite(dataName:String, dataValue:Object): Boolean
		{
			if(dataName == BATTLES_FIELD_NAME)
			{
				var battles:Array = dataValue as Array;
				battlesList = [];
				for each(var battle:Object in battles)
				{
					battlesList.push(new BatHitsBattleVO(battle));
				}
				return false;
			}

			return super.onDataWrite(dataName, dataValue);
		}

		override protected function onDispose(): void
		{
			var disposable:IDisposable = null;

			if(battlesList != null)
			{
				for each(disposable in battlesList)
				{
					disposable.dispose();
				}
				battlesList.splice(0, battlesList.length);
				battlesList = null;
			}

			super.onDispose();
		}
	}
}
