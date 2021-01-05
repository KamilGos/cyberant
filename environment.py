import numpy as np
from tabulate import tabulate


class Map:
    def __init__(self, size):
        self.gridSize = size
        print("Grid size: ", self.gridSize)
        self.grid = np.zeros(self.gridSize, dtype=object)
        self.containerPoss = [size[0] - 2 - 1, size[1] - 1]
        self.grid[self.containerPoss[0], self.containerPoss[1]] = 'C'
        self.reservedRobotRet, self.reservedRobotInit = self.getReservedPoss()
        self.maxRobots = len(self.reservedRobotInit)

    def getReservedPoss(self):
        reservedRobotRet = []
        reservedRobotRet.append([self.gridSize[0] - 1 - 1, self.gridSize[1] - 1])
        for x in range(self.gridSize[1]):
            reservedRobotRet.append([self.gridSize[0] - 1, x])
        reservedRobotInit = []
        for x in range(self.gridSize[1] - 1):
            reservedRobotInit.append([self.gridSize[0] - 1 - 1, x])
        return reservedRobotRet, reservedRobotInit

    def getGridSize(self):
        return self.gridSize

    def showReservedPlaces(self):
        print("Robots initial places: ", self.reservedRobotInit)
        print("Robots return path: ", self.reservedRobotRet)

    def showGrid(self):
        print(tabulate(self.grid, showindex=False, tablefmt='pretty'))

    def updateGrid(self, robots, pucks):
        for place in self.reservedRobotRet:
            self.grid[place[0], place[1]] = 'x'
        for iter, place in enumerate(self.reservedRobotInit):
            self.grid[place[0], place[1]] = 'I'+str(iter)

        for robot in robots:
            robot_id = robot.retId()
            robot_pos = robot.retPosition()
            self.grid[robot_pos[0], robot_pos[1]] = 'R'+str(robot_id)

        for puck in pucks:
            puck_id = puck.retId()
            puck_pos = puck.retPosition()
            self.grid[puck_pos[0], puck_pos[1]] = 'P'+str(puck_id)




if __name__ == "__main__":
    gridSize = 4
    Map = Map([gridSize + 2, gridSize])
    Map.showReservedPlaces()
    Map.showGrid()

    robotsPossDict = {1: [0, 0], 2: [3, 0]}
    pucksPossDict = {1: [2, 2]}

    Map.updateGrid(robotsPossDict, pucksPossDict)
    Map.showGrid()
