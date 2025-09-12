package me.poliroid.battleHits.data
{
	import net.wg.data.daapi.base.DAAPIDataClass;
	import me.poliroid.battleHits.data.BatHitsBattlesVO;
	import me.poliroid.battleHits.data.BatHitsHitsVO;

	public class BatHitsStaticDataVO extends DAAPIDataClass
	{
		private static const BATTLES_FIELD_NAME:String = "battles";
		private static const HITS_FIELD_NAME:String = "hits";

		public var battles:BatHitsBattlesVO = null;
		public var hits:BatHitsHitsVO = null;

		public function BatHitsStaticDataVO(data:Object): void
		{
			super(data);
		}

		override protected function onDataWrite(dataName:String, dataValue:Object): Boolean
		{
			if(dataName == BATTLES_FIELD_NAME)
			{
				battles = new BatHitsBattlesVO(dataValue);
				return false;
			}
			if(dataName == HITS_FIELD_NAME)
			{
				hits = new BatHitsHitsVO(dataValue);
				return false;
			}
			return super.onDataWrite(dataName, dataValue);
		}

		override protected function onDispose(): void
		{
			battles.dispose();
			hits.dispose();

			battles = null;
			hits = null;

			super.onDispose();
		}
	}
}
