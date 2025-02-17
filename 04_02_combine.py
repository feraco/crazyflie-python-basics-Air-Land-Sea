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

    # Loop through a square pattern with obstacle avoidance
    for _ in range(4):
        print("Checking for obstacles...")

        # Move forward until an obstacle is detected or 0.5m is traveled
        distance_traveled = 0.0
        while ranger.front > 0.3 and distance_traveled < 0.5:
            drone.mc.forward(0.1)  # Move forward in small increments
            time.sleep(0.2)
            distance_traveled += 0.1  # Track distance traveled

        # If an obstacle is detected, move up before turning
        if ranger.front <= 0.3:
            print("Obstacle ahead! Moving up...")
            drone.mc.up(0.2)
            time.sleep(0.5)

        print("Turning 90 degrees...")
        drone.mc.turn_left(90)
        time.sleep(0.5)

    drone.mc.land()  # Land safely
    print("Mission complete!")

except KeyboardInterrupt:
    print("Emergency stop activated!")

drone.close()
