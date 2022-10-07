package me.poliroid.battleHits.controls
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.constants.InvalidationType;
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.gui.interfaces.ISoundButtonEx;
	import me.poliroid.battleHits.events.BatHitsIndexEvent;
	import me.poliroid.battleHits.data.BatHitsSortItemVO;

	public class SortButton extends SoundButtonEx implements ISoundButtonEx 
	{
		public var labelTF:TextField = null;
		public var orderMC:MovieClip = null;

		private var model:BatHitsSortItemVO = null;

		public function SortButton() 
		{
			super();
			focusable = false;
			addEventListener(ButtonEvent.CLICK, onClickHandler);
		}

		public function setData(data:Object): void 
		{
			if (data == null) 
				return;
			model = BatHitsSortItemVO(data);
			invalidateData();
		}

		override protected function onDispose(): void
		{
			if (model != null)
				model.dispose();
			model = null;

			labelTF = null;
			orderMC = null;

			super.onDispose();
		}

		override protected function draw(): void 
		{
			super.draw();
			if ((model != null) && (isInvalid(InvalidationType.DATA)))
			{
				labelTF.text = model.label;
				orderMC.visible = model.active;
				orderMC.gotoAndStop(model.reversed ? 'desc':'asc');
			}
		}

		private function onClickHandler(e:ButtonEvent): void 
		{
			dispatchEvent(new BatHitsIndexEvent(BatHitsIndexEvent.SORT_CLICKED, model.id, true));
		}
	}
}
