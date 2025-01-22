import numpy as np
import math

from .baseagent import Agent

ANGLE_BETWEEN_SENSORS = 22.5
GOAL_RADIUS = 5
OBSTACLE_RADIUS = 6

class PFAgent(Agent):
    def __init__(self):
        super().__init__()
        self.obstacles = []

    def calculate_vector(self,x1,x2,y1,y2):
        return x2-x1,y2-y1

    def calculate_goal_delta(self, alpha, theta, distance, r):
        d_x,d_y = 0,0
        s = 4
        if r <= distance <= s + r:
            d_x = alpha * (distance - r) * math.cos(theta)
            d_y = alpha * (distance - r) * math.sin(theta)
        elif distance > s + r:
            d_x = alpha * s * math.cos(theta)
            d_y = alpha * s * math.sin(theta) 


        return d_x, d_y
        

        
    def calculate_obstacle_delta(self, beta, theta, distance, r):
        d_x,d_y = 0, 0
        s = 4
        if distance < r:
            d_x = -np.sign(math.cos(theta)) * 1000
            d_y = -np.sign(math.sin(theta)) * 1000
        elif r <= distance <= s + r:
            d_x = -beta * (s + r - distance) * math.cos(theta)
            d_y = -beta * (s + r - distance) * math.sin(theta)
            

        return d_x, d_y
    def act(self, robot_pos, goal_pos, dist_sensors):
        
        x_dir,y_dir = self.calculate_vector(robot_pos[0],goal_pos[0],robot_pos[1],goal_pos[1])
        
        distance = math.sqrt(x_dir**2 + y_dir**2)
        theta = math.atan2(y_dir,x_dir)
        alpha = 1.1
        change_in_x, change_in_y = self.calculate_goal_delta(
            alpha, 
            theta,
            distance,
            GOAL_RADIUS
        )

        trajectory = [change_in_x,change_in_y]

        for i in range(len(dist_sensors)):
            curr_angle = (i * ANGLE_BETWEEN_SENSORS) + robot_pos[2]
            obs_theta = ((curr_angle) * math.pi) / 180.0 
            beta = 1.2
            obs_d_x, obs_d_y = self.calculate_obstacle_delta(
                beta, 
                obs_theta, 
                dist_sensors[i], 
                6
            )
            trajectory[0] += obs_d_x
            trajectory[1] += obs_d_y

        trajectory_norm = np.linalg.norm(trajectory)
        if trajectory_norm != 0:
            trajectory = trajectory / trajectory_norm

        return trajectory
