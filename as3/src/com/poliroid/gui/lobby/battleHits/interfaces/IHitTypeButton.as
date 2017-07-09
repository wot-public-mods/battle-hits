package com.poliroid.gui.lobby.battleHits.interfaces 
{
	import net.wg.gui.interfaces.ISoundButtonEx;
	
	public interface IHitTypeButton extends ISoundButtonEx
	{
		function set isActive(isActive:Boolean) : void;
		
		function get isActive() : Boolean;
	}
	
}