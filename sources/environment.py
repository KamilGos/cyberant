import numpy as np
from tabulate import tabulate
from matplotlib import pyplot as plt
import logging

logging.getLogger('matplotlib.font_manager').disabled = True


class Map:
    def __init__(self, size):
        self.gridSize = size
        print("Grid size: ", self.gridSize)
        self.grid = np.zeros(self.gridSize, dtype=object)
        self.containerPos = [size[0] - 2 - 1, size[1] - 1]
        self.grid[self.containerPos[0], self.containerPos[1]] = 'C'
        self.reservedRobotRet, self.reservedRobotInit = self.retReservedPos()
        self.maxRobots = len(self.reservedRobotInit)
        self.gridWorldFig = plt.figure(figsize=(10, 10))
        plt.ion()
        plt.draw()

    def retContainerPos(self):
        return self.containerPos

    def retReservedPos(self):
        reservedRobotRet = []
        reservedRobotRet.append([self.gridSize[0] - 1 - 1, self.gridSize[1] - 1])
        for x in range(self.gridSize[1]):
            reservedRobotRet.append([self.gridSize[0] - 1, x])
        reservedRobotInit = []
        for x in range(self.gridSize[1] - 1):
            reservedRobotInit.append([self.gridSize[0] - 1 - 1, x])
        return reservedRobotRet, reservedRobotInit

    def retGridSize(self):
        return self.gridSize

    def showReservedPlaces(self):
        print("Robots initial places: ", self.reservedRobotInit)
        print("Robots return path: ", self.reservedRobotRet)

    def showGridRaw(self):
        print(self.grid)

    def showGrid(self):
        print(tabulate(self.grid, showindex=False, tablefmt='pretty'))

    def updateGrid(self, robots, pucks, container):
        self.grid = np.zeros(self.gridSize, dtype=object)

        for place in self.reservedRobotRet:
            self.grid[place[0], place[1]] = 'x'
        for iter, place in enumerate(self.reservedRobotInit):
            self.grid[place[0], place[1]] = 'I' + str(iter)

        for puck in pucks:
            puck_id = puck.retId()
            puck_pos = puck.retPosition()
            self.grid[puck_pos[0], puck_pos[1]] = 'P' + str(puck_id)

        if len(container) > 0:
            cont_puck = ""
            for puck_id in container:
                cont_puck = cont_puck + "P" + str(puck_id)
            self.grid[self.containerPos[0], self.containerPos[1]] = cont_puck
        else:
            self.grid[self.containerPos[0], self.containerPos[1]] = 'C'

        for robot in robots:
            if robot.checkIfRobotCarrying():
                robot_id = robot.retId()
                robot_pos = robot.retPosition()
                puck_id = robot.mission.retPuckId()
                self.grid[robot_pos[0], robot_pos[1]] = 'R' + str(robot_id) + 'P' + str(puck_id)
            else:
                robot_id = robot.retId()
                robot_pos = robot.retPosition()
                self.grid[robot_pos[0], robot_pos[1]] = 'R' + str(robot_id)



    def createCoordinates(self, x, y):
        coord = [[y, self.gridSize[0] - x],
                 [y + 1, self.gridSize[0] - x],
                 [y + 1, self.gridSize[0] - x - 1],
                 [y, self.gridSize[0] - x - 1],
                 [y, self.gridSize[0] - x]]
        return zip(*coord)

    # translate coordinates - vertical flip
    def trCoords(self, y, x):
        return [x, self.gridSize[0]-y]

    def optSize(self, text):
        size = int((46 - 3*len(text))/(self.gridSize[0]*0.2))
        if size < 1:
            size = 1
        return size

    def createGridWorldWindow(self):
        # self.gridWorldFig = plt.figure(figsize=(10, 10))
        plt.ion()
        plt.draw()
        # plt.show()

    def drawGrid(self):
        # draw outline rectangle
        plt.clf()

        coord = [[0, 0], [self.gridSize[1], 0], [self.gridSize[1], self.gridSize[0]], [0, self.gridSize[0]], [0, 0]]
        xs, ys = zip(*coord)
        plt.plot(xs, ys, "black")

        # draw grid
        X, Y = np.meshgrid(range(self.gridSize[1] + 1), range(self.gridSize[0] + 1))
        plt.plot(X, Y, 'k-')
        plt.plot(X.transpose(), Y.transpose(), 'k-')

        # draw robot return path reserved fields
        for place in self.reservedRobotRet:
            xs, ys = self.createCoordinates(place[0], place[1])
            plt.fill(xs, ys, "gray", alpha=0.3)
            plt.plot(xs, ys, "black")

        # draw robot initial fields
        for iter, place in enumerate(self.reservedRobotInit):
            xs, ys = self.createCoordinates(place[0], place[1])
            plt.fill(xs, ys, "green", alpha=0.3)
            plt.plot(xs, ys, "black")
            plt.text(self.trCoords(place[0], place[1])[0] + 0.5, self.trCoords(place[0], place[1])[1] - 0.5, "I" +
                     str(iter), fontsize=self.optSize(str(iter)), horizontalalignment='center', verticalalignment='center',
                     color='black', alpha=0.1, family='monospace')

    def updategridWorld(self, robots, pucks, container):
        self.drawGrid()
        for puck in pucks:
            if puck.checkIfIdling() or puck.checkIfAssigned():
                puck_id = puck.retId()
                puck_pos = puck.retPosition()
                xs, ys = self.createCoordinates(puck_pos[0], puck_pos[1])
                plt.fill(xs, ys, "red", alpha=0.6)
                plt.plot(xs, ys, "black")
                plt.text(self.trCoords(puck_pos[0], puck_pos[1])[0] + 0.5, self.trCoords(puck_pos[0], puck_pos[1])[1] - 0.5,
                         "P" + str(puck_id), fontsize=self.optSize( "P" + str(puck_id)), horizontalalignment='center', verticalalignment='center',
                         color='black', alpha=1, family='DejaVu Sans')

        xs, ys = self.createCoordinates(self.containerPos[0], self.containerPos[1])
        plt.fill(xs, ys, "blue", alpha=0.3)
        plt.plot(xs, ys, "black")
        plt.text(self.trCoords(self.containerPos[0], self.containerPos[1])[0] + 0.5,
                 self.trCoords(self.containerPos[0], self.containerPos[1])[1] - 0.5,
                 str(len(container)), fontsize=self.optSize(str(len(container))), horizontalalignment='center', verticalalignment='center',
                 color='black', alpha=1, family='DejaVu Sans')

        for robot in robots:
            if robot.checkIfRobotCarrying():
                robot_id = robot.retId()
                robot_pos = robot.retPosition()
                puck_id = robot.mission.retPuckId()
                xs, ys = self.createCoordinates(robot_pos[0], robot_pos[1])
                plt.fill(xs, ys, "green", alpha=0.8)
                plt.plot(xs, ys, "black")
                plt.text(self.trCoords(robot_pos[0], robot_pos[1])[0] + 0.5,
                         self.trCoords(robot_pos[0], robot_pos[1])[1] - 0.5,
                         'R' + str(robot_id) + 'P' + str(puck_id), fontsize=self.optSize( 'R' + str(robot_id) + 'P' + str(puck_id)), horizontalalignment='center', verticalalignment='center',
                         color='black', alpha=1, family='DejaVu Sans')
            else:
                robot_id = robot.retId()
                robot_pos = robot.retPosition()
                xs, ys = self.createCoordinates(robot_pos[0], robot_pos[1])
                plt.fill(xs, ys, "green", alpha=0.8)
                plt.plot(xs, ys, "black")
                plt.text(self.trCoords(robot_pos[0], robot_pos[1])[0] + 0.5,
                         self.trCoords(robot_pos[0], robot_pos[1])[1] - 0.5,
                         'R' + str(robot_id), fontsize=self.optSize( 'R' + str(robot_id)), horizontalalignment='center',
                         verticalalignment='center',
                         color='black', alpha=1, family='DejaVu Sans')
        plt.draw()
        # plt.pause(0.001)


if __name__ == "__main__":
    gridSize = 4
    Map = Map([gridSize + 2, gridSize])
    Map.showReservedPlaces()
    Map.showGrid()

    robotsPosDict = {1: [0, 0], 2: [3, 0]}
    pucksPosDict = {1: [2, 2]}

    Map.updateGrid(robotsPosDict, pucksPosDict)
    Map.showGrid()
