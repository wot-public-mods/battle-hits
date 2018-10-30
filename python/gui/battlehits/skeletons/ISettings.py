
class ISettings(object):
	__slots__ = ()

	def get(self, name, defaultValue = None):
		raise NotImplementedError
	
	def apply(self, data):
		raise NotImplementedError
