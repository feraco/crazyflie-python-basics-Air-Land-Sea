import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from cflib.crazyflie import Crazyflie
import cflib.crtp  # Crazy RealTime Protocol

class CrazyflieSimulator():
    def __init__(self, real=False):
        self.takeoff_alt = 0.3  # Default takeoff height (meters)
        self._init_state()
        self.real_drone = real
        self.cf = None

        # Initialize Crazyflie if running real mode
        if self.real_drone:
            cflib.crtp.init_drivers()
            self.cf = Crazyflie(rw_cache='./cache')
            print("Connected to Crazyflie!")
    
    def _init_state(self):
        self.takeoff_state = False
        self.altitude = 0
        self.cur_loc = (0, 0)
        self.bearing = 0
        self.altitude_data = []
        self.path_coors = [(0, 0)]
        self.command_log = []

    def send_command(self, command: str, *args):
        command_json = {'command': command, 'arguments': args}
        self.command_log.append(command_json)
        print(f'Executing command: {self.serialize_command(command_json)}')
        time.sleep(1)  # Simulating delay

    @staticmethod
    def serialize_command(command: dict):
        serialized = command['command']
        if command.get('arguments'):
            serialized = f"{serialized} {' '.join(map(str, command['arguments']))}"
        return serialized

    def takeoff(self):
        if not self.takeoff_state:
            print("Taking off!")
            self.takeoff_state = True
            self.altitude = self.takeoff_alt
            self.altitude_data.append(self.takeoff_alt)
            self.send_command('takeoff')
        else:
            print("Already in the air!")

    def land(self):
        self._check_takeoff()
        print("Landing now...")
        self.takeoff_state = False
        self.altitude = 0
        self.send_command('land')
        self.plot_flight_path()

    def _check_takeoff(self):
        if not self.takeoff_state:
            raise Exception("Takeoff required before executing this command!")

    def move(self, vx, vy, vz, yaw_rate, duration=1.0):
        """General move function for Crazyflie."""
        self._check_takeoff()
        print(f"Moving: vx={vx}, vy={vy}, vz={vz}, yaw={yaw_rate}")
        self.send_command('move', vx, vy, vz, yaw_rate)
        self.update_position(vx, vy, vz, duration)

    def update_position(self, vx, vy, vz, duration):
        """Simulate movement in the environment."""
        new_x = self.cur_loc[0] + vx * duration
        new_y = self.cur_loc[1] + vy * duration
        self.cur_loc = (new_x, new_y)
        self.path_coors.append(self.cur_loc)
        self.altitude += vz * duration
        self.altitude_data.append(self.altitude)

    ## Tello-Like Movement Functions
    def forward(self, distance, speed=0.2):
        self.move(speed, 0, 0, 0, distance / speed)

    def backward(self, distance, speed=0.2):
        self.move(-speed, 0, 0, 0, distance / speed)

    def left(self, distance, speed=0.2):
        self.move(0, -speed, 0, 0, distance / speed)

    def right(self, distance, speed=0.2):
        self.move(0, speed, 0, 0, distance / speed)

    def up(self, distance, speed=0.1):
        self.move(0, 0, speed, 0, distance / speed)

    def down(self, distance, speed=0.1):
        self.move(0, 0, -speed, 0, distance / speed)

    def rotate(self, yaw_rate, duration=1.0):
        self._check_takeoff()
        print(f"Rotating: yaw_rate={yaw_rate}")
        self.send_command('rotate', yaw_rate)
        self.bearing = (self.bearing + yaw_rate * duration) % 360

    def plot_flight_path(self):
        fig, ax = plt.subplots()
        horz_df = pd.DataFrame(self.path_coors)
        ax.plot(horz_df[0], horz_df[1], 'bo-', linewidth=2, markersize=8)
        ax.grid()
        ax.set(xlabel='X Distance (m)', ylabel='Y Distance (m)', title='Crazyflie Flight Path')
        plt.show()

    def deploy(self):
        """Deploys the stored commands to the real Crazyflie."""
        if not self.real_drone:
            raise Exception("Simulator is not connected to a real Crazyflie!")

        print("Deploying commands to real Crazyflie...")
        for command in self.command_log:
            print(f"Sending: {self.serialize_command(command)}")
            time.sleep(1)  # Simulating real execution delay

    def reset(self):
        """Reset simulator state."""
        print("Resetting simulation...")
        self._init_state()

    def save(self, file_path='commands.json'):
        with open(file_path, 'w') as json_file:
            json.dump(self.command_log, json_file, indent=4)
        print(f"Commands saved to {file_path}")

    def load_commands(self, file_path):
        with open(file_path) as json_file:
            commands = json.load(json_file)

        self._init_state()
        for command in commands:
            getattr(self, command['command'])(*command['arguments'])

# Example Usage:
if __name__ == '__main__':
    drone = CrazyflieSimulator()
    drone.takeoff()
    drone.forward(1.0)   # Move forward 1 meter
    drone.rotate(90, 1.0)  # Rotate 90 degrees
    drone.right(1.0)  # Move right 1 meter
    drone.up(0.5)  # Ascend 0.5 meters
    drone.down(0.5)  # Descend 0.5 meters
    drone.land()
