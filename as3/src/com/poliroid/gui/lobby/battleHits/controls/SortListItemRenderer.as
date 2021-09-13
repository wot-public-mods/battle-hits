package com.poliroid.gui.lobby.battleHits.controls 
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.constants.InvalidationType;
	import com.poliroid.gui.lobby.battleHits.events.BatHitsIndexEvent;
	import com.poliroid.gui.lobby.battleHits.data.BatHitsSortItemVO;
	import net.wg.gui.components.controls.SoundListItemRenderer;

	public class SortListItemRenderer extends SoundListItemRenderer
	{
		public var labelTF:TextField = null;
		public var activeMC:MovieClip = null;
		public var orderAscMC:MovieClip = null;
		public var orderDescMC:MovieClip = null;
		public var hitAreaA:MovieClip = null;

		private var model:BatHitsSortItemVO = null;

		public function SortListItemRenderer() 
		{
			super();
			hitArea = hitAreaA;
			addEventListener(ButtonEvent.CLICK, onClickHandler);
		}

		override public function setData(data:Object): void 
		{
			if (data == null) 
				return;
			super.setData(data);
			model = BatHitsSortItemVO(data);
			invalidateData();
		}

		override protected function onDispose(): void
		{
			labelTF = null;
			activeMC = null;
			orderAscMC = null;
			orderDescMC = null;
			hitAreaA = null;

			super.onDispose();
		}

		override protected function draw(): void 
		{
			super.draw();
			if ((model != null) && (isInvalid(InvalidationType.DATA)))
			{
				labelTF.text = model.label;
				activeMC.visible = model.active;
				orderAscMC.visible = model.active && model.reversed;
				orderDescMC.visible = model.active && !model.reversed;
			}
		}

		private function onClickHandler(e:ButtonEvent): void 
		{
			dispatchEvent(new BatHitsIndexEvent(BatHitsIndexEvent.SORT_CLICKED, model.id, true));
		}
	}
}
