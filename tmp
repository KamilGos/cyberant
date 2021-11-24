# Introduction 
The main idea of the project is coordinating many robots collecting objects from a closed area. The system must work reliably, without delays, collisions or dead-locks in all the time of the system running. Those assumptions need specific control of the system and the best option to achieve those high requirements is event-based control.

## This repository includes:
 * [controller.py](controller.py) - high level event-based controller algorithms
 * [path_finder.py](path_finder.py) - Dijkstra algorithm usinng heap
 * [puck.py](puck.py) - description of pucks
 * [robot.py](robot.py) - description of robots
 * [window.py](window.py) - GUI
 * [environment.py](environment.py) - map display

## Start
1. Copy the contents of this repository to the local folder
2. Run the script:
    `python3 main.py`

## Requirements
- python3
- PyQt5 5.14.1
- numpy 1.18.1 
- matplotlib 3.1.3
- tabulate 0.8.7

## Authors
* Kamil Goś [@KamilGos](https://github.com/KamilGos)
* Jakub Wojtylak [@JakubWojtylak](https://github.com/JakubWojtylak)
* Damian Lickindorf [@dlickindorf](https://github.com/dlickindorf)
* Jakub Rotkiewicz [@jrotkiewicz](https://github.com/jrotkiewicz)


# Environment Description
The environment in which all the processes will take place is a 2D grid map, where every field have it's coordinates (x, y). Every field on the map can be occupied by an object. There is a special row, where initially the robots are placed, and another one for the collision-free return of the robots. One field is reserved for the container, where all the pucks are being dropped at the end of the mission. On all other fields a puck may occur. It's coordinates will be the field's coordinates. The map is represented as the undirected graph with all edges weight set to 1. On this basis, the robot mission path can be found by searching the graph. As the searching algorithm the Dijkstra' algorithm was used. This approach also allows for quick mapping of a new path when a deadlock is detected.

# Graphical User Interface
The GUI for the simulation was created using the PyQT5 Framework. During normal use the user will encounter two windows. First a window for simulation settings. In this window user chooses:
  * The amount of robots that will be collecting pucks, this number must be smaller than the map size in direction X.
  * The amount of pucks that will be collected, this number must be smaller than (Map size X*(Map size Y-2)).
  * Size of the map in direction X – limited to a range between 3 and 20.
  * Size of the map in direction Y – limited to a range between 5 and 20.
![window 1](https://user-images.githubusercontent.com/44849247/107196880-7c669880-69f3-11eb-9bfd-a7c8fb8c7a4c.png)

On the main simulation window we can see the simulation grid of the chosen size. In the middle left area of the window the simulation grid of the chosen size is displayed. On the grid we can see:
  * Red rectangles with P# written on them represent pucks. The # is the ID of the puck.
  *  Vivid green rectangles with R# represent robots. The # is the ID of the robot.
  *  Pale green rectangles with I# represent initial positions for robots. The # is the ID of the robot. Each robot has its own dedicated initial position. Pucks can’t appear on those positions.
  *  The light purple rectangle with a number written on it is the drop-off location. Robots drop the pucks in here. The number shows how many pucks have been delivered so far. Pucks can’t appear in this position.
  *  The gray areas are reserved for robots to be able to return to their initial positions. Pucks can’t appear there.
  
The right side of the window is reserved for controls and statistics. From the top down we can see:
    * The “exit app” button whose function is self-explanatory,
    * Displays with the number of robots and generated so far,
    * A button for adding a puck in a random location
    * The “It’s raining puck” button which starts generating pucks at random positions in fixed time intervals. It will generate 5 pucks and stop,
    * Two input fields for X and Y positions and a button which let the user drop a puck in a given location,
    * A tick box that lets the user trigger whether the output is written to the console or not,
    * A green “start/stop” for running the simulation automatically,
    * A “next step” button – for running the simulation manually, step by step,
    * A slider for slowing down the simulation,
    * And a progress bar which shows the progress of the simulation.
  
![window 2](https://user-images.githubusercontent.com/44849247/107196890-7e305c00-69f3-11eb-88fc-9b0473ea4276.png)

# Tests
In order to check reliability of the algorithm the simulation needed some testing. In that purpose, random number generator provided following parameters:
   * Map height = random number from range (10,30)
   * Map width = random number from range (10,Map height)
   * Number of Pucks = Map height x Map width / 4
   * Number of Robots = Map width - 2
The reliability condition of the algorithm is met if robots collected all of the pucks and successfully put them into the container, meaning that no system blockade emerged.
<br/><br/>
**All tests were successful.** The developed system handles the collection of pucks without any problems. Algorithms implemented to avoid deadlocks work perfectly. During the tests, no combinations of robots and pucks were found that would block the system.
