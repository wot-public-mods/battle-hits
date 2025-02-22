# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

class ISettings(object):
	__slots__ = ()

	def get(self, name, defaultValue=None):
		raise NotImplementedError

	def apply(self, data):
		raise NotImplementedError
