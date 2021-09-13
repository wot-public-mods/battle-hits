package com.poliroid.gui.lobby.battleHits.controls
{
	import net.wg.gui.components.controls.SoundButtonEx;
	import net.wg.gui.interfaces.ISoundButtonEx;

	public class HitTypeButton extends SoundButtonEx implements ISoundButtonEx 
	{

		private var _isActive:Boolean = false;

		public function HitTypeButton() 
		{
			super();
			focusable = false;
		}

		override protected function getStatePrefixes(): Vector.<String>
		{
			if (isActive)
				return Vector.<String>(['active_', '']);
			else
				return Vector.<String>(['pasive_', '']);
		}

		public function set isActive(isActive:Boolean): void
		{
			if(_isActive == isActive)
				return;
			_isActive = isActive;
			setState(state == "over"? "up":state);
		}

		public function get isActive(): Boolean
		{
			return _isActive;
		}
	}
}
