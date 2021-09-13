package com.poliroid.gui.lobby.battleHits.data
{
	import net.wg.data.daapi.base.DAAPIDataClass;

	public class BatHitsHeaderVO extends DAAPIDataClass
	{
		public var closeBtnLabel:String = "";
		public var settingsLabel:String = "";
		public var titleLabel:String = "";
		public var typeBtnMe:String = "";
		public var typeBtnEnemys:String = "";
		public var typeBtnMeActive:Boolean = false;
		public var typeBtnEnemysActive:Boolean = false;

		public function BatHitsHeaderVO(data:Object): void
		{
			super(data);
		}
	}
}
