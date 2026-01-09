# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2026 Andrii Andrushchyshyn

import math
import os

import BigWorld

LANGUAGE_FILES = 'mods/poliroid.battlehits/text'
LANGUAGE_DEFAULT = 'en'
LANGUAGE_FALLBACK = ('ru', 'be', 'kk', )

BATTLE_HITS_MAIN_VIEW_ALIAS = "BattleHitsMainView"
BATTLE_HITS_PREFERENCES_POPOVER_ALIAS = "BattleHitsPreferencesPopover"
BATTLE_HITS_VIEW_HEADER = 'BattleHitsHeaderView'

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

DEFAULT_SETTINGS = {
	SETTINGS.PROCESS_REPLAYS: False,
	SETTINGS.SAVE_ONLY_SESSION: True,
	SETTINGS.CURRENT_STYLE: MODEL_STYLE.CLEAN,
	SETTINGS.SORTING_RULE: 1,
	SETTINGS.SORTING_REVERSED: True,
	SETTINGS.HITS_TO_PLAYER: True
}

class MODEL_TYPES:
	SHELL = 'shell'
	EFFECT = 'effect'
	SPLASH = 'splash'
	RICOCHET = 'ricochet'

class MODEL_NAMES:
	SHELL = ('ap', 'apcr', 'heat', 'hemodern', 'hespg', 'hespgstun', )
	EFFECT = ('ricochet', 'notpenetration', 'penetration', 'critical', )
	SPLASH = ('large', 'middle', 'small', )
	RICOCHET = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14',
				'15', 'cross', )

class MODEL_PATHS:
	SHELL = 'content/battlehits/common/shells/{type}/shell.model'
	EFFECT = 'content/battlehits/{style}/effects/{type}/effect.model'
	SPLASH = 'content/battlehits/{style}/explosions/{type}/explosion.model'
	RICOCHET = 'content/battlehits/{style}/ricochets/{type}/ricochet.model'

from external_strings_utils import unicode_from_utf8
prefsFilePath = unicode_from_utf8(BigWorld.wg_getPreferencesFilePath())[1]
SETTINGS_FILE = os.path.normpath(os.path.join(os.path.dirname(prefsFilePath), 'mods', 'battlehits', 'setting.dat'))
CACHE_FILE = os.path.normpath(os.path.join(os.path.dirname(prefsFilePath), 'mods', 'battlehits', 'cache.dat'))

SETTINGS_VERSION = 13
CACHE_VERSION = 39

CAMERA_DEFAULTS = [
	math.radians(160),
	-math.radians(25.0),
	[10.0, 10.0]
]
