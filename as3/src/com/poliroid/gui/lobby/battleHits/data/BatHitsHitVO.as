package com.poliroid.gui.lobby.battleHits.data
{
	import net.wg.data.daapi.base.DAAPIDataClass;
	
	public class BatHitsHitVO extends DAAPIDataClass
	{	
		
		public var id:Number = 0;
		
		public var enemyTankLabel:String = "";
		
		public var resultLabel:String = "";
		
		public var shellLabel:String = "";
		
		public var damageLabel:String = "";
		
		public function BatHitsHitVO(data:Object)
		{
			super(data);
		}
	}
}
