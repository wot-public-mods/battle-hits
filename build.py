
import compileall
import datetime
import os
import shutil
import zipfile

# software data
ANIMATE_PATH = 'C:\\Program Files\\Adobe\\Adobe Animate CC 2015\\Animate.exe'

# game data
COPY_INTO_GAME = True
GAME_VERSION = '0.9.19.1.1'
GAME_FOLDER = 'X:/wot_ct'

# modification data
MODIFICATION_AUTHOR = 'poliroid'
MODIFICATION_DESCRIPTION = 'Explore received hits by your vehicle in battle'
MODIFICATION_IDENTIFICATOR = 'battlehits'
MODIFICATION_NAME = 'Battle Hits'
MODIFICATION_VERSION = '1.1.1'

# result package name
PACKAGE_NAME = '{author}.{name}_{version}.wotmod'.format( author = MODIFICATION_AUTHOR, \
				name = MODIFICATION_IDENTIFICATOR, version = MODIFICATION_VERSION )


def copytree(source, destination, ignore=None):
	"""implementation of shutil.copytree 
	original sometimes throw error on folders create"""
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

def zipFolder(source, destination, mode='w', compression=zipfile.ZIP_STORED):
	"""ZipFile by default dont create folders info in result zip"""
	def dirInfo(dirPath):
		zi = zipfile.ZipInfo(dirPath, now)
		zi.filename = zi.filename[seek_offset:]
		if zi.filename:
			if not zi.filename.endswith('/'): 
				zi.filename += '/'
			zi.compress_type = compression
			return zi
	def fileInfo(filePath):
		st = os.stat(filePath)
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

# prepere folders
if os.path.isdir('temp'):
	shutil.rmtree('temp')
os.makedirs('temp') 
if os.path.isdir('build'):
	shutil.rmtree('build')
os.makedirs('build')
if not os.path.isdir('resources'):
	os.makedirs('resources')
if not os.path.isdir('as3/bin'):
	os.makedirs('as3/bin')


# build flash
with open('build.jsfl', 'wb') as fh:
	for fileName in os.listdir('as3'):
		if fileName.endswith('fla'):
			fh.write('fl.publishDocument("file:///{path}/as3/{fileName}", "Default");\r\n'.format(path = os.getcwd().replace('\\', '/').replace(':', '|'), fileName = fileName))
	fh.write('fl.quit(false);')
os.system('"{animate}" -e build.jsfl -AlwaysRunJSFL'.format(animate = ANIMATE_PATH))

# build python
for dirName, _, files in os.walk('python'):
	for fileName in files:
		if fileName.endswith(".py"):
			filePath = os.path.join(dirName, fileName)
			compileall.compile_file(filePath)

# copy all staff
copytree('as3/bin/', 'temp/res/gui/flash')
copytree('python', 'temp/res/scripts/client', ignore=shutil.ignore_patterns('*.py'))
copytree('resources', 'temp/res')

# build META
META = """<root>
	
	<!-- Techical MOD ID -->
	<id>{id}</id>
	
	<!-- Package version -->
	<version>{version}</version>
	
	<!-- Human readable name -->
	<name>{name}</name>
	
	<!-- Human readable description -->
	<description>{description}</description>
</root>"""
with open('temp/meta.xml', 'wb') as fh:
	fh.write( META.format( id = '%s.%s' % (MODIFICATION_AUTHOR, MODIFICATION_IDENTIFICATOR), name = MODIFICATION_NAME, \
			description = MODIFICATION_DESCRIPTION, version = MODIFICATION_VERSION ) )

# create package
zipFolder('temp', 'build/%s' % PACKAGE_NAME)

# copy package into game
if COPY_INTO_GAME:
	shutil.copy2('build/%s' % PACKAGE_NAME, '{wot}/mods/{version}/'.format(wot = GAME_FOLDER, version =GAME_VERSION))

# clean up build files
shutil.rmtree('temp')
os.remove('build.jsfl')
for dirname, _, files in os.walk('python'):
	for filename in files:
		if filename.endswith('.pyc'):
			os.remove(os.path.join(dirname, filename))
for dirname, _, files in os.walk('as3'):
	for filename in files:
		if filename.endswith('.swf'):
			os.remove(os.path.join(dirname, filename))