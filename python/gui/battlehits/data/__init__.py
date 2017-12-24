
from gui.battlehits.events import g_eventsManager

__all__ = ('g_data', )

class DataHolder():
	
	currentBattle = None
	hits = None
	battles = None
	
	def init(self):
		
		from gui.battlehits.data.CurrentBattle import CurrentBattle
		from gui.battlehits.data.Hits import Hits
		from gui.battlehits.data.Battles import Battles
				
		self.currentBattle = CurrentBattle()
		self.hits = Hits()
		self.battles = Battles()
		
		g_eventsManager.onAppFinish += self.fini
		
	def fini(self):
		
		self.currentBattle.clean()
		self.hits.clean()
		self.battles.clean()

		self.currentBattle = None
		self.hits = None
		self.battles = None
		
g_data = DataHolder()
