import numpy as np
from tabulate import tabulate
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib import patches

class Map:
    def __init__(self, size):
        self.gridSize = size
        print("Grid size: ", self.gridSize)
        self.grid = np.zeros(self.gridSize, dtype=object)
        self.containerPos = [size[0] - 2 - 1, size[1] - 1]
        self.grid[self.containerPos[0], self.containerPos[1]] = 'C'
        self.reservedRobotRet, self.reservedRobotInit = self.retReservedPos()
        self.maxRobots = len(self.reservedRobotInit)

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

    def updateGrid(self, robots, pucks):
        for place in self.reservedRobotRet:
            self.grid[place[0], place[1]] = 'x'
        for iter, place in enumerate(self.reservedRobotInit):
            self.grid[place[0], place[1]] = 'I' + str(iter)

        for robot in robots:
            robot_id = robot.retId()
            robot_pos = robot.retPosition()
            self.grid[robot_pos[0], robot_pos[1]] = 'R' + str(robot_id)

        for puck in pucks:
            puck_id = puck.retId()
            puck_pos = puck.retPosition()
            self.grid[puck_pos[0], puck_pos[1]] = 'P' + str(puck_id)

    def retGridForFigure(self, robots, pucks):
        fg_grid = np.zeros(self.gridSize)
        fg_grid[self.containerPos[0], self.containerPos[1]] = 1

        for place in self.reservedRobotRet:
            fg_grid[place[0], place[1]] = 2
        for iter, place in enumerate(self.reservedRobotInit):
            fg_grid[place[0], place[1]] = 3

        for robot in robots:
            robot_id = robot.retId()
            robot_pos = robot.retPosition()
            fg_grid[robot_pos[0], robot_pos[1]] = 4

        for puck in pucks:
            puck_id = puck.retId()
            puck_pos = puck.retPosition()
            fg_grid[puck_pos[0], puck_pos[1]] = 5
        return fg_grid

    @staticmethod
    def updateFigure(grid):
        # 0 - nothing
        # 1 - container
        # 2 - robot ret
        # 3 - robot init
        # 4 - robots
        # 5  - pucks
        cols = colors.ListedColormap(['w', 'g', 'tab:gray', 'tab:orange', 'red', 'k'])
        plt.imshow(grid, cmap=cols)
        plt.pause(0.05)


    def createFigure(self):
        plt.figure(figsize=self.gridSize)
        plt.legend(loc=(1.4, 1))
        plt.legend(handles=[patches.Patch(color='w', label='nothing'),
                            patches.Patch(color='g', label='container'),
                            patches.Patch(color='tab:gray', label='return'),
                            patches.Patch(color='tab:orange', label='init'),
                            patches.Patch(color='red', label='robots'),
                            patches.Patch(color='k', label='pucks')])



if __name__ == "__main__":
    gridSize = 4
    Map = Map([gridSize + 2, gridSize])
    Map.showReservedPlaces()
    Map.showGrid()

    robotsPosDict = {1: [0, 0], 2: [3, 0]}
    pucksPosDict = {1: [2, 2]}

    Map.updateGrid(robotsPosDict, pucksPosDict)
    Map.showGrid()
