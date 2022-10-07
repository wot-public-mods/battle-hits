package me.poliroid.battleHits.data
{
	import net.wg.data.constants.Errors;
	import net.wg.infrastructure.interfaces.entity.IDisposable;
	import net.wg.data.daapi.base.DAAPIDataClass;
	import me.poliroid.battleHits.data.BatHitsHitVO;
	import me.poliroid.battleHits.data.BatHitsSortItemVO;
	
	public class BatHitsHitsVO extends DAAPIDataClass
	{
		private static const HITS_FIELD_NAME:String = "hits";
		private static const SORTING_FIELD_NAME:String = "sorting";

		public var hitsList:Array = null;
		public var sortList:Array = null;
		public var selectedIndex:Number = 0;
		public var noDataLabel:String = "";

		public function BatHitsHitsVO(data:Object): void
		{
			super(data);
		}

		override protected function onDataWrite(dataName:String, dataValue:Object): Boolean
		{
			if(dataName == HITS_FIELD_NAME)
			{
				var hitItems:Array = dataValue as Array;
				hitsList = [];
				for each(var hitItem:Object in hitItems)
				{
					hitsList.push(new BatHitsHitVO(hitItem));
				}
				return false;
			}

			if(dataName == SORTING_FIELD_NAME)
			{
				var sortItems:Array = dataValue as Array;
				sortList = [];
				for each(var sortItem:Object in sortItems)
				{
					sortList.push(new BatHitsSortItemVO(sortItem));
				}
				return false;
			}

			return super.onDataWrite(dataName, dataValue);
		}

		override protected function onDispose(): void
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
