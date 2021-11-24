<!-- image -->

<h1 align="center"> cyberant </h1>
<h2 align="center"> Robot swarm for puck collection - simulation of event-based control system  </h2>

<!-- https://shields.io/ -->
<p align="center">
  <img alt="Top language" src="https://img.shields.io/badge/Language-Python-yellow?style=for-the-badge&logo=python">
  <img alt="Status" src="https://img.shields.io/badge/Status-done-green?style=for-the-badge">
  <img alt="Code size" src="https://img.shields.io/github/languages/code-size/KamilGos/cyberant?style=for-the-badge">
</p>

<!-- table of contents -->
<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0;
  <a href="#package-content">Content</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <a href="#eyes-implementation">Implementation</a> &#xa0; | &#xa0;
  <a href="#microscope-tests">Tests</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="#technologist-author">Author</a> &#xa0; | &#xa0;
</p>

<br>


## :dart: About ##
The main idea of the project is coordinating many robots collecting objects from a closed area. The system must work reliably, without delays, collisions or dead-locks in all the time of the system running. Those assumptions need specific control of the system and the best option to achieve those high requirements is event-based control.

## :package: Content
 * [sources](sources) - source files
    * [controller.py](controller.py) - high level event-based controller algorithms
    * [path_finder.py](path_finder.py) - Dijkstra algorithm usinng heap
    * [puck.py](puck.py) - description of pucks
    * [robot.py](robot.py) - description of robots
    * [window.py](window.py) - GUI
    * [environment.py](environment.py) - map display
 * [main.py](main.py) - main executable script

## :checkered_flag: Starting ##
```bash
# Clone this project
$ git clone https://github.com/KamilGos/cyberant

# Access
$ cd cyberant

# Run the project
$ python3 main.py
```

## :eyes: Implementation ##
<h2>Environment Description</h2>
The environment in which all the processes will take place is a 2D grid map, where every field have it's coordinates (x, y). Every field on the map can be occupied by an object. There is a special row, where initially the robots are placed, and another one for the collision-free return of the robots. One field is reserved for the container, where all the pucks are being dropped at the end of the mission. On all other fields a puck may occur. It's coordinates will be the field's coordinates. The map is represented as the undirected graph with all edges weight set to 1. On this basis, the robot mission path can be found by searching the graph. As the searching algorithm the Dijkstra' algorithm was used. This approach also allows for quick mapping of a new path when a deadlock is detected.

<h2>Graphical User Interface</h2>
The GUI for the simulation was created using the PyQT5 Framework. During normal use the user will encounter two windows. First a window for simulation settings. In this window user chooses:

  * The amount of robots that will be collecting pucks, this number must be smaller than the map size in direction X.
  * The amount of pucks that will be collected, this number must be smaller than (Map size X*(Map size Y-2)).
  * Size of the map in direction X – limited to a range between 3 and 20.
  * Size of the map in direction Y – limited to a range between 5 and 20.

<div align="center" id="put_id"> 
  <img src=images/dialog.png width="400" />
  &#xa0;
</div>

<br>

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

<div align="center" id="put_id"> 
  <img src=images/main_window.png width="670" />
  &#xa0;
</div>

## :microscope: Tests ##

---
<center>
You can watch the movie with test at the top of the page
</center>

---

In order to check reliability of the algorithm the simulation needed some testing. In that purpose, random number generator provided following parameters:
   * Map height = random number from range (10,30)
   * Map width = random number from range (10,Map height)
   * Number of Pucks = Map height x Map width / 4
   * Number of Robots = Map width - 2
The reliability condition of the algorithm is met if robots collected all of the pucks and successfully put them into the container, meaning that no system blockade emerged.

<br>

**All tests were successful.** The developed system handles the collection of pucks without any problems. Algorithms implemented to avoid deadlocks work perfectly. During the tests, no combinations of robots and pucks were found that would block the system.


## :memo: License ##

This project is under license from MIT.

## :technologist: Author ##

Made with :heart: by:
* Kamil Goś [@KamilGos](https://github.com/KamilGos)
* Jakub Wojtylak [@JakubWojtylak](https://github.com/JakubWojtylak)
* Damian Lickindorf [@dlickindorf](https://github.com/dlickindorf)
* Jakub Rotkiewicz [@jrotkiewicz](https://github.com/jrotkiewicz)


&#xa0;

<a href="#top">Back to top</a>



<!-- ADDONS -->
<!-- images -->
<!-- <h2 align="left">1. Mechanics </h2>
<div align="center" id="inventor"> 
  <img src=images/model_1.png width="230" />
  <img src=images/model_2.png width="236" />
  <img src=images/model_3.png width="228" />
  &#xa0;
</div> -->

<!-- one image -->
<!-- <h2 align="left">2. Electronics </h1>
<div align="center" id="electronics"> 
  <img src=images/electronics.png width="500" />
  &#xa0;
</div> -->


<!-- project dockerized -->
<!-- <div align="center" id="status"> 
  <img src="https://www.docker.com/sites/default/files/d8/styles/role_icon/public/2019-07/Moby-logo.png" alt="simulator" width="75" style="transform: scaleX(-1);"/>
   <font size="6"> Project dockerized</font> 
  <img src="https://www.docker.com/sites/default/files/d8/styles/role_icon/public/2019-07/Moby-logo.png" alt="simulator" width="75"/>
  &#xa0;
</div>
<h1 align="center"> </h1> -->