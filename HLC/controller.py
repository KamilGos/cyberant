from HLC.path_finder import PathFinder
from robot import Robot, RobotState
from puck import Puck, PuckState
import enum
import numpy as np
import logging
from main import LOGGER_DISABLED
import time

LOG_FORMAT = '%(levelname)-10s %(name)-20s %(funcName)-20s  %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)
LOG.disabled = LOGGER_DISABLED


class Controller(PathFinder, Robot, Puck):
    def __init__(self, gridSize, container_pos):
        super().__init__(gridSize)
        self.gridSize = gridSize
        self.robots = []
        self.pucks = []
        self.allocMatrix = np.zeros(self.gridSize)
        self.allocMatrix.fill(-1)
        self.containerContent = []
        self.container_pos = container_pos

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

    def checkIfPuckIsOnPosition(self, pos):
        for puck in self.pucks:
            if puck.retPosition() == pos:
                return True
        return False

    def returnPucksAsString(self):
        for puck in self.pucks:
            print("Controller.addPuck(puckID={}, init_pos={})".format(puck.retId(), puck.retPosition()))

    @staticmethod
    def returnPosAsString(pos):
        return '[' + str(pos[0]) + ', ' + str(pos[1]) + ']'

    def generatePath(self, start_pos, stop_pos):
        return PathFinder.dijkstra(self, self.returnPosAsString(start_pos), self.returnPosAsString(stop_pos),
                                   edges=self.retEdges())

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

    def determinePathPuckContainer(self, puck_id):
        path = self.generatePath(start_pos=self.pucks[puck_id].retPosition(),
                                 stop_pos=self.container_pos)
        return path[1:len(path)]

    def determinePathRobotReturn(self, robot_id):
        path = [[self.container_pos[0] + 1, self.container_pos[1]],
                [self.container_pos[0] + 2, self.container_pos[1]]]  # add under-conteiner place two places
        for i in range(1, (self.container_pos[1] - robot_id) + 1):  # add last row path
            path.append([self.container_pos[0] + 2, self.container_pos[1] - i])
        path.append(self.robots[robot_id].retInitPos())  # add robot init possition
        return path

    def generateRobotMissionPath(self, robot_id, puck_id):
        robot_puck_path = self.determinePathRobotPuck(robot_id=robot_id, puck_id=puck_id)
        puck_cont_path = self.determinePathPuckContainer(puck_id=puck_id)
        robot_return_path = self.determinePathRobotReturn(robot_id=robot_id)
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

    def generateNewMissionAfterDeadlock(self, robot, dead_field):
        if robot.checkIfRobotCarrying():
            robot_cont_path = PathFinder.dijkstra(self, self.returnPosAsString(robot.retPosition()),
                                                  self.returnPosAsString(self.container_pos),
                                                  edges=PathFinder.removeEdge(self, remove_coord=self.returnPosAsString(
                                                      dead_field)))
            robot_return_path = self.determinePathRobotReturn(robot_id=robot.retId())
            full_path = []
            full_path.extend(robot_cont_path)
            full_path.append('drop')
            full_path.extend(robot_return_path)
            return full_path
        else:  # robot has not puck yet
            robot_puck_path = PathFinder.dijkstra(self, self.returnPosAsString(robot.retPosition()),
                                                  self.returnPosAsString(
                                                      self.pucks[robot.mission.retPuckId()].retPosition()),
                                                  edges=PathFinder.removeEdge(self, remove_coord=self.returnPosAsString(
                                                      dead_field)))
            puck_cont_path = self.determinePathPuckContainer(puck_id=robot.mission.retPuckId())
            robot_return_path = self.determinePathRobotReturn(robot_id=robot.retId())
            full_path = []
            full_path.extend(robot_puck_path)
            full_path.append('pick')
            full_path.extend(puck_cont_path)
            full_path.append('drop')
            full_path.extend(robot_return_path)
            return full_path

    # def updateAllocMatrix(self, robot_id, ):

    def updateAllocationMatrix(self):
        for robot in self.robots:
            if robot.retCurrentState() != RobotState.Idling:
                # 1. usunięcie poprzedniej pozycji jesli była zajęta czyli jesli robot wykonał już jakiś krok
                deadlock = robot.mission.checkIfHadDeadlock()
                if deadlock[0]:
                    self.allocMatrix[deadlock[1][0], deadlock[1][1]] = -1
                elif robot.mission.retCounter() == 1:  # usuniecie pozycji poczatkowej
                    previous_step = robot.retInitPos()
                    self.allocMatrix[previous_step[0], previous_step[1]] = -1
                    LOG.info("Robot " + str(robot.retId()) + " release " + str(previous_step) + " (init)")
                elif robot.mission.retCounter() > 1:  # kazdej kolejnej ze ścieżki
                    previous_step = robot.mission.retPath()[robot.mission.retCounter() - 2]
                    if (previous_step == 'pick') or (previous_step == 'drop'):
                        previous_step = robot.mission.retPath()[robot.mission.retCounter() - 3]
                    if self.allocMatrix[
                        previous_step[0], previous_step[1]] == robot.retId():  # jeśli wcześniej jej nie usunął
                        self.allocMatrix[previous_step[0], previous_step[1]] = -1
                        LOG.info("Robot " + str(robot.retId()) + " release " + str(previous_step))

        # # 2. alokacja aktualnej pozycji robota - jest tam wiec musi miec zajętą
        for robot in self.robots:
            if robot.retCurrentState() != RobotState.Idling:  # robot has active mission
                # 2. alokacja aktualnej pozycji robota - jest tam wiec musi miec zajętą
                if robot.mission.checkIfHadDeadlock()[0] == False:
                    robot_pos = robot.retPosition()
                    self.allocMatrix[robot_pos[0], robot_pos[1]] = robot.retId()
                    LOG.info("Robot " + str(robot.retId()) + " alloc " + str(robot_pos) + " (pos)")
                else:
                    robot.mission.resetDeadlock()

        # 3. alokacja miejsca na kolejny krok jeśli miejsce jest wolne
        # oznacza to tez ze robot na pewno wykona kolejny krok
        for robot in self.robots:
            if robot.retCurrentState() != RobotState.Idling:  # robot has active mission
                LOG.info("Robot " + str(robot.retId()) + " has an active mission")
                if robot.mission.retCounter() < len(robot.mission.retPath()):
                    next_step = robot.mission.retPath()[robot.mission.retCounter()]
                    if next_step != 'pick' and next_step != 'drop':
                        if self.allocMatrix[next_step[0], next_step[1]] == -1:
                            self.allocMatrix[next_step[0], next_step[1]] = robot.retId()  # reserve field for next step
                            LOG.info("Robot " + str(robot.retId()) + " alloc " + str(next_step) + " (next)")
                        else:  # robot stoi w miejscu
                            LOG.info("Robot " + str(robot.retId()) + " couldn't alloc " + str(next_step))
                            # deadlock detection
                            # jesli na polu, na które nie moge wjechać jest robot, który chce wjechać na
                            # moje pole to znaczy ze jest deadlock  |R1| <-> |R2|
                            sec_rob_id = self.allocMatrix[next_step[0], next_step[1]]
                            sec_rob_next_step = self.robots[int(sec_rob_id)].mission.retPath()[
                                self.robots[int(sec_rob_id)].mission.retCounter()]
                            if sec_rob_next_step == robot.retPosition():
                                LOG.warning("DEADLOCK: Robot " + str(robot.retId()) + " on position " + \
                                            str(robot.retPosition()) + " wants allocate " + str(next_step) + \
                                            ". AND Robot " + str(int(sec_rob_id)) + " on position " + \
                                            str(self.robots[int(sec_rob_id)].retPosition()) + \
                                            " wants allocate " + str(sec_rob_next_step))
                                # usuwanie deadlocka - wyznaczenie nowej trasy z pominięciem miejsca powodującego
                                # pojawienie się deadlocka
                                new_path = self.generateNewMissionAfterDeadlock(robot=robot, dead_field=next_step)[1:]
                                LOG.warning("DEADLOCK FIXED: Robot " + str(robot.retId()) + " has new path: " + str(new_path))
                                robot.mission.setPath(new_path)
                                robot.mission.resetCounter()
                                robot.mission.setDeadlock(dead_field=robot.retPosition())

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
                        if int(self.allocMatrix[next_step[0], next_step[1]]) != -1:
                            LOG.info("Robot " + str(robot.retId()) + " stay on " + str(robot.retPosition()) +
                                     ". Field " + str(next_step) + " is allocated for robot " +
                                     str(int(self.allocMatrix[next_step[0], next_step[1]])))
                        else:
                            LOG.info("Robot " + str(robot.retId()) + " stay on " + str(robot.retPosition()) +
                                     ". Field " + str(next_step) +
                                     " was allocated for some robot and can be use in next step")
