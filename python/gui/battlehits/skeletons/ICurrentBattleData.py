
class ICurrentBattleData(object):
	__slots__ = ()

	@property
	def battle(self):
		raise NotImplementedError
	
	@property
	def atacker(self):
		raise NotImplementedError
	
	@property
	def victim(self):
		raise NotImplementedError
	
	@property
	def hit(self):
		raise NotImplementedError
	
	def battleByID(self, battleID):
		raise NotImplementedError
		
	def hitByID(self, hitID):
		raise NotImplementedError
	