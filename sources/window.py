from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sources.controller as controller
import sources.environment as environment
import logging
import time
import sys
from random import randint
import matplotlib.pyplot as plt

LOG_FORMAT = '%(levelname)-10s %(name)-20s %(funcName)-20s  %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)

LOGGER_DISABLED = False
LOG.disabled = LOGGER_DISABLED

PLOT_FIGURE = True
PRINT_CONSOLE_GRID = True

STEP_BY_STEP = False
SIMULATION_TIME = 'MAX'
PUCK_RAIN_NUM = 5

MAX_MAPSIZE_Y = 20
MAX_MAPSIZE_X = 20
MIN_MAPSIZE_Y=5
MIN_MAPSIZE_X = 3


class Algorithm():

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        print("WELCOME TO CyberAnt")

        self.robotsNumber = 8
        self.pucksNumber = 16
        self.mapSizeY = 10
        self.mapSizeX = 8

        self.Dialog = QtWidgets.QDialog()
        self.sizeSelectDialog = SizeSelectDialog()
        self.sizeSelectDialog.setupUi(self.Dialog)
        self.settingsAccepted = False
        self.sizeSelectDialog.buttonBox.accepted.connect(self.accept)
        self.Dialog.exec()
        if(not self.settingsAccepted): sys.exit()


        self.animation_running = False
        self.print_console_grid = PRINT_CONSOLE_GRID

        self.Map = environment.Map(size=[self.mapSizeY, self.mapSizeX])  # for debug with AUTO_GENERATE = False !
        self.Controller = controller.Controller(gridSize=self.Map.retGridSize(),
                                                container_pos=self.Map.retContainerPos())
        self.Window = Main_Window(self.robotsNumber, self.pucksNumber)
        self.Window.startButton.clicked.connect(self.start_clicked)
        self.Window.nextStepButton.clicked.connect(self.one_step)
        self.Window.exitButton.clicked.connect(lambda: self.Window.close())
        self.Window.addPuckButton.clicked.connect(self.add_random_puck)
        self.Window.addChosenPuckButton.clicked.connect(self.add_certain_puck)
        self.Window.timeStepSlider.valueChanged.connect(self.change_step_time)
        self.Window.puckRainButton.clicked.connect(self.puck_rain)
        self.Window.newPuckXEdit.setValidator(QIntValidator(3, self.Map.retGridSize()[1]))
        self.Window.newPuckYEdit.setValidator(QIntValidator(0, self.Map.retGridSize()[0]))
        self.Window.newPuckYEdit.setText(str(5))
        self.Window.newPuckXEdit.setText(str(5))
        self.wrong_puck_msg = QMessageBox()
        self.wrong_puck_msg.setText("You can not add a puck there! ")
        self.simulation_time = 0
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.puck_rain)
        self.timecounter = 0
        self.Window.consoleOutputCheckBox.stateChanged.connect(self.change_flags)
        # self.algorithm.new_puck_in_container.connect(self.update_progress)
        # self.pucksNumber.setProperty("value",len(self.algorithm.Controller.pucks))

        for id in range(self.robotsNumber):
            self.Controller.addRobot(robotId=id)

        for id in range(self.pucksNumber):
            while True:
                rand_pos = [randint(0, self.Map.retGridSize()[0] - 3), randint(1, self.Map.retGridSize()[1]) - 1]
                if not self.Controller.checkIfPuckIsOnPosition(rand_pos) and rand_pos != self.Map.retContainerPos():
                    break
            self.Controller.addPuck(puckId=id, init_pos=rand_pos)

        if self.print_console_grid:
            print("... Initial map ...")
            self.Map.updateGrid(
                robots=self.Controller.retRobots(),
                pucks=self.Controller.retPucks(),
                container=self.Controller.retContainerContent())
            self.Map.showGrid()

        if PLOT_FIGURE:
            self.Map.createGridWorldWindow()
            self.Map.updategridWorld(
                robots=self.Controller.retRobots(),
                pucks=self.Controller.retPucks(),
                container=self.Controller.retContainerContent())
            # creating apyqt5 application
            self.app = QApplication(sys.argv)
            # creating a window object
            print("before window show")
            self.Window.show()
            self.app.processEvents()
            sys.exit(self.app.exec_())
            # self.run_animation()
        self.Window.pucksNumber.setProperty("value", len(self.Controller.retPucks()))

    def change_flags(self):
        if self.Window.consoleOutputCheckBox.isChecked():
            LOG.disabled = False
            self.print_console_grid = True
        else:
            LOG.disabled = True
            self.print_console_grid = False

    def update_progress(self):
        # print("updating progress bar")
        self.Window.progressBar.setValue(len(self.Controller.retContainerContent()))

    def add_random_puck(self):
        while True:
            rand_pos = [randint(0, self.Map.retGridSize()[0] - 3), randint(1, self.Map.retGridSize()[1]) - 1]
            if not self.Controller.checkIfPuckIsOnPosition(rand_pos) and rand_pos != self.Map.retContainerPos():
                self.Controller.addPuck(len(self.Controller.pucks), rand_pos)
                print("found free space")
                break
        self.Map.updategridWorld(
            robots=self.Controller.retRobots(),
            pucks=self.Controller.retPucks(),
            container=self.Controller.retContainerContent())
        self.Window.plot()
        self.app.processEvents()
        self.Window.pucksNumberDisp.setProperty("value", len(self.Controller.pucks))
        self.Window.plot()
        self.Window.repaint()

    def one_step(self):
        if self.animation_running == True:
            return
        else:
            self.update_progress()
        idling_pucks, idling_pucks_ids = self.Controller.checkIdlingPucks()
        if idling_pucks is True:
            LOG.info("Idling Pucks ids:" + str(idling_pucks_ids))
        else:
            LOG.info("NO Ideling Pucks")

        idling_robots, idling_robots_ids = self.Controller.checkIdlingRobots()
        if idling_robots is True:
            LOG.info("Idling Robots ids: " + str(idling_robots_ids))
        else:
            LOG.info("No idling robots")

        '''
            przypisywanie
            '''
        # jeśli istnieją czekające pucki i istnieją wolne roboty
        if (idling_pucks is True) and (idling_robots is True):
            for puck_id in idling_pucks_ids:  # dla kazdego pucka
                if idling_robots is True:  # jesli nadal istnieje czekajacy robot
                    robot_id, distance = self.Controller.DetermineNearestRobot(robots_ids=idling_robots_ids,
                                                                               puck_id=puck_id)  # znajdz najblizszego robota
                    self.Controller.assignRobotToPuck(robot_id=robot_id, puck_id=puck_id)
                    '''
                        wyznaczanie sciezki robot-puck
                        '''
                    path = self.Controller.generateRobotMissionPath(robot_id=robot_id, puck_id=puck_id)
                    self.Controller.setRobotMission(robot_id=robot_id, puck_id=puck_id, path=path)

                    idling_robots, idling_robots_ids = self.Controller.checkIdlingRobots()
                    LOG.info("Left Idling Robots: " + str(idling_robots_ids))

        '''
            wykonywanie kroku
            '''
        self.Controller.updateAllocationMatrix()
        if self.print_console_grid:
            self.Controller.showAllocationMatrix()
            print(self.print_console_grid)

        if STEP_BY_STEP:
            inp = input("Press to do step...")
        elif self.simulation_time != 'MAX':
            time.sleep(self.simulation_time)

        self.Controller.executeOneStep()
        if self.print_console_grid:
            self.Map.updateGrid(
                robots=self.Controller.retRobots(),
                pucks=self.Controller.retPucks(),
                container=self.Controller.retContainerContent())
            self.Map.showGrid()

        if PLOT_FIGURE:
            self.Map.updategridWorld(
                robots=self.Controller.retRobots(),
                pucks=self.Controller.retPucks(),
                container=self.Controller.retContainerContent())
            self.Window.plot()
            self.app.processEvents()
        if self.print_console_grid:
            print("-" * 50)

    def change_step_time(self):
        self.simulation_time = self.Window.timeStepSlider.value() / 2

    def puck_rain(self):
        if not self.timer.isActive():
            self.timer.start()

        if self.timecounter < 5:
            self.add_random_puck()
            self.timecounter = self.timecounter + 1
        else:
            self.timer.stop()
            self.timecounter = 0

    def add_certain_puck(self):
        print(self.Window.newPuckYEdit.text())
        if self.Window.newPuckYEdit.text() != "" and self.Window.newPuckYEdit.text() != "":
            pos = [int(self.Window.newPuckYEdit.text()), int(self.Window.newPuckXEdit.text())]

            if not self.Controller.checkIfPuckIsOnPosition(pos) and pos != self.Map.retContainerPos() and \
                    pos[0] < self.Map.retGridSize()[0] - 2 and pos[1] < self.Map.retGridSize()[1]:
                self.Controller.addPuck(len(self.Controller.pucks), pos)
                self.Map.updategridWorld(
                    robots=self.Controller.retRobots(),
                    pucks=self.Controller.retPucks(),
                    container=self.Controller.retContainerContent())
                self.Window.plot()
                self.Window.plot()
                self.Window.pucksNumberDisp.setProperty("value", len(self.Controller.pucks))
                self.Window.newPuckXEdit.clear()
                self.Window.newPuckYEdit.clear()
            else:
                self.wrong_puck_msg.exec()
        else:
            msg = QMessageBox(icon=QMessageBox.Warning, text="You have to choose coordinates first!")
            msg.setInformativeText("Choose X and Y coordinate")
            msg.setWindowTitle("Error")
            retval = msg.exec_()

    def start_clicked(self):
        _translate = QtCore.QCoreApplication.translate
        if self.animation_running == False:
            self.Window.startButton.setText(_translate("MainWindow", "stop"))
            self.Window.startButton.setStyleSheet("background-color: red")
            self.animation_running = True
            self.Window.nextStepButton.setEnabled(False)
        else:
            self.Window.startButton.setText(_translate("MainWindow", "start"))
            self.Window.startButton.setStyleSheet("background-color: green")
            self.animation_running = False
            self.Window.nextStepButton.setEnabled(True)
        self.run_animation()
        self.Window.startButton.repaint()

    def run_animation(self):

        while True:
            self.update_progress()
            if self.animation_running == False:
                break
            else:
                idling_pucks, idling_pucks_ids = self.Controller.checkIdlingPucks()
                if idling_pucks is True:
                    LOG.info("Idling Pucks ids:" + str(idling_pucks_ids))
                else:
                    LOG.info("NO Ideling Pucks")

                idling_robots, idling_robots_ids = self.Controller.checkIdlingRobots()
                if idling_robots is True:
                    LOG.info("Idling Robots ids: " + str(idling_robots_ids))
                else:
                    LOG.info("No idling robots")

                '''
                    przypisywanie
                    '''
                # jeśli istnieją czekające pucki i istnieją wolne roboty
                if (idling_pucks is True) and (idling_robots is True):
                    for puck_id in idling_pucks_ids:  # dla kazdego pucka
                        if idling_robots is True:  # jesli nadal istnieje czekajacy robot
                            robot_id, distance = self.Controller.DetermineNearestRobot(robots_ids=idling_robots_ids,
                                                                                       puck_id=puck_id)  # znajdz najblizszego robota
                            self.Controller.assignRobotToPuck(robot_id=robot_id, puck_id=puck_id)
                            '''
                                wyznaczanie sciezki robot-puck
                                '''
                            path = self.Controller.generateRobotMissionPath(robot_id=robot_id, puck_id=puck_id)
                            self.Controller.setRobotMission(robot_id=robot_id, puck_id=puck_id, path=path)

                            idling_robots, idling_robots_ids = self.Controller.checkIdlingRobots()
                            LOG.info("Left Idling Robots: " + str(idling_robots_ids))

                '''
                    wykonywanie kroku
                    '''
                self.Controller.updateAllocationMatrix()
                if self.print_console_grid:
                    self.Controller.showAllocationMatrix()

                if STEP_BY_STEP:
                    inp = input("Press to do step...")
                elif self.simulation_time != 'MAX':
                    time.sleep(self.simulation_time)

                self.Controller.executeOneStep()
                if self.print_console_grid:
                    self.Map.updateGrid(
                        robots=self.Controller.retRobots(),
                        pucks=self.Controller.retPucks(),
                        container=self.Controller.retContainerContent())
                    self.Map.showGrid()

                if PLOT_FIGURE:
                    self.Map.updategridWorld(
                        robots=self.Controller.retRobots(),
                        pucks=self.Controller.retPucks(),
                        container=self.Controller.retContainerContent())
                    self.Window.plot()
                    self.app.processEvents()
                if self.print_console_grid:
                    print("-" * 50)

    def accept(self):
        self.robotsNumber = self.sizeSelectDialog.robotsNumber.value()
        self.pucksNumber = self.sizeSelectDialog.pucksNumber.value()
        self.mapSizeX = self.sizeSelectDialog.mapSizeX.value()
        self.mapSizeY = self.sizeSelectDialog.mapSizeY.value()

        if(self.robotsNumber<self.mapSizeX and self.mapSizeX>=MIN_MAPSIZE_X and self.mapSizeY>=MIN_MAPSIZE_Y and
           self.mapSizeY<=MAX_MAPSIZE_Y and self.mapSizeX<=MAX_MAPSIZE_X and self.robotsNumber>0 and self.pucksNumber<=MAX_MAPSIZE_Y*(MAX_MAPSIZE_X-2)):
            self.Dialog.close()
            self.settingsAccepted = True
        else:
            print("Error, incorrect values")
            self.showError("incorrect values")

    def showError(self, errorMsg):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(errorMsg)
        msg.exec_()


class Main_Window(QMainWindow):
    def __init__(self, robotsNumber, pucksNumber):
        super().__init__()
        self.robotsNumber=robotsNumber
        self.pucksNumber = pucksNumber
        self.setObjectName("MainWindow")
        self.resize(1405, 950)
        self.animation_started = False

        self.figure = plt.gcf()
        # this is the Canvas Widget that
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        ############### FROM DESIGNER #################
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.leftLayout = QtWidgets.QVBoxLayout()
        self.leftLayout.setObjectName("leftLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.leftLayout.addWidget(self.widget)
        self.horizontalLayout.addLayout(self.leftLayout)
        self.RightLayout = QtWidgets.QVBoxLayout()
        self.RightLayout.setObjectName("RightLayout")
        self.exitButton = QtWidgets.QPushButton(self.centralwidget)
        self.exitButton.setObjectName("exitButton")
        self.RightLayout.addWidget(self.exitButton)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.robotsNumberLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.robotsNumberLabel.setFont(font)
        self.robotsNumberLabel.setObjectName("robotsNumberLabel")
        self.horizontalLayout_4.addWidget(self.robotsNumberLabel)
        self.pucksNumberLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pucksNumberLabel.setFont(font)
        self.pucksNumberLabel.setObjectName("pucksNumberLabel")
        self.horizontalLayout_4.addWidget(self.pucksNumberLabel)
        self.RightLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.robotsNumberDisp = QtWidgets.QLCDNumber(self.centralwidget)
        self.robotsNumberDisp.setObjectName("robotsNumber")
        self.horizontalLayout_3.addWidget(self.robotsNumberDisp)
        self.pucksNumberDisp = QtWidgets.QLCDNumber(self.centralwidget)
        self.pucksNumberDisp.setProperty("value", self.pucksNumber)
        self.pucksNumberDisp.setObjectName("pucksNumber")
        self.horizontalLayout_3.addWidget(self.pucksNumberDisp)
        self.RightLayout.addLayout(self.horizontalLayout_3)
        self.addPuckButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addPuckButton.sizePolicy().hasHeightForWidth())
        self.addPuckButton.setSizePolicy(sizePolicy)
        self.addPuckButton.setObjectName("addPuckButton")
        self.RightLayout.addWidget(self.addPuckButton)
        self.puckRainButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.puckRainButton.sizePolicy().hasHeightForWidth())
        self.puckRainButton.setSizePolicy(sizePolicy)
        self.puckRainButton.setObjectName("puckRainButton")
        self.RightLayout.addWidget(self.puckRainButton)
        self.addPuckLayout = QtWidgets.QVBoxLayout()
        self.addPuckLayout.setObjectName("addPuckLayout")
        self.ButtonLayout = QtWidgets.QHBoxLayout()
        self.ButtonLayout.setObjectName("ButtonLayout")
        self.coordVLayout = QtWidgets.QVBoxLayout()
        self.coordVLayout.setObjectName("coordVLayout")
        self.yHLayout = QtWidgets.QHBoxLayout()
        self.yHLayout.setObjectName("yHLayout")
        self.NewPuckXLabel = QtWidgets.QLabel(self.centralwidget)
        self.NewPuckXLabel.setObjectName("NewPuckXLabel")
        self.yHLayout.addWidget(self.NewPuckXLabel)
        self.newPuckXEdit = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newPuckXEdit.sizePolicy().hasHeightForWidth())
        self.newPuckXEdit.setSizePolicy(sizePolicy)
        self.newPuckXEdit.setObjectName("newPuckXEdit")
        self.yHLayout.addWidget(self.newPuckXEdit)
        self.coordVLayout.addLayout(self.yHLayout)
        self.xHLayout = QtWidgets.QHBoxLayout()
        self.xHLayout.setObjectName("xHLayout")
        self.newPuckYLabel = QtWidgets.QLabel(self.centralwidget)
        self.newPuckYLabel.setObjectName("newPuckYLabel")
        self.xHLayout.addWidget(self.newPuckYLabel)
        self.newPuckYEdit = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newPuckYEdit.sizePolicy().hasHeightForWidth())
        self.newPuckYEdit.setSizePolicy(sizePolicy)
        self.newPuckYEdit.setObjectName("newPuckYEdit")
        self.xHLayout.addWidget(self.newPuckYEdit)
        self.coordVLayout.addLayout(self.xHLayout)
        self.ButtonLayout.addLayout(self.coordVLayout)
        self.addChosenPuckButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addChosenPuckButton.sizePolicy().hasHeightForWidth())
        self.addChosenPuckButton.setSizePolicy(sizePolicy)
        self.addChosenPuckButton.setObjectName("addChosenPuckButton")
        self.ButtonLayout.addWidget(self.addChosenPuckButton)
        self.addPuckLayout.addLayout(self.ButtonLayout)
        self.RightLayout.addLayout(self.addPuckLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.RightLayout.addItem(spacerItem)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.consoleOutputCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.consoleOutputCheckBox.setObjectName("consoleOutputCheckBox")
        self.horizontalLayout_5.addWidget(self.consoleOutputCheckBox)
        self.RightLayout.addLayout(self.horizontalLayout_5)
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startButton.sizePolicy().hasHeightForWidth())
        self.startButton.setSizePolicy(sizePolicy)
        self.startButton.setObjectName("startButton")
        self.RightLayout.addWidget(self.startButton)
        self.nextStepButton = QtWidgets.QPushButton(self.centralwidget)
        self.nextStepButton.setObjectName("nextStepButton")
        self.RightLayout.addWidget(self.nextStepButton)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.RightLayout.addItem(spacerItem1)
        self.timeStepSlider = QtWidgets.QSlider(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timeStepSlider.sizePolicy().hasHeightForWidth())
        self.timeStepSlider.setSizePolicy(sizePolicy)
        self.timeStepSlider.setMinimum(1)
        self.timeStepSlider.setMaximum(10)
        self.timeStepSlider.setSingleStep(1)
        self.timeStepSlider.setOrientation(QtCore.Qt.Horizontal)
        self.timeStepSlider.setObjectName("timeStepSlider")
        self.RightLayout.addWidget(self.timeStepSlider)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setStyleSheet("#ProgressBar {\n"
                                       "    border: 2px solid #2196F3;\n"
                                       "    border-radius: 5px;\n"
                                       "    background-color: #E0E0E0;\n"
                                       "}")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.RightLayout.addWidget(self.progressBar)
        self.horizontalLayout.addLayout(self.RightLayout)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 815, 21))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.consoleOutputCheckBox.setChecked(False)
        ########## END ##########

        self.startButton.setStyleSheet("background-color: green")
        self.leftLayout.addWidget(self.canvas)
        self.robotsNumberDisp.setProperty("value", self.robotsNumber)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.exitButton.setText(_translate("MainWindow", "exit app"))
        self.robotsNumberLabel.setText(_translate("MainWindow", "Number of robots:"))
        self.pucksNumberLabel.setText(_translate("MainWindow", "Number of pucks:"))
        self.puckRainButton.setText(_translate("MainWindow", "It\'s raining pucks.."))
        self.addPuckButton.setText(_translate("MainWindow", "Add random puck"))
        self.NewPuckXLabel.setText(_translate("MainWindow", "Coord X:"))
        self.newPuckYLabel.setText(_translate("MainWindow", "Coord Y:"))
        self.addChosenPuckButton.setText(_translate("MainWindow", "Add puck for chosen field"))
        self.startButton.setText(_translate("MainWindow", "start/stop"))
        self.nextStepButton.setText(_translate("MainWindow", "next step "))
        self.consoleOutputCheckBox.setText(_translate("MainWindow", "print output to console"))

    def plot(self):
        self.canvas.draw()

class SizeSelectDialog(object):

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(557, 261)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setMinimumSize(QtCore.QSize(0, 30))
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setMinimumSize(QtCore.QSize(170, 30))
        self.label_2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.robotsNumber = QtWidgets.QSpinBox(Dialog)
        self.robotsNumber.setMinimumSize(QtCore.QSize(60, 30))
        self.robotsNumber.setProperty("value", 8)
        self.robotsNumber.setObjectName("robotsNumber")
        self.horizontalLayout_3.addWidget(self.robotsNumber)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setMinimumSize(QtCore.QSize(170, 30))
        self.label_3.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.pucksNumber = QtWidgets.QSpinBox(Dialog)
        self.pucksNumber.setMinimumSize(QtCore.QSize(60, 30))
        self.pucksNumber.setProperty("value", 16)
        self.pucksNumber.setObjectName("pucksNumber")
        self.horizontalLayout_3.addWidget(self.pucksNumber)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setMinimumSize(QtCore.QSize(170, 30))
        self.label_4.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.mapSizeX = QtWidgets.QSpinBox(Dialog)
        self.mapSizeX.setMinimumSize(QtCore.QSize(60, 30))
        self.mapSizeX.setProperty("value", 10)
        self.mapSizeX.setObjectName("mapSizeX")
        self.horizontalLayout_2.addWidget(self.mapSizeX)
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setMinimumSize(QtCore.QSize(170, 30))
        self.label_5.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.mapSizeY = QtWidgets.QSpinBox(Dialog)
        self.mapSizeY.setMinimumSize(QtCore.QSize(60, 30))
        self.mapSizeY.setProperty("value", 10)
        self.mapSizeY.setObjectName("mapSizeY")
        self.horizontalLayout_2.addWidget(self.mapSizeY)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)
        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Welcome to CyberAnt \n Please select simulation parameters"))
        self.label.setFont(QtGui.QFont('Arial', 16, QtGui.QFont.Bold))
        self.label_2.setText(_translate("Dialog", "Amount of Robots"))
        self.label_2.setFont(QtGui.QFont('Arial', 10))
        self.label_3.setText(_translate("Dialog", "Initial amount of Pucks"))
        self.label_3.setFont(QtGui.QFont('Arial', 10))
        self.label_4.setText(_translate("Dialog", "Map size X"))
        self.label_4.setFont(QtGui.QFont('Arial', 10))
        self.label_5.setText(_translate("Dialog", "Map size Y"))
        self.label_5.setFont(QtGui.QFont('Arial', 10))


if __name__ == "__main__":
    import sys

    # app = QtWidgets.QApplication(sys.argv)
    # MainWindow = QtWidgets.QMainWindow()
    # ui = Ui_MainWindow()
    # ui.setupUi(MainWindow)
    # MainWindow.show()
    # sys.exit(app.exec_())
    alg = Algorithm()
