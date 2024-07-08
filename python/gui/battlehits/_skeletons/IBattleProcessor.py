# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

class IBattleProcessor(object):
	__slots__ = ()

	def processVehicleInit(self, vehicle):
		raise NotImplementedError

	def processHealthChanged(self, vehicle, newHealth, attackerID, attackReasonID):
		raise NotImplementedError

	def onModelsRefresh(self, vehicle, modelState):
		raise NotImplementedError

	def processShot(self, vehicle, attackerID, points, effectsIndex, damageFactor):
		raise NotImplementedError

	def processExplosion(self, vehicle, attackerID, center, effectsIndex, damageFactor):
		raise NotImplementedError
