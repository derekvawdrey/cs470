import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
from copy import deepcopy

from .basicgeometry import OrientedCircle, LineSegment
from .utils import minimized_angle

class RobotArtist:
    def __init__(self):
        self.artists = {}

    def setup(self, robot, obstacles):
        self.artists["core"] = plt.Circle(
                robot.position, 
                robot.radius, 
                color=robot.rgb,
                alpha=1.0,
                fill=True
            )
        command = robot.command_trajectory if robot.command_trajectory is not None else np.zeros(2)
        self.artists["command"] = ConnectionPatch(
            robot.position, 
            robot.position + command * robot.radius * 2, 
            'data', 
            'data', 
            color=(0.2, 1.0, 0.2), 
            arrowstyle='->',
            linewidth=2
        )
        self.artists["heading"] = ConnectionPatch(
                robot.position, 
                robot.position + robot.heading * robot.radius, 
                'data', 
                'data', 
                color=(1.0, 1.0, 0.5), 
                arrowstyle='->',
                linewidth=2
            )
        self.artists['sensor_bars'] = []
        sensor_bars = robot.get_sensor_reading(obstacles)
        for sensor_bar in sensor_bars:
            self.artists[f'sensor_bars'].append(
                ConnectionPatch(
                    sensor_bar.start_pos, 
                    sensor_bar.end_pos, 
                    'data', 
                    'data', 
                    color=sensor_bar.rgb, 
                    linewidth=2
                )
            )
        return [
            self.artists["core"],
            self.artists["command"],
            self.artists["heading"],
            *self.artists['sensor_bars']
        ]


    def update(self, robot, obstacles):
        self.artists["core"].center = robot.position
        command = robot.command_trajectory if robot.command_trajectory is not None else np.zeros(2)
        self.artists["command"].xy1 = robot.position
        self.artists["command"].xy2 = robot.position + command * robot.radius * 2
        self.artists["heading"].xy1 = robot.position
        self.artists["heading"].xy2 = robot.position + robot.heading * robot.radius
        sensor_bars = robot.get_sensor_reading(obstacles)
        for i, sensor_bar in enumerate(sensor_bars):
            self.artists[f'sensor_bars'][i].xy1 = sensor_bar.start_pos
            self.artists[f'sensor_bars'][i].xy2 = sensor_bar.end_pos

        return [
            self.artists["core"],
            self.artists["command"],
            self.artists["heading"],
            *self.artists['sensor_bars']
        ]

class SensorBar(LineSegment):
    def __init__(self, start_pos, end_pos, rgb):
        super().__init__(start_pos, end_pos)
        self.rgb = rgb

class Robot(OrientedCircle):
    def __init__(self, id, position, radius, heading, sensor_range, speed, spin, bias, rgb):
        super().__init__(position, radius, heading)
        self.id = id
        self.spin = spin
        self.speed = speed
        self.bias = bias # Not used in this version
        self.num_sensors = 16
        theta = 2*np.pi / self.num_sensors
        self.sensor_headings = np.array([
            np.array([np.cos(theta*i), np.sin(theta*i)])
            for i in range(self.num_sensors)
        ])
        self.command_trajectory = None
        self.command_complete = False
        self.sensor_range = sensor_range
        self.rgb = rgb

    def rotate_heading(self, angle_radians):
        super().rotate_heading(angle_radians)
        self.sensor_headings = (self.rotation_matrix @ self.sensor_headings.T).T

    def move_forward(self, step_size):
        self.position += self.heading * step_size

    def get_sensor_bars(self):
        return [
            SensorBar(
                self.sensor_headings[i] * self.radius + self.position, 
                self.sensor_headings[i] * (self.radius + self.sensor_range) + self.position,
                (0.0, 0.85, 0.85) if np.all(np.isclose(self.sensor_headings[i], self.heading)) else (0.85, 0.0, 0.85)
            )
            for i in range(self.num_sensors)
        ]
    
    def get_sensor_reading(self, obstacles):
        sensor_bars = self.get_sensor_bars()
        for i in range(self.num_sensors):
            for obstacle in obstacles:
                hit, hit_pos = sensor_bars[i].check_intersection(obstacle)
                if hit:
                    sensor_bars[i].end_pos = np.asarray(hit_pos)

        return sensor_bars
    
    def act(self, trajectory, rate, obstacles):
        if np.linalg.norm(trajectory) == 0.0:
            return
        self.command_trajectory = trajectory
        dtime = 0.1
        theta_traj = np.arctan2(trajectory[1], trajectory[0])
        theta_heading = np.arctan2(self.heading[1], self.heading[0])
        dtheta = np.degrees(minimized_angle(theta_heading - theta_traj))
        if np.abs(dtheta) < 1.5:
            move_dist = self.speed * rate * dtime
            prev_position = deepcopy(self.position)
            hit_obstacle = True
            decay = 1.0
            while hit_obstacle:
                self.move_forward(move_dist * decay)
                hit_obstacle = False
                for obstacle in obstacles:
                    if self.check_intersection(obstacle)[0]:
                        decay = max(0, decay - 0.05)
                        self.position = deepcopy(prev_position)
                        hit_obstacle = True
                        break
            self.command_complete = True
        else:
            self.command_complete = False
            direction = -1 if dtheta > 0 else 1
            dRot = np.radians(self.spin * rate * dtime * direction)
            self.rotate_heading(dRot)

    def get_json(self):
        return {
            "id": self.id,
            "color": self.rgb,
            "heading": tuple(self.heading),
            "position": tuple(self.position),
            "radius": self.radius,
            "spin": self.spin,
            "speed": self.speed,
            "bias": self.bias,
            "sensor_range": self.sensor_range
        }        