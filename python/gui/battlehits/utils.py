
import types
import ResMgr

__all__ = ('byteify', 'override', 'getShellParams', 'parseLangFields', 'readFromVFS')

def override(holder, name, target = None):
	"""using for override any staff"""
	if target is None:
		return lambda target: override(holder, name, target)
	original = getattr(holder, name)
	overrided = lambda *a, **kw: target(original, *a, **kw)
	if not isinstance(holder, types.ModuleType) and isinstance(original, types.FunctionType):
		setattr(holder, name, staticmethod(overrided))
	elif isinstance(original, property):
		setattr(holder, name, property(overrided))
	else:
		setattr(holder, name, overrided)

def byteify(data):
	"""using for convert unicode key/value to utf-8"""
	if isinstance(data, types.DictType): 
		return { byteify(key): byteify(value) for key, value in data.iteritems() }
	elif isinstance(data, types.ListType) or isinstance(data, tuple) or isinstance(data, set):
		return [ byteify(element) for element in data ]
	elif isinstance(data, types.UnicodeType):
		return data.encode('utf-8')
	else: 
		return data

def getShellParams(vehicleDescriptor, effectsIndex):
	"""form shell params from descr"""
	from constants import SHELL_TYPES
	from items import vehicles
	
	shellType, shellSplash = 0, 0.0
	
	for shell in vehicleDescriptor.gun.shots:
		
		if effectsIndex == shell.shell.effectsIndex:
			if shell.shell.kind == SHELL_TYPES.ARMOR_PIERCING:
				shellType = 0
			elif shell.shell.kind == SHELL_TYPES.ARMOR_PIERCING_CR:
				shellType = 1
			elif shell.shell.kind == SHELL_TYPES.HOLLOW_CHARGE:
				shellType = 2
			elif shell.shell.kind in [SHELL_TYPES.HIGH_EXPLOSIVE, SHELL_TYPES.ARMOR_PIERCING_HE]:
				shellType = 3
				shellSplash = shell.shell.type.explosionRadius
			break
	

	return (shellType, shellSplash, )

def parseLangFields(langCode):
	"""split items by lines and key value by : 
	like yaml format"""
	from gui.battlehits._constants import LANGUAGE_FILE_PATH
	result = {}
	langData = readFromVFS(LANGUAGE_FILE_PATH % langCode)
	if langData:
		for item in langData.splitlines():
			if ': ' not in item: continue
			key, value = item.split(": ", 1)
			result[key] = value
	return result

def readFromVFS(path):
	"""using for read files from VFS"""
	file = ResMgr.openSection(path)
	if file is not None and ResMgr.isFile(path):
		return str(file.asBinary)
	return None
