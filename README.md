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

## 🚀 Advanced Position Control

If you are using absolute positioning, you can use:

```python
mc.go_to(x, y, z, yaw, velocity)
# x, y, z → Coordinates in meters
# yaw → Final heading angle (degrees)
# velocity → Speed of movement (m/s)
```

### Example:

```python
mc.go_to(1.0, 1.0, 0.5, 90, 0.5)  # Move to (1,1,0.5) at 0.5 m/s, facing 90°
```

---

## 🛠️ Emergency Stop

```python
mc.stop()  # Stops all motion immediately
```

⚠️ **This is useful if something goes wrong during flight.**

---

## ✈️ Example: Full Flight Script

```python
from crazyflie_controller import CrazyflieController

drone = CrazyflieController()

commands = [
    (drone.mc.take_off, 0.5),      # Takeoff to 0.5m
    (drone.mc.forward, 0.3),       # Move forward
    (drone.mc.turn_right, 90),     # Turn right
    (drone.mc.right, 0.3),         # Move right
    (drone.mc.up, 0.3),            # Move up
    (drone.mc.circle_left, (1.0, 0.5)),  # Circle left
    (drone.mc.land, None),         # Land the drone
]

try:
    drone.execute_commands(commands)
except KeyboardInterrupt:
    print("Shutting down.")

drone.close()
```

---

🚀 **Enjoy flying with Crazyflie!**

