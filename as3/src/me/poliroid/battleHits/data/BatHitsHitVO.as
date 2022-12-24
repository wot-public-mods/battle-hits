package me.poliroid.battleHits.data
{
	import net.wg.data.daapi.base.DAAPIDataClass;

	public class BatHitsHitVO extends DAAPIDataClass
	{
		public var id:Number = 0;
		public var numberLabel:String = "";
		public var vehicleLabel:String = "";
		public var resultLabel:String = "";
		public var shellLabel:String = "";
		public var damageLabel:String = "";
		public var anonymized:Boolean = false;
		public var isImproved:Boolean = false;
		public var isSPG:Boolean = false;

		public function BatHitsHitVO(data:Object): void
		{
			super(data);
		}
	}
}
