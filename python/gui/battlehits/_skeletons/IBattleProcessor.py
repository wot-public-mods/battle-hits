# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

class IBattleProcessor(object):
	__slots__ = ()

	def processVehicleInit(self, vehicle):
		raise NotImplementedError

	def onModelsRefresh(self, vehicle, modelState):
		raise NotImplementedError

	def processShot(self, vehicle, attackerID, hitPoints, effectsIndex, damage, damageFactor):
		raise NotImplementedError

	def processExplosion(self, vehicle, attackerID, center, effectsIndex, damage, damageFactor):
		raise NotImplementedError
