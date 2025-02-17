import time
from crazyflie_controller import CrazyflieController  # Import the reusable controller

# Initialize the Crazyflie controller
drone = CrazyflieController()

try:
    print("Getting ready to fly...")
    drone.mc.take_off(0.5)  # Take off to 0.5 meters
    time.sleep(3)  # Hover for 3 seconds
    drone.mc.land()  # Land the drone
    print("Landed safe and sound!")
    
except KeyboardInterrupt:
    print("Emergency stop activated!")

drone.close()
