import math
import os

import BigWorld
import Math

LANGUAGE_CODES = ('ru', 'uk', 'be', 'en', 'de', 'et', 'bg', 'da', 'fi', 'fil', 'fr', 'el', \
					'hu', 'id', 'it', 'ja', 'ms', 'nl', 'no', 'pl', 'pt', 'pt_br', 'ro', \
					'sr', 'vi', 'zh_sg', 'zh_tw', 'hr', 'th', 'lv', 'lt', 'cs', 'es_ar', \
					'tr', 'zh_cn', 'es', 'kk', 'sv', )

LANGUAGE_FILE_PATH = 'mods/poliroid.battlehits/text/%s.yml'

DEFAULT_UI_LANGUAGE = 'ru'

BATTLE_HITS_MAIN_VIEW_ALIAS = "BattleHitsMainView"
BATTLE_HITS_PREFERENCES_POPOVER_ALIAS = "BattleHitsPreferencesPopover"

class SETTINGS:
	PROCESS_REPLAYS = 'processReplays'
	SAVE_ONLY_SESSION = 'saveOnlySession'
	CURRENT_STYLE = 'currentStyle'
	SORTING_RULE = 'sortingRule'
	SORTING_REVERSED = 'sortingReversed'
	HITS_TO_PLAYER = 'hitsToPlayer'

DEFAULT_SETTINGS = { \
	SETTINGS.PROCESS_REPLAYS: False, \
	SETTINGS.SAVE_ONLY_SESSION: True, \
	SETTINGS.CURRENT_STYLE: 'style1', \
	SETTINGS.SORTING_RULE: 1, \
	SETTINGS.SORTING_REVERSED: True, \
	SETTINGS.HITS_TO_PLAYER: True \
}

class MODEL_TYPES:
	SHELL = 'shell'
	EFFECT = 'effect'
	SPLASH = 'splash'
	RICOCHET = 'ricochet'
	DOME = 'dome'

class MODEL_NAMES:
	SHELL = ('ap', 'apcr', 'heat', 'he', )
	EFFECT = ('ricochet', 'notpenetration', 'penetration', 'critical', )
	SPLASH = ('large', 'middle', 'small', )
	RICOCHET = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', \
				'15', 'cross', )

class MODEL_PATHS:
	SHELL = 'content/battlehits/%s/shells/%s/shell.model'
	EFFECT = 'content/battlehits/%s/effects/%s/effect.model'
	SPLASH = 'content/battlehits/%s/explosions/%s/explosion.model'
	RICOCHET = 'content/battlehits/%s/ricochets/%s/ricochet.model'
	DOME = 'content/battlehits/doom/doom.model'

preferencesFilePath = BigWorld.wg_getPreferencesFilePath()
wgAppDataFolder = os.path.dirname(unicode(preferencesFilePath, 'utf-8', errors='ignore'))

SETTINGS_FILE = "%s\\battlehits\\%s" % (wgAppDataFolder, 'setting.dat')
CACHE_FILE = "%s\\battlehits\\%s" % (wgAppDataFolder, 'cache.dat')

SETTINGS_VERSION = 10
CACHE_VERSION = 18

SCENE_OFFSET = Math.Vector3(0.0, 200.0, 0.0)

CAMERA_DEFAULTS = ((math.radians(160), -math.radians(25.0)), (math.radians(160), \
				-math.radians(25.0), 10.0), (math.radians(0.001), math.radians(0.001), \
				(10.0, 10.001)), (0.005, 0.005, 0.001), SCENE_OFFSET, True)

CAMERA_UNDER_FLOOR_OFFSET = 0.25

del wgAppDataFolder, preferencesFilePath, BigWorld, os, Math, math
