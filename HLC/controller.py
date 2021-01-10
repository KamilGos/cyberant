from HLC.path_finder import PathFinder
from robot import Robot, RobotState
from puck import Puck, PuckState
import enum
import numpy as np
import logging

LOG_FORMAT = '%(levelname)-10s %(name)-20s %(funcName)-20s  %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)


class Controller(PathFinder, Robot, Puck):
    def __init__(self, gridSize):
        super().__init__(gridSize)
        self.gridSize = gridSize
        self.robots = []
        self.pucks = []
        self.allocMatrix = np.zeros(self.gridSize)
        self.allocMatrix.fill(-1)
        self.containerContent = []

    def addPuckToContainer(self, puck_id):
        self.containerContent.append(puck_id)

    def retContainerContent(self):
        return self.containerContent

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

    def DetermineNearestRobot(self, robots_ids, puck_id):
        s_distance = (self.gridSize[0] * self.gridSize[1]) ** 2
        s_robot_id = None

        for rob_id in robots_ids:
            path = self.generatePath(self.robots[rob_id].retPosition(), self.pucks[puck_id].retPosition())
            distance = len(path)
            if distance < s_distance:
                s_distance = distance
                s_robot_id = rob_id

        return s_robot_id, s_distance

    def assignRobotToPuck(self, robot_id, puck_id):
        self.robots[robot_id].setStateMoving(puck_id=puck_id)
        self.robots[robot_id].mission.setPuck(puck_id=puck_id)
        self.pucks[puck_id].setStateCarrying(robot_id=robot_id)
        LOG.info("Assigned Puck " + str(puck_id) + " to Robot " + str(robot_id))

    def checkIdlingRobots(self):
        idling_robots = []
        for robot in self.robots:
            if robot.retCurrentState() == RobotState.Idling:
                idling_robots.append(robot.retId())
        if len(idling_robots) > 0:
            return True, idling_robots
        else:
            return False, None

    def checkIdlingPucks(self):
        idling_pucks = []
        for puck in self.pucks:
            if puck.retCurrentState() == PuckState.Idling:
                idling_pucks.append(puck.retId())
        if len(idling_pucks) > 0:
            return True, idling_pucks
        else:
            return False, None

    def determinePathRobotPuck(self, robot_id, puck_id):
        path = self.generatePath(start_pos=self.robots[robot_id].retPosition(),
                                 stop_pos=self.pucks[puck_id].retPosition())
        return path[1:len(path)]

    def determinePathPuckContainer(self, puck_id, container_pos):
        path = self.generatePath(start_pos=self.pucks[puck_id].retPosition(),
                                 stop_pos=container_pos)
        return path[1:len(path)]

    def determinePathRobotReturn(self, robot_id, container_pos):
        path = [[container_pos[0] + 1, container_pos[1]],
                [container_pos[0] + 2, container_pos[1]]]  # add under-conteiner place two places
        for i in range(1, (container_pos[1] - robot_id) + 1):  # add last row path
            path.append([container_pos[0] + 2, container_pos[1] - i])
        path.append(self.robots[robot_id].retInitPos())  # add robot init possition
        return path

    def generateRobotMissionPath(self, robot_id, puck_id, container_pos):
        robot_puck_path = self.determinePathRobotPuck(robot_id=robot_id, puck_id=puck_id)
        puck_cont_path = self.determinePathPuckContainer(puck_id=puck_id, container_pos=container_pos)
        robot_return_path = self.determinePathRobotReturn(robot_id=robot_id, container_pos=container_pos)
        full_path = []
        full_path.extend(robot_puck_path)
        full_path.append('pick')
        full_path.extend(puck_cont_path)
        full_path.append('drop')
        full_path.extend(robot_return_path)
        return full_path

    def setRobotMission(self, robot_id, puck_id, path):
        LOG.info("Robot " + str(robot_id) + " mission set as: " + str(path))
        self.robots[robot_id].mission.setPuck(puck_id=puck_id)
        self.robots[robot_id].mission.setStateReaching()
        self.robots[robot_id].mission.setPath(path=path)
        self.robots[robot_id].mission.resetCounter()
        self.pucks[puck_id].setStateAssigned(robot_id=robot_id)

    def showAllocationMatrix(self):
        print(self.allocMatrix)

    # def updateAllocMatrix(self, robot_id, ):

    def updateAllocationMatrix(self):
        for robot in self.robots:
            if robot.retCurrentState() != RobotState.Idling: # robot has active mission
                LOG.info("Robot " + str(robot.retId()) + " has an active mission")

                # 1. usunięcie poprzedniej pozycji jesli była zajęta czyli jesli robot wykonał już jakiś krok
                if robot.mission.retCounter() == 1:
                    previous_step = robot.retInitPos()
                    self.allocMatrix[previous_step[0], previous_step[1]] = -1
                    LOG.info("Robot " + str(robot.retId()) + " release " + str(previous_step) + " (init)")
                elif robot.mission.retCounter() > 1:
                    previous_step = robot.mission.retPath()[robot.mission.retCounter() - 2]
                    if (previous_step == 'pick') or (previous_step == 'drop'):
                        previous_step = robot.mission.retPath()[robot.mission.retCounter() - 3]
                    self.allocMatrix[previous_step[0], previous_step[1]] = -1
                    LOG.info("Robot " + str(robot.retId()) + " release " + str(previous_step))

                # 2. alokacja aktualnej pozycji robota - jest tam wiec musi miec zajętą
                robot_pos = robot.retPosition()
                self.allocMatrix[robot_pos[0], robot_pos[1]] = robot.retId()
                LOG.info("Robot " + str(robot.retId()) + " alloc " + str(robot_pos) + " (pos)")

                # 3. alokacja miejsca na kolejny krok jeśli miejsce jest wolne
                # oznacza to tez ze robot na pewno wykona kolejny krok
                if robot.mission.retCounter() < len(robot.mission.retPath()):
                    next_step = robot.mission.retPath()[robot.mission.retCounter()]
                    if next_step != 'pick' and next_step != 'drop':
                        if self.allocMatrix[next_step[0], next_step[1]] == -1:
                            self.allocMatrix[next_step[0], next_step[1]] = robot.retId()  # reserve field for next step
                            LOG.info("Robot " + str(robot.retId()) + " alloc " + str(next_step) + " (next)")
                        else:  # robot stoi w miejscu
                            LOG.info("Robot " + str(robot.retId()) + " couldn't alloc " + str(next_step))

                # 4. robot zakończył misję. Wyczyszczenie misji oraz robot w stan idling
                else:
                    robot.mission.disableMission()
                    robot.setStateIdling()
                    LOG.info("Robot " + str(robot.retId()) + " finished mission...")

    def executeOneStep(self):
        # jeśli kolejne pole nalezy do robota to może on wykonac ruch

        for robot in self.robots:
            if robot.retCurrentState() != RobotState.Idling:  # robot has active mission
                next_step = robot.mission.retPath()[robot.mission.retCounter()]

                # 1. jeśli kolejny krok to zabranie pucka
                if next_step == 'pick':
                    robot.mission.setStateCarrying()
                    self.pucks[robot.mission.retPuckId()].setStateCarrying(robot_id=robot.retId())
                    robot.mission.incrementCounter()
                    LOG.info("Robot " + str(robot.retId()) + " increment counter to " + str(robot.mission.retCounter()))
                    LOG.info("Robot " + str(robot.retId()) + " picked up puck " + str(robot.mission.retPuckId()))

                # 2. jeśli kolejny krok to odłożenie pucka do kontenera
                elif next_step == 'drop':
                    robot.mission.setStateReturning()
                    self.pucks[robot.mission.retPuckId()].setStateDelivered()
                    self.addPuckToContainer(puck_id=robot.mission.retPuckId())
                    robot.mission.incrementCounter()
                    LOG.info("Robot " + str(robot.retId()) + " increment counter to " + str(robot.mission.retCounter()))
                    LOG.info("Robot " + str(robot.retId()) + " delivered puck " + str(robot.mission.retPuckId()) +
                             ' to container')

                # 3. jeśli kolejny krok to ruch
                if next_step != 'pick' and next_step != 'drop':
                    # jeśli kolejne pole nalezy do robota to moze się ruszyć
                    if self.allocMatrix[next_step[0], next_step[1]] == robot.retId():
                        robot.updatePosition(new=next_step)
                        # jesli robot ma pucka to aktualizuj pozycję pucka
                        if robot.checkIfRobotCarrying() is True:
                            self.pucks[robot.mission.retPuckId()].updatePosition(new=next_step)
                            LOG.info("Robot " + str(robot.retId()) + " and puck " + str(robot.mission.retPuckId()) +
                                     " moved to " + str(robot.retPosition()))
                        else:
                            LOG.info("Robot " + str(robot.retId()) + " moved to " + str(robot.retPosition()))
                        robot.mission.incrementCounter()
                        LOG.info("Robot " + str(robot.retId()) + " increment counter to " +
                                 str(robot.mission.retCounter()))


                    else:  # robot stoi w miejscu
                        LOG.info("Robot " + str(robot.retId()) + " stay on " + str(robot.retPosition()) +
                                 ". Field " + str(next_step) + " is allocated for robot " +
                                 str(int(self.allocMatrix[next_step[0], next_step[1]])))












