
__all__ = ('IController', )

class IController(object):
	
	def __init__(self):
		self.__enabled = False

	@property
	def enabled(self):
		return self.__enabled
	
	@enabled.setter
	def enabled(self, value):
		self.__enabled = value

	def init(self):
		pass
	
	def fini(self):
		pass
	
	