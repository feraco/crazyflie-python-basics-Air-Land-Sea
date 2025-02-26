import time
from crazyflie_controller import CrazyflieController
from cflib.utils.multiranger import Multiranger

# Initialize Crazyflie controller
drone = CrazyflieController()
ranger = Multiranger(drone.scf)  # Initialize Multi-Ranger sensors

try:
    print("Taking off!")
    drone.mc.take_off(0.5)  # Takeoff to 0.5 meters
    time.sleep(1)

    # Check if an obstacle is ahead before moving forward
    if ranger.front > 0.3:  # No obstacle within 30 cm
        print("Path is clear! Moving forward...")
        drone.mc.forward(0.5)  # Move forward 0.5 meters
    else:
        print("Obstacle detected! Stopping movement.")
    
    drone.mc.land()  # Land safely
    print("Mission complete!")

except KeyboardInterrupt:
    print("Emergency stop activated!")

drone.close()
