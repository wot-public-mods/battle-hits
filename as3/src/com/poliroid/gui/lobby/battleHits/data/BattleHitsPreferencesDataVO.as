package com.poliroid.gui.lobby.battleHits.data 
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
		
		public var changeStyleLabel:String = "changeStyleLabel";
		
		
		public function BattleHitsPreferencesDataVO(data:Object)
		{
			super(data);
		}
		
	}

}