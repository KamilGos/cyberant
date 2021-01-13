import HLC.controller
import environment
import logging
import time
from random import randint

LOG_FORMAT = '%(levelname)-10s %(name)-20s %(funcName)-20s  %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)

LOGGER_DISABLED = False
LOG.disabled = LOGGER_DISABLED

PLOT_FIGURE = True
PRINT_CONSOLE_GRID = False

AUTO_GENERATE = True
STEP_BY_STEP = False
# SIMULATION_TIME = 0.1  # sec per step
SIMULATION_TIME = 'MAX'
ROBOTS_NUM = 17
PUCKS_NUM = 30


if __name__ == "__main__":
#    Map = environment.Map(size=[10, 8])
    Map = environment.Map(size=[10, 8])  # for debug with AUTO_GENERATE = False !

    Controller = HLC.controller.Controller(gridSize=Map.retGridSize())

    if AUTO_GENERATE:
        ROBOTS_NUM = Map.retGridSize()[1]-1
        for id in range(ROBOTS_NUM):
            Controller.addRobot(robotId=id)
            # time.sleep(0.1)

        for id in range(PUCKS_NUM):
            while True:
                rand_pos = [randint(0, Map.retGridSize()[0] - 3), randint(1, Map.retGridSize()[1]) - 1]
                if not Controller.checkIfPuckIsOnPosition(rand_pos) and rand_pos != Map.retContainerPos():
                    break
            Controller.addPuck(puckId=id, init_pos=rand_pos)
            # time.sleep(0.1)
        Controller.returnPucksAsString()
    else:
        for i in range(7):
            Controller.addRobot(robotId=i)

        Controller.addPuck(puckId=0, init_pos=[3, 3])
        Controller.addPuck(puckId=1, init_pos=[0, 7])
        Controller.addPuck(puckId=2, init_pos=[6, 2])
        Controller.addPuck(puckId=3, init_pos=[6, 1])
        Controller.addPuck(puckId=4, init_pos=[7, 1])
        Controller.addPuck(puckId=5, init_pos=[3, 5])
        Controller.addPuck(puckId=6, init_pos=[4, 6])
        Controller.addPuck(puckId=7, init_pos=[6, 7])
        Controller.addPuck(puckId=8, init_pos=[6, 4])
        Controller.addPuck(puckId=9, init_pos=[1, 7])
        Controller.addPuck(puckId=10, init_pos=[1, 6])
        Controller.addPuck(puckId=11, init_pos=[0, 2])
        Controller.addPuck(puckId=12, init_pos=[7, 2])
        Controller.addPuck(puckId=13, init_pos=[5, 2])
        Controller.addPuck(puckId=14, init_pos=[5, 1])
        Controller.addPuck(puckId=15, init_pos=[6, 0])
        Controller.addPuck(puckId=16, init_pos=[1, 0])
        Controller.addPuck(puckId=17, init_pos=[1, 3])
        Controller.addPuck(puckId=18, init_pos=[4, 0])
        Controller.addPuck(puckId=19, init_pos=[7, 5])
        Controller.addPuck(puckId=20, init_pos=[1, 1])
        Controller.addPuck(puckId=21, init_pos=[4, 4])
        Controller.addPuck(puckId=22, init_pos=[2, 2])
        Controller.addPuck(puckId=23, init_pos=[0, 3])
        Controller.addPuck(puckId=24, init_pos=[5, 7])
        Controller.addPuck(puckId=25, init_pos=[1, 5])
        Controller.addPuck(puckId=26, init_pos=[3, 1])
        Controller.addPuck(puckId=27, init_pos=[3, 2])
        Controller.addPuck(puckId=28, init_pos=[4, 2])
        Controller.addPuck(puckId=29, init_pos=[0, 6])

    if PRINT_CONSOLE_GRID:
        print("... Initial map ...")
        Map.updateGrid(
            robots=Controller.retRobots(),
            pucks=Controller.retPucks(),
            container=Controller.retContainerContent())
        Map.showGrid()

    if PLOT_FIGURE:
        Map.createGridWorldWindow()
        Map.updategridWorld(
            robots=Controller.retRobots(),
            pucks=Controller.retPucks(),
            container=Controller.retContainerContent())

    while True:
        idling_pucks, idling_pucks_ids = Controller.checkIdlingPucks()
        if idling_pucks is True:
            LOG.info("Idling Pucks ids:" + str(idling_pucks_ids))
        else:
            LOG.info("NO Ideling Pucks")

        idling_robots, idling_robots_ids = Controller.checkIdlingRobots()
        if idling_robots is True:
            LOG.info("Idling Robots ids: " + str(idling_robots_ids))
        else:
            LOG.info("No idling robots")

        '''
        przypisywanie
        '''
        # jeśli istnieją czekające pucki i istnieją wolne roboty
        if (idling_pucks is True) and (idling_robots is True):
            for puck_id in idling_pucks_ids:  # dla kazdego pucka
                if idling_robots is True:  # jesli nadal istnieje czekajacy robot
                    robot_id, distance = Controller.DetermineNearestRobot(robots_ids=idling_robots_ids,
                                                                          puck_id=puck_id)  # znajdz najblizszego robota
                    Controller.assignRobotToPuck(robot_id=robot_id, puck_id=puck_id) # naprawic
                    '''
                    wyznaczanie sciezki robot-puck
                    '''
                    path = Controller.generateRobotMissionPath(robot_id=robot_id, puck_id=puck_id, container_pos=Map.retContainerPos())
                    Controller.setRobotMission(robot_id=robot_id, puck_id=puck_id, path=path)

                    idling_robots, idling_robots_ids = Controller.checkIdlingRobots()
                    LOG.info("Left Idling Robots: " + str(idling_robots_ids))

        '''
        wykonywanie kroku
        '''
        Controller.updateAllocationMatrix()
        if PRINT_CONSOLE_GRID:
            Controller.showAllocationMatrix()

        if STEP_BY_STEP:
            inp = input("Press to do step...")
        elif SIMULATION_TIME != 'MAX':
            time.sleep(SIMULATION_TIME)

        Controller.executeOneStep()

        if PRINT_CONSOLE_GRID:
            Map.updateGrid(
                robots=Controller.retRobots(),
                pucks=Controller.retPucks(),
                container=Controller.retContainerContent())
            Map.showGrid()

        if PLOT_FIGURE:
            Map.updategridWorld(
                robots=Controller.retRobots(),
                pucks=Controller.retPucks(),
                container=Controller.retContainerContent())
        if PRINT_CONSOLE_GRID:
            print("-" * 50)