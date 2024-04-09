import functools
import types
import ResMgr
from collections import namedtuple
from constants import SHELL_TYPES
from helpers import dependency
from items import vehicles
from skeletons.gui.impl import IGuiLoader

__all__ = ('byteify', 'override', 'getShellParams', 'getShell', 'parse_lang_fields', 'readFromVFS', 
			'simplifyVehicleCompactDescr', 'cancelCallbackSafe', 'cache_result')

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

_SHELL_PARAMS = namedtuple('ShellParams', ['index', 'explosionRadius', 'isImproved', 'isSpg',
										'hasStun'])
_SHELL_PARAMS.__new__.__defaults__ = (None,) * len(_SHELL_PARAMS._fields)

_SHELL_NAME_TO_ID = {
	SHELL_TYPES.ARMOR_PIERCING: 0,
	SHELL_TYPES.ARMOR_PIERCING_CR: 1,
	SHELL_TYPES.HOLLOW_CHARGE: 2,
	SHELL_TYPES.HIGH_EXPLOSIVE: 3,
}

def _common_effect_name(effectsIndex):
	value = vehicles.g_cache.shotEffectsNames.get(effectsIndex, '')
	for item in ('ArmorPiercing', 'APCR', 'HighExplosive', 'HollowCharge'):
		if item.lower() in value.lower():
			return item.lower()

def getShellParams(vehicleDescriptor, effectsIndex):
	# get shell from gun shells by it effectsIndex
	shellDescr = None
	gunDamageMutable = False
	for shotDescr in vehicleDescriptor.gun.shots:
		gunDamageMutable |= getattr(shotDescr.shell, 'isDamageMutable', False)
		if effectsIndex == shotDescr.shell.effectsIndex:
			shellDescr = shotDescr.shell
			break

	# get shell by common shell type
	# poland with mutable damage, intoduces in 1.24.1
	if not shellDescr and gunDamageMutable:
		effectName = _common_effect_name(effectsIndex)
		for shotDescr in vehicleDescriptor.gun.shots:
			if effectName == _common_effect_name(shotDescr.shell.effectsIndex):
				shellDescr = shotDescr.shell
				break

	if not shellDescr:
		return _SHELL_PARAMS()

	explosionRadius = 0
	hasStun = False
	if shellDescr.kind == SHELL_TYPES.HIGH_EXPLOSIVE:
		explosionRadius = shellDescr.type.explosionRadius
		hasStun = shellDescr.stun is not None

	shellIndex = 0
	if shellDescr.kind in _SHELL_NAME_TO_ID:
		shellIndex = _SHELL_NAME_TO_ID[shellDescr.kind]

	isSPG = 'SPG' in vehicleDescriptor.type.tags
	if isSPG and shellDescr.kind == SHELL_TYPES.HIGH_EXPLOSIVE:
		shellIndex += 1
		if hasStun:
			shellIndex += 1

	return _SHELL_PARAMS(shellIndex, explosionRadius, shellDescr.isGold, isSPG, hasStun)

def parse_lang_fields(langFile):
	"""split items by lines and key value by ':'
	like yaml format"""
	result = {}
	langData = readFromVFS(langFile)
	if langData:
		for item in langData.splitlines():
			if ': ' not in item:
				continue
			key, value = item.split(": ", 1)
			result[key] = value.replace('\\n', '\n')
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
	if not compactDescr:
		return
	splitted = vehicles._splitVehicleCompactDescr(compactDescr)
	fixed = []
	for idx, param in enumerate(splitted):
		if idx < 2: fixed.append(param)
		elif idx == 2: fixed.append(0)
		elif idx == 3: fixed.append('')
		else: fixed.append(None)
	return vehicles._combineVehicleCompactDescr(*fixed)

def cancelCallbackSafe(cbid):
	import BigWorld
	try:
		BigWorld.cancelCallback(cbid)
		return True
	except (AttributeError, ValueError):
		return False

def cache_result(function):
	memo = {}
	@functools.wraps(function)
	def wrapper(*args):
		try:
			return memo[args]
		except KeyError:
			rv = function(*args)
			memo[args] = rv
			return rv
	return wrapper

def getParentWindow():
	uiLoader = dependency.instance(IGuiLoader)
	if uiLoader and uiLoader.windowsManager:
		return uiLoader.windowsManager.getMainWindow()
