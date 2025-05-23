# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

import math

import BigWorld
import Math

import math_utils
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

from .._constants import SCENE_OFFSET, CAMERA_UNDER_FLOOR_OFFSET, CAMERA_DEFAULTS
from ..controllers import AbstractController

class HangarCamera(AbstractController):

	hangarSpace = dependency.descriptor(IHangarSpace)

	def __init__(self):
		super(HangarCamera, self).__init__()
		self.enabled = False

		self.__forcedUpdate = True
		self.__offset = SCENE_OFFSET[1]
		self.__yaw = None
		self.__pitch = None
		self.__dist = None
		self.__yawLimits = None
		self.__pitchLimits = None
		self.__distLimits = None
		self.__sens = None
		self.__targetPosition = None

	def enable(self):
		if self.hangarSpace.space:
			self.enabled = True
		self.setCameraData(*CAMERA_DEFAULTS)
		self.updateCamera(0.0, 0.0, 0.0)

	def disable(self):
		self.enabled = False
		self.__forcedUpdate = True

	def setCameraData(self, default, current, lim, sens, target):

		if not self.enabled:
			return

		if not self.hangarSpace.space:
			return

		self.__yaw = current[0] + self.__offset
		self.__pitch = current[1] + self.__offset
		self.__dist = current[2] + self.__offset
		self.__yawLimits = (default[0] + self.__offset - lim[0], default[0] + self.__offset + lim[0]) if lim[0] else None
		self.__pitchLimits = (default[1] + self.__offset - lim[1], default[1] + self.__offset + lim[1]) if lim[1] else None
		self.__distLimits = (self.__offset + lim[2][0], self.__offset + lim[2][1]) if lim[2] else None
		self.__sens = sens
		self.__targetPosition = target

		self.updateCamera(0.0, 0.0, 0.0)

		camera = self._get_camera()
		if not camera:
			return

		if lim[2]:
			camera.pivotMinDist = lim[2][0]
		if camera.target:
			camera.target.setTranslate(Math.Vector3(target))
		camera.pivotPosition = Math.Vector3(0.0, 0.3, 0.0)

		# force update camera
		if self.__forcedUpdate:
			self.__forcedUpdate = False
			self.forceUpdateCamera()
			BigWorld.callback(.0, self.forceUpdateCamera)

	def forceUpdateCamera(self):
		camera = self._get_camera()
		if not camera:
			return
		self.updateCamera(0.0, 0.0, 1.0)
		camera.forceUpdate()

	def updateCamera(self, dx, dy, dz):

		if not self.enabled:
			return

		self.__yaw += dx * self.__sens[0]
		if self.__yawLimits:
			self.__yaw = math_utils.clamp(self.__yawLimits[0], self.__yawLimits[1], self.__yaw)

		self.__pitch -= dy * self.__sens[1]
		if self.__pitchLimits:
			self.__pitch = math_utils.clamp(self.__pitchLimits[0], self.__pitchLimits[1], self.__pitch)

		self.__dist -= dz * self.__sens[2]
		if self.__distLimits:
			self.__dist = math_utils.clamp(self.__distLimits[0], self.__distLimits[1], self.__dist)

		camera = self._get_camera()
		if not camera:
			return

		yaw = math_utils.reduceToPI(self.__yaw - self.__offset)
		pitch = (self.__pitch - self.__offset)
		dist = self.__dist - self.__offset

		# We do not want the camera falling under the floor
		# We cant collide floor with camera because it doesn't have collision
		# Filter pitch by target height and distance from target
		# Actual distance is used instead of the calculated distance
		# In case of a camera collide with vehicle
		#
		# Some strange shit
		if pitch > 0.0 and self.__targetPosition[1] > self.__offset:
			targetHeight = self.__targetPosition[1] - self.__offset
			currentDist = (camera.position - self.__targetPosition).length
			cameraHeightUnderFloor = (math.sin(math.pi - pitch) * currentDist) + CAMERA_UNDER_FLOOR_OFFSET
			if cameraHeightUnderFloor > targetHeight:
				pitch = (math.pi / 2) - math.acos((targetHeight - CAMERA_UNDER_FLOOR_OFFSET) / currentDist)

		# filter pitch
		pitch = math_utils.clamp(-math.pi / 2 * 0.99, math.pi / 2 * 0.99, pitch)

		cameraMatrix = Math.Matrix()
		cameraMatrix.setRotateYPR((yaw, pitch, 0.0))
		camera.source = cameraMatrix
		camera.pivotMaxDist = dist

	# We can properly work only with BigWorld.SphericalTransitionCamera
	# Sometimes camera is not a BigWorld.SphericalTransitionCamera
	# so we can properly update it
	# It can be BigWorld.CollidableTransitionCamera 
	# or BigWorld.RouteTransitionCamera 
	# or BigWorld.FreeCamera
	# in all this cases we just skip any our logic
	def _get_camera(self):
		camera = BigWorld.camera()
		if isinstance(camera, BigWorld.SphericalTransitionCamera):
			return camera
