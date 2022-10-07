package me.poliroid.battleHits.components
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	import net.wg.data.constants.Linkages;
	import net.wg.gui.components.controls.SoundButton;
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.events.ListEvent;
	import scaleform.clik.data.DataProvider;
	import scaleform.clik.utils.Padding;
	import net.wg.infrastructure.base.UIComponentEx;
	import me.poliroid.battleHits.data.BatHitsHitsVO;
	import me.poliroid.battleHits.data.BatHitsHitVO;
	import me.poliroid.battleHits.events.BatHitsIndexEvent;
	import me.poliroid.battleHits.interfaces.IBatHitsHitsPanel;
	import me.poliroid.battleHits.controls.CustomScrollingList;
	import me.poliroid.battleHits.controls.SortButton;

	public class BatHitsHitsPanel extends UIComponentEx implements IBatHitsHitsPanel
	{
		private static const RENDER_HEIGHT:Number = 35;
		private static const BG_PADDING:Number = 20;
		public var hitsList:CustomScrollingList = null;
		public var background:MovieClip = null;
		public var sortNumber:SortButton = null;
		public var sortVehicle:SortButton = null;
		public var sortResult:SortButton = null;
		public var sortDamage:SortButton = null;
		public var noDataMC:MovieClip = null;
		public var noDataTF:TextField = null;

		override protected function configUI(): void
		{
			super.configUI();
			hitsList.scrollBar = Linkages.SCROLL_BAR;
			hitsList.smartScrollBar = true;
			hitsList.sbPadding = new Padding(12, 0, 0, -30);
			hitsList.widthAutoResize = false;
			hitsList.addEventListener(ListEvent.ITEM_CLICK, onHitClickHandler);
			hitsList.rowHeight = RENDER_HEIGHT;
		}

		override protected function onDispose(): void
		{
			hitsList.removeEventListener(ListEvent.ITEM_CLICK, onHitClickHandler);
			hitsList.dispose();
			sortNumber.dispose();
			sortVehicle.dispose();
			sortResult.dispose();
			sortDamage.dispose();

			hitsList = null;
			sortNumber = null;
			sortVehicle = null;
			sortResult = null;
			sortDamage = null;
			background = null;
			noDataMC = null;
			noDataTF = null;

			super.onDispose();
		}

		public function updateDP(model:BatHitsHitsVO): void
		{
			if (hitsList.dataProvider != null)
				hitsList.dataProvider.cleanUp();
			noDataTF.text = model.noDataLabel;
			hitsList.selectedIndex = model.selectedIndex;
			hitsList.dataProvider = new DataProvider(model.hitsList);
			updateSorting(model.sortList);
			invalidateData();
		}

		override protected function draw(): void
		{
			super.draw();
			if (isInvalid(InvalidationType.DATA)) 
			{
				if (hitsList.dataProvider.length > 0) 
				{
					updateVisibility();
					hitsList.invalidateData();
					hitsList.validateNow();
					hitsList.height = Math.min(RENDER_HEIGHT * 10, RENDER_HEIGHT * hitsList.dataProvider.length);
					hitsList.scrollToSelected();
					background.height = hitsList.y + hitsList.height + BG_PADDING;
				} 
				else 
				{
					updateVisibility();
					background.height = BG_PADDING * 3;
				}
			}
		}

		private function updateVisibility(): void
		{
			var isVisible:Boolean = Boolean(hitsList.dataProvider.length == 0);
			sortNumber.visible = !isVisible;
			sortVehicle.visible = !isVisible;
			sortResult.visible = !isVisible;
			sortDamage.visible = !isVisible;
			hitsList.visible = !isVisible;
			noDataTF.visible = isVisible;
			noDataMC.visible = isVisible;
		}

		private function onHitClickHandler(e:ListEvent): void 
		{
			dispatchEvent(new BatHitsIndexEvent(BatHitsIndexEvent.HIT_CHANGED, BatHitsHitVO(e.itemData).id, true));
		}

		private function updateSorting(sortListDP:Array): void
		{
			sortNumber.setData(sortListDP[0]);
			sortVehicle.setData(sortListDP[1]);
			sortResult.setData(sortListDP[2]);
			sortDamage.setData(sortListDP[3]);
		}
	}
}
