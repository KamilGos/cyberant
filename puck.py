import enum
import logging


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)


class PuckState(enum.Enum):
    Idling = 1
    Carrying = 2


class Puck:
    def __init__(self, puckId, init_pos):
        self.id = puckId
        self.position = init_pos
        self.state = PuckState.Idling
        self.robotId = None
        LOG.info("Added puck with ID: {} on position {}".format(self.id, self.position))

    def updatePosition(self, new):
        self.position = new

    def retPosition(self):
        return self.position

    def setStateIdling(self):
        self.state = PuckState.Idling

    def setStateCarrying(self, robotId):
        self.state = PuckState.Carrying
        self.robotId = robotId

    def retCurrentState(self):
        return self.state

    def showCurrentState(self):
        if self.state == PuckState.Idling:
            print("Puck {} in state: Idling".format(self.id))
        elif self.state == PuckState.Carrying:
            print("Puck {} in state: Carrying by robot with id: {}".format(self.id, self.robotId))

    def retId(self):
        return self.id


if __name__ == "__main__":
    puck1 = Puck( puckId=1, init_pos=[0, 1])
    print(puck1.retCurrentState())
    print(puck1.retId())
    print(puck1.retPosition())
    puck1.setStateCarrying(robotId=1)
    puck1.showCurrentState()
