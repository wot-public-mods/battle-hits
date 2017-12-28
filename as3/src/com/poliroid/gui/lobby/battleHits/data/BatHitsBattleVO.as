package com.poliroid.gui.lobby.battleHits.data
{
	import net.wg.data.daapi.base.DAAPIDataClass;
	
	public class BatHitsBattleVO extends DAAPIDataClass
	{	
		
		public var id:Number = 0;
		
		public var mapNameLabel:String = "";
		
		public var vehicleNameLabel:String = "";
		
		public var battleStartLabel:String = "";
		
		public function BatHitsBattleVO(param1:Object)
		{
			super(param1);
		}
	}
}
