# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

import math
import os

import BigWorld
import Math

LANGUAGE_FILES = 'mods/poliroid.battlehits/text'
LANGUAGE_DEFAULT = 'en'
LANGUAGE_FALLBACK = ('ru', 'be', 'kk', )

BATTLE_HITS_MAIN_VIEW_ALIAS = "BattleHitsMainView"
BATTLE_HITS_PREFERENCES_POPOVER_ALIAS = "BattleHitsPreferencesPopover"

class MODEL_STYLE:
	CLEAN = 'style1'
	NICE = 'style2'
	ALL = (CLEAN, NICE)

class SETTINGS:
	PROCESS_REPLAYS = 'processReplays'
	SAVE_ONLY_SESSION = 'saveOnlySession'
	CURRENT_STYLE = 'currentStyle'
	SORTING_RULE = 'sortingRule'
	SORTING_REVERSED = 'sortingReversed'
	HITS_TO_PLAYER = 'hitsToPlayer'
	SWAP_HANGAR = 'swapHangar'

DEFAULT_SETTINGS = {
	SETTINGS.PROCESS_REPLAYS: False,
	SETTINGS.SAVE_ONLY_SESSION: True,
	SETTINGS.CURRENT_STYLE: MODEL_STYLE.CLEAN,
	SETTINGS.SORTING_RULE: 1,
	SETTINGS.SORTING_REVERSED: True,
	SETTINGS.HITS_TO_PLAYER: True,
	SETTINGS.SWAP_HANGAR: False
}

class MODEL_TYPES:
	SHELL = 'shell'
	EFFECT = 'effect'
	SPLASH = 'splash'
	RICOCHET = 'ricochet'
	DOME = 'dome'

class MODEL_NAMES:
	SHELL = ('ap', 'apcr', 'heat', 'hemodern', 'hespg', 'hespgstun')
	EFFECT = ('ricochet', 'notpenetration', 'penetration', 'critical', )
	SPLASH = ('large', 'middle', 'small', )
	RICOCHET = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14',
				'15', 'cross', )

class MODEL_PATHS:
	SHELL = 'content/battlehits/common/shells/{type}/shell.model'
	EFFECT = 'content/battlehits/{style}/effects/{type}/effect.model'
	SPLASH = 'content/battlehits/{style}/explosions/{type}/explosion.model'
	RICOCHET = 'content/battlehits/{style}/ricochets/{type}/ricochet.model'
	DOME = 'content/battlehits/common/doom/doom.model'

from external_strings_utils import unicode_from_utf8
prefsFilePath = unicode_from_utf8(BigWorld.wg_getPreferencesFilePath())[1]
SETTINGS_FILE = os.path.normpath(os.path.join(os.path.dirname(prefsFilePath), 'mods', 'battlehits', 'setting.dat'))
CACHE_FILE = os.path.normpath(os.path.join(os.path.dirname(prefsFilePath), 'mods', 'battlehits', 'cache.dat'))

SETTINGS_VERSION = 11
CACHE_VERSION = 36

try:
	import version_utils
	IS_MT_CLIENT = True
except ImportError:
	IS_MT_CLIENT = False

BATTLE_HITS_SPACE_PATH = 'spaces/battlehits_%s' % ('mt' if IS_MT_CLIENT else 'wot')

DEFAULT_HANGAR_SPACES = (
	# wot spaces
	'spaces/hangar_v3',                # default wot hangar
	'spaces/h34_lunar_ny_2025',        # lunar_ny wot hangar
	# mt spaces
	'spaces/h08_mt_hangar',            # default mt hangar
	'spaces/h10_mt_23feb_2025'         # special mt hangar
)

SCENE_OFFSET = Math.Vector3(0.0, 200.0, 0.0)

CAMERA_DEFAULTS = ((math.radians(160), -math.radians(25.0)), (math.radians(160),
				-math.radians(25.0), 10.0), (math.radians(0.001), math.radians(0.001),
				(10.0, 10.001)), (0.005, 0.005, 0.001), SCENE_OFFSET)

CAMERA_UNDER_FLOOR_OFFSET = 0.25
