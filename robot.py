import enum


class RobotState(enum.Enum):
    Idling = 1
    Moving = 2
    Carrying = 3
    Returning = 4


class Robot:
    def __init__(self, init_palce, robotId):
        self.id = robotId
        self.place = init_palce
        self.position = None # dokonczyć !!!! 
        self.state = RobotState.Idling
        self.mission = None
        self.puckId = None

    def getId(self):
        return self.id

    def setMission(self, new):
        self.mission = new

    def updatePossition(self, new):
        self.position = new

    def getPossition(self):
        return self.position

    def setStateIdling(self):
        self.state = RobotState.Idling

    def setStateMoving(self):
        self.state = RobotState.Moving

    def setStateCarrying(self, puckId):
        self.state = RobotState.Carrying
        self.puckId = puckId

    def getCurrentState(self):
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


if __name__=="__main__":
    robot1 = Robot(init_palce=1, robotId=1)
    print(robot1.getCurrentState())
    print(robot1.getId())
    print(robot1.getPossition())
    robot1.setStateCarrying(puckId=1)
    robot1.showCurrentState()


