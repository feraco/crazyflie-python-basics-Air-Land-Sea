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
