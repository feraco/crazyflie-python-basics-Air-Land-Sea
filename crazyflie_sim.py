import json
import time
import math
import pandas as pd
import plotly.graph_objects as go

# Crazyflie imports
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper
from cflib.utils.multiranger import Multiranger
from cflib.crazyflie.log import LogConfig  # Required for zrange logging

# Default URI and height
URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
DEFAULT_HEIGHT = 0.3

class CrazyflieSimulator:
    def __init__(self, real=False):
        self.real_drone = real
        self.takeoff_alt = DEFAULT_HEIGHT
        self._init_state()
        self.zrange = None  # For Flow Deck / Z-Ranger sensor

        if self.real_drone:
            print("🔌 Connecting to real Crazyflie...")
            cflib.crtp.init_drivers()
            self.scf = SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache'))
            self.scf.__enter__()

            # Initialize motion and sensing tools
            self.mc = MotionCommander(self.scf, default_height=self.takeoff_alt)
            self.ranger = Multiranger(self.scf)
            self.ranger.start()
            
            # Start logging z-range from sensor
            self._init_zrange_logging()
    
    def _init_state(self):
        """Initialize simulator or state tracking for real drone."""
        self.takeoff_state = False
        self.altitude = 0
        self.cur_loc = (0, 0)
        self.bearing = 0
        self.altitude_data = []
        self.path_coors = [(0, 0)]
        self.yaw_data = []
        self.command_log = []

    def takeoff(self, height=DEFAULT_HEIGHT, velocity=0.3):
        if not self.takeoff_state:
            print(f"🚀 Taking off to {height}m at {velocity}m/s!")
            self.takeoff_state = True
            self.altitude = height

            if self.real_drone:
                self.mc.take_off(height=height, velocity=velocity)
                time.sleep(height / velocity + 1)

            self.altitude_data.append(self.altitude)
            self.send_command('takeoff', height, velocity)
            self.plot_flight_path()
        else:
            print("Already in the air!")
    def _check_takeoff(self):
        if not self.takeoff_state:
            raise Exception("🚫 Takeoff required before executing this command!")
    def start_setpoint_stream(self):
        """
        Start sending zero setpoints to unlock motors (required before manual thrust).
        """
        if self.real_drone:
            print("Starting setpoint stream...")
            self.scf.cf.commander.send_setpoint(0, 0, 0, 0)
            time.sleep(0.1)
    def set_raw_thrust(self, thrust_value, duration=1.0):
        """
        Manually set thrust value (bypassing MotionCommander).
        
        Args:
            thrust_value (int): The raw thrust value to set (approx 10000 to 60000).
            duration (float): How long (seconds) to apply thrust before stopping.
        """
        if self.real_drone:
            self.scf.cf.commander.send_setpoint(0, 0, 0, thrust_value)
            time.sleep(duration)
            self.scf.cf.commander.send_stop_setpoint()
        self.send_command('set_raw_thrust', thrust_value, duration)

    def _init_zrange_logging(self):
        from cflib.crazyflie.log import LogConfig

        log_conf = LogConfig(name='Zrange', period_in_ms=100)
        log_conf.add_variable('range.zrange', 'float')

        def log_callback(timestamp, data, logconf):
            self.zrange = data['range.zrange']

        log_conf.data_received_cb.add_callback(log_callback)
        self.scf.cf.log.add_config(log_conf)
        log_conf.start()
    def get_zrange(self):
        """
        Return the height from the Flow or Z-Ranger sensor.
        Returns None if not available or not yet initialized.
        """
        if self.real_drone:
            if self.zrange is not None:
                return self.zrange
            else:
                print("⚠️ Z-range not yet initialized.")
                return None
        else:
            return self.altitude  # Simulated mode uses current altitude

    def land(self, velocity=0.3):
        self._check_takeoff()
        print(f"🛬 Landing at {velocity}m/s...")
        if self.real_drone:
            self.mc.land(velocity=velocity)
            time.sleep(self.altitude / velocity + 1)
        self.takeoff_state = False
        self.altitude = 0
        self.send_command('land', velocity)
        self.plot_flight_path()

    def move(self, vx, vy, vz, yaw_rate=0.0, duration=1.0):
        self._check_takeoff()
        print(f"Moving: vx={vx}, vy={vy}, vz={vz}, yaw={yaw_rate}")
        self.send_command('move', vx, vy, vz, yaw_rate, duration)
        if self.real_drone:
            self.mc.start_linear_motion(vx, vy, vz, yaw_rate)
            time.sleep(duration)
            self.mc.stop()
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
        self.send_command('rotate', yaw_rate, duration)
        self.bearing = (self.bearing + yaw_rate * duration) % 360
        self.yaw_data.append(self.bearing)
        self.plot_flight_path()

    def get_height(self):
        return self.altitude if not self.real_drone else self.mc._thread.get_height()

    def get_position(self):
        return self.cur_loc

    def get_yaw(self):
        return self.bearing

    def get_velocity(self):
        if len(self.path_coors) < 2:
            return (0, 0, 0)
        x1, y1 = self.path_coors[-2]
        x2, y2 = self.path_coors[-1]
        dz = self.altitude_data[-1] - self.altitude_data[-2] if len(self.altitude_data) >= 2 else 0
        return (x2 - x1, y2 - y1, dz)

    def get_status(self):
        return {
            'airborne': self.takeoff_state,
            'position': self.get_position(),
            'altitude': self.get_height(),
            'yaw': self.get_yaw(),
            'velocity': self.get_velocity() if not self.real_drone else 'N/A'
        }

    def get_log(self):
        return self.command_log

    def send_command(self, command: str, *args):
        command_json = {'command': command, 'arguments': args}
        self.command_log.append(command_json)
        print(f'Executing command: {self.serialize_command(command_json)}')
        time.sleep(1)

    @staticmethod
    def serialize_command(command: dict):
        serialized = command['command']
        if command.get('arguments'):
            serialized = f"{serialized} {' '.join(map(str, command['arguments']))}"
        return serialized
        
    def circle_right(self, radius=0.3, velocity=0.3, angle_degrees=360.0):
        print("⭕ Executing circle right (optimized)...")
        self._check_takeoff()

        distance = 2 * math.pi * radius * (angle_degrees / 360.0)
        duration = distance / velocity

        if self.real_drone:
            self.mc.start_circle_right(radius, velocity)
            time.sleep(duration)
            self.mc.stop()
        else:
            omega = velocity / radius
            dt = 0.2
            steps = int(duration / dt)

            cx = self.cur_loc[0] - radius
            cy = self.cur_loc[1]

            path_buffer = []
            alt_buffer = []

            for step in range(steps):
                angle = omega * step * dt
                new_x = cx + radius * math.cos(angle)
                new_y = cy + radius * math.sin(angle)

                self.cur_loc = (new_x, new_y)
                path_buffer.append(self.cur_loc)
                alt_buffer.append(self.altitude)

            # Batch update only once
            self.path_coors.extend(path_buffer)
            self.altitude_data.extend(alt_buffer)

            # Plot the final result once
            self.plot_flight_path()


    def circle_left(self, radius=0.3, velocity=0.3, angle_degrees=360.0):
        print("⭕ Executing circle left (optimized)...")
        self._check_takeoff()

        distance = 2 * math.pi * radius * (angle_degrees / 360.0)
        duration = distance / velocity

        if self.real_drone:
            self.mc.start_circle_left(radius, velocity)
            time.sleep(duration)
            self.mc.stop()
        else:
            omega = velocity / radius
            dt = 0.2
            steps = int(duration / dt)

            cx = self.cur_loc[0] + radius
            cy = self.cur_loc[1]

            path_buffer = []
            alt_buffer = []

            for step in range(steps):
                angle = omega * step * dt
                new_x = cx - radius * math.cos(angle)
                new_y = cy + radius * math.sin(angle)

                self.cur_loc = (new_x, new_y)
                path_buffer.append(self.cur_loc)
                alt_buffer.append(self.altitude)

            # Batch update the path once
            self.path_coors.extend(path_buffer)
            self.altitude_data.extend(alt_buffer)

            # Show one plot at the end
            self.plot_flight_path()


    def plot_flight_path(self):
        if not self.real_drone:
            import plotly.graph_objects as go
            import numpy as np
            import pandas as pd

            horz_df = pd.DataFrame(self.path_coors, columns=['X', 'Y'])
            altitudes = self.altitude_data

            if len(horz_df) == 0 or len(altitudes) == 0:
                print("No flight data to plot.")
                return

            # Compute direction for arrow at last segment
            if len(horz_df) >= 2:
                dx = horz_df['X'].iloc[-1] - horz_df['X'].iloc[-2]
                dy = horz_df['Y'].iloc[-1] - horz_df['Y'].iloc[-2]
            else:
                dx = dy = 0

            mag = max(np.sqrt(dx**2 + dy**2), 1e-6)
            arrow_length = 0.2
            ux = dx / mag * arrow_length
            uy = dy / mag * arrow_length

            fig = go.Figure()

            # Flight path line
            fig.add_trace(go.Scatter3d(
                x=horz_df['X'],
                y=horz_df['Y'],
                z=altitudes,
                mode='lines+markers',
                line=dict(color='blue', width=4),
                marker=dict(size=4),
                name='Drone Path'
            ))

            # Takeoff marker
            fig.add_trace(go.Scatter3d(
                x=[0],
                y=[0],
                z=[0],
                mode='markers',
                marker=dict(color='green', size=10, symbol='circle'),
                name='Takeoff Point'
            ))

            # Takeoff climb line
            if len(altitudes) > 0:
                fig.add_trace(go.Scatter3d(
                    x=[0, 0],
                    y=[0, 0],
                    z=[0, altitudes[0]],
                    mode='lines',
                    line=dict(color='green', width=2, dash='dot'),
                    name='Takeoff Climb'
                ))

            # Landing marker at z = 0
            fig.add_trace(go.Scatter3d(
                x=[horz_df.iloc[-1, 0]],
                y=[horz_df.iloc[-1, 1]],
                z=[0],
                mode='markers',
                marker=dict(color='red', size=10, symbol='x'),
                name='Landing Point'
            ))

            # Drone facing direction (arrow cone)
            fig.add_trace(go.Cone(
                x=[horz_df.iloc[-1, 0]],
                y=[horz_df.iloc[-1, 1]],
                z=[altitudes[-1]],
                u=[ux],
                v=[uy],
                w=[0],
                sizemode="absolute",
                sizeref=0.2,
                anchor="tail",
                showscale=False,
                colorscale="Blues",
                name="Drone Facing"
            ))

            fig.update_layout(
                scene=dict(
                    xaxis_title='X (meters)',
                    yaxis_title='Y (meters)',
                    zaxis_title='Altitude (meters)',
                    aspectmode='data'
                ),
                title='Enhanced 3D Drone Flight Path',
                margin=dict(l=0, r=0, b=0, t=30),
                legend=dict(x=0.02, y=0.98)
            )

            fig.show()

    def detect_obstacle(self, threshold=0.3):
        if self.real_drone:
            return any(
                distance is not None and distance < threshold
                for distance in [self.ranger.front, self.ranger.back, self.ranger.left, self.ranger.right, self.ranger.up]
            )
        return False

    
    def get_distances(self):
        if self.real_drone:
            return {
                "front": self.ranger.front if self.ranger.front is not None else "No Data",
                "back": self.ranger.back if self.ranger.back is not None else "No Data",
                "left": self.ranger.left if self.ranger.left is not None else "No Data",
                "right": self.ranger.right if self.ranger.right is not None else "No Data",
                "up": self.ranger.up if self.ranger.up is not None else "No Data"
            }
        else:
            # Simulated obstacle values (can be randomized or tuned later)
            return {
                "front": 0.6,
                "back": 1.0,
                "left": 0.8,
                "right": 1.2,
                "up": 0.5
            }
        return {k: "Simulated" for k in ["front", "back", "left", "right", "up"]}

    def execute_commands(self, commands, avoid_obstacles=False):
        for action, value in commands:
            if avoid_obstacles and self.detect_obstacle():
                print("Obstacle detected! Stopping movement.")
                if self.real_drone:
                    self.mc.stop()
                break
            action(value)
            time.sleep(0.5)

    def reset(self):
        print("Resetting simulation...")
        self._init_state()

    def save(self, file_path='commands.json'):
        with open(file_path, 'w') as json_file:
            json.dump(self.command_log, json_file, indent=4)
        print(f"Commands saved to {file_path}")

    def close(self):
        if self.real_drone:
            print("🔄 Closing connection...")
            self.mc.stop()
            self.ranger.stop()
            self.mc.__exit__(None, None, None)
            self.scf.__exit__(None, None, None)

    def load_commands(self, file_path):
        with open(file_path) as json_file:
            commands = json.load(json_file)
        self._init_state()
        for command in commands:
            getattr(self, command['command'])(*command['arguments'])
