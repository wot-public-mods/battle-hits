
import types
import ResMgr
import Math

__all__ = ('byteify', 'override', 'getShellParams', 'getShell', 'parseLangFields', 'readFromVFS',
			'generateWheelsData', 'unpackMatrix', 'packMatrix')

def override(target, name, hook=None):
	"""Override methods, properties, functions
	:param target: """
	if hook is None:
		return lambda hook: override(target, name, hook)
	original = getattr(target, name)
	overrided = lambda *a, **kw: hook(original, *a, **kw)
	if not isinstance(target, types.ModuleType) and isinstance(original, types.FunctionType):
		setattr(target, name, staticmethod(overrided))
	elif isinstance(original, property):
		setattr(target, name, property(overrided))
	else:
		setattr(target, name, overrided)

def byteify(data):
	"""Encodes data with UTF-8
	:param data: Data to encode"""
	result = data
	if isinstance(data, dict):
		result = {byteify(key): byteify(value) for key, value in data.iteritems()}
	elif isinstance(data, (list, tuple, set)):
		result = [byteify(element) for element in data]
	elif isinstance(data, unicode):
		result = data.encode('utf-8')
	return result

def getShell(vehicleDescriptor, effectsIndex):
	"""get shellDescr by effectsIndex"""
	for shellDescr in vehicleDescriptor.gun.shots:
		if effectsIndex == shellDescr.shell.effectsIndex:
			return shellDescr
	return None

def getShellParams(vehicleDescriptor, effectsIndex):
	"""form shell params from shellDescr"""
	from constants import SHELL_TYPES
	shellType, shellSplash = 0, 0.0
	shellDescr = getShell(vehicleDescriptor, effectsIndex)
	if shellDescr.shell.kind == SHELL_TYPES.ARMOR_PIERCING:
		shellType = 0
	elif shellDescr.shell.kind == SHELL_TYPES.ARMOR_PIERCING_CR:
		shellType = 1
	elif shellDescr.shell.kind == SHELL_TYPES.HOLLOW_CHARGE:
		shellType = 2
	elif shellDescr.shell.kind in [SHELL_TYPES.HIGH_EXPLOSIVE, SHELL_TYPES.ARMOR_PIERCING_HE]:
		shellType = 3
		shellSplash = shellDescr.shell.type.explosionRadius
	return shellType, shellSplash

def parseLangFields(langCode):
	"""split items by lines and key value by ': ' like yaml format"""
	from gui.battlehits._constants import LANGUAGE_FILE_PATH
	result = {}
	langData = readFromVFS(LANGUAGE_FILE_PATH % langCode)
	if langData:
		for item in langData.splitlines():
			if ': ' not in item:
				continue
			key, value = item.split(": ", 1)
			result[key] = value
	return result

def readFromVFS(path):
	"""using for read files from VFS"""
	file = ResMgr.openSection(path)
	if file is not None and ResMgr.isFile(path):
		return str(file.asBinary)
	return None

def packMatrix(matrix):
	accuracy = 7
	result = []
	result.append(round(matrix.translation.x, accuracy))
	result.append(round(matrix.translation.y, accuracy))
	result.append(round(matrix.translation.z, accuracy))
	result.append(round(matrix.yaw, accuracy))
	result.append(round(matrix.pitch, accuracy))
	result.append(round(matrix.roll, accuracy))
	return result

def unpackMatrix(data):
	matrix = Math.Matrix()
	matrix.setRotateYPR((data[3], data[4], data[5]))
	matrix.translation = (data[0], data[1], data[2])
	return matrix

def generateWheelsData(vehicle):
	wheels = {}
	wheelsConfig = vehicle.appearance.typeDescriptor.chassis.generalWheelsAnimatorConfig
	if wheelsConfig:
		nodesNames = wheelsConfig.getWheelNodeNames()
		for nodeName in nodesNames:
			wheels[nodeName] = packMatrix(vehicle.appearance.compoundModel.node(nodeName).localMatrix)
	return wheels
