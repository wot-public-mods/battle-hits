
package com.poliroid.gui.lobby.battleHits.interfaces.impl 
{
	
	import net.wg.data.constants.Errors;
	import net.wg.infrastructure.base.SmartPopOverView;
	import net.wg.infrastructure.exceptions.AbstractException;
	
	import com.poliroid.gui.lobby.battleHits.data.BattleHitsPreferencesDataVO;
	import net.wg.data.constants.Linkages;
	
	public class PreferencesPopoverMeta extends SmartPopOverView
	{
		
		public var invokeChange:Function;
		public var invokeStyle:Function;
		
		public function PreferencesPopoverMeta() 
		{	
			super();
		}
		
		// bcs SWC in very good condition
		public function get wrapperLinkage() : String 
		{
			return Linkages.SMART_POPOVER;
		}
		
		public function invokeChangeS(processReplays:Boolean, saveOnlySession:Boolean, showCollisionModel:Boolean) : void
		{
			App.utils.asserter.assertNotNull(invokeChange, "invokeChange" + Errors.CANT_NULL);
			invokeChange(processReplays, saveOnlySession, showCollisionModel);
		}
		
		public function invokeStyleS() : void
		{
			App.utils.asserter.assertNotNull(invokeStyle, "invokeStyle" + Errors.CANT_NULL);
			invokeStyle();
		}
		
		public final function as_setPreferences(data:Object) : void
		{
			setPreferences(new BattleHitsPreferencesDataVO(data));
		}
		
		protected function setPreferences(data:BattleHitsPreferencesDataVO) : void
		{
			var message:String = "as_setPreferences" + Errors.ABSTRACT_INVOKE;
			DebugUtils.LOG_ERROR(message);
			throw new AbstractException(message);
		}
	}
}