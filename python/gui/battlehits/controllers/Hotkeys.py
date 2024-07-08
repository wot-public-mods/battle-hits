# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

from messenger import MessengerEntry

from ..events import g_eventsManager
from ..controllers import AbstractController

class Hotkeys(AbstractController):

	@property
	def forcedHandlers(self):
		return self.__handlers

	def __init__(self):
		super(Hotkeys, self).__init__()
		self.__handlers = []

	def init(self):
		g_eventsManager.onKeyEvent += self.onKeyEvent

	def fini(self):
		g_eventsManager.onKeyEvent -= self.onKeyEvent
		self.__handlers = []

	def addForced(self, handler):
		if handler not in self.__handlers:
			self.__handlers.append(handler)

	def delForced(self, handler):
		if handler in self.__handlers:
			self.__handlers.remove(handler)

	def onKeyEvent(self, event, alreadyHandled):

		if not event.isKeyDown():
			return

		if MessengerEntry.g_instance.gui.isFocused():
			return
