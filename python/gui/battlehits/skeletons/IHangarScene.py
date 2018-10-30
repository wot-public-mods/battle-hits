
class IHangarScene(object):
	__slots__ = ()

	def create(self):
		raise NotImplementedError
	
	def destroy(self):
		raise NotImplementedError
	
	def noDataHit(self):
		raise NotImplementedError
