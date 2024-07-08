# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

class IState(object):
	__slots__ = ()

	@property
	def currentBattleID(self):
		raise NotImplementedError

	@property
	def currentHitID(self):
		raise NotImplementedError

	def enable(self):
		raise NotImplementedError

	def disable(self, silent=False):
		raise NotImplementedError

	def switch(self):
		raise NotImplementedError
