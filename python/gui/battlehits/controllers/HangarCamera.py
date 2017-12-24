
import math
import Math

from AvatarInputHandler import mathUtils
from gui.shared.utils.HangarSpace import g_hangarSpace

from gui.battlehits._constants import CAMERA_DEFAULTS, SCENE_OFFSET

class HangarCamera(object):
	
	enabled = property(lambda self: self.__enabled)
	
	def __init__(self):
		self.__enabled = False
		self.__originalCameraData = None
		self.__offset = SCENE_OFFSET[1]
	
	def init(self): 
		pass
	
	def fini(self): 
		pass
	
	def enable(self):
		
		g_hangarSpace.onSpaceCreate -= self.enable
		
		if g_hangarSpace.space:
			
			self.__originalCameraData = g_hangarSpace.space.getCameraLocation()
			
			self.__enabled = True
			
			self.setCameraData(*CAMERA_DEFAULTS)
	
	def disable(self):
		
		if g_hangarSpace.space and self.__originalCameraData:
			g_hangarSpace.space.setCameraLocation(**self.__originalCameraData)
		
		self.__enabled = False
		self.__originalCameraData = None
	
	def setCameraData(self, default, current, limits, sens, target):
		self.__yaw = current[0] + self.__offset
		self.__pitch = current[1] + self.__offset
		self.__dist = current[2] + self.__offset
		self.__yawLimits = (default[0] + self.__offset - limits[0], default[0] + self.__offset + limits[0]) if limits[0] else None
		self.__pitchLimits = (default[1] + self.__offset - limits[1], default[1] + self.__offset + limits[1]) if limits[1] else None
		self.__distLimits = (self.__offset + limits[2][0], self.__offset + limits[2][1]) if limits[2] else None
		self.__sens = sens
		self.__targetPosition = target
		
		cam = g_hangarSpace.space.getCamera()
		if limits[2]:
			cam.pivotMinDist = limits[2][0]
		cam.target.setTranslate(target)
		cam.pivotPosition = Math.Vector3(0.0, 0.0, 0.0)
		
		self.updateCamera(0.0, 0.0, 0.0)
	
	def updateCamera(self, dx, dy, dz):
		self.__yaw += dx * self.__sens[0]
		if self.__yawLimits: self.__yaw = mathUtils.clamp(self.__yawLimits[0], self.__yawLimits[1], self.__yaw)
		
		self.__pitch -= dy * self.__sens[1]
		if self.__pitchLimits: self.__pitch = mathUtils.clamp(self.__pitchLimits[0], self.__pitchLimits[1], self.__pitch)
		
		self.__dist -= dz * self.__sens[2]
		if self.__distLimits: self.__dist = mathUtils.clamp(self.__distLimits[0], self.__distLimits[1], self.__dist)
		
		yaw, pitch, dist = mathUtils.reduceToPI(self.__yaw - self.__offset), (self.__pitch - self.__offset), self.__dist - self.__offset
		
		# we do not want the camera falling under the floor	
		# we can collide floor with camera because it doesn't have collision
		# filter pitch by target height and distance from target
		# some strange shit	
		if pitch > 0.0 and self.__targetPosition[1] > self.__offset:
			targetHeight = self.__targetPosition[1] - self.__offset
			underFloorOffset = 0.25
			cameraHeightUnderFloor = (math.sin(math.pi - pitch) * dist) + underFloorOffset
			if cameraHeightUnderFloor > targetHeight: 
				pitch = (math.pi / 2) - math.acos((targetHeight - underFloorOffset) / dist)
			
		cameraMatrix = Math.Matrix()
		cameraMatrix.setRotateYPR((yaw, pitch, 0.0))
		cam = g_hangarSpace.space.getCamera()
		cam.source = cameraMatrix
		cam.pivotMaxDist = dist
