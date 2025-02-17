import time
from crazyflie_controller import CrazyflieController
from cflib.swarms.multiranger import Multiranger  # Import Multi-Ranger for obstacle detection

# Initialize Crazyflie controller
drone = CrazyflieController()
ranger = Multiranger(drone.scf)  # Initialize Multi-Ranger sensors

try:
    print("Taking off!")
    drone.mc.take_off(0.5)  # Takeoff to 0.5 meters
    time.sleep(1)

    # Check if there is enough space ahead before moving
    if ranger.front > 0.3:  
        print("Path is clear! Moving forward...")
        drone.mc.forward(0.5)  # Move forward 0.5 meters

    drone.mc.land()  # Land safely
    print("Mission complete!")

except KeyboardInterrupt:
    print("Emergency stop activated!")

drone.close()
