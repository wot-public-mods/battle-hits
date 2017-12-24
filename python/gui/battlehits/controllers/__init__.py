
from gui.battlehits.events import g_eventsManager

__all__ = ('g_controllers', )

class ControllersHolder():
	
	battlesHistory = None
	battleProcessor = None
	hangarCamera = None
	hangarScene = None
	state = None
	settings = None
	
	def init(self):
		
		from gui.battlehits.controllers.BattlesHistory import BattlesHistory
		from gui.battlehits.controllers.BattleProcessor import BattleProcessor
		from gui.battlehits.controllers.HangarCamera import HangarCamera
		from gui.battlehits.controllers.HangarScene import HangarScene
		from gui.battlehits.controllers.State import State
		from gui.battlehits.controllers.Settings import Settings
		
		self.battlesHistory = BattlesHistory()
		self.battleProcessor = BattleProcessor()
		self.hangarCamera = HangarCamera()
		self.hangarScene = HangarScene()
		self.state = State()
		self.settings = Settings()

		self.battlesHistory.init()
		self.battleProcessor.init()
		self.hangarCamera.init()
		self.hangarScene.init()
		self.state.init()
		self.settings.init()

		g_eventsManager.onAppFinish += self.fini
		
	def fini(self):
		
		self.battlesHistory.fini()
		self.battleProcessor.fini()
		self.hangarCamera.fini()
		self.hangarScene.fini()
		self.state.fini()
		self.settings.fini()

		self.battlesHistory = None
		self.battleProcessor = None
		self.hangarCamera = None
		self.hangarScene = None
		self.state = None
		self.settings = None

g_controllers = ControllersHolder()
