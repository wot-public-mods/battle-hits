# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

from helpers import getClientLanguage

from ._constants import LANGUAGE_DEFAULT_UI, LANGUAGE_CODES, LANGUAGE_FILE_MASK, LANGUAGE_RU_FALLBACK
from .utils import parse_lang_fields, cache_result

__all__ = ('l10n', )

class Localization:

	def __init__(self, file_mask, codes=LANGUAGE_CODES, default=LANGUAGE_DEFAULT_UI, fallback=LANGUAGE_RU_FALLBACK):
		self.language = {}
		self.languages = {}

		for langCode in codes:
			vfs_path = file_mask % langCode
			lang_data = parse_lang_fields(vfs_path)
			if lang_data:
				self.languages[langCode] = lang_data

		client_language = getClientLanguage()
		self._client_default = 'en'
		if client_language in fallback:
			self._client_default = 'ru'

		self._file_mask = file_mask
		self._ui_default = default

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

l10n = Localization(LANGUAGE_FILE_MASK)
