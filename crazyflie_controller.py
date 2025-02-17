import logging
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from cflib.swarms.multiranger import Multiranger  # Import Multi-Ranger

# Set URI and default height
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
DEFAULT_HEIGHT = 0.3

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

class CrazyflieController:
    def __init__(self):
        """Initialize the Crazyflie connection with Multi-Ranger support."""
        cflib.crtp.init_drivers()
        self.scf = SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache'))
        self.scf.__enter__()  # Manually enter context
        self.mc = MotionCommander(self.scf, default_height=DEFAULT_HEIGHT)
        self.ranger = Multiranger(self.scf)  # Initialize Multi-Ranger sensors

    def execute_commands(self, commands, avoid_obstacles=False):
        """Run a list of movement commands, with optional obstacle avoidance."""
        for action, value in commands:
            if avoid_obstacles and self.detect_obstacle():
                print("Obstacle detected! Stopping movement.")
                self.mc.stop()
                break
            action(value)
            time.sleep(0.5)

    def detect_obstacle(self, threshold=0.3):
        """Returns True if any obstacle is detected within the threshold distance."""
        return (
            self.ranger.front < threshold or
            self.ranger.back < threshold or
            self.ranger.left < threshold or
            self.ranger.right < threshold or
            self.ranger.up < threshold
        )

    def get_distances(self):
        """Returns the current Multi-Ranger sensor readings."""
        return {
            "front": self.ranger.front,
            "back": self.ranger.back,
            "left": self.ranger.left,
            "right": self.ranger.right,
            "up": self.ranger.up
        }

    def take_off(self, duration=3):
        """Take off and hover for a specified duration."""
        time.sleep(duration)

    def land(self):
        """Land the drone safely."""
        self.mc.stop()

    def close(self):
        """Close the connection properly."""
        self.mc.__exit__(None, None, None)
        self.scf.__exit__(None, None, None)
