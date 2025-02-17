import time
from crazyflie_controller import CrazyflieController  # Import reusable controller

# Initialize Crazyflie controller
drone = CrazyflieController()

try:
    drone.mc.take_off(0.5)  # Takeoff to 0.5 meters
    time.sleep(0.5)

    # Movement sequence
    drone.mc.forward(0.3)
    time.sleep(0.5)
    
    drone.mc.back(0.3)
    time.sleep(0.5)
    
    drone.mc.turn_left(90)
    drone.mc.turn_right(180)
    time.sleep(0.5)
    
    drone.mc.right(0.3)
    time.sleep(0.5)
    
    drone.mc.up(0.3)
    time.sleep(0.5)

    print("Getting tired... time to land.")
    drone.mc.down(0.3)
    time.sleep(0.5)

    drone.mc.land()  # Land safely

except KeyboardInterrupt:
    print("Emergency stop activated!")

drone.close()
