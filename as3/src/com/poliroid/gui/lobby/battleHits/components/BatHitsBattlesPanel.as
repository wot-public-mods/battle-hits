package com.poliroid.gui.lobby.battleHits.components
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	
	import net.wg.gui.components.controls.ScrollingListEx;
	import net.wg.data.constants.Linkages;
	import net.wg.gui.components.controls.DropdownMenu;
	import net.wg.gui.components.controls.ScrollingListEx;
	
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.events.ListEvent;
	
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.events.InputEvent;
	import scaleform.clik.data.DataProvider;
	import scaleform.clik.utils.Padding;
	
	import net.wg.gui.components.advanced.interfaces.IBackButton;
	import net.wg.gui.interfaces.ISoundButtonEx;
	import net.wg.infrastructure.base.UIComponentEx;
	
	import com.poliroid.gui.lobby.battleHits.data.BatHitsBattlesVO;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsBattleVO;
	import com.poliroid.gui.lobby.battleHits.events.BatHitsEvent;
	import com.poliroid.gui.lobby.battleHits.events.BatHitsIndexEvent;
	import com.poliroid.gui.lobby.battleHits.interfaces.IBatHitsBattlesPanel;
	import com.poliroid.gui.lobby.battleHits.interfaces.IExtendedScrollingList;
	import com.poliroid.gui.lobby.battleHits.controls.CustomScrollingList;
	
	public class BatHitsBattlesPanel extends UIComponentEx implements IBatHitsBattlesPanel
	{
		
		private static const RENDER_HEIGHT:Number = 35;
		
		private static const BG_PADDING:Number = 20;
		
		public var battlesList:CustomScrollingList = null;
		
		public var background:MovieClip = null;
		
		public var noDataMC:MovieClip = null;
		
		public var noDataTF:TextField = null;
		
		public function BatHitsBattlesPanel() 
		{
			super();
		}
		
		override protected function configUI() : void
		{
			battlesList.scrollBar = Linkages.SCROLL_BAR;
			battlesList.sbPadding = new Padding(8, 0, 0, -30);
			battlesList.widthAutoResize = false;
			battlesList.smartScrollBar = true;
			battlesList.isOpened = false;
			battlesList.addEventListener(ListEvent.ITEM_CLICK, onBattleClickHandler);
		}
		
		override protected function onDispose() : void
		{
			battlesList.removeEventListener(ListEvent.ITEM_CLICK, onBattleClickHandler);
			battlesList.dispose();
			battlesList = null;
			super.onDispose();
		}
		
		public function update(data:Object) : void
		{
			var dp:BatHitsBattlesVO = BatHitsBattlesVO(data);
			
			noDataTF.text = dp.noDataLabel;	
			
			battlesList.dataProvider = new DataProvider(dp.battlesList);
			battlesList.selectedIndex = dp.selectedIndex;
			
			dp.dispose();
			
			invalidateData();
		
		}
		
		public function updateDP(data:BatHitsBattlesVO) : void
		{
			noDataTF.text = data.noDataLabel;	
			
			battlesList.dataProvider = new DataProvider(data.battlesList);
			battlesList.selectedIndex = data.selectedIndex;
			
			invalidateData();
		}
		
		override protected function draw() : void
		{
			super.draw();
			if (isInvalid(InvalidationType.DATA)) 
			{
				if (battlesList.dataProvider.length > 0) 
				{
					battlesList.visible = true;
					battlesList.rowHeight = RENDER_HEIGHT;
					battlesList.invalidateData();
					battlesList.validateNow();
					var targetHeights:Number = Math.min(RENDER_HEIGHT * 10, RENDER_HEIGHT * battlesList.dataProvider.length);
					battlesList.height = battlesList.isOpened ? targetHeights : RENDER_HEIGHT;
					battlesList.validateNow();
					battlesList.scrollBar.x = battlesList.isOpened? 337 : 387;
					background.height = battlesList.y + battlesList.height + BG_PADDING;
					battlesList.scrollToSelected();
					noDataTF.visible = false;
					noDataMC.visible = false;
				} 
				else 
				{
					battlesList.visible = false;
					background.height = BG_PADDING * 3;
					noDataTF.visible = true;
					noDataMC.visible = true;
				}
			}
		}
		
		private function onBattleClickHandler(e:ListEvent) : void 
		{
			battlesList.isOpened = !battlesList.isOpened;
			invalidateData();
			if (!battlesList.isOpened)
			{
				dispatchEvent(new BatHitsIndexEvent(BatHitsIndexEvent.BATTLE_CHANGED, BatHitsBattleVO(e.itemData).id, true));
			}
		}
		
		public function get _battlesList():CustomScrollingList 
		{
			return battlesList;
		}
	}
}