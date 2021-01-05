import enum
import logging

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)


class RobotState(enum.Enum):
    Idling = 1
    Moving = 2
    Carrying = 3
    Returning = 4


class Robot:
    def __init__(self, robotId, init_pos):
        self.id = robotId
        self.position = init_pos
        self.state = RobotState.Idling
        self.mission = None
        self.puckId = None
        LOG.info("Added robot with ID: {} on position {}".format(self.id, self.position))

    def retId(self):
        return self.id

    def setMission(self, new):
        self.mission = new

    def updatePosition(self, new):
        self.position = new

    def retPosition(self):
        return self.position

    def setStateIdling(self):
        self.state = RobotState.Idling

    def setStateMoving(self):
        self.state = RobotState.Moving

    def setStateCarrying(self, puckId):
        self.state = RobotState.Carrying
        self.puckId = puckId

    def retCurrentState(self):
        return self.state

    def showCurrentState(self):
        if self.state == RobotState.Idling:
            print("Robot {} in state: Idling".format(self.id))
        elif self.state == RobotState.Moving:
            print("Robot {} in state: Moving".format(self.id))
        elif self.state == RobotState.Returning:
            print("Robot {} in state: Returning".format(self.id))
        elif self.state == RobotState.Carrying:
            print("Robot {} in state: Carrying puck with id: {}".format(self.id, self.puckId))


if __name__ == "__main__":
    robot1 = Robot(robotId=1, init_pos=1)
    print(robot1.retCurrentState())
    print(robot1.retId())
    print(robot1.retPosition())
    robot1.setStateCarrying(puckId=1)
    robot1.showCurrentState()
