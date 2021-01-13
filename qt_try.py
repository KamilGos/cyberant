import sys
import random
import matplotlib
from PyQt5.QtWidgets import QMainWindow

matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt

import time


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = plt.figure(num="abc", figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui_MainWindow, self).__init__(*args, **kwargs)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)

    def update_plot(self, y_data, x_data):
        # Drop off the first y element, append a new one.
        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(x_data, y_data, 'r')
        # Trigger the canvas to update and redraw.
        self.canvas.draw()




class Algorithm(Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        n_data = 50
        self.xdata = list(range(n_data))
        self.ydata = [random.randint(0, 10) for i in range(n_data)]

        self.update_plot(y_data=self.ydata, x_data=self.xdata)
        # self.run()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.run)
        self.timer.start()

    def run(self):
        self.ydata = self.ydata[1:] + [random.randint(0, 10)]
        self.update_plot(y_data=self.ydata, x_data=self.xdata)
        print("ok")




app = QtWidgets.QApplication(sys.argv)
w = Algorithm()
w.show()
app.exec_(app.exec_())