package com.poliroid.gui.lobby.battleHits.data
{
	import net.wg.data.daapi.base.DAAPIDataClass;
	
	public class BatHitsSortItemVO extends DAAPIDataClass
	{
		
		public var id:Number = 0;
		
		public var label:String = "";
		
		public var active:Boolean = false;
		
		public var reversed:Boolean = false;
		
		public function BatHitsSortItemVO(data:Object)
		{
			super(data);
		}
	}

}