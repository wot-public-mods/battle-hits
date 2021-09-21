
import types
import ResMgr

__all__ = ('byteify', 'override', 'getShellParams', 'getShell', 'parseLangFields', 'readFromVFS', 'simplifyVehicleCompactDescr')

def override(holder, name, wrapper=None, setter=None):
	"""Override methods, properties, functions, attributes
	:param holder: holder in which target will be overrided
	:param name: name of target to be overriden
	:param wrapper: replacement for override target
	:param setter: replacement for target property setter"""
	if wrapper is None:
		return lambda wrapper, setter=None: override(holder, name, wrapper, setter)
	target = getattr(holder, name)
	wrapped = lambda *a, **kw: wrapper(target, *a, **kw)
	if not isinstance(holder, types.ModuleType) and isinstance(target, types.FunctionType):
		setattr(holder, name, staticmethod(wrapped))
	elif isinstance(target, property):
		prop_getter = lambda *a, **kw: wrapper(target.fget, *a, **kw)
		prop_setter = target.fset if not setter else lambda *a, **kw: setter(target.fset, *a, **kw)
		setattr(holder, name, property(prop_getter, prop_setter, target.fdel))
	else:
		setattr(holder, name, wrapped)

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

	# return None if shellDescr is None
	if shellDescr is None:
		return None, None

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

def getLobbyHeader():
	""" Getter of LobbyHeader view instance """
	from gui.app_loader.settings import APP_NAME_SPACE
	from gui.shared.personality import ServicesLocator
	from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
	from frameworks.wulf import WindowLayer
	app = ServicesLocator.appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app or not app.containerManager:
		return
	lobby = app.containerManager.getContainer(WindowLayer.VIEW)
	if not lobby:
		return
	view = lobby.getView()
	if not view:
		return
	return view.components.get(VIEW_ALIAS.LOBBY_HEADER, None)

def simplifyVehicleCompactDescr(compactDescr):
	from items.vehicles import _combineVehicleCompactDescr, _splitVehicleCompactDescr
	if not compactDescr:
		return
	splitted = _splitVehicleCompactDescr(compactDescr)
	fixed = []
	for idx, param in enumerate(splitted):
		if idx < 2: fixed.append(param)
		elif idx == 2: fixed.append(0)
		elif idx == 3: fixed.append('')
		else: fixed.append(None)
	return _combineVehicleCompactDescr(*fixed)
