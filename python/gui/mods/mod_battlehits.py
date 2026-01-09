# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2026 Andrii Andrushchyshyn

__version__ = "2.3.4"

try:
	import openwg_gameface
	from gui.battlehits import *
except ImportError:
	# log to handle with sentry
	import logging
	logger = logging.getLogger()
	logger.error('\n' +
				'!!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!\n'
				'!!!\n'
				'!!!   Battle hits requires the openwg_gameface module to function.\n'
				'!!!   Without it, this and other GF UI mods will not work correctly.\n'
				'!!!   Please download and install it from: https://gitlab.com/openwg/wot.gameface/-/releases/\n'
				'!!!\n'
				'!!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!   !!!\n')
	# Kill game client
	import sys
	sys.exit()
