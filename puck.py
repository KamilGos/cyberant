import enum


class PuckState(enum.Enum):
    Idling = 1
    Carrying = 2


class Puck:
    def __init__(self, init_pos, puckId):
        self.id = puckId
        self.position = init_pos
        self.state = PuckState.Idling
        self.robotId = None

    def updatePossition(self, new):
        self.position = new

    def getPossition(self):
        return self.position

    def setStateIdling(self):
        self.state = PuckState.Idling

    def setStateCarrying(self, robotId):
        self.state = PuckState.Carrying
        self.robotId = robotId

    def getCurrentState(self):
        return self.state

    def showCurrentState(self):
        if self.state == PuckState.Idling:
            print("Puck {} in state: Idling".format(self.id))
        elif self.state == PuckState.Carrying:
            print("Puck {} in state: Carrying by robot with id: {}".format(self.id, self.robotId))

    def getId(self):
        return self.id


if __name__=="__main__":
    puck1 = Puck(init_pos=[0, 1], puckId=1)
    print(puck1.getCurrentState())
    print(puck1.getId())
    print(puck1.getPossition())
    puck1.setStateCarrying(robotId=1)
    puck1.showCurrentState()


