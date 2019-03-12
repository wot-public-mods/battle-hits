package com.poliroid.gui.lobby.battleHits.data
{
	import net.wg.data.constants.Errors;
	import net.wg.infrastructure.interfaces.entity.IDisposable;
	import net.wg.data.daapi.base.DAAPIDataClass;
	
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHitVO;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsSortItemVO;
	
	public class BatHitsHitsVO extends DAAPIDataClass
	{
		
		private static const HITS_FIELD_NAME:String = "hits";
		
		private static const SORTING_FIELD_NAME:String = "sorting";
		
		public var hitsList:Array = null;
		
		public var sortList:Array = null;
		
		public var selectedIndex:Number = 0;
		
		public var noDataLabel:String = "";
		
		public function BatHitsHitsVO(param1:Object)
		{
			super(param1);
		}
		
		override protected function onDataWrite(param1:String, param2:Object) : Boolean
		{
			
			if(param1 == HITS_FIELD_NAME)
			{
				var hitItems:Array = param2 as Array;
				
				hitsList = [];
				
				for each(var hitItem:Object in hitItems)
				{
					hitsList.push(new BatHitsHitVO(hitItem));
				}
				return false;
			}
			
			if(param1 == SORTING_FIELD_NAME)
			{
				var sortItems:Array = param2 as Array;
				
				sortList = [];
				
				for each(var sortItem:Object in sortItems)
				{
					sortList.push(new BatHitsSortItemVO(sortItem));
				}
				return false;
			}
			
			return super.onDataWrite(param1, param2);
		}
		
		override protected function onDispose() : void
		{
			var disposable:IDisposable = null;
			
			if(hitsList != null)
			{
				for each(disposable in hitsList)
				{
					disposable.dispose();
				}
				hitsList.splice(0, hitsList.length);
				hitsList = null;
			}
			
			if(sortList != null)
			{
				for each(disposable in sortList)
				{
					disposable.dispose();
				}
				sortList.splice(0, sortList.length);
				sortList = null;
			}
			
			super.onDispose();
		}
	}
}
