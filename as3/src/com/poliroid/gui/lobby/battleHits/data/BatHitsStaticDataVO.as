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
		
		
		public function BatHitsStaticDataVO(param1:Object)
		{
			super(param1);
		}
		
		override protected function onDataWrite(param1:String, param2:Object) : Boolean
		{
			if(param1 == HEADER_FIELD_NAME)
			{
				header = new BatHitsHeaderVO(param2);
				return false;
			}
			
			if(param1 == BATTLES_FIELD_NAME)
			{
				battles = new BatHitsBattlesVO(param2);
				return false;
			}
			
			if(param1 == HITS_FIELD_NAME)
			{
				hits = new BatHitsHitsVO(param2);
				return false;
			}
			
			if(param1 == DETAILED_HIT_FIELD_NAME)
			{
				detaildeHit = new BatHitsDetailedHitVO(param2);
				return false;
			}
			
			return super.onDataWrite(param1,param2);
		}
		
		override protected function onDispose() : void
		{
			header.dispose();
			header = null;
			
			battles.dispose();
			battles = null;
			
			hits.dispose();
			hits = null;
			
			detaildeHit.dispose();
			detaildeHit = null;
			
			super.onDispose();
		}
	}
}
