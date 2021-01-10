from HLC.path_finder import PathFinder
from robot import Robot, RobotState
from puck import Puck, PuckState
import enum
import numpy as np


class Controller(PathFinder, Robot, Puck):
    def __init__(self, gridSize):
        super().__init__(gridSize)
        self.gridSize = gridSize
        self.robots = []
        self.pucks = []
        self.allocMatrix = np.zeros(self.gridSize, dtype=object)

    def calculateRobotInitialPosition(self, robotId):
        if robotId > self.gridSize[1] - 1:
            print("Map is to small to create {}'th robot. Available spaces: {}".format(robotId, self.gridSize[1]))
            return -1
        else:
            return [self.gridSize[0] - 2, robotId]

    def addRobot(self, robotId):
        self.robots.append(Robot(robotId=robotId, init_pos=self.calculateRobotInitialPosition(robotId=robotId)))

    def addPuck(self, puckId, init_pos):
        self.pucks.append(Puck(puckId=puckId, init_pos=init_pos))

    def retRobots(self):
        return self.robots

    def retPucks(self):
        return self.pucks

    @staticmethod
    def returnPosAsString(pos):
        return '[' + str(pos[0]) + ', ' + str(pos[1]) + ']'

    def generatePath(self, start_pos, stop_pos):
        return PathFinder.dijkstra(self, self.returnPosAsString(start_pos), self.returnPosAsString(stop_pos))

    def returnShortestPathToPuck(self, puck_pos):
        s_distance = (self.gridSize[0] * self.gridSize[1]) ** 2
        robot_id = None
        s_path = None
        for robot in self.robots:
            if robot.retCurrentState() == RobotState.Idling:
                path = self.generatePath(robot.retPosition(), puck_pos)
                distance = len(path)
                if distance < s_distance:
                    s_distance = distance
                    s_path = path
                    robot_id = robot.retId()
        if robot_id is None:
            return None, None, None
        else:
            return robot_id, s_distance, s_path

    def assignRobotToPuck(self, robotId, puckId):
        self.robots[robotId].setStateCarrying(puckId=puckId)
        self.pucks[puckId].setStateCarrying(robotId=robotId)

