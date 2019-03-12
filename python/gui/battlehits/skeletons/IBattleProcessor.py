class IBattleProcessor(object):
	__slots__ = ()

	def processEnterWorld(self, vehicle):
		raise NotImplementedError

	def processHealthChanged(self, vehicle, newHealth, attackerID, attackReasonID):
		raise NotImplementedError

	def onModelsRefresh(self, vehicle, modelState):
		raise NotImplementedError

	def processShot(self, vehicle, attackerID, points, effectsIndex, damageFactor):
		raise NotImplementedError

	def processExplosion(self, vehicle, attackerID, center, effectsIndex, damageFactor):
		raise NotImplementedError
