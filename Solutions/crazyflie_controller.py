import logging
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from cflib.utils.multiranger import Multiranger

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
        self.ranger.start()  # Start sensor logging

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
        return any(
            distance is not None and distance < threshold 
            for distance in [self.ranger.front, self.ranger.back, self.ranger.left, self.ranger.right, self.ranger.up]
        )

    def get_distances(self):
        """Returns the current Multi-Ranger sensor readings."""
        return {
            "front": self.ranger.front if self.ranger.front is not None else "No Data",
            "back": self.ranger.back if self.ranger.back is not None else "No Data",
            "left": self.ranger.left if self.ranger.left is not None else "No Data",
            "right": self.ranger.right if self.ranger.right is not None else "No Data",
            "up": self.ranger.up if self.ranger.up is not None else "No Data"
        }

    def take_off(self, duration=3):
        """Take off and hover for a specified duration."""
        print("🚀 Taking off!")
        self.mc.take_off(DEFAULT_HEIGHT)
        time.sleep(duration)

    def land(self):
        """Land the drone safely."""
        print("🛬 Landing...")
        self.mc.land()
        time.sleep(2)


    def spiral(self, duration=6, radius=0.3, turns=2, ascend=True):
        print("🌀 Executing spiral...")
        start_time = time.time()
        t = 0
        dt = 0.1
        omega = (2 * math.pi * turns) / duration
        vz = (DEFAULT_HEIGHT if ascend else -DEFAULT_HEIGHT) / duration

        while time.time() - start_time < duration:
            angle = omega * t
            vx = radius * math.cos(angle) * omega
            vy = radius * math.sin(angle) * omega
            self.mc.start_linear_motion(vx, vy, vz)
            time.sleep(dt)
            t += dt

        self.mc.stop()



    def close(self):
        """Close the connection properly."""
        print("🔄 Closing connection...")
        self.mc.stop()
        self.ranger.stop()
        self.mc.__exit__(None, None, None)
        self.scf.__exit__(None, None, None)
