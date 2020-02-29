import collections
import datetime
import json
import os
import shutil
import subprocess
import sys
import zipfile
import time

def copytree(source, destination, ignore=None):
	"""implementation of shutil.copytree
	original sometimes throw error on folders create"""
	for item in os.listdir(source):
		# skip git files
		if '.gitkeep' in item:
			continue
		sourcePath = os.path.join(source, item)
		destinationPath = os.path.join(destination, item)
		# use copytree for directory
		if not os.path.isfile(sourcePath):
			copytree(sourcePath, destinationPath, ignore)
			continue
		# make dir by os module
		dirName, fileName = os.path.split(destinationPath)
		if not os.path.isdir(dirName):
			os.makedirs(dirName)
		# skip files by ignore pattern
		if ignore:
			ignored_names = ignore(source, os.listdir(source))
			if fileName in ignored_names:
				continue
		# copy file
		shutil.copy2(sourcePath, destinationPath)

def zipFolder(source, destination, mode='w', compression=zipfile.ZIP_STORED):
	""" ZipFile by default dont create folders info in result zip """
	def dirInfo(path):
		"""return fixed ZipInfo for directory"""
		info = zipfile.ZipInfo(path, now)
		info.filename = info.filename[seek_offset:]
		if not info.filename:
			return None
		if not info.filename.endswith('/'):
			info.filename += '/'
		info.compress_type = compression
		return info
	def fileInfo(path):
		"""return fixed ZipInfo for file"""
		info = zipfile.ZipInfo(path, now)
		info.external_attr = 33206 << 16 # -rw-rw-rw-
		info.filename = info.filename[seek_offset:]
		info.compress_type = compression
		return info
	with zipfile.ZipFile(destination, mode, compression) as zipfh:
		now = tuple(datetime.datetime.now().timetuple())[:6]
		seek_offset = len(source) + 1
		for dirName, _, files in os.walk(source):
			info = dirInfo(dirName)
			if info:
				zipfh.writestr(info, '')
			for fileName in files:
				filePath = os.path.join(dirName, fileName)
				info = fileInfo(filePath)
				zipfh.writestr(info, open(filePath, 'rb').read())

def processRunning(path):
	"""Cheek is process runing, no"""
	processName = os.path.basename(path).lower()
	try:
		import psutil
		for proc in psutil.process_iter():
			if proc.name().lower() == processName:
				return True
		return False
	except ImportError:
		if os.name == 'nt':
			for task in (x.split() for x in subprocess.check_output('tasklist').splitlines()):
				if task and task[0].lower() == processName:
					return True
			return False
		else:
			print('cant list process on your system')
			print('run -> pip install psutil')
			raise NotImplementedError

# handle args from command line
BUILD_FLASH = 'flash' in sys.argv
COPY_INTO_GAME = 'ingame' in sys.argv
CREATE_DISTRIBUTE = 'distribute' in sys.argv
RUN_SONAR = 'sonar' in sys.argv

# load config
assert os.path.isfile('build.json'), 'Config not found'
with open('build.json', 'r') as fh:
	hook = lambda x: collections.namedtuple('object', x.keys())(*x.values())
	CONFIG = json.loads(fh.read(), object_hook=hook)

GAME_FOLDER = os.environ.get('WOT_FOLDER', CONFIG.game.folder)
GAME_VERSION = os.environ.get('WOT_VERSION', CONFIG.game.version)

# cheek ingame folder
WOT_PACKAGES_DIR = '{wot}/mods/{version}/'.format(wot=GAME_FOLDER, version=GAME_VERSION)
if COPY_INTO_GAME:
	assert os.path.isdir(WOT_PACKAGES_DIR), 'Wot mods folder notfound'

# package data
PACKAGE_NAME = '{author}.{name}_{version}.wotmod'.format(author=CONFIG.info.author,
				name=CONFIG.info.id, version=CONFIG.info.version)

# generate package meta file
META = """<root>
	<!-- Techical MOD ID -->
	<id>{id}</id>
	<!-- Package version -->
	<version>{version}</version>
	<!-- Human readable name -->
	<name>{name}</name>
	<!-- Human readable description -->
	<description>{description}</description>
</root>""".format(id='%s.%s' % (CONFIG.info.author, CONFIG.info.id), name=CONFIG.info.name,
					description=CONFIG.info.description, version=CONFIG.info.version)

# prepere folders
if os.path.isdir('temp'):
	shutil.rmtree('temp')
os.makedirs('temp')
if os.path.isdir('build'):
	shutil.rmtree('build')
os.makedirs('build')

# build flash
if BUILD_FLASH:
	# JSFL file with commands for Animate
	jsflContent = ''
	flashWD = os.getcwd().replace('\\', '/').replace(':', '|')
	jsflFile = 'build.jsfl'
	logFile = 'as-build.log'
	logFileURI = 'file:///%s/%s' % (flashWD, logFile)
	# add publishDocument command for all *.fla and *.xfl files
	for dirPath, _, fileNames in os.walk('as3'):
		for fileName in fileNames:
			if fileName.endswith('.fla') or fileName.endswith('.xfl'):
				filePath = '%s/%s' % (dirPath.replace('\\', '/'), fileName)
				jsflContent += 'FLfile.write("%s", "Publishing: %s\\n", "append");\n' % (logFileURI, filePath)
				jsflContent += 'fl.publishDocument("file:///%s/%s", "Default");\n' % (flashWD, filePath)
				jsflContent += 'fl.compilerErrors.save("%s", "append");\n' % (logFileURI)
	# add close command only if Animate not opened
	if not processRunning(CONFIG.software.animate):
		jsflContent += 'fl.quit(false);'
	with open(jsflFile, 'w') as fh:
		fh.write(jsflContent)
	# run Animate
	try:
		subprocess.call([CONFIG.software.animate, '-e', jsflFile, '-AlwaysRunJSFL'], stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		print e
	# publishing can be asynchronous when Animate is already opened
	# so waiting script file unlock to remove, which means publishing is done
	while os.path.exists(jsflFile):
		try:
			os.remove(jsflFile)
			if os.path.isfile(logFile):
				print (open(logFile, 'r').read())
		except: #NOSONAR
			time.sleep(.1)

# build python
subprocess.call([CONFIG.software.python, '-m', 'compileall', '-f', 'python'])

# copy all staff
if os.path.isdir('resources/in'):
	copytree('resources/in', 'temp/res')
if os.path.isdir('as3/bin'):
	copytree('as3/bin', 'temp/res/gui/flash')
copytree('python', 'temp/res/scripts/client', ignore=shutil.ignore_patterns('*.py'))
with open('temp/meta.xml', 'w') as fh:
	fh.write(META)

# create package
zipFolder('temp', 'build/%s' % PACKAGE_NAME)

# copy package into game
if COPY_INTO_GAME:
	shutil.copy2('build/%s' % PACKAGE_NAME, WOT_PACKAGES_DIR)

# create distribution
if CREATE_DISTRIBUTE:
	os.makedirs('temp/distribute/mods/%s' % GAME_VERSION)
	shutil.copy2('build/%s' % PACKAGE_NAME, 'temp/distribute/mods/%s' % GAME_VERSION)
	if os.path.isdir('resources/out'):
		copytree('resources/out', 'temp/distribute')
	zipFolder('temp/distribute', 'build/{name}_{version}.zip'.format(name=CONFIG.info.id,
				version=CONFIG.info.version))

# list for cleaning
cleanup_list = set([])

# builder temporary
cleanup_list.add('temp')

# Animate unnecessary
cleanup_list.add('EvalScript error.tmp')
cleanup_list.add('as3/DataStore')
cleanup_list.add('as-build.log')

# python bytecode
for dirName, _, files in os.walk('python'):
	for fileName in files:
		if fileName.endswith('.pyc'):
			cleanup_list.add(os.path.join(dirName, fileName))

# delete files
for path in cleanup_list:
	if os.path.isdir(path):
		shutil.rmtree(path)
	elif os.path.isfile(path):
		os.remove(path)

# run sonar
if RUN_SONAR and os.path.isfile(CONFIG.software.sonar):
		subprocess.call([CONFIG.software.sonar])
