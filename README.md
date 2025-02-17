# 🚀 Crazyflie Motion Commands

## 🛫 Takeoff & Landing

```python
mc.take_off(height=0.3)  # Take off to 0.3 meters (default height)
mc.land()                # Land the drone
mc.stop()                # Immediately stop all movement
```

---

## 📍 Basic Movements

```python
mc.forward(distance_m)  # Move forward by X meters
mc.back(distance_m)     # Move backward by X meters
mc.left(distance_m)     # Move left by X meters
mc.right(distance_m)    # Move right by X meters
mc.up(distance_m)       # Move up by X meters
mc.down(distance_m)     # Move down by X meters
```

### Example:

```python
mc.forward(0.5)  # Move forward 0.5 meters
mc.left(0.3)     # Move left 0.3 meters
mc.down(0.2)     # Move down 0.2 meters
```

---

## 🔄 Rotations (Yaw)

```python
mc.turn_left(angle_deg)   # Turn left (counterclockwise) by X degrees
mc.turn_right(angle_deg)  # Turn right (clockwise) by X degrees
```

### Example:

```python
mc.turn_left(90)   # Turn left by 90 degrees
mc.turn_right(180) # Turn right by 180 degrees
```

---

## 🏎️ Velocity-Based Movements (Continuous Speed Control)

```python
mc.start_linear_motion(vx, vy, vz, rate_yaw=0)  # Move at a velocity
# vx → Forward speed (m/s)
# vy → Sideways speed (m/s)
# vz → Vertical speed (m/s)
# rate_yaw → Rotation speed (deg/s)
```

### Example:

```python
mc.start_linear_motion(0.5, 0, 0)  # Move forward at 0.5 m/s
mc.start_linear_motion(0, 0, 0.3)  # Move up at 0.3 m/s
mc.start_linear_motion(0.2, 0.2, 0, 30)  # Move diagonally & rotate at 30°/s
```

⚠️ **This function must be stopped manually with `mc.stop()`**

---

## 🔄 Circle and Curve Movements

```python
mc.circle_right(radius_m, velocity_m_s)  # Fly a circle to the right
mc.circle_left(radius_m, velocity_m_s)   # Fly a circle to the left
```

### Example:

```python
mc.circle_right(radius_m=1.0, velocity_m_s=0.5)  # Circle right with 1m radius
mc.circle_left(radius_m=0.5, velocity_m_s=0.3)   # Circle left with 0.5m radius
```

---

## 🌀 Spiral Motion

```python
mc.spiral_right(radius_start_m, radius_end_m, velocity_m_s, angle_degrees)
mc.spiral_left(radius_start_m, radius_end_m, velocity_m_s, angle_degrees)
```

### Example:

```python
mc.spiral_right(0.2, 1.0, 0.5, 360)  # Spiral outward right (360°)
mc.spiral_left(0.5, 0.1, 0.3, 180)   # Spiral inward left (180°)
```

---

## 🚀 Crazyflie Flow Deck Commands & Conditional Statements

The Flow Deck is an optical flow and distance sensor that enables autonomous positioning for the Crazyflie drone. It allows the drone to hover, move precisely, and hold position without external tracking systems.

### 📌 Required Import for Flow Deck

```python
from cflib.positioning.motion_commander import MotionCommander
```

### 📡 Flow Deck Sensor Readings

#### 🔹 Get Height (Z-axis distance)
```python
altitude = mc.get_height()
print(f"Current altitude: {altitude} meters")
```

#### 🔹 Get Optical Flow-Based Velocity
```python
velocity = mc.get_velocity()
print(f"Velocity (X, Y, Z): {velocity}")
```

#### 🔹 Get Position Estimate
```python
position = mc.get_position()
print(f"Estimated position (X, Y, Z): {position}")
```

### 🛫 Takeoff & Landing with Flow Deck
```python
mc.take_off(0.5)  # Takeoff to 0.5 meters using Flow Deck
mc.land()  # Land safely using Flow Deck
```

### 📍 Position Control (Using Flow Deck)
```python
mc.move_distance(x=0.5, y=0.0, z=0.0)  # Move forward 0.5 meters
mc.move_distance(x=0.0, y=0.5, z=0.0)  # Move right 0.5 meters
mc.move_distance(x=0.0, y=0.0, z=0.3)  # Move up 0.3 meters
```

### 🔄 Flow Deck-Based Conditional Statements

#### 🔹 Example: Stop Moving if Height is Too Low
```python
altitude = mc.get_height()
if altitude < 0.2:
    print("Warning: Too low! Stopping movement.")
    mc.stop()
```

#### 🔹 Example: Hover Until a Certain Height is Reached
```python
while mc.get_height() < 0.5:
    print("Ascending...")
    mc.up(0.1)
    time.sleep(0.1)

print("Reached target altitude!")
```

#### 🔹 Example: Move Only if Altitude is Safe
```python
if mc.get_height() > 0.3:
    mc.move_distance(0.5, 0, 0)  # Move forward 0.5m
else:
    print("Altitude too low, not moving!")
```

### 🏁 Full Example: Smart Movement with Flow Deck
```python
from crazyflie_controller import CrazyflieController
import time

drone = CrazyflieController()

try:
    drone.mc.take_off(0.5)  # Takeoff to 0.5m

    if drone.mc.get_height() > 0.3:
        drone.mc.move_distance(0.5, 0, 0)
        drone.mc.move_distance(0, 0.5, 0)
    else:
        print("Altitude too low! Adjusting height...")
        drone.mc.up(0.2)

    drone.mc.land()

except KeyboardInterrupt:
    print("Emergency stop activated!")

drone.close()
```

🚀 **Now, you can use Flow Deck-powered movements and logic for safe and accurate Crazyflie flights!**

