
class IVehicle(object):
	__slots__ = ()
	
	def setVehicleData(self, vehicleDescr, aimParts):
		raise NotImplementedError
	
	def partDescriptor(self, partName):
		raise NotImplementedError
		
	def partWorldMatrix(self, partName):
		raise NotImplementedError
