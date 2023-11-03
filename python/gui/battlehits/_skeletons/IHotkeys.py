class IHotkeys(object):
	__slots__ = ()

	@property
	def forcedHandlers(self):
		raise NotImplementedError

	def addForced(self, handler):
		raise NotImplementedError

	def delForced(self, handler):
		raise NotImplementedError
