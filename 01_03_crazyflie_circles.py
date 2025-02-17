import time
from crazyflie_controller import CrazyflieController  # Import reusable controller

# Initialize Crazyflie controller
drone = CrazyflieController()

try:
    print("Taking off!")
    drone.mc.take_off(0.5)  # Takeoff to 0.5 meters
    time.sleep(1)  # Hover for 1 second

    # Fly in half-circle counterclockwise
    drone.mc.circle_left(0.2, 0.2, 180)
    time.sleep(0.5)

    # Fly in half-circle clockwise
    drone.mc.circle_right(0.2)
    time.sleep(0.5)

    drone.mc.land()  # Land safely
    print("Game Over!!")

except KeyboardInterrupt:
    print("Emergency stop activated!")

drone.close()
