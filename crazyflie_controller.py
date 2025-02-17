import logging
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper

# Set URI and default height
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
DEFAULT_HEIGHT = 0.3

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

class CrazyflieController:
    def __init__(self):
        """Initialize the Crazyflie connection."""
        cflib.crtp.init_drivers()
        self.scf = SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache'))
        self.scf.__enter__()  # Manually enter context
        self.mc = MotionCommander(self.scf, default_height=DEFAULT_HEIGHT)

    def execute_commands(self, commands):
        """Run a list of movement commands."""
        for action, value in commands:
            action(value)
            time.sleep(0.5)

    def close(self):
        """Close the connection properly."""
        self.mc.__exit__(None, None, None)
        self.scf.__exit__(None, None, None)
