package me.poliroid.battleHits.data 
{
	import net.wg.data.daapi.base.DAAPIDataClass;

	public class BattleHitsPreferencesDataVO extends DAAPIDataClass
	{
		public var titleLabel:String = "preferences";
		public var closeButtonVisible:Boolean = true;
		public var saveOnlySession:Boolean = false;
		public var saveOnlySessionLabel:String = "saveOnlySessionLabel";
		public var saveOnlySessionDescription:String = "saveOnlySessionDescription";
		public var processReplays:Boolean = false;
		public var processReplaysLabel:String = "processReplaysLabel";
		public var processReplaysDescription:String = "processReplaysDescription";
		public var swapHangar:Boolean = false;
		public var swapHangarLabel:String = "swapHangarLabel";
		public var swapHangarDescription:String = "swapHangarDescription";
		public var changeStyleLabel:String = "changeStyleLabel";
		public var deleteHistoryLabel:String = "deleteHistoryLabel";

		public function BattleHitsPreferencesDataVO(data:Object): void
		{
			super(data);
		}
	}
}
