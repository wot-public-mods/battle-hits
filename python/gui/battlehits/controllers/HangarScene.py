import math

import math_utils
import BigWorld
import Math
from constants import VEHICLE_HIT_EFFECT as HIT_EFFECT
from gui.battlehits._constants import (MODEL_NAMES, MODEL_PATHS, MODEL_TYPES, SETTINGS,
									SCENE_OFFSET, CAMERA_DEFAULTS)
from gui.battlehits.controllers import AbstractController
from gui.battlehits.events import g_eventsManager
from gui.Scaleform.Waiting import Waiting
from debug_utils import LOG_ERROR
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import TankPartIndexes

class HangarScene(AbstractController):

	hangarSpace = dependency.descriptor(IHangarSpace)

	def __init__(self):
		super(HangarScene, self).__init__()

		self.__forceCameraUpdate = False

		self.__models = {
			MODEL_TYPES.DOME: None,
			MODEL_TYPES.SHELL: [],
			MODEL_TYPES.EFFECT: [],
			MODEL_TYPES.SPLASH: [],
			MODEL_TYPES.RICOCHET: []
		}

		self.__motors = {
			MODEL_TYPES.SHELL: [],
			MODEL_TYPES.EFFECT: [],
			MODEL_TYPES.SPLASH: [],
			MODEL_TYPES.RICOCHET: []
		}

	def create(self):

		self.hangarSpace.onSpaceCreate -= self.create

		g_eventsManager.onChangedBattleData += self.__onBattleChanged
		g_eventsManager.onChangedHitData += self.__onHitChanged
		g_eventsManager.onSettingsChanged += self.__onSettingsChanged
		g_eventsManager.onVehicleBuilded += self.__onVehicleBuilded

		self.hangarCameraCtrl.setCameraData(*CAMERA_DEFAULTS)

		self.vehicleCtrl.initialize()

		self.__forceCameraUpdate = True

		self._assambleModels()

		self.vehicleCtrl.loadVehicle()

		g_eventsManager.showMainView()

		Waiting.hide('loadHangarSpaceVehicle')
		Waiting.hide('loadHangarSpace')

	def destroy(self):

		g_eventsManager.onChangedBattleData -= self.__onBattleChanged
		g_eventsManager.onChangedHitData -= self.__onHitChanged
		g_eventsManager.onSettingsChanged -= self.__onSettingsChanged
		g_eventsManager.onVehicleBuilded -= self.__onVehicleBuilded

		self._deleteModels()

	def processNoData(self):

		self.hangarCameraCtrl.setCameraData(*CAMERA_DEFAULTS)

		self.vehicleCtrl.removeVehicle()
		self._hideModels()

	def _assambleModels(self):

		self._deleteModels()

		currentStyle = self.settingsCtrl.get(SETTINGS.CURRENT_STYLE)
		currentSpaceID = BigWorld.camera().spaceID

		domeModel = self.__models[MODEL_TYPES.DOME] = BigWorld.Model(MODEL_PATHS.DOME)
		domeModel.position = SCENE_OFFSET
		BigWorld.addModel(domeModel, currentSpaceID)

		SHELL_SET = (self.__models[MODEL_TYPES.SHELL], self.__motors[MODEL_TYPES.SHELL],
					MODEL_NAMES.SHELL, MODEL_PATHS.SHELL)
		EFFECT_SET = (self.__models[MODEL_TYPES.EFFECT], self.__motors[MODEL_TYPES.EFFECT],
					MODEL_NAMES.EFFECT, MODEL_PATHS.EFFECT)
		SPLASH_SET = (self.__models[MODEL_TYPES.SPLASH], self.__motors[MODEL_TYPES.SPLASH],
					MODEL_NAMES.SPLASH, MODEL_PATHS.SPLASH)
		RICOCHET_SET = (self.__models[MODEL_TYPES.RICOCHET], self.__motors[MODEL_TYPES.RICOCHET],
						MODEL_NAMES.RICOCHET, MODEL_PATHS.RICOCHET)

		for models, motors, modelTypes, modelPath in SHELL_SET, EFFECT_SET, SPLASH_SET, RICOCHET_SET:
			del models[:], motors[:]
			for modelType in modelTypes:
				model = BigWorld.Model(modelPath % (currentStyle, modelType))
				motor = BigWorld.Servo(Math.Matrix())
				model.addMotor(motor)
				models.append(model)
				motors.append(motor)
				model.castsShadow = model.visible = False
				BigWorld.addModel(model, currentSpaceID)

	def _hideModels(self):

		for model in self.__models[MODEL_TYPES.SHELL] + self.__models[MODEL_TYPES.SPLASH] + \
					self.__models[MODEL_TYPES.RICOCHET] + self.__models[MODEL_TYPES.EFFECT]:
			model.visible = False

	def _deleteModels(self):
		if self.__models[MODEL_TYPES.DOME]:
			domeModel = self.__models[MODEL_TYPES.DOME]
			if domeModel in BigWorld.models():
				BigWorld.delModel(domeModel)
			self.__models[MODEL_TYPES.DOME] = None

		SHELL_SET = (self.__models[MODEL_TYPES.SHELL], self.__motors[MODEL_TYPES.SHELL])
		EFFECT_SET = (self.__models[MODEL_TYPES.EFFECT], self.__motors[MODEL_TYPES.EFFECT])
		SPLASH_SET = (self.__models[MODEL_TYPES.SPLASH], self.__motors[MODEL_TYPES.SPLASH])
		RICOCHET_SET = (self.__models[MODEL_TYPES.RICOCHET], self.__motors[MODEL_TYPES.RICOCHET])

		for models, motors in SHELL_SET, EFFECT_SET, SPLASH_SET, RICOCHET_SET:
			for model in models:
				if model in BigWorld.models():
					BigWorld.delModel(model)
			del models[:], motors[:]

	def __onBattleChanged(self):
		self._hideModels()

	def __onHitChanged(self):
		self._hideModels()

		if not self.currentBattleData.victim:
			self.hangarCameraCtrl.setCameraData(*CAMERA_DEFAULTS)
			self.vehicleCtrl.removeVehicle()
			return

		self.vehicleCtrl.loadVehicle()

	def __onSettingsChanged(self, key, _):
		if key == SETTINGS.CURRENT_STYLE:
			self._assambleModels()
			self.vehicleCtrl.loadVehicle()

	def __onVehicleBuilded(self):
		self.__updateCamera()
		self.__updateShell()
		self.__updateEffect()
		self.__updateSplash()
		self.__updateRicochet()
		self.__updateOutRicochet()

	def __updateCamera(self):

		hitData = self.currentBattleData.hit
		if not hitData:
			return

		if hitData['isExplosion']:

			fallenPoint = SCENE_OFFSET + Math.Vector3(hitData['position'])
			worldHitDirection = SCENE_OFFSET - fallenPoint

			targetPoint = fallenPoint + Math.Vector3(0.0, (SCENE_OFFSET - fallenPoint).length / 2.0, 0.0)

			# default, current, limits, sens, targetPoint
			self.hangarCameraCtrl.setCameraData(
				(math_utils.reduceToPI(worldHitDirection.yaw), -math.radians(25.0)),
				(math_utils.reduceToPI(worldHitDirection.yaw), -math.radians(25.0), 10.0),
				(None, math.radians(20.0), (5.0, 15.0)),
				(0.005, 0.005, 0.001),
				targetPoint,
				self.__forceCameraUpdate
			)
		else:

			componentIDx, _, startPoint, endPoint = hitData['points'][0]

			worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(componentIDx)

			worldStartPoint = worldComponentMatrix.applyPoint(startPoint)
			worldEndPoint = worldComponentMatrix.applyPoint(endPoint)

			worldHitDirection = worldEndPoint - worldStartPoint

			# default, current, limits, sens, targetPoint
			self.hangarCameraCtrl.setCameraData(
				(worldHitDirection.yaw, -worldHitDirection.pitch),
				(worldHitDirection.yaw + 0.2, -worldHitDirection.pitch, 4.0),
				(math.radians(35.0), math.radians(25.0), (2.9, 9.0)),
				(0.005, 0.005, 0.001),
				worldStartPoint,
				self.__forceCameraUpdate
			)

		if self.__forceCameraUpdate:
			self.__forceCameraUpdate = False

	def __updateShell(self):

		for model in self.__models[MODEL_TYPES.SHELL]:
			model.visible = False

		hitData = self.currentBattleData.hit
		if not hitData:
			return

		if hitData['isExplosion']:

			worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(TankPartIndexes.CHASSIS)

			worldHitPoint = worldComponentMatrix.applyPoint(hitData['position'])

			worldContactMatrix = Math.Matrix()
			worldContactMatrix.setRotateYPR((0.0, math.pi / 2, 0.0))
			worldContactMatrix.translation = Math.Vector3(worldHitPoint)

			self.__motors[MODEL_TYPES.SHELL][hitData['shellType']].signal = worldContactMatrix
			self.__models[MODEL_TYPES.SHELL][hitData['shellType']].visible = True

		else:

			componentIDx, _, startPoint, endPoint = hitData['points'][0]

			localStartPoint = Math.Vector3(startPoint)
			localEndPoint = Math.Vector3(endPoint)

			worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(componentIDx)

			worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
			worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)

			worldHitPoint = (worldStartPoint + worldEndPoint) / 2

			worldHitDirection = worldEndPoint - worldStartPoint

			worldContactMatrix = Math.Matrix()
			worldContactMatrix.setRotateYPR((worldHitDirection.yaw, worldHitDirection.pitch, 0.0))
			worldContactMatrix.translation = worldHitPoint

			self.__motors[MODEL_TYPES.SHELL][hitData['shellType']].signal = worldContactMatrix
			self.__models[MODEL_TYPES.SHELL][hitData['shellType']].visible = True

	def __updateEffect(self):

		for model in self.__models[MODEL_TYPES.EFFECT]:
			model.visible = False

		hitData = self.currentBattleData.hit
		if not hitData:
			return

		if not hitData['isExplosion']:

			componentIDx, shotResult, startPoint, endPoint = hitData['points'][0]

			if shotResult in [HIT_EFFECT.INTERMEDIATE_RICOCHET, HIT_EFFECT.FINAL_RICOCHET]:
				effectType = 0
			elif shotResult == HIT_EFFECT.ARMOR_NOT_PIERCED:
				effectType = 1
			elif shotResult == HIT_EFFECT.ARMOR_PIERCED:
				effectType = 2
			elif shotResult == HIT_EFFECT.ARMOR_PIERCED_DEVICE_DAMAGED:
				effectType = 2
			elif shotResult == HIT_EFFECT.CRITICAL_HIT and hitData['damageFactor'] > 0:
				effectType = 2
			elif shotResult in [HIT_EFFECT.ARMOR_PIERCED_NO_DAMAGE, HIT_EFFECT.CRITICAL_HIT]:
				effectType = 3
			else:
				LOG_ERROR('unknown effectType')

			worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(componentIDx)
			worldStartPoint = worldComponentMatrix.applyPoint(Math.Vector3(startPoint))
			worldEndPoint = worldComponentMatrix.applyPoint(Math.Vector3(endPoint))

			worldHitPoint = (worldStartPoint + worldEndPoint) / 2

			worldHitDirection = worldEndPoint - worldStartPoint

			worldContactMatrix = Math.Matrix()
			worldContactMatrix.setRotateYPR((worldHitDirection.yaw, worldHitDirection.pitch, 0.0))
			worldContactMatrix.translation = worldHitPoint

			self.__motors[MODEL_TYPES.EFFECT][effectType].signal = worldContactMatrix
			self.__models[MODEL_TYPES.EFFECT][effectType].visible = True

	def __updateSplash(self):

		for model in self.__models[MODEL_TYPES.SPLASH]:
			model.visible = False

		hitData = self.currentBattleData.hit
		if not hitData:
			return

		if hitData['isExplosion']:
			if hitData['shellSplash'] <= 6:
				splashIndex = 2
			elif hitData['shellSplash'] <= 12:
				splashIndex = 1
			else:
				splashIndex = 0

			worldContactMatrix = Math.Matrix()
			worldContactMatrix.translation = Math.Vector3(SCENE_OFFSET + Math.Vector3(hitData['position']))

			self.__motors[MODEL_TYPES.SPLASH][splashIndex].signal = worldContactMatrix
			self.__models[MODEL_TYPES.SPLASH][splashIndex].visible = True

	def __updateRicochet(self):

		for model in self.__models[MODEL_TYPES.RICOCHET]:
			model.visible = False

		hitData = self.currentBattleData.hit
		if not hitData:
			return

		if hitData['isExplosion']:
			return

		previosPointData = []

		modelsFreeIdx = range(15)

		for componentIDx, shotResult, startPoint, endPoint in hitData['points']:

			if previosPointData:

				preComponentIDx, preShotResult, preStartPoint, preEndPoint = previosPointData

				if preShotResult == HIT_EFFECT.INTERMEDIATE_RICOCHET:

					worldPreComponentMatrix = self.vehicleCtrl.partWorldMatrix(preComponentIDx)
					localPreStartPoint = Math.Vector3(preStartPoint)
					localPreEndPoint = Math.Vector3(preEndPoint)
					worldPreStartPoint = worldPreComponentMatrix.applyPoint(localPreStartPoint)
					worldPreEndPoint = worldPreComponentMatrix.applyPoint(localPreEndPoint)
					worldStartRicochetPoint = (worldPreStartPoint + worldPreEndPoint) / 2

					worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(componentIDx)
					localStartPoint = Math.Vector3(startPoint)
					localEndPoint = Math.Vector3(endPoint)
					worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
					worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)
					worldEndRicochetPoint = (worldStartPoint + worldEndPoint) / 2

					distance = (worldStartRicochetPoint - worldEndRicochetPoint).length

					worldRicochetDirection = worldStartRicochetPoint - worldEndRicochetPoint
					worldRicochetMatrix = Math.Matrix()
					worldRicochetMatrix.setRotateYPR((worldRicochetDirection.yaw, worldRicochetDirection.pitch, 0.0))
					worldRicochetMatrix.translation = worldStartRicochetPoint

					perfectIdx = int(distance * 3.2)
					targetIdx = min(modelsFreeIdx, key=lambda x: abs(x-perfectIdx))
					modelsFreeIdx.pop(targetIdx)

					self.__models[MODEL_TYPES.RICOCHET][targetIdx].visible = True
					self.__motors[MODEL_TYPES.RICOCHET][targetIdx].signal = worldRicochetMatrix

			previosPointData = componentIDx, shotResult, startPoint, endPoint

	def __updateOutRicochet(self, attemp=0):

		hitData = self.currentBattleData.hit
		if not hitData:
			return

		if hitData['isExplosion']:
			return

		componentIDx, shotResult, startPoint, endPoint = hitData['points'][-1]

		if shotResult == HIT_EFFECT.INTERMEDIATE_RICOCHET:

			localStartPoint = Math.Vector3(startPoint)
			localEndPoint = Math.Vector3(endPoint)
			localHitPoint = (localStartPoint + localEndPoint) / 2
			worldComponentMatrix = self.vehicleCtrl.partWorldMatrix(componentIDx)
			worldStartPoint = worldComponentMatrix.applyPoint(localStartPoint)
			worldEndPoint = worldComponentMatrix.applyPoint(localEndPoint)
			worldHitPoint = (worldStartPoint + worldEndPoint) / 2

			collisionResult = self.vehicleCtrl.collision.collideAllWorld(worldStartPoint, worldEndPoint)
			if not collisionResult:
				BigWorld.callback(0.01, lambda: self.__updateOutRicochet(attemp + 1))
				return

			collisionPoints = []

			for offsetVector in (0.001, 0.0, 0.0), (0.0, 0.001, 0.0), (0.0, 0.0, 0.001):
				collisionPoint = self.vehicleCtrl.collision.collideLocalPoint(componentIDx, localHitPoint + offsetVector, 10.0)
				collisionPoints.append(collisionPoint)

			if len(collisionPoints) < 3:
				return

			planeNormal = (collisionPoints[1] - collisionPoints[0]) * (collisionPoints[2] - collisionPoints[0])
			planeDistanceCoeffD = -planeNormal.dot(collisionPoints[0])
			distance = Math.Vector4(planeNormal.x, planeNormal.y, planeNormal.z, planeDistanceCoeffD).dot(Math.Vector4(
											localStartPoint.x, localStartPoint.y, localStartPoint.z, 1.0))
			# in normal case we need check for distance lower than 0
			# but we live in bagworld Kappa
			if distance > 0:
				planeNormal = -planeNormal

			_, hitAngleCos, _, _ = collisionResult[0]

			worldNormalDirection = worldComponentMatrix.applyVector(planeNormal)
			worldNormalDirection.normalise()

			doubleCathetus = hitAngleCos * (worldHitPoint - worldStartPoint).length * 2.0

			worldRicochetDirection = worldHitPoint - (worldEndPoint + worldNormalDirection.scale(-doubleCathetus))
			worldRicochetMatrix = Math.Matrix()
			worldRicochetMatrix.setRotateYPR((worldRicochetDirection.yaw, worldRicochetDirection.pitch, 0.0))
			worldRicochetMatrix.translation = worldHitPoint

			self.__models[MODEL_TYPES.RICOCHET][15].visible = True
			self.__motors[MODEL_TYPES.RICOCHET][15].signal = worldRicochetMatrix
