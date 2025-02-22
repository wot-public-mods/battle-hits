# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

class IHitsData(object):
	__slots__ = ()

	@property
	def dataVO(self):
		raise NotImplementedError

	@property
	def sortingVO(self):
		raise NotImplementedError

	@property
	def selectedIndex(self):
		raise NotImplementedError

	@property
	def nextItemID(self):
		raise NotImplementedError

	@property
	def prevItemID(self):
		raise NotImplementedError

	@property
	def desiredID(self):
		raise NotImplementedError

	def updateData(self):
		raise NotImplementedError

	def sort(self, row):
		raise NotImplementedError
