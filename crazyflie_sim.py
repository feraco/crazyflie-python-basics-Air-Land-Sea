import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Import 3D plotting
from cflib.crazyflie import Crazyflie
import cflib.crtp  # Crazy RealTime Protocol

class CrazyflieSimulator():
    def __init__(self, real=False):
        self.takeoff_alt = 0.3  # Default takeoff height (meters)
        self._init_state()
        self.real_drone = real
        self.cf = None

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
        self.yaw_data = []
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
        self._check_takeoff()
        print(f"Moving: vx={vx}, vy={vy}, vz={vz}, yaw={yaw_rate}")
        self.send_command('move', vx, vy, vz, yaw_rate)
        self.update_position(vx, vy, vz, yaw_rate, duration)
        self.plot_flight_path()

    def update_position(self, vx, vy, vz, yaw_rate, duration):
        new_x = self.cur_loc[0] + vx * duration
        new_y = self.cur_loc[1] + vy * duration
        self.cur_loc = (new_x, new_y)
        self.path_coors.append(self.cur_loc)
        self.altitude += vz * duration
        self.altitude_data.append(self.altitude)
        self.bearing = (self.bearing + yaw_rate * duration) % 360
        self.yaw_data.append(self.bearing)

    def plot_flight_path(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        horz_df = pd.DataFrame(self.path_coors, columns=['X', 'Y'])
        altitudes = self.altitude_data
        
        ax.plot(horz_df['X'], horz_df['Y'], altitudes, 'bo-', linewidth=2, markersize=8, label='Drone Path')
        ax.scatter(horz_df.iloc[-1, 0], horz_df.iloc[-1, 1], altitudes[-1], c='red', marker='^', s=100, label='Current Position')
        
        ax.set_xlabel('X Distance (m)')
        ax.set_ylabel('Y Distance (m)')
        ax.set_zlabel('Altitude (m)')
        ax.set_title('3D Flight Path')
        ax.legend()
        plt.show()

    def reset(self):
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
