package com.poliroid.gui.lobby.battleHits.data
{
	import net.wg.data.constants.Errors;
	import net.wg.infrastructure.interfaces.entity.IDisposable;
	import net.wg.data.daapi.base.DAAPIDataClass;
	
	import com.poliroid.gui.lobby.battleHits.data.BatHitsBattleVO;
	
	public class BatHitsBattlesVO extends DAAPIDataClass
	{
		
		private static const BATTLES_FIELD_NAME:String = "battles";
		
		public var battlesList:Array = null;
		
		public var selectedIndex:Number = 0;
		
		public var noDataLabel:String = "";
		
		public function BatHitsBattlesVO(param1:Object)
		{
			super(param1);
		}
		
		override protected function onDataWrite(param1:String, param2:Object) : Boolean
		{
			
			if(param1 == BATTLES_FIELD_NAME)
			{
				var battles:Array = param2 as Array;
				
				battlesList = [];
				
				for each(var battle:Object in battles)
				{
					battlesList.push(new BatHitsBattleVO(battle));
				}
				return false;
			}
			
			return super.onDataWrite(param1, param2);
		}
		
		override protected function onDispose() : void
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
