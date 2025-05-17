# Crazyflie Python Basics – Air, Land, and Sea

This repository provides educational example files and control scripts for exploring drone flight and autonomy using the Crazyflie 2.1. It is part of the DroneBlocks InnovatED STEM Air, Land, and Sea course and supports both simulated and real drone interaction using Python and Jupyter Notebooks.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Quick Start](#quick-start)
* [Drone Initialization](#drone-initialization)
* [Drone Commands](#drone-commands)

  * [Navigation Commands](#navigation-commands)
  * [Sensor Commands](#sensor-commands)
  * [Advanced Movement](#advanced-movement)
  * [Obstacle Detection](#obstacle-detection)
  * [Utility and Logging](#utility-and-logging)
* [Contributors](#contributors)

---

## Project Overview

* Modular Python classes for drone control
* Jupyter notebooks covering takeoff, landing, loops, conditionals, sensor integration
* Flow Deck and Multi-Ranger sensor integration
* Simulated and real drone flight with 3D plotting

---

## Quick Start

**Python Version Required:** 3.10 or higher

```bash
git clone https://github.com/feraco/crazyflie-python-basics-Air-Land-Sea.git
cd crazyflie-python-basics-Air-Land-Sea
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

---

## Drone Initialization

```python
from crazyflie_sim import CrazyflieSimulator

drone = CrazyflieSimulator(real=False)  # Set real=True to control a physical Crazyflie drone
```

* `real=False`: simulation only
* `real=True`: connects to physical drone using radio

---

## Drone Commands

### Navigation Commands

```python
drone.takeoff(0.5)             # Take off to 0.5 meters
drone.land()                  # Land the drone
drone.forward(1.0)            # Move forward 1 meter
drone.backward(0.5)           # Move backward

drone.left(0.5)               # Move left

drone.right(0.5)              # Move right

drone.up(0.3)                 # Ascend

drone.down(0.3)               # Descend

drone.rotate(90, 1.0)         # Rotate 90 degrees over 1 second

drone.move(0.2, 0, 0, 0, 3.0) # Move with velocity (vx, vy, vz, yaw, duration)
```

### Sensor Commands

```python
z = drone.get_height()            # Get altitude
position = drone.get_position()  # Get current (x, y) position
yaw = drone.get_yaw()            # Get current yaw
velocity = drone.get_velocity()  # Get velocity (sim only)
status = drone.get_status()      # Get all above in one dict
```

### Advanced Movement

```python
drone.circle_right(1.0, 0.5)     # Circle right with radius 1.0 at speed 0.5

drone.circle_left(1.0, 0.5)      # Circle left with radius 1.0 at speed 0.5

drone.start_setpoint_stream()   # Begin sending setpoints (needed before raw thrust)
drone.set_raw_thrust(38000, 2.0) # Raw motor control (real drone only)
```

### Obstacle Detection

```python
distances = drone.get_distances()

# Individual direction readings:
print(distances['front'])   # Distance to object in front
print(distances['back'])    # Distance to object behind
print(distances['left'])    # Distance to the left
print(distances['right'])   # Distance to the right
print(distances['up'])      # Distance to object above

# Example conditional usage
if drone.detect_obstacle():
    drone.stop()

if distances['front'] < 0.3:
    drone.stop()
```

### Utility and Logging

```python
drone.plot_flight_path()           # Show 3D path (sim only)
drone.execute_commands([(drone.forward, 0.5)], avoid_obstacles=True)
drone.save("log.json")            # Save flight log
drone.load_commands("log.json")   # Load and replay

drone.reset()                      # Reset internal state
drone.close()                      # Shutdown connection
```

---

## Contributors

* Fred Feraco [@feraco](https://github.com/feraco)
