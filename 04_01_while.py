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

    # Move forward until an obstacle is detected within 30 cm
    while ranger.front > 0.3:
        print("Moving forward...")
        drone.mc.forward(0.1)  # Move forward in small increments
        time.sleep(0.2)

    print("Obstacle detected! Stopping movement.")
    drone.mc.stop()
    
    drone.mc.land()  # Land safely
    print("Mission complete!")

except KeyboardInterrupt:
    print("Emergency stop activated!")

drone.close()
