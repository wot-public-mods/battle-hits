# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

class IHangarScene(object):
	__slots__ = ()

	def create(self):
		raise NotImplementedError

	def destroy(self):
		raise NotImplementedError

	def processNoData(self):
		raise NotImplementedError
