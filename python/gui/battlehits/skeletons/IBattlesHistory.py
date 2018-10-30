
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
