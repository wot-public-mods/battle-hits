
class IVehicle(object):
	__slots__ = ()
	
	@property
	def compoundModel(self):
		raise NotImplementedError
	
	@property
	def collision(self):
		raise NotImplementedError
	
	def removeVehicle(self):
		raise NotImplementedError
	
	def loadVehicle(self):
		raise NotImplementedError
	
	def partDescriptor(self, partName):
		raise NotImplementedError
		
	def partWorldMatrix(self, partName):
		raise NotImplementedError
