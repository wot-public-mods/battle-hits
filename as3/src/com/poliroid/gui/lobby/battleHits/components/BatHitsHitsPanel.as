package com.poliroid.gui.lobby.battleHits.components
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	
	import net.wg.gui.components.advanced.ButtonBarEx;
	import net.wg.gui.components.controls.ScrollingListEx;
	import net.wg.data.constants.Linkages;
	import net.wg.gui.components.controls.DropdownMenu;
	import net.wg.gui.components.controls.ScrollingListEx;
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.gui.components.controls.TileList;
	import net.wg.gui.components.controls.SimpleTileList;
	
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.events.ListEvent;
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.events.InputEvent;
	import scaleform.clik.data.DataProvider;
	import scaleform.clik.utils.Padding;
	import scaleform.clik.constants.DirectionMode;
	
	import net.wg.gui.components.advanced.interfaces.IBackButton;
	import net.wg.gui.interfaces.ISoundButtonEx;
	import net.wg.gui.lobby.vehiclePreview.controls.VehPreviewBackground;
	import net.wg.infrastructure.base.UIComponentEx;
	
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHitsVO;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsHitVO;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsSortItemVO;
	import com.poliroid.gui.lobby.battleHits.events.BatHitsEvent;
	import com.poliroid.gui.lobby.battleHits.events.BatHitsIndexEvent;
	import com.poliroid.gui.lobby.battleHits.interfaces.IBatHitsHitsPanel;
	import com.poliroid.gui.lobby.battleHits.controls.CustomScrollingList;
	import com.poliroid.gui.lobby.battleHits.controls.AutosizeTileList;
	
	public class BatHitsHitsPanel extends UIComponentEx implements IBatHitsHitsPanel
	{
		
		private static const RENDER_HEIGHT:Number = 35;
		
		private static const BG_PADDING:Number = 20;
		
		public var hitsList:CustomScrollingList = null;
		
		public var background:MovieClip = null;
		
		public var sortButtons:SimpleTileList = null;
		
		public var noDataMC:MovieClip = null;
		
		public var noDataTF:TextField = null;
		
		public function BatHitsHitsPanel() 
		{
			super();
		}
		
		override protected function configUI() : void
		{
			hitsList.scrollBar = Linkages.SCROLL_BAR;
			hitsList.smartScrollBar = true;
			hitsList.sbPadding = new Padding(12, 0, 0, -30);
			hitsList.widthAutoResize = false;
			hitsList.addEventListener(ListEvent.ITEM_CLICK, onHitClickHandler);
			hitsList.rowHeight = RENDER_HEIGHT;
			
			sortButtons.itemRenderer = App.utils.classFactory.getClass('BattleHitsSortListItemRendererUI');
			sortButtons.tileHeight = 35;
			sortButtons.tileWidth = 105;
			sortButtons.horizontalGap = 7;
			sortButtons.autoSize = true;
			sortButtons.directionMode = DirectionMode.HORIZONTAL;
		}
		
		override protected function onDispose() : void
		{
			hitsList.removeEventListener(ListEvent.ITEM_CLICK, onHitClickHandler);
			hitsList.dispose();
			hitsList = null;
			
			super.onDispose();
		}
		
		public function update(data:Object) : void
		{
			var dp:BatHitsHitsVO = BatHitsHitsVO(data);
			
			if (hitsList.dataProvider != null)
				hitsList.dataProvider.cleanUp();
			
			noDataTF.text = dp.noDataLabel;	
			
			hitsList.selectedIndex = dp.selectedIndex;
			hitsList.dataProvider = new DataProvider(dp.hitsList);
			
			sortButtons.dataProvider = new DataProvider(dp.sortList);
			
			dp.dispose();
			
			invalidateData();
		}
		
		public function updateDP(dp:BatHitsHitsVO) : void
		{
			if (hitsList.dataProvider != null)
				hitsList.dataProvider.cleanUp();
			
			noDataTF.text = dp.noDataLabel;	
			
			hitsList.dataProvider = new DataProvider(dp.hitsList);
			
			hitsList.selectedIndex = dp.selectedIndex;
			
			sortButtons.dataProvider = new DataProvider(dp.sortList);
			
			invalidateData();
		}
		
		override protected function draw() : void
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
		
		private function updateVisibility() : void
		{
			var isVisible:Boolean = Boolean(hitsList.dataProvider.length == 0);
			
			sortButtons.visible = !isVisible;
			hitsList.visible = !isVisible;
			noDataTF.visible = isVisible;
			noDataMC.visible = isVisible;
		}
		
		private function onHitClickHandler(e:ListEvent) : void 
		{
			dispatchEvent(new BatHitsIndexEvent(BatHitsIndexEvent.HIT_CHANGED, BatHitsHitVO(e.itemData).id, true));
		}
		
		public function get _hitsList() : CustomScrollingList 
		{
			return hitsList;
		}
	}
}