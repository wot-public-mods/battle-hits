
import Event

__all__ = ('g_eventsManager', )

class EventsManager(object):

    def __init__(self):
		
		self.onChangedBattleData = Event.Event()
		self.onChangedHitData = Event.Event()
		
		self.invalidateBattlesDP = Event.Event()
		self.invalidateHitsDP = Event.Event()
		
		self.showPopover = Event.Event()
		self.showUI = Event.Event()
		self.closeUI = Event.Event()
		
		self.onShowBattle = Event.Event()
		self.onDestroyBattle = Event.Event()
		
		self.onSettingsChanged = Event.Event()
		
		self.onAppFinish = Event.Event()
		
		self.onKeyEvent = Event.Event()
		
g_eventsManager = EventsManager()