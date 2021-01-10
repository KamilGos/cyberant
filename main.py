import HLC.controller as controller
import environment
import puck
import robot
import logging
import time
import traceback

LOG_FORMAT = '%(levelname)-10s %(name)-20s %(funcName)-20s  %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)

PLOT_FIGURE = False

if __name__ == "__main__":
    Map = environment.Map(size=[6, 4])

    Controller = controller.Controller(gridSize=Map.retGridSize())

    Controller.addRobot(robotId=0)
    Controller.addRobot(robotId=1)

    Controller.addPuck(puckId=0, init_pos=[1, 2])
    Controller.addPuck(puckId=1, init_pos=[1, 3])

    print("... Initial map ...")
    Map.updateGrid(
        robots=Controller.retRobots(),
        pucks=Controller.retPucks(),
        container=Controller.retContainerContent())
    Map.showGrid()

    if PLOT_FIGURE:
        Map.createFigure()
        Map.updateFigure(Map.retGridForFigure(
            robots=Controller.retRobots(),
            pucks=Controller.retPucks()))

    # while True:
        # try:
    for i in range(100):  # debug
        print("STEP: ", i)

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
                    Controller.assignRobotToPuck(robot_id=robot_id, puck_id=puck_id)
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
        Controller.showAllocationMatrix()

        inp = input("Do step...")

        Controller.executeOneStep()

        Map.updateGrid(
            robots=Controller.retRobots(),
            pucks=Controller.retPucks(),
            container=Controller.retContainerContent())

        Map.showGrid()

        if PLOT_FIGURE:
            Map.updateFigure(Map.retGridForFigure(
                robots=Controller.retRobots(),
                pucks=Controller.retPucks()))

        time.sleep(1)
        print("-"*50)
        inp = input("Next loop...")



        # except Exception as ex:
        #     mss = traceback.format_tb()
        #     LOG.error("WHILE LOOP ERROR: Exception: " + str(ex))
        #     exit()
