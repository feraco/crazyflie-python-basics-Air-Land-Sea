import time
from crazyflie_controller import CrazyflieController  # Import reusable controller

# Initialize Crazyflie controller
drone = CrazyflieController()

try:
    print("Taking off!")
    drone.mc.take_off(0.5)  # Takeoff to 0.5 meters
    time.sleep(1)

    # Repeat movement 4 times (like a square)
    for _ in range(4):
        print("Flying forward...")
        drone.mc.forward(0.3)  # Move forward 0.3 meters
        time.sleep(0.5)

        print("Turning 90 degrees...")
        drone.mc.turn_left(90)  # Turn 90 degrees
        time.sleep(0.5)

    drone.mc.land()  # Land safely
    print("Mission complete!")

except KeyboardInterrupt:
    print("Emergency stop activated!")

drone.close()
