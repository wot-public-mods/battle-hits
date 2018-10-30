
class IHangarCamera(object):
	__slots__ = ()

	@property
	def enabled(self):
		raise NotImplementedError

	def enable(self):
		raise NotImplementedError

	def disable(self):
		raise NotImplementedError
	
	def setCameraData(self, default, current, limits, sens, target, forceUpdate = False):
		raise NotImplementedError
	
	def updateCamera(self, dx, dy, dz):
		raise NotImplementedError
