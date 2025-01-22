import numpy as np
from copy import deepcopy
import pandas as pd
from datetime import datetime
import json

from .robot import Robot
from .goal import Goal
from .obstacle import Obstacle

class Environment:
    def __init__(self):
        self.robot = None
        self.goal = None
        self.obstacles = []
        self.xmin, self.xmax = float('inf'), float('-inf')
        self.ymin, self.ymax = float('inf'), float('-inf')
        self.steps = 0
        self.data_record = []
        self.recording = False
        self.complete = False

    def load_file(self, filename):
        self.robot = None
        self.goal = None
        self.obstacles = []
        self.xmin, self.xmax = float('inf'), float('-inf')
        self.ymin, self.ymax = float('inf'), float('-inf')
        self.steps = 0
        self.complete = False
        with open(f'./maps/{filename}', 'r') as file:
            data = json.load(file)
            robot_data = data["robot"]
            self.robot = Robot(
                id=robot_data['id'],
                position=robot_data['position'],
                radius=robot_data['radius'],
                heading=robot_data['heading'], 
                sensor_range=robot_data['sensor_range'], 
                speed=robot_data['speed'], 
                spin=robot_data['spin'], 
                bias=robot_data['bias'], 
                rgb=robot_data['color']

            )
            goal_data = data["goal"]
            self.goal = Goal(
                id=goal_data['id'],
                position=goal_data['position'],
                radius=goal_data['radius']
            )
            all_obstacles_data = data['obstacles']
            for obstacle_data in all_obstacles_data:
                new_obstacle = Obstacle(
                    id=obstacle_data['id'],
                    start_pos=obstacle_data['start_pos'],
                    end_pos=obstacle_data['end_pos'],
                    rgb=obstacle_data['color']
                )
                self.obstacles.append(new_obstacle)
                self.xmin = np.amin([self.xmin, new_obstacle.start_pos[0], new_obstacle.end_pos[0]])
                self.ymin = np.amin([self.ymin, new_obstacle.start_pos[1], new_obstacle.end_pos[1]])
                self.xmax = np.amax([self.xmax, new_obstacle.start_pos[0], new_obstacle.end_pos[0]])
                self.ymax = np.amax([self.ymax, new_obstacle.start_pos[1], new_obstacle.end_pos[1]])

    def update(self, robot_command):
        if self.recording:
            robot_pos, goal_pos, dist_sensors = self.get_robot_data()
            self.data_record.append(
                {
                    "robot_pos_x": robot_pos[0],
                    "robot_pos_y": robot_pos[1],
                    "robot_pos_theta": robot_pos[2],
                    "goal_pos_x": goal_pos[0],
                    "goal_pos_y": goal_pos[1],
                    **{
                        f"dist_sensor_{i}": dist_sensor_val 
                        for i, dist_sensor_val in enumerate(dist_sensors)
                    },
                    "step": self.steps,
                    "command_type": robot_command["category"],
                    "trajectory_x": robot_command["trajectory"][0],
                    "trajectory_y": robot_command["trajectory"][1]
                }
            )
        trajectory = self.robot.command_trajectory
        if trajectory is None or robot_command["override"] or (self.robot.command_complete):
            trajectory = robot_command["trajectory"]
        rate = 1.0
        self.robot.act(trajectory, rate, self.obstacles)
        self.steps += 1
        if self.robot.overlaps_with(self.goal):
            self.complete = True
        else:
            self.complete = False

    def reset_record(self):
        self.data_record = []

    def save_record(self):
        if len(self.data_record) > 0:
            record_df = pd.DataFrame(self.data_record)
            timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
            record_df.to_csv(f'./data/robot_recording_{timestamp}.csv', index=False)

    def get_record_size(self):
        return len(self.data_record)

    def reset_steps(self):
        self.steps = 0

    def get_step_count(self):
        return self.steps

    def set_robot_pos(self, new_pos):
        prev_pos = deepcopy(self.robot.position)
        self.robot.position = new_pos
        for obstacle in self.obstacles:
            if self.robot.check_intersection(obstacle)[0]:
                self.robot.position = prev_pos
                break

    def get_robot_data(self):
        return self._robot_features(self.robot)
    
    def _robot_features(self, robot):
        robot_pos = np.array([
            *robot.position, 
            np.degrees(np.arctan2(robot.heading[1], robot.heading[0]))
        ]) 
        goal_pos = self.goal.position
        dist_sensors = np.array([
            sensor_reading.get_length() + robot.radius
            for sensor_reading in robot.get_sensor_reading(self.obstacles)
        ])
        return robot_pos, goal_pos, dist_sensors
    
    def get_action_field(self, agent, force_load=False):
        step_size = self.robot.radius
        robot_clone = deepcopy(self.robot)
        X, Y = np.meshgrid(
                    np.arange(self.xmin + step_size, self.xmax, step_size*2), 
                    np.arange(self.ymin + step_size, self.ymax, step_size*2)
                )
        u = []
        v = []
        for (x, y) in zip(X.flatten(), Y.flatten()):
            if force_load:
                robot_clone.position = np.array([x, y])
                robot_pos, goal_pos, dist_sensors = self._robot_features(robot_clone)
                trajectory = agent.act(robot_pos, goal_pos, dist_sensors)
            else:
                trajectory = np.ones(2)
            u.append(trajectory[0])
            v.append(trajectory[1])
        
        U = np.array(u).reshape(X.shape)
        V = np.array(v).reshape(X.shape)

        return X, Y, U, V
    
    def save(self, outfile):
        save_data = {
            "robot": self.robot.get_json(),
            "goal": self.goal.get_json(),
            "obstacles": [
                obstacle.get_json() for obstacle in self.obstacles
            ]
        }

        with open(f'./maps/{outfile}', "w") as f:
            json.dump(save_data, f)