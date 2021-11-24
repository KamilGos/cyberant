import enum
import logging

LOG_FORMAT = '%(levelname)-10s %(name)-20s %(funcName)-20s  %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)

class PuckState(enum.Enum):
    Idling = 1
    Assigned = 2
    Carrying = 3
    Delivered = 4


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

    def setStateAssigned(self, robot_id):
        self.state = PuckState.Assigned
        self.robotId = robot_id

    def setStateCarrying(self, robot_id):
        self.state = PuckState.Carrying
        self.robotId = robot_id

    def setStateDelivered(self):
        self.state = PuckState.Delivered

    def retCurrentState(self):
        return self.state

    def showCurrentState(self):
        if self.state == PuckState.Idling:
            print("Puck {} in state: Idling".format(self.id))
        elif self.state == PuckState.Carrying:
            print("Puck {} in state: Carrying by robot with id: {}".format(self.id, self.robotId))

    def retId(self):
        return self.id

    def checkIfIdling(self):
        return self.state == PuckState.Idling

    def checkIfAssigned(self):
        return self.state == PuckState.Assigned

if __name__ == "__main__":
    puck1 = Puck( puckId=1, init_pos=[0, 1])
    print(puck1.retCurrentState())
    print(puck1.retId())
    print(puck1.retPosition())
    puck1.setStateCarrying(robotId=1)
    puck1.showCurrentState()
