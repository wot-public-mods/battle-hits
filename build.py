# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

import collections
import datetime
import json
import os
import shutil
import logging
import subprocess
import sys
import zipfile
import time
import signal
import string
import psutil
import random

def rand_str(num):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(num))

class ElapsedFormatter():

	def __init__(self):
		self.start_time = time.time()

	def format(self, record):
		elapsed_seconds = record.created - self.start_time
		elapsed = datetime.timedelta(seconds = elapsed_seconds)
		return "{}.{} {}".format(
			str(elapsed.seconds).zfill(3), # seconds
			str(elapsed.microseconds).zfill(6), # microseconds
			record.getMessage() # message
		)

handler = logging.StreamHandler()
handler.setFormatter(ElapsedFormatter())
logging.getLogger().addHandler(handler)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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

def process_running(path):
	"""Cheek is process runing, no"""
	processName = os.path.basename(path).lower()
	for proc in psutil.process_iter():
		if proc.name().lower() == processName:
			return True
	return False

def build_flash():
	if not BUILD_FLASH:
		return

	# working directory URI for Animate
	flashWD = os.getcwd().replace('\\', '/').replace(':', '|')

	files = set()

	# add publishDocument command for all *.fla and *.xfl files
	for dirPath, _, fileNames in os.walk('as3'):
		for fileName in fileNames:
			if fileName.endswith('.fla') or fileName.endswith('.xfl'):
				dirPath = dirPath.replace('\\', '/')
				logName = fileName.replace('.fla', '.log').replace('.xfl', '.log')
				files.add((dirPath, fileName, logName))

	if not files:
		return

	if not process_running(CONFIG.software.animate):
		raise Exception('Animate not running') 

	for dirPath, fileName, logName in files:
		# JSFL file with commands for Animate
		jsflFile = 'build-%s.jsfl' % rand_str(5)
		jsflContent = ''
		documentURI = 'file:///{}/{}/{}'.format(flashWD, dirPath, fileName)
		logFileURI = 'file:///{}/{}'.format(flashWD, logName)
		jsflContent += 'fl.publishDocument("{}", "Default");\n'.format(documentURI)
		jsflContent += 'fl.compilerErrors.save("{}", false, true);\n'.format(logFileURI)
		jsflContent += '\n'

		with open(jsflFile, 'w') as fh:
			fh.write(jsflContent)

		try:
			subprocess.check_call([CONFIG.software.animate, '-e', jsflFile, '-AlwaysRunJSFL'], stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError as e:
			logger.exception('build_flash')

		while os.path.exists(jsflFile):
			try:
				os.remove(jsflFile)
			except:
				time.sleep(.01)

		log_data = ''
		if os.path.isfile(logName):
			data = open(logName, 'r').read().splitlines()
			if len(data) > 1:
				log_data = '\n'.join(data[:-2])
			os.remove(logName)

		if log_data:
			logger.error('failed flash publish %s/%s\n%s', dirPath, fileName, log_data)
		else:
			logger.info('flash published: %s/%s', dirPath, fileName)

def build_python():
	for dirPath, _, fileNames in os.walk('python'):
		for fileName in fileNames:
			if not fileName.endswith('.py'):
				continue
			filePath = "{}/{}".format(dirPath, fileName).replace('\\', '/')
			try:
				subprocess.check_output([CONFIG.software.python, '-m', 'py_compile', filePath],
												stderr=subprocess.STDOUT).decode()
				logger.info('python compiled: %s', filePath)
			except subprocess.CalledProcessError as e:
				logger.error('python fail compile: %s\n%s', filePath, e.output.decode())

# handle args from command line
BUILD_FLASH = 'flash' in sys.argv
COPY_INTO_GAME = 'ingame' in sys.argv
CREATE_DISTRIBUTE = 'distribute' in sys.argv
RUN_GAME = 'run' in sys.argv

# load config
assert os.path.isfile('build.json'), 'Config not found'
with open('build.json', 'r') as fh:
	hook = lambda x: collections.namedtuple('object', x.keys())(*x.values())
	CONFIG = json.loads(fh.read(), object_hook=hook)

GAME_FOLDER = os.environ.get('WOT_FOLDER', CONFIG.game.folder)
GAME_VERSION = os.environ.get('WOT_VERSION', CONFIG.game.version)
if CONFIG.version > 3 and CONFIG.game.force:
	GAME_FOLDER = CONFIG.game.folder
	GAME_VERSION = CONFIG.game.version

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
	<id>{author}.{id}</id>
	<!-- Package version -->
	<version>{version}</version>
	<!-- Human readable name -->
	<name>{name}</name>
	<!-- Human readable description -->
	<description>{description}</description>
</root>""".format(author=CONFIG.info.author, id=CONFIG.info.id, name=CONFIG.info.name,
					description=CONFIG.info.description, version=CONFIG.info.version)

# prepere folders
if os.path.isdir('temp'):
	shutil.rmtree('temp')
os.makedirs('temp')
if os.path.isdir('build'):
	shutil.rmtree('build')
os.makedirs('build')

# build python
build_python()

# build flash
build_flash()

# copy all staff
if os.path.isdir('resources/in'):
	copytree('resources/in', 'temp/res')
if os.path.isdir('as3/bin'):
	copytree('as3/bin', 'temp/res/gui/flash')
copytree('python', 'temp/res/scripts/client', ignore=shutil.ignore_patterns('*.py'))
with open('temp/meta.xml', 'w') as fh:
	fh.write(META)

# create package
zipFolder('temp', 'build/{}'.format(PACKAGE_NAME))

# copy package into game
if COPY_INTO_GAME:
	for exe_name in ('worldoftanks', 'tanki'):
		for proc in psutil.process_iter():
			if exe_name in proc.name().lower():
				os.kill(proc.pid, signal.SIGTERM)
				logger.info('wot client closed (pid: %s)', proc.pid)
		while process_running('%s.exe' % exe_name):
			time.sleep(.01)
	logger.info('copied into wot: %s%s', WOT_PACKAGES_DIR, PACKAGE_NAME)
	shutil.copy2('build/{}'.format(PACKAGE_NAME), WOT_PACKAGES_DIR)

# create distribution
if CREATE_DISTRIBUTE:
	os.makedirs('temp/distribute/mods/{}'.format(GAME_VERSION))
	shutil.copy2('build/{}'.format(PACKAGE_NAME), 'temp/distribute/mods/{}'.format(GAME_VERSION))
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

# start client on build finish
if RUN_GAME:
	for exe_name in ('worldoftanks', 'tanki'):
		executable_path = '%s/%s.exe' % (GAME_FOLDER, exe_name)
		if os.path.isfile(executable_path):
			subprocess.Popen([executable_path])
