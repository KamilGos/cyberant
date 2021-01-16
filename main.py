# import HLC.HLC.controller as HLC.controller
import sys

from PyQt5.QtWidgets import QApplication

import HLC.controller
import environment
import logging
import time
from random import randint
from window import Algorithm
LOG_FORMAT = '%(levelname)-10s %(name)-20s %(funcName)-20s  %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)

LOGGER_DISABLED = False
LOG.disabled = LOGGER_DISABLED

PLOT_FIGURE = True
PRINT_CONSOLE_GRID = True

AUTO_GENERATE = True
STEP_BY_STEP = False
# SIMULATION_TIME = 0.1  # sec per step
SIMULATION_TIME = 'MAX'
ROBOTS_NUM = 7
PUCKS_NUM = 30

if __name__ == "__main__":
    app = QApplication(sys.argv)
    al = Algorithm()
