package com.poliroid.gui.lobby.battleHits.data
{
	import net.wg.data.daapi.base.DAAPIDataClass;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsBattlesVO;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsDetailedHitVO;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHeaderVO;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHitsVO;

	public class BatHitsStaticDataVO extends DAAPIDataClass
	{
		private static const HEADER_FIELD_NAME:String = "header";
		private static const BATTLES_FIELD_NAME:String = "battles";
		private static const HITS_FIELD_NAME:String = "hits";
		private static const DETAILED_HIT_FIELD_NAME:String = "detailedHit";

		public var header:BatHitsHeaderVO = null;
		public var battles:BatHitsBattlesVO = null;
		public var hits:BatHitsHitsVO = null;
		public var detaildeHit:BatHitsDetailedHitVO = null;

		public function BatHitsStaticDataVO(data:Object): void
		{
			super(data);
		}

		override protected function onDataWrite(dataName:String, dataValue:Object): Boolean
		{
			if(dataName == HEADER_FIELD_NAME)
			{
				header = new BatHitsHeaderVO(dataValue);
				return false;
			}
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
			if(dataName == DETAILED_HIT_FIELD_NAME)
			{
				detaildeHit = new BatHitsDetailedHitVO(dataValue);
				return false;
			}
			return super.onDataWrite(dataName, dataValue);
		}

		override protected function onDispose(): void
		{
			header.dispose();
			battles.dispose();
			hits.dispose();
			detaildeHit.dispose();

			header = null;
			battles = null;
			hits = null;
			detaildeHit = null;

			super.onDispose();
		}
	}
}
