
import BigWorld, os


LANGUAGE_CODES = ('ru', 'uk', 'be', 'en', 'de', 'et', 'bg', 'da', 'fi', 'fil', 'fr', 'el', 'hu', 'id', \
	'it', 'ja', 'ms', 'nl', 'no', 'pl', 'pt', 'pt_br', 'ro', 'sr', 'vi', 'zh_sg', 'zh_tw', 'hr', 'th', \
	'lv', 'lt', 'cs', 'es_ar', 'tr', 'zh_cn', 'es', 'kk', 'sv', )

LANGUAGE_FILE_PATH = 'mods/poliroid.battlehits/text/%s.yml'

DEFAULT_UI_LANGUAGE = 'ru'

BATTLE_HITS_VIEW_ALIAS = "BattleHitsLobby"

BATTLE_HITS_PREFERENCES_POPOVER_ALIAS = "BattleHitsPreferencesPopover"

DEFAULT_SETTINGS = {
	'processReplays': False,
	'saveOnlySession': True,
	'currentStyle': 'style1',
	'sortingRule': 3,
	'sortingReversed': True,
	'hitsToPlayer': True
}

wgAppDataFolder = os.path.dirname(unicode(BigWorld.wg_getPreferencesFilePath(), 'utf-8', errors='ignore'))
SETTINGS_FILE = "%s\\battlehits\\%s" % (wgAppDataFolder, 'setting.dat')
CACHE_FILE = "%s\\battlehits\\%s" % (wgAppDataFolder, 'cache.dat')

SETTINGS_VERSION = 1
CACHE_VERSION = 3

class SHELL_TYPES:
	# бронебойный
	ARMOR_PIERCING = 0 
	# подкалиберынй
	ARMOR_PIERCING_CALIBER_REDUCED = 1
	# камулятивный
	HIGHT_EXPLOSIVE_ANTI_TANK = 2
	# фугас
	HIGHT_EXPLOSIVE = 3

del wgAppDataFolder, BigWorld, os