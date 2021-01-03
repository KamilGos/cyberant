import HLC.controller as controller
import environment
import puck
import robot


if __name__=="__main__":
    Map = environment.Map(size=[6, 4])
    Robots = []
    Robots.append(robot.Robot(init_palce=1, robotId=1))


