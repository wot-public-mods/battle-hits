import collections
import compileall
import datetime
import json
import os
import shutil
import subprocess
import sys
import zipfile

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

# handle args from command line
BUILD_FLASH = 'flash' in sys.argv
COPY_INTO_GAME = 'ingame' in sys.argv
CREATE_DISTRIBUTE = 'distribute' in sys.argv
RUN_SONAR = 'sonar' in sys.argv

# load config
assert os.path.isfile('./build.json'), 'Config not found'
with open('./build.json', 'rb') as fh:
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
if os.path.isdir('./temp'):
	shutil.rmtree('./temp')
os.makedirs('./temp')
if os.path.isdir('./build'):
	shutil.rmtree('./build')
os.makedirs('./build')
if not os.path.isdir('./resources'):
	os.makedirs('./resources')
	os.makedirs('./resources/in')
	os.makedirs('./resources/out')
if not os.path.isdir('./as3/bin'):
	os.makedirs('./as3/bin')

# build flash
if BUILD_FLASH:
	flashWorkDir = os.getcwd().replace('\\', '/').replace(':', '|')
	with open('./build.jsfl', 'wb') as fh:
		for fileName in os.listdir('./as3'):
			if fileName.endswith('fla'):
				publishDocument = 'fl.publishDocument("file:///{path}/as3/{fileName}", "Default");\r\n'
				fh.write(publishDocument.format(path=flashWorkDir, fileName=fileName))
		fh.write('fl.quit(false);')
	subprocess.call([CONFIG.software.animate, '-e', 'build.jsfl', '-AlwaysRunJSFL'])

# build python
for dirName, _, files in os.walk('python'):
	for fileName in files:
		if fileName.endswith(".py"):
			filePath = os.path.join(dirName, fileName)
			compileall.compile_file(filePath)

# copy all staff
copytree('./resources/in', './temp/res')
copytree('./as3/bin/', './temp/res/gui/flash')
copytree('./python', './temp/res/scripts/client', ignore=shutil.ignore_patterns('*.py'))
with open('temp/meta.xml', 'wb') as fh:
	fh.write(META)

# create package
zipFolder('./temp', './build/%s' % PACKAGE_NAME)

# copy package into game
if COPY_INTO_GAME:
	shutil.copy2('./build/%s' % PACKAGE_NAME, WOT_PACKAGES_DIR)

# create distribution
if CREATE_DISTRIBUTE:
	os.makedirs('./temp/distribute/mods/%s' % GAME_VERSION)
	shutil.copy2('./build/%s' % PACKAGE_NAME, './temp/distribute/mods/%s' % GAME_VERSION)
	copytree('./resources/out', './temp/distribute')
	zipFolder('./temp/distribute', './build/{name}_{version}.zip'.format(name=CONFIG.info.id,
				version=CONFIG.info.version))

# clean up build files
shutil.rmtree('temp')

# clean python build files
for dirName, _, files in os.walk('./python'):
	for fileName in files:
		if fileName.endswith('.pyc'):
			os.remove(os.path.join(dirName, fileName))

# clean flash build files
if BUILD_FLASH:
	os.remove('build.jsfl')

# run sonar
if RUN_SONAR:
	subprocess.call([CONFIG.software.sonar])
