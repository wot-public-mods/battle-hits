import math
import os

import BigWorld
import Math

LANGUAGE_CODES = ('ru', 'uk', 'be', 'en', 'de', 'et', 'bg', 'da', 'fi', 'fil', 'fr', 'el',
					'hu', 'id', 'it', 'ja', 'ms', 'nl', 'no', 'pl', 'pt', 'pt_br', 'ro',
					'sr', 'vi', 'zh_sg', 'zh_tw', 'hr', 'th', 'lv', 'lt', 'cs', 'es_ar',
					'tr', 'zh_cn', 'es', 'kk', 'sv', )

LANGUAGE_FILE_MASK = 'mods/poliroid.battlehits/text/%s.yml'

DEFAULT_UI_LANGUAGE = 'ru'

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
CACHE_VERSION = 35

BATTLE_HITS_SPACE_PATH = 'spaces/battlehits'
BATTLE_ROYALE_SPACE_PATH = 'spaces/h33_battle_royale_2021'
DEFAULT_HANGAR_SPACES = ('spaces/hangar_v3', 'spaces/hangar_v3_poster_2020', 'spaces/h34_lunar_ny_2022',
	'spaces/hangar_v3_rts', 'spaces/h33_hangar_v3_wt_2021', 'spaces/hangar_v3_hw22', 'spaces/h30_newyear_2023',
	'spaces/h01_victory_day_2023', 'spaces/h02_tmday_2015', 'spaces/h04_remday_2015', )

SCENE_OFFSET = Math.Vector3(0.0, 200.0, 0.0)

CAMERA_DEFAULTS = ((math.radians(160), -math.radians(25.0)), (math.radians(160),
				-math.radians(25.0), 10.0), (math.radians(0.001), math.radians(0.001),
				(10.0, 10.001)), (0.005, 0.005, 0.001), SCENE_OFFSET)

CAMERA_UNDER_FLOOR_OFFSET = 0.25
