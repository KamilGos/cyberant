import HLC.controller as controller
import environment
import puck
import robot
import logging

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)

if __name__ == "__main__":
    Map = environment.Map(size=[6, 4])
    Map.showGrid()

    Controller = controller.Controller(gridSize=Map.getGridSize())
    Controller.addRobot(robotId=0)
    Controller.addRobot(robotId=1)
    Controller.addPuck(puckId=0, init_pos=[1, 2])

    Map.updateGrid(
        robots=Controller.retRobots(),
        pucks=Controller.retPucks())
    Map.showGrid()

    print("Test dystansu: ", Controller.calculateDistance(Controller.robots[0].retPosition(), Controller.pucks[0].retPosition()))
    id, dys = Controller.returnShortestPathRobotId(Controller.pucks[0].retPosition())
    print("Test najblizszego robota: id: {}, dys: {}".format(id, dys))
