# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

class IVehicle(object):
	__slots__ = ()

	@property
	def compoundModel(self):
		raise NotImplementedError

	@property
	def collision(self):
		raise NotImplementedError

	@property
	def compactDescr(self):
		raise NotImplementedError

	@property
	def isWheeledTech(self):
		raise NotImplementedError

	def removeVehicle(self):
		raise NotImplementedError

	def loadVehicle(self):
		raise NotImplementedError

	def partWorldMatrix(self, partIndex):
		raise NotImplementedError
