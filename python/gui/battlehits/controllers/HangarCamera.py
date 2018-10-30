
import BigWorld
import math
import Math

from AvatarInputHandler import mathUtils
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

from gui.battlehits._constants import SCENE_OFFSET, CAMERA_UNDER_FLOOR_OFFSET
from gui.battlehits.controllers import IController

class HangarCamera(IController):
	
	hangarSpace = dependency.descriptor(IHangarSpace)
	
	def __init__(self):
		super(HangarCamera, self).__init__()
		self.__originalCameraData = None
		self.__offset = SCENE_OFFSET[1]
	
	def enable(self):
		self.hangarSpace.onSpaceCreate -= self.enable
		if self.hangarSpace.space:
			self.__originalCameraData = self.hangarSpace.space.getCameraLocation()
			self.enabled = True
		
		self.updateCamera(0.0, 0.0, 100.0)
	
	def disable(self):
		
		if self.hangarSpace.space and self.__originalCameraData:
			manager = self.hangarSpace.space._ClientHangarSpace__cameraManager
			if manager:
				del self.__originalCameraData['pivotDist']
				manager.setCameraLocation(**self.__originalCameraData)

		self.enabled = False
		self.__originalCameraData = None
	
	def setCameraData(self, default, current, limits, sens, target, forceUpdate = False):
		self.__yaw = current[0] + self.__offset
		self.__pitch = current[1] + self.__offset
		self.__dist = current[2] + self.__offset
		self.__yawLimits = (default[0] + self.__offset - limits[0], default[0] + self.__offset + limits[0]) if limits[0] else None
		self.__pitchLimits = (default[1] + self.__offset - limits[1], default[1] + self.__offset + limits[1]) if limits[1] else None
		self.__distLimits = (self.__offset + limits[2][0], self.__offset + limits[2][1]) if limits[2] else None
		self.__sens = sens
		self.__targetPosition = target
		
		self.updateCamera(0.0, 0.0, 0.0)
		
		cam = self.hangarSpace.space.camera
		if limits[2]:
			cam.pivotMinDist = limits[2][0]
		cam.target.setTranslate(Math.Vector3(target))
		cam.pivotPosition = Math.Vector3(0.0, 0.0, 0.0)
		
		# force update camera
		if forceUpdate:
			cam.forceUpdate()
	
	def updateCamera(self, dx, dy, dz):
		self.__yaw += dx * self.__sens[0]
		if self.__yawLimits: self.__yaw = mathUtils.clamp(self.__yawLimits[0], self.__yawLimits[1], self.__yaw)
		
		self.__pitch -= dy * self.__sens[1]
		if self.__pitchLimits: self.__pitch = mathUtils.clamp(self.__pitchLimits[0], self.__pitchLimits[1], self.__pitch)
		
		self.__dist -= dz * self.__sens[2]
		if self.__distLimits: self.__dist = mathUtils.clamp(self.__distLimits[0], self.__distLimits[1], self.__dist)
		
		camera = self.hangarSpace.space.camera
		yaw, pitch, dist = mathUtils.reduceToPI(self.__yaw - self.__offset), (self.__pitch - self.__offset), self.__dist - self.__offset
		
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
		pitch = mathUtils.clamp(-math.pi / 2 * 0.99, math.pi / 2 * 0.99, pitch)
		
		cameraMatrix = Math.Matrix()
		cameraMatrix.setRotateYPR((yaw, pitch, 0.0))
		camera.source = cameraMatrix
		camera.pivotMaxDist = dist
