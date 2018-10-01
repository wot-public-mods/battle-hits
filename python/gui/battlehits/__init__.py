
__author__ = "Andruschyshyn Andrey"
__copyright__ = "Copyright 2018, Wargaming"
__credits__ = ["Andruschyshyn Andrey"]
__license__ = "CC BY-NC-SA 4.0"
__version__ = "1.2.8"
__maintainer__ = "Andruschyshyn Andrey"
__email__ = "prn.a_andruschyshyn@wargaming.net"
__status__ = "Production"

from gui.battlehits.events import *
from gui.battlehits.controllers import *
from gui.battlehits.data import *
from gui.battlehits.hooks import *
from gui.battlehits.views import *

g_controllers.init()
g_data.init()
