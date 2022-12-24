package me.poliroid.battleHits.controls
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	import me.poliroid.battleHits.data.BatHitsHitVO;

	public class ShellRenderer extends MovieClip 
	{

		public var labelTF:TextField = null;
		public var background:MovieClip = null;

		private static const LABEL_COLOR_SPG:uint = 0xF9F9F9;
		private static const LABEL_COLOR_NORMAL:uint = 0x212121;
		
		private static const BACKGROUND_HEIGHT:int = 18;
		private static const BACKGROUND_PADDING:int = 14;

		public function setData(model:BatHitsHitVO): void 
		{
			labelTF.text = model.shellLabel;
			labelTF.textColor = model.isSPG ? LABEL_COLOR_SPG : LABEL_COLOR_NORMAL;

			var shellbg = 'white';
			if (model.isImproved)
				shellbg = 'gold'
			if (model.isSPG)
				shellbg += 'Black'
			background.gotoAndStop(shellbg);

			background.height = BACKGROUND_HEIGHT;
			background.width = int(labelTF.textWidth + 14);
		}
	}
}
