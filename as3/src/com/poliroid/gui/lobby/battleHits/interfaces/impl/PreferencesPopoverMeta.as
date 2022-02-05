package com.poliroid.gui.lobby.battleHits.interfaces.impl 
{
	import net.wg.data.constants.Errors;
	import net.wg.infrastructure.base.SmartPopOverView;
	import net.wg.infrastructure.exceptions.AbstractException;
	import com.poliroid.gui.lobby.battleHits.data.BattleHitsPreferencesDataVO;
	import net.wg.data.constants.Linkages;

	public class PreferencesPopoverMeta extends SmartPopOverView
	{
		public var invokeSettingsChange:Function;
		public var invokeStyleChange:Function;
		public var invokeHistoryDelete:Function;

		// bcs SWC in very good condition
		public function get wrapperLinkage(): String 
		{
			return Linkages.SMART_POPOVER;
		}

		public function invokeSettingsChangeS(processReplays:Boolean, saveOnlySession:Boolean, swapHangar:Boolean): void
		{
			App.utils.asserter.assertNotNull(invokeSettingsChange, "invokeSettingsChange" + Errors.CANT_NULL);
			invokeSettingsChange(processReplays, saveOnlySession, swapHangar);
		}

		public function invokeStyleChangeS(): void
		{
			App.utils.asserter.assertNotNull(invokeStyleChange, "invokeStyleChange" + Errors.CANT_NULL);
			invokeStyleChange();
		}

		public function invokeHistoryDeleteS(): void
		{
			App.utils.asserter.assertNotNull(invokeHistoryDelete, "invokeHistoryDelete" + Errors.CANT_NULL);
			invokeHistoryDelete();
		}

		public final function as_setPreferences(data:Object): void
		{
			setPreferences(new BattleHitsPreferencesDataVO(data));
		}

		protected function setPreferences(data:BattleHitsPreferencesDataVO): void
		{
			var message:String = "as_setPreferences" + Errors.ABSTRACT_INVOKE;
			DebugUtils.LOG_ERROR(message);
			throw new AbstractException(message);
		}
	}
}
