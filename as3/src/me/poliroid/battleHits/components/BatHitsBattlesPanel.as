package me.poliroid.battleHits.components
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	import net.wg.data.constants.Linkages;
	import scaleform.clik.events.ListEvent;
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.data.DataProvider;
	import scaleform.clik.utils.Padding;
	import net.wg.infrastructure.base.UIComponentEx;
	import me.poliroid.battleHits.data.BatHitsBattlesVO;
	import me.poliroid.battleHits.data.BatHitsBattleVO;
	import me.poliroid.battleHits.events.BatHitsIndexEvent;
	import me.poliroid.battleHits.interfaces.IBatHitsBattlesPanel;
	import me.poliroid.battleHits.controls.CustomScrollingList;

	public class BatHitsBattlesPanel extends UIComponentEx implements IBatHitsBattlesPanel
	{
		private static const RENDER_HEIGHT:Number = 35;
		private static const BG_PADDING:Number = 20;

		public var battlesList:CustomScrollingList = null;
		public var background:MovieClip = null;
		public var noDataMC:MovieClip = null;
		public var noDataTF:TextField = null;

		override protected function configUI(): void
		{
			super.configUI();
			battlesList.scrollBar = Linkages.SCROLL_BAR;
			battlesList.sbPadding = new Padding(8, 0, 0, -30);
			battlesList.widthAutoResize = false;
			battlesList.smartScrollBar = true;
			battlesList.isOpened = false;
			battlesList.addEventListener(ListEvent.ITEM_CLICK, onBattleClickHandler);
		}

		override protected function onDispose(): void
		{
			battlesList.removeEventListener(ListEvent.ITEM_CLICK, onBattleClickHandler);
			battlesList.dispose();

			battlesList = null;
			background = null;
			noDataMC = null;
			noDataTF = null;

			super.onDispose();
		}

		public function updateDP(model:BatHitsBattlesVO): void
		{
			noDataTF.text = model.noDataLabel;
			battlesList.dataProvider = new DataProvider(model.battlesList);
			battlesList.selectedIndex = model.selectedIndex;
			invalidateData();
		}

		override protected function draw(): void
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

		private function onBattleClickHandler(e:ListEvent): void 
		{
			battlesList.isOpened = !battlesList.isOpened;
			invalidateData();
			if (!battlesList.isOpened)
			{
				dispatchEvent(new BatHitsIndexEvent(BatHitsIndexEvent.BATTLE_CHANGED, BatHitsBattleVO(e.itemData).id, true));
			}
		}
	}
}
