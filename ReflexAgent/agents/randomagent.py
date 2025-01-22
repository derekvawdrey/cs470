import numpy as np

from .baseagent import Agent

class RandomAgent(Agent):
    def __init__(self):
        super().__init__()

    def act(self, robot_pos, goal_pos, dist_sensors):
        random_dir = np.random.uniform(-1, 1, size=2)
        return random_dir / np.linalg.norm(random_dir, ord=2)