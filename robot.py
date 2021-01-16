import enum
import logging
from main import LOGGER_DISABLED


LOG_FORMAT = '%(levelname)-10s %(name)-20s %(funcName)-20s  %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)
LOG.disabled = LOGGER_DISABLED


class RobotState(enum.Enum):
    Idling = 1
    Moving = 2


class RobotMissionState(enum.Enum):
    Reaching = 1
    Carrying = 2
    Returning = 3


class Mission:
    def __init__(self):
        self.mission_state = None
        self.path = None
        self.counter = 0
        self.puck = None
        self.had_deadlock = [False, None]

    def checkIfHadDeadlock(self):
        return self.had_deadlock

    def setDeadlock(self, dead_field):
        self.had_deadlock = [True, dead_field]

    def resetDeadlock(self):
        self.had_deadlock = [False, None]

    def setStateReaching(self):
        self.mission_state = RobotMissionState.Reaching

    def setStateCarrying(self):
        self.mission_state = RobotMissionState.Carrying

    def setStateReturning(self):
        self.mission_state = RobotMissionState.Returning

    def setPath(self, path):
        self.path = path

    def retState(self):
        return self.mission_state

    def retPath(self):
        return self.path

    def incrementCounter(self):
        self.counter = self.counter + 1

    def resetCounter(self):
        self.counter = 0

    def retCounter(self):
        return self.counter

    def disableMission(self):
        self.mission_state = None
        self.path = None
        self.counter = 0

    def setPuck(self, puck_id):
        self.puck = puck_id

    def retPuckId(self):
        return self.puck

    def resetPuck(self):
        self.puck = None


class Robot:
    def __init__(self, robotId, init_pos):
        self.id = robotId
        self.position = init_pos
        self.initPos = init_pos
        self.state = RobotState.Idling
        self.mission = Mission()
        LOG.info("Added robot with ID: {} on position {}".format(self.id, self.position))

    def retId(self):
        return self.id

    def retInitPos(self):
        return self.initPos

    def setMission(self, new):
        self.mission = new

    def updatePosition(self, new):
        self.position = new

    def retPosition(self):
        return self.position

    def setStateIdling(self):
        self.state = RobotState.Idling

    def setStateMoving(self, puck_id):
        self.state = RobotState.Moving

    def retCurrentState(self):
        return self.state

    def showCurrentState(self):
        if self.state == RobotState.Idling:
            print("Robot {} in state: Idling".format(self.id))
        elif self.state == RobotState.Moving:
            print("Robot {} in state: Moving. Mission puck id: {} ".format(self.id, self.mission.retPuckId()))

    def checkIfRobotCarrying(self):
        return self.mission.retState() == RobotMissionState.Carrying


if __name__ == "__main__":
    robot1 = Robot(robotId=1, init_pos=1)
    print(robot1.retCurrentState())
    print(robot1.retId())
    print(robot1.retPosition())
    robot1.setStateMoving(puck_id=0)
    robot1.showCurrentState()
