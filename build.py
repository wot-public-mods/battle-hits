
import collections
import compileall
import datetime
import json
import os
import shlex
import shutil
import subprocess
import sys
import zipfile

# implementation of shutil.copytree 
# original sometimes throw error on folders create
def copytree(source, destination, ignore=None):
	for item in os.listdir(source):
		if '.gitkeep' in item:
			continue
		sourcePath = os.path.join(source, item)
		destinationPath = os.path.join(destination, item)
		if os.path.isfile(sourcePath):
			baseDir, fileName = os.path.split(destinationPath)
			if not os.path.isdir(baseDir):
				os.makedirs(baseDir)
			if ignore:
				ignored_names = ignore(source, os.listdir(source))
				if fileName in ignored_names:
					continue
			shutil.copy2(sourcePath, destinationPath)
		else:
			copytree(sourcePath, destinationPath, ignore)

# ZipFile by default dont create folders info in result zip
def zipFolder(source, destination, mode='w', compression=zipfile.ZIP_STORED):
	def dirInfo(dirPath):
		zi = zipfile.ZipInfo(dirPath, now)
		zi.filename = zi.filename[seek_offset:]
		if zi.filename:
			if not zi.filename.endswith('/'): 
				zi.filename += '/'
			zi.compress_type = compression
			return zi
	def fileInfo(filePath):
		zi = zipfile.ZipInfo(filePath, now)
		zi.external_attr = 33206 << 16 # -rw-rw-rw-
		zi.filename = zi.filename[seek_offset:]
		zi.compress_type = compression
		return zi
	with zipfile.ZipFile(destination, mode, compression) as zip:
		now = tuple(datetime.datetime.now().timetuple())[:6]
		seek_offset = len(source) + 1
		for dirPath, _, files in os.walk(source):
			info = dirInfo(dirPath)
			if info:
				zip.writestr(info, '')
			for fileName in files:
				filePath = os.path.join(dirPath, fileName)
				info = fileInfo(filePath)
				zip.writestr(info, open(filePath, 'rb').read())

# handle args from command line
BUILD_FLASH = 'flash' in sys.argv
COPY_INTO_GAME = 'ingame' in sys.argv

# load config
assert os.path.isfile('./build.json'), 'Config not found'
with open('./build.json', 'rb') as fh:
	hook = lambda x: collections.namedtuple('object', x.keys())(*x.values())
	CONFIG = json.loads(fh.read(), object_hook=hook)

# cheek ingame folder
WOT_PACKAGES_DIR = '{wot}/mods/{version}/'.format(wot = CONFIG.game.folder, version = CONFIG.game.version)
if COPY_INTO_GAME:
	assert os.path.isdir(WOT_PACKAGES_DIR), 'Wot mods folder notfound'

# package data
PACKAGE_NAME = '{author}.{name}_{version}.wotmod'.format( author = CONFIG.info.author, \
				name = CONFIG.info.id, version = CONFIG.info.version )
META = """<root>
	
	<!-- Techical MOD ID -->
	<id>{id}</id>
	
	<!-- Package version -->
	<version>{version}</version>
	
	<!-- Human readable name -->
	<name>{name}</name>
	
	<!-- Human readable description -->
	<description>{description}</description>
</root>""".format( id = '%s.%s' % (CONFIG.info.author, CONFIG.info.id), name = CONFIG.info.name, \
					description = CONFIG.info.description, version = CONFIG.info.version )

# prepere folders
if os.path.isdir('./temp'):
	shutil.rmtree('./temp')
os.makedirs('./temp') 
if os.path.isdir('./build'):
	shutil.rmtree('./build')
os.makedirs('./build')
if not os.path.isdir('./resources'):
	os.makedirs('./resources')
if not os.path.isdir('./as3/bin'):
	os.makedirs('./as3/bin')

# build flash
if BUILD_FLASH:
	flashWorkDir = os.getcwd().replace('\\', '/').replace(':', '|')
	with open('./build.jsfl', 'wb') as fh:
		for fileName in os.listdir('./as3'):
			if fileName.endswith('fla'):
				fh.write('fl.publishDocument("file:///{path}/as3/{fileName}", "Default");\r\n'.format(path = flashWorkDir, fileName = fileName))
		fh.write('fl.quit(false);')
	subprocess.call(shlex.split('"{animate}" -e build.jsfl -AlwaysRunJSFL'.format(animate = CONFIG.software.animate)))

# build python
for dirName, _, files in os.walk('python'):
	for fileName in files:
		if fileName.endswith(".py"):
			filePath = os.path.join(dirName, fileName)
			compileall.compile_file(filePath)

# copy all staff
copytree('./as3/bin/', './temp/res/gui/flash')
copytree('./python', './temp/res/scripts/client', ignore=shutil.ignore_patterns('*.py'))
copytree('./resources', './temp/res')
with open('temp/meta.xml', 'wb') as fh:
	fh.write(META)

# create package
zipFolder('./temp', './build/%s' % PACKAGE_NAME)

# copy package into game
if COPY_INTO_GAME:
	shutil.copy2('./build/%s' % PACKAGE_NAME, WOT_PACKAGES_DIR)

# clean up build files
shutil.rmtree('temp')
for dirname, _, files in os.walk('./python'):
	for filename in files:
		if filename.endswith('.pyc'):
			os.remove(os.path.join(dirname, filename))
if BUILD_FLASH:
	os.remove('build.jsfl')
	