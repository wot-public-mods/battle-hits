# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

class IBattlesHistory(object):
	__slots__ = ()

	@property
	def history(self):
		raise NotImplementedError

	def getBattleByUniqueID(self, arenaUniqueID):
		raise NotImplementedError

	def getBattleByID(self, battleID):
		raise NotImplementedError

	def addBattle(self, data):
		raise NotImplementedError

	def deleteHistory(self):
		raise NotImplementedError
