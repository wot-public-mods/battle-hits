# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

from helpers import getClientLanguage

from ._constants import LANGUAGE_DEFAULT, LANGUAGE_FALLBACK, LANGUAGE_FILES
from .utils import parse_localization_file, vfs_dir_list_files, cache_result

__all__ = ('l10n', )

class Localization:

	def __init__(self, locale_folder, default=LANGUAGE_DEFAULT, fallback=LANGUAGE_FALLBACK):

		# all available languages
		self.languages = {}
		for file_name in vfs_dir_list_files(locale_folder):
			if not file_name.endswith('.yml'):
				continue
			file_path = '%s/%s' % (locale_folder, file_name)
			lang_data = parse_localization_file(file_path)
			if lang_data:
				lang_code = file_name.replace('.yml', '')
				self.languages[lang_code] = lang_data

		# default language
		self._ui_default = default

		# client language (with fallback)
		client_language = getClientLanguage()
		self._client_default = default
		if client_language in fallback:
			self._client_default = fallback[0]

		# use most suitable language
		self.language = {}
		if client_language in self.languages.keys():
			self.language = self.languages[client_language]
		elif self._client_default in self.languages.keys():
			self.language = self.languages[self._client_default]
		else:
			self.language = self.languages[self._ui_default]

	@cache_result
	def __call__(self, locale_key):
		if locale_key in self.language:
			return self.language[locale_key]
		elif locale_key in self.languages[self._client_default]:
			return self.languages[self._client_default][locale_key]
		elif locale_key in self.languages[self._ui_default]:
			return self.languages[self._ui_default][locale_key]
		return locale_key

	@cache_result
	def get_sentences(self):
		result = {}
		for k, v in self.languages[self._ui_default].items():
			result[k] = v
		for k, v in self.languages[self._client_default].items():
			result[k] = v
		for k, v in self.language.items():
			result[k] = v
		return result

l10n = Localization(LANGUAGE_FILES)
