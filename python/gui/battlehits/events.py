# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

import Event

__all__ = ('g_eventsManager', )

class EventsManager(object):

	def __init__(self):
		self.onChangedBattleData = Event.Event()
		self.onChangedHitData = Event.Event()

		self.onVehicleBuilded = Event.Event()

		self.invalidateBattlesDP = Event.Event()
		self.invalidateHitsDP = Event.Event()

		self.showPreferencesPopover = Event.Event()
		self.showMainView = Event.Event()
		self.closeMainView = Event.Event()

		self.onShowBattle = Event.Event()
		self.onDestroyBattle = Event.Event()

		self.onSettingsChanged = Event.Event()
		self.onKeyEvent = Event.Event()

g_eventsManager = EventsManager()
