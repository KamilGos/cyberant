import numpy as np
import re
from tabulate import tabulate

def stringListToList(slist):
    retlist = []
    for elem in slist:
        retlist.append([int(re.search('\[(.*),', elem).group(1)), int(re.search(',(.*)\]', elem).group(1))])
    return retlist


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

    def showReservedPlaces(self):
        print("Robots initial places: ", self.reservedRobotInit)
        print("Robots return path: ", self.reservedRobotRet)

    def showGrid(self):
        print(tabulate(self.grid, showindex=False, tablefmt='pretty'))

    def updateGrid(self, robotsPossDict, pucksPossDict):
        print("map gen")
        robotsPossitions = stringListToList(list(robotsPossDict.values()))
        for place in self.reservedRobotRet:
            if place not in robotsPossitions:
                self.grid[place[0], place[1]] = 'x'
        iter = 0
        for place in self.reservedRobotInit:
            if place not in robotsPossitions:
                self.grid[place[0], place[1]] = 'I'+str(iter)
            iter = iter + 1
        for robot in robotsPossDict.items():
            poss = stringListToList([robot[1]])
            self.grid[poss[0][0], poss[0][1]] = 'R'+str(robot[0])
        for puck in pucksPossDict.items():
            poss = stringListToList([puck[1]])
            self.grid[poss[0][0], poss[0][1]] = 'P' + str(puck[0])


if __name__ == "__main__":
    gridSize = 4
    Map = Map([gridSize + 2, gridSize])
    Map.showReservedPlaces()
    Map.showGrid()

    robotsPossDict = {1: '[0, 0]', 2: '[3, 0]'}
    pucksPossDict = {1: '[2, 2]'}

    Map.updateGrid(robotsPossDict, pucksPossDict)
    Map.showGrid()
